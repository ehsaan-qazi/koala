"""
Auth middleware — validates Supabase JWT and resolves to our app User.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
import httpx

from app.config import settings
from app.database import get_db
from app.models.user import User

# Supabase uses HS256 JWTs signed with the JWT secret
ALGORITHM = "HS256"

# FastAPI security scheme — extracts Bearer token from Authorization header
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency that:
    1. Decodes the Supabase JWT from the Authorization header
    2. Extracts the Supabase user ID (sub claim)
    3. Looks up or creates the user in our database
    4. Returns the User ORM object

    If JWT_SECRET is not set, falls back to calling Supabase's /auth/v1/user
    endpoint to verify the token (slower but works without the secret).
    """
    token = credentials.credentials

    supabase_uid: str | None = None
    email: str | None = None
    full_name: str | None = None
    avatar_url: str | None = None

    # Strategy 1: Local JWT verification (fast, preferred)
    if settings.supabase_jwt_secret:
        try:
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=[ALGORITHM],
                audience="authenticated",
            )
            supabase_uid = payload.get("sub")
            email = payload.get("email")
            # User metadata may contain name/avatar from Google OAuth
            user_metadata = payload.get("user_metadata", {})
            full_name = user_metadata.get("full_name") or user_metadata.get("name")
            avatar_url = user_metadata.get("avatar_url") or user_metadata.get("picture")
        except JWTError as e:
            print(f"JWT Verification Failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
    else:
        # Strategy 2: Verify via Supabase API (slower fallback)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.supabase_url}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.supabase_anon_key,
                },
            )
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                )
            data = resp.json()
            supabase_uid = data.get("id")
            email = data.get("email")
            user_metadata = data.get("user_metadata", {})
            full_name = user_metadata.get("full_name") or user_metadata.get("name")
            avatar_url = user_metadata.get("avatar_url") or user_metadata.get("picture")

    if not supabase_uid or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not identify user from token",
        )

    # Look up user in our database
    result = await db.execute(
        select(User).where(User.supabase_uid == supabase_uid)
    )
    user = result.scalar_one_or_none()

    # Auto-create user on first login (sync from Supabase auth)
    if user is None:
        user = User(
            supabase_uid=supabase_uid,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
            plan="free",
        )
        db.add(user)
        await db.flush()  # get the ID assigned

    # Update profile fields if they changed (e.g., user updated Google profile)
    else:
        changed = False
        if full_name and user.full_name != full_name:
            user.full_name = full_name
            changed = True
        if avatar_url and user.avatar_url != avatar_url:
            user.avatar_url = avatar_url
            changed = True
        if email and user.email != email:
            user.email = email
            changed = True
        if changed:
            await db.flush()

    return user
