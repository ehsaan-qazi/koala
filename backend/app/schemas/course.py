"""Course schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CourseBase(BaseModel):
    name: str
    code: Optional[str] = None
    semester: str
    academic_year: Optional[str] = None
    is_archived: bool = False
    credit_hours: Optional[float] = None
    grade_letter: Optional[str] = None
    grade_scale: str = "4.0"

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    semester: Optional[str] = None
    academic_year: Optional[str] = None
    is_archived: Optional[bool] = None
    credit_hours: Optional[float] = None
    grade_letter: Optional[str] = None
    grade_scale: Optional[str] = None

class CourseResponse(CourseBase):
    id: int
    user_id: int
    doc_upload_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
