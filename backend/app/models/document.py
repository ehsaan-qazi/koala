"""Document model — uploaded files (syllabus, CLO, notes, slides).

Enriched metadata schema for Cloudflare R2 object storage:
- original_filename: display name for the user
- r2_key: object key in R2 bucket
- mime_type: content type validation
- size_bytes: file size display + limit enforcement
- sha256: integrity checks + duplicate detection
"""

from datetime import datetime
from sqlalchemy import (
    String, Integer, Text, DateTime, ForeignKey, Index, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # File metadata
    doc_type: Mapped[str] = mapped_column(String(50), nullable=False)  # syllabus|clo|instructor_notes|slides|academic_calendar
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    r2_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    mime_type: Mapped[str | None] = mapped_column(String(100))
    size_bytes: Mapped[int | None] = mapped_column(Integer)
    sha256: Mapped[str | None] = mapped_column(String(64))  # 64 hex chars for SHA-256

    # Processing state (AI extraction)
    processing_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending", server_default="pending"
    )  # pending|processing|processed|failed
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)

    # Timestamps
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    course = relationship("Course", back_populates="documents")
    topics = relationship("Topic", back_populates="source_document")

    __table_args__ = (
        Index("idx_documents_course_id", "course_id"),
        Index("idx_documents_sha256", "user_id", "sha256"),
    )
