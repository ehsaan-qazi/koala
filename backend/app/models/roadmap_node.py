"""Roadmap Node model — assessment items on a course roadmap."""

# Allowed node types — must match the DB CHECK constraint on node_type
ALLOWED_NODE_TYPES = {"Assignment", "Quiz", "Exam", "Project", "Lab", "Other"}

from datetime import datetime
from sqlalchemy import (
    String, Integer, Boolean, Numeric, SmallInteger, DateTime, ForeignKey, Index, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RoadmapNode(Base):
    __tablename__ = "roadmap_nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source_document_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("documents.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    node_type: Mapped[str] = mapped_column(String(100), nullable=False, default="Other", server_default="Other")
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    weight_percent: Mapped[float | None] = mapped_column(Numeric(5, 2))
    is_placeholder: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    is_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    extraction_confidence: Mapped[float | None] = mapped_column(Numeric(3, 2))
    estimated_hours: Mapped[float | None] = mapped_column(Numeric(5, 2))
    actual_hours: Mapped[float | None] = mapped_column(Numeric(5, 2))
    confidence_at_creation: Mapped[int | None] = mapped_column(SmallInteger)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Pending", server_default="Pending")
    grade: Mapped[float | None] = mapped_column(Numeric(5, 2))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    course = relationship("Course", back_populates="roadmap_nodes")
    topics = relationship("Topic", back_populates="linked_node")
    notes = relationship("Note", back_populates="roadmap_node")

    __table_args__ = (
        Index("idx_roadmap_nodes_course_id", "course_id"),
        Index("idx_roadmap_nodes_user_id", "user_id"),
        Index("idx_roadmap_nodes_deadline", "user_id", "deadline"),
        Index("idx_roadmap_nodes_status", "user_id", "status"),
    )
