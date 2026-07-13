"""
Tier gate middleware — enforces Free/Pro tier restrictions.
"""

from datetime import datetime, timezone
from fastapi import HTTPException, status

from app.models.user import User
from app.models.course import Course
from app.config import settings


def require_pro(user: User) -> None:
    """
    Raises 403 if user is not on Pro plan (or plan has expired).
    Admin users bypass this check entirely.
    """
    if user.is_admin:
        return

    if user.plan != "pro":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "upgrade_required",
                "message": "This feature requires a Pro subscription.",
                "upgrade_url": "/settings",  # Frontend will show upgrade UI
            },
        )

    # Check if Pro plan has expired
    if user.plan_expires_at and user.plan_expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "plan_expired",
                "message": "Your Pro subscription has expired. Please renew to continue using Pro features.",
                "upgrade_url": "/settings",
            },
        )


def check_upload_limit(course: Course, user: User) -> None:
    """
    Raises 403 if the course has reached its document upload limit
    for the user's current tier. Admin users bypass this check.
    """
    if user.is_admin:
        return

    limit = settings.pro_upload_limit if user.plan == "pro" else settings.free_upload_limit

    if course.doc_upload_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "upload_limit_reached",
                "message": f"Upload limit reached ({course.doc_upload_count}/{limit} documents for this course).",
                "current_count": course.doc_upload_count,
                "limit": limit,
                "upgrade_url": "/settings" if user.plan == "free" else None,
            },
        )


def get_file_size_limit_bytes(user: User) -> int:
    """Returns the max file size in bytes for the user's tier."""
    if user.is_admin:
        return 100 * 1024 * 1024  # 100 MB for admin
    if user.plan == "pro":
        return settings.pro_max_file_size_mb * 1024 * 1024
    return settings.free_max_file_size_mb * 1024 * 1024
