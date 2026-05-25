import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import DateTime, ForeignKey, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.decision_record import DecisionRecord


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ChangeSource(Base):
    __tablename__ = "change_sources"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    decision_record_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("decision_records.id", ondelete="CASCADE")
    )
    source_type: Mapped[str] = mapped_column(String(100))
    external_id: Mapped[Optional[str]] = mapped_column(String(500))
    url: Mapped[Optional[str]] = mapped_column(String(1000))
    raw_payload: Mapped[Optional[Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    decision_record: Mapped["DecisionRecord"] = relationship(back_populates="change_sources")
