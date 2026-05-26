# Data Model

DevOpsLedger stores infrastructure changes as decision records with attached source, risk,
rollback, deployment, incident, approval, and learning context.

## DecisionRecord

Core record for one infrastructure change.

Fields:
- `id` - UUID primary key
- `title`, `description` - intent and context
- `environment`, `service_name` - local correlation fields
- `repository`, `pr_number`, `pr_url`, `author`, `commit_sha` - GitHub PR metadata
- `jira_issues` - parsed Jira issue keys from PR text
- `status` - lifecycle state, default `open`
- `created_at`, `updated_at`

## Attached Entities

- `ChangeSource` - source type, external ID, URL, and raw webhook/plan payload
- `ChangedResource` - Terraform/OpenTofu resource address, type, provider, actions, before/after summaries
- `RiskAssessment` - rules-based score, severity, and reasons
- `RollbackAssessment` - readiness score, missing items, and recommendations
- `DeploymentEvent` - Argo CD app, environment, status, revision, and event time
- `IncidentCorrelation` - PagerDuty or generic incident link, service/environment, severity, confidence
- `LearningNote` - retrospective note attached to a decision record
- `ApprovalEvidence` - CODEOWNERS/GitHub approval evidence

## Relationships

```
DecisionRecord
  ├── ChangeSource[]          (1:N)
  ├── ChangedResource[]       (1:N)
  ├── RiskAssessment          (1:1)
  ├── RollbackAssessment      (1:1)
  ├── DeploymentEvent[]       (1:N)
  ├── IncidentCorrelation[]   (1:N)
  ├── LearningNote[]          (1:N)
  └── ApprovalEvidence[]      (1:N)
```

## CE Ingestion Endpoints

- `POST /api/v1/ingest/github/pr`
- `POST /api/v1/decision-records/{record_id}/terraform-plan`
- `POST /api/v1/ingest/argocd`
- `POST /api/v1/ingest/pagerduty`
- `POST /api/v1/ingest/incidents/generic`
- `GET /api/v1/dashboard`
- `GET /api/v1/resources/timeline`

All ingestion paths accept local webhook JSON and do not make outbound SaaS calls.
