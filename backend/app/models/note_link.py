"""NoteLink model — bi-directional links between notes."""

from datetime import datetime
from sqlalchemy import (
    Integer, DateTime, ForeignKey, Index, UniqueConstraint, CheckConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NoteLink(Base):
    __tablename__ = "note_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_note_id: Mapped[int] = mapped_column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
    target_note_id: Mapped[int] = mapped_column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("source_note_id", "target_note_id", name="uq_note_links_source_target"),
        CheckConstraint("source_note_id != target_note_id", name="ck_note_links_no_self"),
        Index("idx_note_links_source", "source_note_id"),
        Index("idx_note_links_target", "target_note_id"),
    )
