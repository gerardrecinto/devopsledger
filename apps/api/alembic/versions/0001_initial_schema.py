"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-24

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "decision_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("environment", sa.String(100), nullable=True),
        sa.Column("service_name", sa.String(200), nullable=True),
        sa.Column("repository", sa.String(500), nullable=True),
        sa.Column("pr_number", sa.Integer(), nullable=True),
        sa.Column("pr_url", sa.String(1000), nullable=True),
        sa.Column("author", sa.String(200), nullable=True),
        sa.Column("commit_sha", sa.String(40), nullable=True),
        sa.Column("jira_issues", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "change_sources",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_record_id", sa.Uuid(), nullable=False),
        sa.Column("source_type", sa.String(100), nullable=False),
        sa.Column("external_id", sa.String(500), nullable=True),
        sa.Column("url", sa.String(1000), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["decision_record_id"], ["decision_records.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "changed_resources",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_record_id", sa.Uuid(), nullable=False),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("resource_type", sa.String(200), nullable=False),
        sa.Column("provider", sa.String(100), nullable=True),
        sa.Column("actions", sa.JSON(), nullable=False),
        sa.Column("before_summary", sa.JSON(), nullable=True),
        sa.Column("after_summary", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["decision_record_id"], ["decision_records.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "risk_assessments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_record_id", sa.Uuid(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("severity", sa.String(50), nullable=False),
        sa.Column("reasons", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["decision_record_id"], ["decision_records.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("decision_record_id"),
    )

    op.create_table(
        "rollback_assessments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_record_id", sa.Uuid(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("missing_items", sa.JSON(), nullable=False),
        sa.Column("recommendations", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["decision_record_id"], ["decision_records.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("decision_record_id"),
    )

    op.create_table(
        "deployment_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_record_id", sa.Uuid(), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("app_name", sa.String(200), nullable=True),
        sa.Column("environment", sa.String(100), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("revision", sa.String(100), nullable=True),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["decision_record_id"], ["decision_records.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "incident_correlations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_record_id", sa.Uuid(), nullable=False),
        sa.Column("incident_source", sa.String(100), nullable=False),
        sa.Column("incident_title", sa.String(500), nullable=False),
        sa.Column("incident_url", sa.String(1000), nullable=True),
        sa.Column("service_name", sa.String(200), nullable=True),
        sa.Column("environment", sa.String(100), nullable=True),
        sa.Column("severity", sa.String(50), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("correlation_reason", sa.Text(), nullable=True),
        sa.Column("confidence", sa.String(50), nullable=False, server_default="possible"),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["decision_record_id"], ["decision_records.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "learning_notes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_record_id", sa.Uuid(), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("author", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["decision_record_id"], ["decision_records.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "approval_evidence",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_record_id", sa.Uuid(), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("owner", sa.String(200), nullable=True),
        sa.Column("approver", sa.String(200), nullable=True),
        sa.Column("required", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("approved", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["decision_record_id"], ["decision_records.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("approval_evidence")
    op.drop_table("learning_notes")
    op.drop_table("incident_correlations")
    op.drop_table("deployment_events")
    op.drop_table("rollback_assessments")
    op.drop_table("risk_assessments")
    op.drop_table("changed_resources")
    op.drop_table("change_sources")
    op.drop_table("decision_records")
