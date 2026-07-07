import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decision_record import DecisionRecord
from app.schemas.decision_record import DecisionRecordCreate, DecisionRecordUpdate


async def list_decision_records(db: AsyncSession) -> list[DecisionRecord]:
    result = await db.execute(
        select(DecisionRecord).order_by(DecisionRecord.created_at.desc())
    )
    return list(result.scalars().all())


async def create_decision_record(
    db: AsyncSession, data: DecisionRecordCreate
) -> DecisionRecord:
    record = DecisionRecord(**data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_decision_record(
    db: AsyncSession, record_id: uuid.UUID
) -> DecisionRecord | None:
    result = await db.execute(
        select(DecisionRecord).where(DecisionRecord.id == record_id)
    )
    return result.scalar_one_or_none()


async def update_decision_record(
    db: AsyncSession,
    record: DecisionRecord,
    data: DecisionRecordUpdate,
) -> DecisionRecord:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    await db.commit()
    await db.refresh(record)
    return record


async def delete_decision_record(db: AsyncSession, record: DecisionRecord) -> None:
    await db.delete(record)
    await db.commit()
