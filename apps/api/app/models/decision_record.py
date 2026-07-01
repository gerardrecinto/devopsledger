import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, DateTime, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.approval_evidence import ApprovalEvidence
    from app.models.change_source import ChangeSource
    from app.models.changed_resource import ChangedResource
    from app.models.deployment_event import DeploymentEvent
    from app.models.incident_correlation import IncidentCorrelation
    from app.models.learning_note import LearningNote
    from app.models.risk_assessment import RiskAssessment
    from app.models.rollback_assessment import RollbackAssessment


def _now() -> datetime:
    return datetime.now(UTC)


class DecisionRecord(Base):
    __tablename__ = "decision_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    environment: Mapped[str | None] = mapped_column(String(100))
    service_name: Mapped[str | None] = mapped_column(String(200))
    repository: Mapped[str | None] = mapped_column(String(500))
    pr_number: Mapped[int | None] = mapped_column(Integer)
    pr_url: Mapped[str | None] = mapped_column(String(1000))
    author: Mapped[str | None] = mapped_column(String(200))
    commit_sha: Mapped[str | None] = mapped_column(String(40))
    jira_issues: Mapped[list[str]] = mapped_column(JSON, default=list, server_default="[]")
    status: Mapped[str] = mapped_column(String(50), default="open", server_default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )

    change_sources: Mapped[list["ChangeSource"]] = relationship(
        back_populates="decision_record", cascade="all, delete-orphan"
    )
    changed_resources: Mapped[list["ChangedResource"]] = relationship(
        back_populates="decision_record", cascade="all, delete-orphan"
    )
    risk_assessment: Mapped[Optional["RiskAssessment"]] = relationship(
        back_populates="decision_record", cascade="all, delete-orphan", uselist=False
    )
    rollback_assessment: Mapped[Optional["RollbackAssessment"]] = relationship(
        back_populates="decision_record", cascade="all, delete-orphan", uselist=False
    )
    deployment_events: Mapped[list["DeploymentEvent"]] = relationship(
        back_populates="decision_record", cascade="all, delete-orphan"
    )
    incident_correlations: Mapped[list["IncidentCorrelation"]] = relationship(
        back_populates="decision_record", cascade="all, delete-orphan"
    )
    learning_notes: Mapped[list["LearningNote"]] = relationship(
        back_populates="decision_record", cascade="all, delete-orphan"
    )
    approval_evidence: Mapped[list["ApprovalEvidence"]] = relationship(
        back_populates="decision_record", cascade="all, delete-orphan"
    )
