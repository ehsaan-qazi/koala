"""Course model."""

from datetime import datetime
from sqlalchemy import (
    String, Integer, Boolean, Numeric, DateTime, ForeignKey, Index, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50))
    semester: Mapped[str] = mapped_column(String(50), nullable=False)
    academic_year: Mapped[str | None] = mapped_column(String(20))
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    # GPA fields
    credit_hours: Mapped[float | None] = mapped_column(Numeric(4, 2))
    grade_letter: Mapped[str | None] = mapped_column(String(5))
    grade_scale: Mapped[str] = mapped_column(String(10), nullable=False, default="4.0", server_default="4.0")

    # Upload limit tracking
    doc_upload_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="courses")
    documents = relationship("Document", back_populates="course", cascade="all, delete-orphan")
    roadmap_nodes = relationship("RoadmapNode", back_populates="course", cascade="all, delete-orphan")
    topics = relationship("Topic", back_populates="course", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_courses_user_id", "user_id"),
        Index("idx_courses_semester", "user_id", "semester", "academic_year"),
    )
