from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.approval_evidence import ApprovalEvidence
from app.models.change_source import ChangeSource
from app.models.changed_resource import ChangedResource
from app.models.decision_record import DecisionRecord
from app.models.deployment_event import DeploymentEvent
from app.models.incident_correlation import IncidentCorrelation
from app.models.risk_assessment import RiskAssessment
from app.models.rollback_assessment import RollbackAssessment
from app.scoring import score_risk, score_rollback_readiness


async def get_record_detail(db: AsyncSession, record_id: uuid.UUID) -> DecisionRecord | None:
    result = await db.execute(
        select(DecisionRecord)
        .options(
            selectinload(DecisionRecord.changed_resources),
            selectinload(DecisionRecord.change_sources),
            selectinload(DecisionRecord.risk_assessment),
            selectinload(DecisionRecord.rollback_assessment),
            selectinload(DecisionRecord.deployment_events),
            selectinload(DecisionRecord.incident_correlations),
            selectinload(DecisionRecord.learning_notes),
            selectinload(DecisionRecord.approval_evidence),
        )
        .where(DecisionRecord.id == record_id)
        .execution_options(populate_existing=True)
    )
    return result.scalar_one_or_none()


async def create_from_github_pr(
    db: AsyncSession,
    parsed: dict[str, Any],
    raw_payload: dict[str, Any],
) -> DecisionRecord:
    rollback = score_rollback_readiness(parsed.get("description"))
    record = DecisionRecord(**parsed)
    db.add(record)
    await db.flush()
    db.add(
        ChangeSource(
            decision_record_id=record.id,
            source_type="github_pr",
            external_id=(
                str(parsed.get("pr_number")) if parsed.get("pr_number") is not None else None
            ),
            url=parsed.get("pr_url"),
            raw_payload=raw_payload,
        )
    )
    db.add(
        RollbackAssessment(
            decision_record_id=record.id,
            score=rollback["score"],
            missing_items=rollback["missing_items"],
            recommendations=rollback["recommendations"],
        )
    )
    await db.commit()
    detail = await get_record_detail(db, record.id)
    if detail is None:
        raise RuntimeError("Created decision record could not be loaded")
    return detail


async def add_changed_resources(
    db: AsyncSession,
    record: DecisionRecord,
    changed_resources: list[dict[str, Any]],
    raw_payload: dict[str, Any],
) -> DecisionRecord:
    db.add(
        ChangeSource(
            decision_record_id=record.id,
            source_type="terraform_plan",
            raw_payload=raw_payload,
        )
    )
    for resource in changed_resources:
        db.add(ChangedResource(decision_record_id=record.id, **resource))

    risk = score_risk(
        environment=record.environment,
        changed_resources=changed_resources,
        config_path=settings.risk_rules_path,
    )
    rollback = score_rollback_readiness(record.description)
    await _upsert_risk(db, record.id, risk)
    await _upsert_rollback(db, record.id, rollback)
    await db.commit()
    detail = await get_record_detail(db, record.id)
    if detail is None:
        raise RuntimeError("Updated decision record could not be loaded")
    return detail


async def add_deployment_event(
    db: AsyncSession,
    record: DecisionRecord,
    event: dict[str, Any],
) -> DecisionRecord:
    db.add(DeploymentEvent(decision_record_id=record.id, **_coerce_event_datetimes(event)))
    await db.commit()
    detail = await get_record_detail(db, record.id)
    if detail is None:
        raise RuntimeError("Updated decision record could not be loaded")
    return detail


async def correlate_incident(
    db: AsyncSession,
    incident: dict[str, Any],
) -> list[IncidentCorrelation]:
    result = await db.execute(select(DecisionRecord))
    records = list(result.scalars().all())
    correlations: list[IncidentCorrelation] = []
    for record in records:
        confidence = _incident_confidence(record, incident)
        if confidence is None:
            continue
        correlation = IncidentCorrelation(
            decision_record_id=record.id,
            incident_source=incident["incident_source"],
            incident_title=incident["incident_title"],
            incident_url=incident.get("incident_url"),
            service_name=incident.get("service_name"),
            environment=incident.get("environment"),
            severity=incident.get("severity"),
            started_at=_parse_datetime(incident.get("started_at")),
            correlation_reason=incident.get("correlation_reason"),
            confidence=confidence,
            raw_payload=incident.get("raw_payload"),
        )
        db.add(correlation)
        correlations.append(correlation)
    await db.commit()
    for correlation in correlations:
        await db.refresh(correlation)
    return correlations


async def dashboard_summary(db: AsyncSession) -> dict[str, int]:
    return {
        "decision_records": await _count(db, DecisionRecord),
        "changed_resources": await _count(db, ChangedResource),
        "deployment_events": await _count(db, DeploymentEvent),
        "incident_correlations": await _count(db, IncidentCorrelation),
    }


async def changed_resource_timeline(db: AsyncSession) -> list[dict[str, Any]]:
    result = await db.execute(
        select(ChangedResource, DecisionRecord)
        .join(DecisionRecord, ChangedResource.decision_record_id == DecisionRecord.id)
        .order_by(ChangedResource.created_at.desc())
    )
    return [
        {
            "id": str(resource.id),
            "decision_record_id": str(record.id),
            "decision_record_title": record.title,
            "address": resource.address,
            "resource_type": resource.resource_type,
            "provider": resource.provider,
            "actions": resource.actions,
            "created_at": resource.created_at.isoformat(),
        }
        for resource, record in result.all()
    ]


