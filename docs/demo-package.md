# Demo Package

DevOpsLedger releases ship a self-hosted demo package for people who want to
evaluate the API, web portal, and worker without cloning the full repository.

The package includes:

- API, web portal, and worker image references
- Docker Compose release file
- Helm chart
- Environment variable reference
- Architecture, data model, on-prem, security, product, and go-to-market docs
- Demo GIF at `docs/assets/demo.gif`

## Build Locally

```bash
make package VERSION=v1.1.0
```

The archive is written to:

```text
dist/devopsledger-v1.1.0-demo-package.tar.gz
```

## Run From The Package

```bash
tar -xzf devopsledger-v1.1.0-demo-package.tar.gz
cd devopsledger-v1.1.0-demo-package
cp env.example .env
DEVOPSLEDGER_VERSION=1.1.0 docker compose -f deploy/docker-compose/docker-compose.release.yml up -d
```

Open:

- API health: `http://localhost:8000/health`
- API docs when `ENABLE_DOCS=true`: `http://localhost:8000/docs`
- Web portal: `http://localhost:3000`

The demo package keeps the CE defaults: offline mode on, telemetry off, and no
required SaaS credentials.
