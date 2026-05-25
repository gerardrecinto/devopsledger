import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.decision_record import DecisionRecord


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    decision_record_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("decision_records.id", ondelete="CASCADE"), unique=True
    )
    score: Mapped[int] = mapped_column(Integer)
    severity: Mapped[str] = mapped_column(String(50))
    reasons: Mapped[Any] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    decision_record: Mapped["DecisionRecord"] = relationship(back_populates="risk_assessment")
