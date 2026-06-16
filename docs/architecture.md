# DevOpsLedger Architecture

## Overview

DevOpsLedger is a monorepo with three applications, shared deployment config, and documentation.

```
apps/api      - FastAPI backend, primary data store interface
apps/web      - Next.js frontend, decision record UI
apps/worker   - Background processor, async job queue consumer
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
  models/         SQLAlchemy 2.x async models
  schemas/        Pydantic v2 request / response schemas
  integrations/   Optional CE parsers, no outbound SaaS calls
  scoring/        YAML-configurable risk and rollback scoring
```

### Web (apps/web)

Next.js 15 frontend with server-side rendering. Talks only to the API - no direct database access.

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

Integrations live under `apps/api/app/integrations/`. CE integrations are pure
payload parsers and ingestion endpoints. They accept local webhook payloads and
do not call GitHub, Argo CD, PagerDuty, Jira, Terraform Cloud, or any other SaaS.

```
app/integrations/
  github/         PR ingestion, CODEOWNERS (CE)
  terraform/      Plan parsing (CE)
  argocd/         Deployment and sync events (CE)
  pagerduty/      Incident and change webhooks (CE)
  generic_incident/ Generic incident webhook (CE)
  github/         Jira issue link parsing from PR text (CE)
  # premium integrations are not in this directory
```

Premium integration modules are not part of the open-source repository.
They are loaded as optional packages at runtime if installed.

This design ensures local/offline mode works after images are available and
that CE features do not require credentials or outbound network access.

## Configuration

All configuration via environment variables. See `.env.example` for full reference.
No configuration is baked into images. Secrets must never be committed.

Important defaults:
- `OFFLINE_MODE=true`
- `TELEMETRY_ENABLED=false`
- `RISK_RULES_PATH` optional path to a mounted YAML file for rules-based risk scoring

No analytics, telemetry, or phone-home behavior is configured by default.

## On-Prem Deployment

See `docs/on-prem.md`.

## Release Packaging

Release tags publish three GHCR images:

```
ghcr.io/gerardrecinto/devopsledger/api:<version>
ghcr.io/gerardrecinto/devopsledger/web:<version>
ghcr.io/gerardrecinto/devopsledger/worker:<version>
```

The release workflow also attaches a demo package containing the release Compose
file, Helm chart, env reference, docs, and demo GIF. The release Compose file
uses immutable release image tags instead of local Docker build contexts.

## Security

See `docs/security-model.md`.

## Data Model

See `docs/data-model.md`.

## Product Strategy

See `docs/product-strategy.md`.