def serialize_record(record: DecisionRecord) -> dict[str, Any]:
    return {
        "id": str(record.id),
        "title": record.title,
        "description": record.description,
        "environment": record.environment,
        "service_name": record.service_name,
        "repository": record.repository,
        "pr_number": record.pr_number,
        "pr_url": record.pr_url,
        "author": record.author,
        "commit_sha": record.commit_sha,
        "jira_issues": record.jira_issues or [],
        "status": record.status,
        "created_at": record.created_at.isoformat(),
        "updated_at": record.updated_at.isoformat(),
        "changed_resources": [
            _serialize_changed_resource(item) for item in record.changed_resources
        ],
        "risk_assessment": _serialize_risk(record.risk_assessment),
        "rollback_assessment": _serialize_rollback(record.rollback_assessment),
        "deployment_events": [
            _serialize_deployment_event(item) for item in record.deployment_events
        ],
        "incident_correlations": [
            serialize_incident(item) for item in record.incident_correlations
        ],
        "approval_evidence": [_serialize_approval(item) for item in record.approval_evidence],
    }


async def _upsert_risk(
    db: AsyncSession,
    record_id: uuid.UUID,
    risk: dict[str, Any],
) -> None:
    existing = (
        await db.execute(
            select(RiskAssessment).where(RiskAssessment.decision_record_id == record_id)
        )
    ).scalar_one_or_none()
    if existing:
        existing.score = risk["score"]
        existing.severity = risk["severity"]
        existing.reasons = risk["reasons"]
        return
    db.add(RiskAssessment(decision_record_id=record_id, **risk))


async def _upsert_rollback(
    db: AsyncSession,
    record_id: uuid.UUID,
    rollback: dict[str, Any],
) -> None:
    existing = (
        await db.execute(
            select(RollbackAssessment).where(RollbackAssessment.decision_record_id == record_id)
        )
    ).scalar_one_or_none()
    if existing:
        existing.score = rollback["score"]
        existing.missing_items = rollback["missing_items"]
        existing.recommendations = rollback["recommendations"]
        return
    db.add(RollbackAssessment(decision_record_id=record_id, **rollback))


async def _count(db: AsyncSession, model: type) -> int:
    result = await db.execute(select(func.count()).select_from(model))
    return int(result.scalar_one())


def _incident_confidence(record: DecisionRecord, incident: dict[str, Any]) -> str | None:
    service_matches = bool(
        record.service_name
        and incident.get("service_name")
        and record.service_name.lower() == str(incident["service_name"]).lower()
    )
    env_matches = bool(
        record.environment
        and incident.get("environment")
        and record.environment.lower() == str(incident["environment"]).lower()
    )
    if service_matches and env_matches:
        return "likely"
    if service_matches or env_matches:
        return "possible"
    return None


def _coerce_event_datetimes(event: dict[str, Any]) -> dict[str, Any]:
    coerced = event.copy()
    coerced["event_time"] = _parse_datetime(coerced.get("event_time"))
    return coerced


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return None


def _serialize_changed_resource(resource: ChangedResource) -> dict[str, Any]:
    return {
        "id": str(resource.id),
        "address": resource.address,
        "resource_type": resource.resource_type,
        "provider": resource.provider,
        "actions": resource.actions,
        "before_summary": resource.before_summary,
        "after_summary": resource.after_summary,
        "created_at": resource.created_at.isoformat(),
    }


def _serialize_risk(risk: RiskAssessment | None) -> dict[str, Any] | None:
    if risk is None:
        return None
    return {"score": risk.score, "severity": risk.severity, "reasons": risk.reasons}


def _serialize_rollback(rollback: RollbackAssessment | None) -> dict[str, Any] | None:
    if rollback is None:
        return None
    return {
        "score": rollback.score,
        "missing_items": rollback.missing_items,
        "recommendations": rollback.recommendations,
    }


def _serialize_deployment_event(event: DeploymentEvent) -> dict[str, Any]:
    return {
        "id": str(event.id),
        "source": event.source,
        "app_name": event.app_name,
        "environment": event.environment,
        "status": event.status,
        "revision": event.revision,
        "event_time": event.event_time.isoformat() if event.event_time else None,
        "created_at": event.created_at.isoformat(),
    }


def serialize_incident(incident: IncidentCorrelation) -> dict[str, Any]:
    return {
        "id": str(incident.id),
        "decision_record_id": str(incident.decision_record_id),
        "incident_source": incident.incident_source,
        "incident_title": incident.incident_title,
        "incident_url": incident.incident_url,
        "service_name": incident.service_name,
        "environment": incident.environment,
        "severity": incident.severity,
        "confidence": incident.confidence,
    }


def _serialize_approval(approval: ApprovalEvidence) -> dict[str, Any]:
    return {
        "id": str(approval.id),
        "source": approval.source,
        "owner": approval.owner,
        "approver": approval.approver,
        "required": approval.required,
        "approved": approval.approved,
        "reason": approval.reason,
    }
