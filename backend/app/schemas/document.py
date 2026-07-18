"""Document schemas — request/response models for file uploads."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentResponse(BaseModel):
    """Full document metadata returned to the client."""
    id: int
    course_id: int
    user_id: int
    doc_type: str
    original_filename: str
    r2_key: str
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    sha256: Optional[str] = None
    processing_status: str
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    uploaded_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListItem(BaseModel):
    """Lightweight document for list views."""
    id: int
    doc_type: str
    original_filename: str
    size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    processing_status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True
