import uuid
from datetime import datetime

from pydantic import BaseModel


class DecisionRecordCreate(BaseModel):
    title: str
    description: str | None = None
    environment: str | None = None
    service_name: str | None = None
    repository: str | None = None
    pr_number: int | None = None
    pr_url: str | None = None
    author: str | None = None
    commit_sha: str | None = None
    status: str = "open"


class DecisionRecordUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    environment: str | None = None
    service_name: str | None = None
    repository: str | None = None
    pr_number: int | None = None
    pr_url: str | None = None
    author: str | None = None
    commit_sha: str | None = None
    status: str | None = None


class DecisionRecordSummary(BaseModel):
    id: uuid.UUID
    title: str
    environment: str | None
    service_name: str | None
    repository: str | None
    author: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DecisionRecordDetail(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    environment: str | None
    service_name: str | None
    repository: str | None
    pr_number: int | None
    pr_url: str | None
    author: str | None
    commit_sha: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
