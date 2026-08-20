from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import ce_features as crud
from app.db import get_db
from app.integrations.argocd.parser import parse_sync_event
from app.integrations.generic_incident.parser import parse_generic_incident
from app.integrations.github.parser import check_codeowners_approval, parse_pr_event
from app.integrations.pagerduty.parser import parse_incident_webhook
from app.integrations.terraform.parser import parse_plan
from app.models.approval_evidence import ApprovalEvidence
from app.models.decision_record import DecisionRecord
from app.schemas.learning_note import LearningNoteCreate

router = APIRouter(prefix="/api/v1")


@router.post("/ingest/github/pr", status_code=status.HTTP_201_CREATED)
async def ingest_github_pr(
    payload: dict[str, Any],
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    parsed = parse_pr_event(payload)
    record = await crud.create_from_github_pr(db, parsed, payload)
    await _maybe_add_codeowners_approval(db, record.id, payload)
    record = await crud.get_record_detail(db, record.id)
    if record is None:
        raise HTTPException(status_code=500, detail="Decision record could not be loaded")
    return crud.serialize_record(record)


@router.post("/decision-records/{record_id}/terraform-plan")
async def ingest_terraform_plan(
    record_id: uuid.UUID,
    payload: dict[str, Any],
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    record = await crud.get_record_detail(db, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Decision record not found")
    updated = await crud.add_changed_resources(db, record, parse_plan(payload), payload)
    return crud.serialize_record(updated)


@router.post(
    "/decision-records/{record_id}/learning-notes",
    status_code=status.HTTP_201_CREATED,
)
async def add_learning_note(
    record_id: uuid.UUID,
    data: LearningNoteCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    record = await crud.get_record_detail(db, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Decision record not found")
    updated = await crud.add_learning_note(db, record, data.note, data.author)
    return crud.serialize_record(updated)


@router.post("/ingest/argocd", status_code=status.HTTP_201_CREATED)
async def ingest_argocd(
    payload: dict[str, Any],
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    event = parse_sync_event(payload)
    record = await _record_for_event(db, payload.get("decision_record_id"), event.get("revision"))
    if record is None:
        raise HTTPException(status_code=404, detail="Decision record not found")
    updated = await crud.add_deployment_event(db, record, event)
    return crud.serialize_record(updated)


@router.post("/ingest/pagerduty", status_code=status.HTTP_201_CREATED)
async def ingest_pagerduty(
    payload: dict[str, Any],
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    correlations = []
    for incident in parse_incident_webhook(payload):
        correlations.extend(await crud.correlate_incident(db, incident))
    return {
        "correlated_count": len(correlations),
        "correlations": [crud.serialize_incident(item) for item in correlations],
    }


@router.post("/ingest/incidents/generic", status_code=status.HTTP_201_CREATED)
async def ingest_generic_incident(
    payload: dict[str, Any],
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    correlations = await crud.correlate_incident(db, parse_generic_incident(payload))
    return {
        "correlated_count": len(correlations),
        "correlations": [crud.serialize_incident(item) for item in correlations],
    }


@router.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db)) -> dict[str, int]:
    return await crud.dashboard_summary(db)


@router.get("/resources/timeline")
async def resource_timeline(db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    return await crud.changed_resource_timeline(db)


async def _record_for_event(
    db: AsyncSession,
    record_id: str | None,
    revision: str | None,
) -> DecisionRecord | None:
    if record_id:
        try:
            parsed_id = uuid.UUID(record_id)
        except ValueError:
            return None
        return await crud.get_record_detail(db, parsed_id)
    if revision:
        result = await db.execute(
            select(DecisionRecord).where(DecisionRecord.commit_sha == revision)
        )
        record = result.scalar_one_or_none()
        if record:
            return await crud.get_record_detail(db, record.id)
    return None


async def _maybe_add_codeowners_approval(
    db: AsyncSession,
    record_id: uuid.UUID,
    payload: dict[str, Any],
) -> None:
    pr = payload.get("pull_request") or {}
    codeowners_text = payload.get("codeowners") or payload.get("codeowners_text")
    if not codeowners_text:
        return
    evidence = check_codeowners_approval(
        changed_files=pr.get("changed_files") or payload.get("changed_files") or [],
        codeowners_text=codeowners_text,
        reviews=payload.get("reviews") or [],
    )
    db.add(ApprovalEvidence(decision_record_id=record_id, **evidence))
    await db.commit()
