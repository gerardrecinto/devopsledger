# DevOpsLedger — Claude Code Context

## Product Definition

DevOpsLedger is an open-source operational memory layer for GitOps teams.
It turns infrastructure changes into decision records: intent, Terraform/OpenTofu diff,
risk assessment, approval, rollback readiness, deployment event, incident/cost aftermath,
and learning note.

**Not a CI/CD dashboard. Not an ITSM ticketing system. Not a CMDB.**

It answers:
- Why did this infrastructure change happen?
- What resources changed?
- How risky was it?
- Who approved it?
- Was it rollback-ready?
- What happened afterward?
- Did the team learn from it?

---

## Open-Core Product Strategy

DevOpsLedger is open-core. The Community Edition is open source, self-hosted,
and must be genuinely useful without upgrading. Premium adds hosted convenience,
governance, compliance, enterprise identity, advanced analytics, AI assistance,
and support — not gating on core product value.

**Community Edition includes (all free, all planned):**
- Decision record CRUD
- GitHub PR ingestion (open source + GitHub Enterprise basic)
- Terraform / OpenTofu plan parsing
- Argo CD basic deployment and sync events
- PagerDuty incident and change webhook
- Generic incident webhook
- Jira issue link parsing
- CODEOWNERS approval checks
- Risk scoring (rules-based, YAML-configurable)
- Rollback readiness scoring
- Basic incident correlation
- Changed resource timeline
- Basic dashboard
- Docker Compose deployment
- Helm chart
- Local / offline mode
- No telemetry by default

**Premium features (not implemented — not in scope yet):**
- DevOpsLedger Cloud (hosted)
- Team workspaces
- SSO / SAML / OIDC
- SCIM
- RBAC
- SOC 2 evidence exports
- Advanced compliance and audit exports
- Advanced analytics
- Team maturity dashboards
- Advanced graph queries
- AI-generated change narratives
- AI-generated postmortem drafts
- Advanced Jira / ServiceNow / PagerDuty bidirectional sync
- AWS / GCP / Azure cost integrations
- Air-gapped enterprise install bundles
- Private registry images
- Enterprise support SLA
- Change window enforcement
- Policy enforcement and merge gates

**Payment and subscription features are not implemented yet.**
Do not implement payment or subscription checks. Do not add artificial CE limitations.

See `docs/product-strategy.md` for full strategy.

---

## MVP Scope (Current Phase)

- Decision record CRUD (create, read, update, archive)
- API-first (FastAPI)
- PostgreSQL storage
- Redis for queues and caching
- Next.js frontend
- Docker Compose for local and on-prem deployment
- No required SaaS integrations
- No authentication in MVP (add in a later slice)
- No telemetry

Out of scope for current slice:
- Helm chart
- GitHub ingestion
- Terraform / OpenTofu parsing
- Argo CD events
- PagerDuty / Jira / ServiceNow
- AI features
- Premium features

---

## Architecture Decisions

| Decision | Choice | Reason |
|---|---|---|
| Backend | FastAPI + Python 3.12 | Fast iteration, strong type hints, async-ready |
| Database | PostgreSQL 16 | Reliable, on-prem, no managed-service lock-in |
| Queue / cache | Redis 7 | Simple, no cloud dependency |
| Frontend | Next.js 15 + TypeScript | SSR, zero vendor lock-in |
| Container | Docker Compose → Helm (later) | Simple start, Kubernetes path later |
| Config | Environment variables | No secret management required at start |
| Migrations | Alembic | Never use `create_all()` in production |
| ORM | SQLAlchemy 2.x async | Async-native, type-safe |
| Schemas | Pydantic v2 | Request / response validation |
| Integrations | Plugin modules under `apps/api/app/integrations/` | Isolates optional deps from core |

Integration modules are optional. Each integration can be imported only when its
environment variables are set. Core product never imports integration code directly.

---

## On-Prem Requirements

- Must run with `docker compose up` and zero outbound internet calls after image pull.
- No hardcoded external URLs in any image or config.
- No telemetry, analytics, or phone-home behavior — ever.
- All integrations optional and disabled by default, configured only via env vars.
- Must be deployable on air-gapped networks if images are pre-pulled.
- Helm chart (when added) must support private registries.
- Local / offline mode must work with sample data.

---

## Security Requirements

- No secrets in code or Docker images.
- All secrets via environment variables or mounted secret files.
- No telemetry or outbound calls by default.
- Auth not required for MVP, but the data model must not assume no-auth
  (record who approved — even if "local user" for now).
