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

## Configuration

All configuration via environment variables. See `.env.example` for full reference.
No configuration is baked into images. Secrets must never be committed.

## On-Prem Deployment

See `docs/on-prem.md`.

## Security

See `docs/security-model.md`.

## Data Model

See `docs/data-model.md`.
