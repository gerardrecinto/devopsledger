# DevOpsLedger — Claude Code Context

## Product Definition

DevOpsLedger is an open-source operational memory layer for GitOps teams.
It turns infrastructure changes into decision records: intent, Terraform diff,
risk assessment, approval, rollback readiness, deployment event, incident/cost aftermath,
and learning note.

**Not a dashboard. Not a CMDB. Not an incident manager.**
It answers: "Why did we make this change, who approved it, what was the risk,
how would we roll it back, and what did we learn?"

---

## MVP Scope

- Decision record CRUD (create, read, update, archive)
- API-first (FastAPI)
- PostgreSQL storage
- Redis for queues and caching
- Next.js frontend
- Docker Compose for local and on-prem deployment
- No required SaaS integrations
- No authentication in MVP (add in a later slice)
- No telemetry

Out of scope for MVP:
- Helm chart
- GitHub integration
- Terraform integration
- PagerDuty / Jira / ServiceNow
- AI risk scoring
- Premium or paid features (this product is open source — no premium tier)

---

## Architecture Decisions

| Decision | Choice | Reason |
|---|---|---|
| Backend | FastAPI + Python 3.12 | Fast iteration, strong type hints, async-ready |
| Database | PostgreSQL 16 | Reliable, on-prem, no managed-service lock-in |
| Queue/cache | Redis 7 | Simple, no cloud dependency |
| Frontend | Next.js 15 + TypeScript | SSR, zero vendor lock-in |
| Container | Docker Compose → Helm (later) | Simple start, Kubernetes path later |
| Config | Environment variables | No secret management required at start |
| Migrations | Alembic | Never use `create_all()` in production |
| ORM | SQLAlchemy 2.x async | Async-native, type-safe |
| Schemas | Pydantic v2 | Request/response validation |

---

## On-Prem Requirements

- Must run with `docker compose up` and zero outbound internet calls after image pull.
- No hardcoded external URLs in any image or config.
- No telemetry, analytics, or phone-home behavior — ever.
- All integrations (GitHub, Terraform Cloud, PagerDuty, etc.) optional and disabled by default.
- Must be deployable on air-gapped networks if images are pre-pulled.
- Helm chart (when added) must support private registries.

---

## Security Requirements

- No secrets in code or Docker images.
- All secrets via environment variables or mounted secret files.
- No telemetry or outbound calls by default.
- Auth not required for MVP, but the data model must not assume no-auth
  (record who approved — even if "local user" for now).
- HTTPS termination at the ingress / reverse proxy, not in the application.
- Future: OIDC/SAML for enterprise SSO — design the API to not assume a specific auth provider.

---

## Coding Standards

- Python 3.12+, strict type hints on all functions and return values.
- FastAPI for all API endpoints.
- Pydantic v2 for request/response models.
- SQLAlchemy 2.x with async sessions for database access.
- Alembic for migrations — never `Base.metadata.create_all()` in production code.
- No `print()` — use the `logging` module.
- Black + isort for formatting, Ruff for linting.
- TypeScript strict mode for all frontend code.
- ESLint + Prettier for frontend formatting.
- No `any` types in TypeScript.
- No inline comments explaining what the code does — only why (non-obvious constraints, workarounds).

---

## Testing Standards

- Every API endpoint must have at minimum:
  - A happy-path test
  - A test for missing/invalid input
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

---

## Non-Negotiable Rules

1. **Every feature must include tests and docs.** No exceptions.
2. **No integration is required for local/offline mode.** All integrations optional,
   disabled by default, configured only via environment variables.
3. **No telemetry or outbound calls by default.** DevOpsLedger must work in air-gapped
   environments. No analytics SDKs, error-reporting services, or beacon URLs — ever.
4. **All integrations must be optional.** GitHub, Terraform, PagerDuty, Jira, ServiceNow,
   AI providers — optional. Product is fully functional without any of them.
5. **On-prem from day one.** Every feature must work with `docker compose up`.
   Cloud-managed or SaaS features come later and are always optional.

---

## Repo Structure

```
apps/
  api/          FastAPI backend
  web/          Next.js frontend
  worker/       Background job processor
deploy/
  docker-compose/  Local + on-prem deployment
docs/
  architecture.md
  on-prem.md
  security-model.md
  data-model.md
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
- Alembic migrations (never `create_all()`)
- Pydantic v2 schemas in `apps/api/app/schemas/`
- Basic CRUD endpoints for `DecisionRecord`
- Tests for all new endpoints
- Update `docs/data-model.md`
- Keep implementation small — no GitHub or Terraform parsing yet
- No auth in this slice either
