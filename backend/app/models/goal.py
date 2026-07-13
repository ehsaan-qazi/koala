"""Goal model — semester goals with optional GPA target."""

from datetime import datetime, date
from sqlalchemy import (
    String, Integer, Boolean, Text, Numeric, Date, DateTime, ForeignKey, Index, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100))
    semester: Mapped[str | None] = mapped_column(String(50))
    target_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Active", server_default="Active")
    is_gpa_goal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    gpa_target: Mapped[float | None] = mapped_column(Numeric(4, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="goals")

    __table_args__ = (
        Index("idx_goals_user_id", "user_id"),
    )
