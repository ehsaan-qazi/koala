"""Auth schemas."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    institution: Optional[str] = None
    avatar_url: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    institution: Optional[str] = None
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: int
    plan: str
    plan_expires_at: Optional[datetime] = None
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
