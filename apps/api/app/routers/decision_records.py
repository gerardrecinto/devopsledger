import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import decision_record as crud
from app.db import get_db
from app.schemas.decision_record import (
    DecisionRecordCreate,
    DecisionRecordDetail,
    DecisionRecordSummary,
    DecisionRecordUpdate,
)

router = APIRouter(prefix="/api/v1/decision-records")


@router.get("", response_model=list[DecisionRecordSummary])
async def list_records(db: AsyncSession = Depends(get_db)) -> list:
    return await crud.list_decision_records(db)


@router.post("", response_model=DecisionRecordDetail, status_code=status.HTTP_201_CREATED)
async def create_record(
    data: DecisionRecordCreate, db: AsyncSession = Depends(get_db)
) -> object:
    return await crud.create_decision_record(db, data)


@router.get("/{record_id}", response_model=DecisionRecordDetail)
async def get_record(record_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> object:
    record = await crud.get_decision_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Decision record not found")
    return record


@router.patch("/{record_id}", response_model=DecisionRecordDetail)
async def update_record(
    record_id: uuid.UUID,
    data: DecisionRecordUpdate,
    db: AsyncSession = Depends(get_db),
) -> object:
    record = await crud.get_decision_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Decision record not found")
    return await crud.update_decision_record(db, record, data)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(
    record_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> None:
    record = await crud.get_decision_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Decision record not found")
    await crud.delete_decision_record(db, record)
