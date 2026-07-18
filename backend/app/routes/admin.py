"""
Admin routes — internal operational endpoints.
Requires authentication (any authenticated user can view; you could restrict to admins later).
"""

from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.groq_router import get_router, GROQ_MODEL_PRIORITY, COOLDOWN_SECONDS, FAILURE_THRESHOLD

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/llm/status")
async def get_llm_status(current_user: User = Depends(get_current_user)) -> dict:
    """
    Return the current circuit-breaker state for each Groq model.

    Useful for debugging rate-limit fallback behavior at runtime.

    Example response:
    {
      "config": { "failure_threshold": 2, "cooldown_seconds": 60 },
      "models": {
        "llama-3.3-70b-versatile": { "state": "closed", "failure_count": 0, ... },
        "llama-3.1-70b-specdec":   { "state": "open",   "failure_count": 2, "time_until_retry_seconds": 47 },
        ...
      }
    }
    """
    router_instance = get_router()
    return {
        "config": {
            "failure_threshold": FAILURE_THRESHOLD,
            "cooldown_seconds": COOLDOWN_SECONDS,
            "model_priority": GROQ_MODEL_PRIORITY,
        },
        "models": router_instance.status(),
    }
