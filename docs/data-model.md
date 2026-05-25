# Data Model

> Placeholder. This document is filled in when the data model slice is implemented.

## Planned Entities

### DecisionRecord

Core record capturing a single infrastructure change decision.

Planned fields:
- `id` — UUID primary key
- `title` — short description of the change
- `intent` — why we made this change (freeform text)
- `created_by` — user identifier (string for now; FK to User later)
- `created_at` — UTC timestamp
- `status` — `draft | pending_approval | approved | deployed | rolled_back | archived`
- `change_source_id` — FK to ChangeSource
- `risk_assessment_id` — FK to RiskAssessment
- `rollback_assessment_id` — FK to RollbackAssessment

### ChangeSource

Origin of the change (Terraform plan, manual, config push, script).

Planned fields:
- `id`, `type`, `reference` (e.g., plan file path or run URL), `raw_diff`

### ChangedResource

Individual resource affected by a decision (e.g., `aws_ecs_service.api`).

Planned fields:
- `id`, `decision_record_id` (FK), `resource_type`, `resource_address`, `action` (create/update/delete)

### RiskAssessment

Risk level, blast radius, reversibility, and reviewer notes.

Planned fields:
- `id`, `level` (low/medium/high/critical), `blast_radius`, `reversible` (bool), `notes`

### RollbackAssessment

Rollback plan, estimated time, pre-conditions, readiness flag.

Planned fields:
- `id`, `plan` (text), `estimated_minutes`, `pre_conditions`, `ready` (bool)

### DeploymentEvent

Record of when and how the change was deployed.

Planned fields:
- `id`, `decision_record_id` (FK), `deployed_at`, `deployed_by`, `environment`, `outcome` (success/failure/partial)

### IncidentCorrelation

Link between a decision record and a subsequent incident or cost event.

Planned fields:
- `id`, `decision_record_id` (FK), `incident_id`, `source` (string), `correlated_at`, `notes`

### LearningNote

Post-deployment retrospective note attached to a decision record.

Planned fields:
- `id`, `decision_record_id` (FK), `body` (text), `created_by`, `created_at`

## Entity Relationships

```
DecisionRecord
  ├── ChangeSource         (1:1)
  ├── ChangedResource[]    (1:N)
  ├── RiskAssessment       (1:1)
  ├── RollbackAssessment   (1:1)
  ├── DeploymentEvent[]    (1:N)
  ├── IncidentCorrelation[] (1:N)
  └── LearningNote[]       (1:N)
```

## Implementation Requirements (Next Slice)

- SQLAlchemy 2.x async models
- Alembic migrations — never use `create_all()` in production
- Pydantic v2 schemas for request/response
- Basic CRUD endpoints for `DecisionRecord`
- Tests for all new endpoints
- Do not implement GitHub or Terraform parsing in this slice
