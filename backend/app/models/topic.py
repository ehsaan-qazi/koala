"""Topic model — course content units extracted from notes/slides."""

from datetime import datetime
from sqlalchemy import (
    String, Integer, Boolean, DateTime, ForeignKey, Index, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source_document_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("documents.id", ondelete="SET NULL"))
    linked_node_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("roadmap_nodes.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    is_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    course = relationship("Course", back_populates="topics")
    source_document = relationship("Document", back_populates="topics")
    linked_node = relationship("RoadmapNode", back_populates="topics")
    completions = relationship("TopicCompletion", back_populates="topic", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="topic")

    __table_args__ = (
        Index("idx_topics_course_id", "course_id"),
        Index("idx_topics_order", "course_id", "order_index"),
    )
