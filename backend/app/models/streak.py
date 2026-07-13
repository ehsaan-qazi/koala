"""Streak model — user activity and on-time streaks."""

from datetime import datetime, date
from sqlalchemy import Integer, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Streak(Base):
    __tablename__ = "streaks"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    activity_streak_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    on_time_streak_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    longest_activity_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    longest_on_time_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    last_activity_date: Mapped[date | None] = mapped_column(Date)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