- HTTPS termination at the ingress / reverse proxy, not in the application.
- Future: OIDC / SAML for enterprise SSO — design the API to not assume a specific auth provider.

---

## Coding Standards

- Python 3.12+, strict type hints on all functions and return values.
- FastAPI for all API endpoints.
- Pydantic v2 for request / response models.
- SQLAlchemy 2.x with async sessions for database access.
- Alembic for migrations — never `Base.metadata.create_all()` in production code.
- No `print()` — use the `logging` module.
- Black + isort for formatting, Ruff for linting.
- TypeScript strict mode for all frontend code.
- ESLint + Prettier for frontend formatting.
- No `any` types in TypeScript.
- No inline comments explaining what the code does — only why (non-obvious constraints, workarounds).
- Boring, maintainable architecture over clever abstractions.

---

## Testing Standards

- Every API endpoint must have at minimum:
  - A happy-path test
  - A test for missing / invalid input
- Use `pytest` + `httpx` (via FastAPI `TestClient`) for API tests.
- Use `pytest-asyncio` for async tests.
- No mocking the database in integration tests — use a test database.
- Unit tests may mock external dependencies.
- Frontend: Jest + React Testing Library.
- No PR reduces test coverage.

---

## Documentation Standards

- Every new entity or endpoint must update `docs/data-model.md`.
- Architecture changes must update `docs/architecture.md`.
- On-prem deployment changes must update `docs/on-prem.md`.
- No inline comments explaining what code does — only why.
- API docs via FastAPI's auto-generated OpenAPI (`ENABLE_DOCS=true` in dev, optional in prod).
- Product strategy changes must update `docs/product-strategy.md`.

---

## Non-Negotiable Rules

1. **Every feature must include tests and docs.** No exceptions.
2. **No integration is required for local / offline mode.** All integrations optional,
   disabled by default, configured only via environment variables.
3. **No telemetry or outbound calls by default.** DevOpsLedger must work in air-gapped
   environments. No analytics SDKs, error-reporting services, or beacon URLs — ever.
4. **All integrations must be optional.** GitHub, Terraform/OpenTofu, Argo CD, PagerDuty,
   Jira, ServiceNow, AI providers — optional. Product is fully functional without any of them.
5. **On-prem from day one.** Every feature must work with `docker compose up`.
   Cloud-managed or SaaS features come later and are always optional.
6. **Community Edition must include useful core DevOps integrations.** GitHub PR ingestion,
   Terraform/OpenTofu parsing, Argo CD events, PagerDuty webhooks, Jira linking, and
   CODEOWNERS support are part of CE — not premium.
7. **Premium focuses on hosted convenience, governance, compliance, scale, analytics,
   identity, AI assistance, and enterprise support.** Do not gate core DevOps functionality.
8. **No payment or subscription features.** Not in scope yet. Do not add billing checks,
   license gates, or artificial feature limits to the open-source core.

---

## Repo Structure

```
apps/
  api/                FastAPI backend
    app/
      routers/        API route handlers
      models/         SQLAlchemy models (next slice)
      schemas/        Pydantic v2 schemas (next slice)
      integrations/   Optional integration modules (GitHub, Terraform, etc.)
  web/                Next.js frontend
  worker/             Background job processor
deploy/
  docker-compose/     Local + on-prem deployment
docs/
  architecture.md
  data-model.md
  on-prem.md
  product-strategy.md
  security-model.md
Makefile
CLAUDE.md
.env.example
```

---

## Common Commands

```bash
make up           # Start all services (Docker Compose)
make down         # Stop all services
make test         # Run all tests
make test-api     # Run API tests only
make dev          # Start API locally with hot-reload
make logs         # Tail logs
make build        # Build all Docker images
```

---

## Next Implementation Slice

**Implement the initial DevOpsLedger data model.**

Entities: DecisionRecord, ChangeSource, ChangedResource, RiskAssessment,
RollbackAssessment, DeploymentEvent, IncidentCorrelation, LearningNote.

Requirements:
- SQLAlchemy 2.x async models in `apps/api/app/models/`
- Alembic migrations — never `create_all()`
- Pydantic v2 schemas in `apps/api/app/schemas/`
- Basic CRUD endpoints for `DecisionRecord`
- Tests for all new endpoints
- Update `docs/data-model.md`
- Keep implementation small — no GitHub or Terraform/OpenTofu parsing yet
- No auth in this slice either
