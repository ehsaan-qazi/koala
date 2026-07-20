"""
Admin routes — internal operational endpoints.
Requires authentication (any authenticated user can view; you could restrict to admins later).
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.groq_router import get_router, GROQ_MODEL_PRIORITY, COOLDOWN_SECONDS, FAILURE_THRESHOLD

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/llm/status")
async def get_llm_status(current_user: User = Depends(get_current_user)) -> dict:
    """
    Return the current circuit-breaker state for each Groq model.

    Useful for debugging rate-limit fallback behavior at runtime.

    Requires admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    router_instance = get_router()
    return {
        "config": {
            "failure_threshold": FAILURE_THRESHOLD,
            "cooldown_seconds": COOLDOWN_SECONDS,
            "model_priority": GROQ_MODEL_PRIORITY,
        },
        "models": router_instance.status(),
    }
