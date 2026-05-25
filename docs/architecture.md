# DevOpsLedger Architecture

## Overview

DevOpsLedger is a monorepo with three applications, shared deployment config, and documentation.

```
apps/api      — FastAPI backend, primary data store interface
apps/web      — Next.js frontend, decision record UI
apps/worker   — Background processor, async job queue consumer
```

## Components

### API (apps/api)

FastAPI application. Handles all CRUD operations and optional integration webhooks.
Connects to PostgreSQL for persistent storage and Redis for job queues and caching.

Startup: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

Internal layout:

```
app/
  routers/        Route handlers
  models/         SQLAlchemy 2.x async models (next slice)
  schemas/        Pydantic v2 request / response schemas (next slice)
  integrations/   Optional integration modules — imported only when configured
```

### Web (apps/web)

Next.js 15 frontend with server-side rendering. Talks only to the API — no direct database access.

Startup: `next dev` (dev) | `node server.js` (prod standalone build)

### Worker (apps/worker)

Background process consuming jobs from Redis queues. Handles async tasks:
parsing diffs, scoring risk, sending optional notifications.
All integrations invoked by the worker are optional and disabled by default.

### PostgreSQL

Primary data store. Version 16+. On-prem: runs in Docker. Production: any PostgreSQL-compatible instance.

### Redis

Job queue and cache. Version 7+. On-prem: runs in Docker. Production: any Redis-compatible instance.

## Network Topology (Docker Compose)

```
[browser] → [web:3000] → [api:8000] → [postgres:5432]
                                     → [redis:6379]
[worker]               → [api:8000]
                       → [redis:6379]
                       → [postgres:5432]
```

Only `web` (3000) and `api` (8000) are exposed externally by default.
PostgreSQL and Redis are internal only.

## Integration Module Design (Open-Core)

Integrations live under `apps/api/app/integrations/`. Each integration is a
self-contained module with its own dependencies declared separately. The core
application never imports integration code directly. Instead, integrations
register themselves at startup if their environment variables are present.

```
app/integrations/
  github/         PR ingestion, CODEOWNERS (CE)
  terraform/      Plan parsing (CE)
  argocd/         Deployment and sync events (CE)
  pagerduty/      Incident and change webhooks (CE)
  incident/       Generic incident webhook (CE)
  jira/           Issue link parsing (CE)
  # premium integrations are not in this directory
```

Premium integration modules are not part of the open-source repository.
They are loaded as optional packages at runtime if installed.

This design ensures:
- `pip install devopsledger` installs only the open-source core.
- Optional integration dependencies are not pulled in unless needed.
- Premium modules can be distributed separately without polluting CE code.
- Air-gapped installs work without internet access to integration endpoints.

## Configuration

All configuration via environment variables. See `.env.example` for full reference.
No configuration is baked into images. Secrets must never be committed.

Each integration reads its own env vars at startup. If the vars are absent,
the integration is skipped silently. No errors. No required network calls.

## On-Prem Deployment

See `docs/on-prem.md`.

## Security

See `docs/security-model.md`.

## Data Model

See `docs/data-model.md`.

## Product Strategy

See `docs/product-strategy.md`.
