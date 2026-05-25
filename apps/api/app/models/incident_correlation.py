import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.decision_record import DecisionRecord


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IncidentCorrelation(Base):
    __tablename__ = "incident_correlations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    decision_record_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("decision_records.id", ondelete="CASCADE")
    )
    incident_source: Mapped[str] = mapped_column(String(100))
    incident_title: Mapped[str] = mapped_column(String(500))
    incident_url: Mapped[Optional[str]] = mapped_column(String(1000))
    service_name: Mapped[Optional[str]] = mapped_column(String(200))
    environment: Mapped[Optional[str]] = mapped_column(String(100))
    severity: Mapped[Optional[str]] = mapped_column(String(50))
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    correlation_reason: Mapped[Optional[str]] = mapped_column(Text)
    confidence: Mapped[str] = mapped_column(String(50), default="possible", server_default="possible")
    raw_payload: Mapped[Optional[Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    decision_record: Mapped["DecisionRecord"] = relationship(back_populates="incident_correlations")
