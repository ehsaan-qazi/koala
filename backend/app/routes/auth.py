from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.auth import UserResponse, UserUpdate

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently logged in user based on the Supabase JWT token."""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile information."""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.institution is not None:
        current_user.institution = user_update.institution
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url
    
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.post("/callback", response_model=UserResponse)
async def auth_callback(current_user: User = Depends(get_current_user)):
    """
    Called by the frontend after a successful Supabase login.
    The `get_current_user` dependency automatically handles creating
    or updating the user record in our database based on the JWT token.
    """
    return current_user
