"""TopicCompletion model — student progress on individual topics."""

from datetime import datetime
from sqlalchemy import (
    Integer, Boolean, SmallInteger, DateTime, ForeignKey, Index, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TopicCompletion(Base):
    __tablename__ = "topic_completions"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    confidence_rating: Mapped[int | None] = mapped_column(SmallInteger)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    linked_note_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("notes.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    topic = relationship("Topic", back_populates="completions")

    __table_args__ = (
        UniqueConstraint("topic_id", "user_id", name="uq_topic_completions_topic_user"),
        Index("idx_topic_completions_user", "user_id"),
    )
