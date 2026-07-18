"""
Groq model router — circuit-breaker-based fallback across multiple Groq models.

Pattern: Circuit Breaker (per-model state machine)
  CLOSED    → Model is healthy. All calls routed here.
  OPEN      → Model tripped (too many failures). Bypassed until cooldown expires.
  HALF_OPEN → Cooldown expired. One probe call allowed to test recovery.

Model priority list (highest priority first):
  1. llama-3.3-70b-versatile    — best quality, try first
  2. llama-3.1-70b-specdec      — fast speculative decoding fallback
  3. llama3-70b-8192            — stable older generation
  4. llama3-8b-8192             — lightweight last resort

Errors that trip a breaker:
  - groq.RateLimitError (HTTP 429)      — rate limit hit
  - groq.APIStatusError with 503/529    — overloaded / service unavailable
  - groq.APITimeoutError                — inference timeout

Errors that do NOT trip a breaker:
  - groq.BadRequestError               — bad prompt / content policy (our bug)
  - groq.AuthenticationError           — bad API key (our bug)
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum

from groq import (
    APIStatusError,
    APITimeoutError,
    RateLimitError,
    Groq,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

# Chat/completion models only — ordered from highest to lowest preference.
# Non-chat models (whisper, prompt-guard, etc.) are intentionally excluded.
GROQ_MODEL_PRIORITY: list[str] = [
    "openai/gpt-oss-120b",                        # 1. Largest, highest capability
    "groq/compound",                               # 2. Groq's own compound reasoning model
    "qwen/qwen3.6-27b",                            # 3. Qwen 3.6 27B
    "qwen/qwen3-32b",                              # 4. Qwen 3 32B
    "llama-3.3-70b-versatile",                     # 5. Llama 3.3 70B — reliable workhorse
    "groq/compound-mini",                          # 6. Groq compound (smaller)
    "meta-llama/llama-4-scout-17b-16e-instruct",   # 7. Llama 4 Scout 17B MoE
    "llama-3.1-8b-instant",                        # 8. Last resort — fast 8B
]

# How many consecutive failures before tripping the breaker
FAILURE_THRESHOLD: int = 2

# How long (seconds) a tripped breaker stays OPEN before trying a probe
COOLDOWN_SECONDS: int = 60


# ──────────────────────────────────────────────────────────────────────────────
# State Machine
# ──────────────────────────────────────────────────────────────────────────────

class BreakerState(Enum):
    CLOSED = "closed"        # Healthy — normal routing
    OPEN = "open"            # Tripped — skip this model
    HALF_OPEN = "half_open"  # Cooldown expired — allow one probe


@dataclass
class CircuitBreaker:
    model: str
    state: BreakerState = BreakerState.CLOSED
    failure_count: int = 0
    opened_at: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def is_available(self) -> bool:
        """Return True if this breaker allows a call to be attempted."""
        with self._lock:
            if self.state == BreakerState.CLOSED:
                return True
            if self.state == BreakerState.OPEN:
                if time.monotonic() - self.opened_at >= COOLDOWN_SECONDS:
                    logger.info(
                        "[GroqRouter] Breaker for %s entering HALF_OPEN (probe allowed)",
                        self.model,
                    )
                    self.state = BreakerState.HALF_OPEN
                    return True
                return False
            # HALF_OPEN — allow exactly one probe through
            return True

    def record_success(self) -> None:
        """Reset breaker to CLOSED after a successful call."""
        with self._lock:
            if self.state != BreakerState.CLOSED:
                logger.info(
                    "[GroqRouter] %s recovered → CLOSED (failure_count reset)",
                    self.model,
                )
            self.state = BreakerState.CLOSED
            self.failure_count = 0
            self.opened_at = 0.0

    def record_failure(self) -> None:
        """Increment failure count; trip breaker when threshold is reached."""
        with self._lock:
            self.failure_count += 1
            if self.state == BreakerState.HALF_OPEN:
                # Probe failed — go back to OPEN and restart cooldown
                logger.warning(
                    "[GroqRouter] %s probe FAILED → back to OPEN for %ds",
                    self.model, COOLDOWN_SECONDS,
                )
                self.state = BreakerState.OPEN
                self.opened_at = time.monotonic()
            elif self.failure_count >= FAILURE_THRESHOLD:
                logger.warning(
                    "[GroqRouter] %s hit %d failures → OPEN for %ds",
                    self.model, self.failure_count, COOLDOWN_SECONDS,
                )
                self.state = BreakerState.OPEN
                self.opened_at = time.monotonic()
            else:
                logger.warning(
                    "[GroqRouter] %s failure %d/%d",
                    self.model, self.failure_count, FAILURE_THRESHOLD,
                )


# ──────────────────────────────────────────────────────────────────────────────
# Router (singleton)
# ──────────────────────────────────────────────────────────────────────────────

class GroqModelRouter:
    """
    Manages a pool of Groq models with per-model circuit breakers.
    Call `.chat()` the same way you'd call Groq's API — the router
    handles model selection and fallback transparently.
    """

    def __init__(self, api_key: str) -> None:
        self._client = Groq(api_key=api_key)
        self._breakers: dict[str, CircuitBreaker] = {
            m: CircuitBreaker(model=m) for m in GROQ_MODEL_PRIORITY
        }

    def _is_transient_error(self, exc: Exception) -> bool:
        """
        True = the error is a capacity/rate issue → trip the breaker.
        False = the error is our fault → don't trip, just propagate.
        """
        if isinstance(exc, RateLimitError):
            return True
        if isinstance(exc, APITimeoutError):
            return True
        if isinstance(exc, APIStatusError) and exc.status_code in (503, 529):
            return True
        # BadRequestError, AuthenticationError, etc. are our bugs — don't trip
        return False

    def status(self) -> dict[str, dict]:
        """Return current state of all breakers (useful for health checks)."""
        result = {}
        for model, breaker in self._breakers.items():
            time_until_retry = None
            if breaker.state == BreakerState.OPEN:
                elapsed = time.monotonic() - breaker.opened_at
                remaining = COOLDOWN_SECONDS - elapsed
                time_until_retry = max(0, round(remaining))
            result[model] = {
                "state": breaker.state.value,
                "failure_count": breaker.failure_count,
                "time_until_retry_seconds": time_until_retry,
            }
        return result

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ) -> tuple[str, str]:
        """
        Attempt a chat completion using the highest-priority available model.
        Falls back through the priority list on transient errors.

        Returns:
            (response_text, model_used) — the raw content and the model name.

        Raises:
            RuntimeError if all models are unavailable or all failed.
        """
        tried: list[str] = []

        for model in GROQ_MODEL_PRIORITY:
            breaker = self._breakers[model]

            if not breaker.is_available():
                logger.debug("[GroqRouter] Skipping %s (breaker %s)", model, breaker.state.value)
                continue

            tried.append(model)
            logger.info("[GroqRouter] Attempting model: %s", model)

            try:
                completion = self._client.chat.completions.create(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                breaker.record_success()
                content = completion.choices[0].message.content.strip()
                logger.info("[GroqRouter] Success with model: %s", model)
                return content, model

            except Exception as exc:
                if self._is_transient_error(exc):
                    logger.warning(
                        "[GroqRouter] Transient error on %s (%s: %s) — trying next model",
                        model, type(exc).__name__, exc,
                    )
                    breaker.record_failure()
                    continue  # Try next model
                else:
                    # Non-transient (our bug) — don't fallback, raise immediately
                    logger.error(
                        "[GroqRouter] Non-transient error on %s (%s): %s",
                        model, type(exc).__name__, exc,
                    )
                    raise

        raise RuntimeError(
            f"All Groq models exhausted or unavailable. Tried: {tried}. "
            "Check model availability or try again later."
        )


# ──────────────────────────────────────────────────────────────────────────────
# Module-level singleton — shared across all requests in the process
# ──────────────────────────────────────────────────────────────────────────────
# Initialized lazily so config is fully loaded before first use.
_router_instance: GroqModelRouter | None = None
_router_lock = threading.Lock()


def get_router() -> GroqModelRouter:
    """Return the shared GroqModelRouter singleton, creating it on first call."""
    global _router_instance
    if _router_instance is None:
        with _router_lock:
            if _router_instance is None:
                from app.config import settings
                _router_instance = GroqModelRouter(api_key=settings.llm_api_key)
                logger.info(
                    "[GroqRouter] Initialized with %d models: %s",
                    len(GROQ_MODEL_PRIORITY), GROQ_MODEL_PRIORITY,
                )
    return _router_instance
