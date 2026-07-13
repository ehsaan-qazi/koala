"""GpaEntry model — per-course grade entries and historical semester aggregates."""

from datetime import datetime
from sqlalchemy import (
    String, Integer, Numeric, DateTime, ForeignKey, Index, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GpaEntry(Base):
    __tablename__ = "gpa_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    semester: Mapped[str] = mapped_column(String(50), nullable=False)
    academic_year: Mapped[str | None] = mapped_column(String(20))
    entry_type: Mapped[str] = mapped_column(String(20), nullable=False)  # course|historical
    course_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("courses.id", ondelete="SET NULL"))
    course_label: Mapped[str] = mapped_column(String(255), nullable=False)
    credit_hours: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    grade_letter: Mapped[str | None] = mapped_column(String(5))
    semester_gpa: Mapped[float | None] = mapped_column(Numeric(4, 2))
    grade_scale: Mapped[str] = mapped_column(String(10), nullable=False, default="4.0", server_default="4.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="gpa_entries")

    __table_args__ = (
        Index("idx_gpa_entries_user", "user_id"),
        Index("idx_gpa_entries_semester", "user_id", "semester", "academic_year"),
    )
