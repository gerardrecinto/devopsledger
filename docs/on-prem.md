# On-Prem Deployment

DevOpsLedger is designed for on-prem-first deployment. It runs entirely without outbound SaaS calls.

## Quick Start

```bash
cp .env.example .env
# Edit .env - change POSTGRES_PASSWORD at minimum
make up
# API:  http://localhost:8000/health
# Web:  http://localhost:3000
# Docs: http://localhost:8000/docs  (only if ENABLE_DOCS=true)
```

## Requirements

- Docker 24+
- Docker Compose v2
- 2 vCPU / 4 GB RAM minimum
- Persistent volume mount for PostgreSQL data

## Environment Variables

All configuration via environment variables. See `.env.example`.

Mandatory changes before production:
- `POSTGRES_PASSWORD` - never use the default
- `ENVIRONMENT=production`
- `ENABLE_DOCS=false` - disables Swagger UI in prod

Offline and telemetry defaults:
- `OFFLINE_MODE=true`
- `TELEMETRY_ENABLED=false`
- `RISK_RULES_PATH` can point at a mounted YAML file to override risk scoring rules

## Air-Gapped Deployment

Pull and save images on a machine with internet access:

```bash
docker pull postgres:16-alpine redis:7-alpine python:3.12-slim node:22-alpine
docker save postgres:16-alpine redis:7-alpine python:3.12-slim node:22-alpine \
  | gzip > devopsledger-base-images.tar.gz
```

Transfer to the air-gapped host, then:

```bash
docker load < devopsledger-base-images.tar.gz
# Build app images locally (they extend the base images above)
make build
make up
```

## Data Persistence

PostgreSQL data lives in the `postgres_data` Docker volume.

Backup:
```bash
docker exec devopsledger-postgres-1 \
  pg_dump -U devopsledger devopsledger > backup-$(date +%Y%m%d).sql
```

Restore:
```bash
docker exec -i devopsledger-postgres-1 \
  psql -U devopsledger devopsledger < backup-20260524.sql
```

## Upgrading

```bash
git pull
make build
make down
make up
```

Migrations run automatically on API startup.

## Helm Chart

A basic Kubernetes chart is available at `deploy/helm/devopsledger`.

```bash
helm install devopsledger deploy/helm/devopsledger \
  --set secrets.databaseUrl='postgresql://devopsledger:changeme@postgres:5432/devopsledger' \
  --set config.redisUrl='redis://redis:6379'
```

The chart assumes PostgreSQL and Redis are provided separately. Images, private
registries, ingress, offline mode, telemetry, and risk rules are configured in
`values.yaml`.

## Reverse Proxy (Recommended for Production)

Terminate TLS at nginx, Caddy, or Traefik - not in the app.

Example nginx snippet:

```nginx
server {
    listen 443 ssl;
    server_name devopsledger.internal;

    location /api/ {
        proxy_pass http://localhost:8000/;
    }

    location / {
        proxy_pass http://localhost:3000/;
    }
}
```

## No Outbound SaaS

DevOpsLedger makes zero outbound calls by default. All integrations (GitHub, Terraform Cloud,
PagerDuty, Jira, ServiceNow, AI providers) are disabled unless explicitly configured via
environment variables. The product is fully functional offline after the initial image pull.
