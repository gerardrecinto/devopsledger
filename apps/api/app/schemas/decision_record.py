import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


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
    jira_issues: list[str] = Field(default_factory=list)
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
    jira_issues: list[str] | None = None
    status: str | None = None

    @field_validator("title", "status", "jira_issues")
    @classmethod
    def _reject_explicit_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("field cannot be set to null")
        return value


class DecisionRecordSummary(BaseModel):
    id: uuid.UUID
    title: str
    environment: str | None
    service_name: str | None
    repository: str | None
    author: str | None
    jira_issues: list[str]
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
    jira_issues: list[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
