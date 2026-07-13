"""SelfAssessmentLog model — reflection data attached to roadmap nodes."""

from datetime import datetime
from sqlalchemy import (
    Integer, SmallInteger, Text, Numeric, DateTime, ForeignKey, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SelfAssessmentLog(Base):
    __tablename__ = "self_assessment_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    roadmap_node_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roadmap_nodes.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quality_self_rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    mood_energy: Mapped[int | None] = mapped_column(SmallInteger)
    reflection_note: Mapped[str | None] = mapped_column(Text)
    hours_before_deadline: Mapped[float | None] = mapped_column(Numeric(8, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
