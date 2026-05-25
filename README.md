# DevOpsLedger

Open-source operational memory layer for GitOps teams.

Every infrastructure change becomes a decision record: intent, Terraform diff, risk assessment,
approval, rollback readiness, deployment event, incident correlation, and learning note.

**Self-hosted. No required SaaS. No telemetry.**

## Quick Start

```bash
cp .env.example .env   # change POSTGRES_PASSWORD
make up
# API:  http://localhost:8000/health
# Web:  http://localhost:3000
```

## Architecture

- FastAPI backend (`apps/api`)
- PostgreSQL — persistent storage
- Redis — job queue and cache
- Next.js frontend (`apps/web`)
- Background worker (`apps/worker`)
- Docker Compose for on-prem deployment

See [docs/architecture.md](docs/architecture.md).

## On-Prem

Runs entirely without outbound SaaS calls. All integrations optional and disabled by default.
Works in air-gapped environments. See [docs/on-prem.md](docs/on-prem.md).

## Development

```bash
make test-api   # run API tests
make dev        # start API with hot-reload
make up         # start full stack
make down       # stop
make logs       # tail logs
```

## License

MIT
