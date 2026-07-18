"""Topic schemas — request/response models for course topics."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TopicCreate(BaseModel):
    """Create a new topic manually."""
    title: str
    order_index: int = 0


class TopicUpdate(BaseModel):
    """Update topic fields."""
    title: Optional[str] = None
    order_index: Optional[int] = None


class TopicToggle(BaseModel):
    """Toggle topic completion."""
    is_completed: bool
    confidence_rating: Optional[int] = None  # 1-5


class TopicResponse(BaseModel):
    """Full topic returned to client."""
    id: int
    course_id: int
    title: str
    order_index: int
    is_confirmed: bool
    source_document_id: Optional[int] = None
    linked_node_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TopicWithCompletion(TopicResponse):
    """Topic with current user's completion state."""
    is_completed: bool = False
    confidence_rating: Optional[int] = None
