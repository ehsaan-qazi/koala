"""Roadmap node schemas — request/response models for assessment items."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.roadmap_node import ALLOWED_NODE_TYPES  # type: ignore


class RoadmapNodeBase(BaseModel):
    title: str
    node_type: str = "Other"
    deadline: Optional[datetime] = None
    weight_percent: Optional[float] = None
    estimated_hours: Optional[float] = None
    status: str = "Pending"


class RoadmapNodeCreate(RoadmapNodeBase):
    pass


class RoadmapNodeUpdate(BaseModel):
    title: Optional[str] = None
    node_type: Optional[str] = None
    deadline: Optional[datetime] = None
    weight_percent: Optional[float] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    confidence_at_creation: Optional[int] = None
    status: Optional[str] = None


class RoadmapNodeResponse(RoadmapNodeBase):
    id: int
    course_id: int
    user_id: int
    source_document_id: Optional[int] = None
    is_placeholder: bool
    is_confirmed: bool
    extraction_confidence: Optional[float] = None
    actual_hours: Optional[float] = None
    confidence_at_creation: Optional[int] = None
    grade: Optional[float] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


ALLOWED_NODE_TYPE_VALUES = ALLOWED_NODE_TYPES
