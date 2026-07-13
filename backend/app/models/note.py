"""Note model — markdown notes with bi-directional linking."""

from datetime import datetime
from sqlalchemy import (
    String, Integer, Boolean, Text, DateTime, ForeignKey, Index, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("courses.id", ondelete="SET NULL"))
    roadmap_node_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("roadmap_nodes.id", ondelete="SET NULL"))
    topic_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("topics.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    is_stub: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    is_quick_capture: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="notes")
    roadmap_node = relationship("RoadmapNode", back_populates="notes")
    topic = relationship("Topic", back_populates="notes")

    __table_args__ = (
        Index("idx_notes_user_id", "user_id"),
        Index("idx_notes_course_id", "course_id"),
        Index("idx_notes_roadmap_node", "roadmap_node_id"),
        Index("idx_notes_topic", "topic_id"),
    )
