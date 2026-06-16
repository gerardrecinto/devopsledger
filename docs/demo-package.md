# Demo Package

DevOpsLedger releases ship a self-hosted demo package for people who want to
evaluate the API, web portal, and worker without cloning the full repository.

Use it as the short, buyer-facing walkthrough: a platform lead can see the
product story, run the stack, inspect the API, and verify the on-prem posture in
one pass.

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

## What To Show

For a polished demo, walk through this order:

1. Open the web portal at `http://localhost:3000`.
2. Show the dashboard metrics and changed-resource timeline.
3. Open `http://localhost:8000/health` to prove the API is live.
4. Enable `ENABLE_DOCS=true` and open `http://localhost:8000/docs` for the API surface.
5. Show `docs/architecture.md`, `docs/security-model.md`, and `docs/on-prem.md` to make the self-hosted story concrete.

The selling point is simple: DevOpsLedger turns an infrastructure change from a
scattered trail of PRs, diffs, approvals, incidents, and memories into one record
a team can trust later.
