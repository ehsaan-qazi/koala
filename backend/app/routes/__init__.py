from app.routes.auth import router as auth_router
from app.routes.courses import router as courses_router
from app.routes.billing import router as billing_router

__all__ = ["auth_router", "courses_router", "billing_router"]
