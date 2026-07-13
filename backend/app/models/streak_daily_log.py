"""StreakDailyLog model — heatmap data for daily activity."""

from datetime import date
from sqlalchemy import Integer, Date, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class StreakDailyLog(Base):
    __tablename__ = "streak_daily_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    action_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    __table_args__ = (
        UniqueConstraint("user_id", "log_date", name="uq_streak_log_user_date"),
        Index("idx_streak_log_user_date", "user_id", "log_date"),
    )
