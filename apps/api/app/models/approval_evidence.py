import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.decision_record import DecisionRecord


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ApprovalEvidence(Base):
    __tablename__ = "approval_evidence"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    decision_record_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("decision_records.id", ondelete="CASCADE")
    )
    source: Mapped[str] = mapped_column(String(100))
    owner: Mapped[Optional[str]] = mapped_column(String(200))
    approver: Mapped[Optional[str]] = mapped_column(String(200))
    required: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    approved: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    reason: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    decision_record: Mapped["DecisionRecord"] = relationship(back_populates="approval_evidence")
