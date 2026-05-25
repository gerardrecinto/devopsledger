# Security Model

## Principles

1. **No secrets in code or images.** All credentials via environment variables or mounted secret files.
2. **No telemetry.** DevOpsLedger never phones home. No analytics, no error beacons, no usage reporting.
3. **Least privilege.** Each service connects only to what it needs.
4. **No required outbound internet.** Works in air-gapped environments after image pull.
5. **Optional authentication.** MVP supports local/trusted-network deployment. OIDC/SAML added in a later slice.

## Secrets Management

| Secret | Where Configured | Default (dev only — change in prod) |
|---|---|---|
| `POSTGRES_PASSWORD` | `.env` / secret mount | `devopsledger` |
| Integration tokens | `.env` / secret mount | unset (integration disabled) |

Never commit `.env`. The `.env.example` file contains only safe placeholder values.

## Network Security

- API and Web are the only services exposed externally.
- PostgreSQL and Redis bind to the internal Docker network only.
- TLS termination at the reverse proxy (nginx / Caddy / Traefik) — not in the application.
- No ports bound to `0.0.0.0` in production without a firewall or ingress rule.

## Authentication (Future)

The MVP does not enforce authentication. Intended for trusted-network or single-user deployment.

Planned: OIDC/SAML support configurable via environment variables, with no assumption about
a specific identity provider. The API will never hard-code an auth backend.

## Audit Trail

Decision records are designed as immutable, append-only records. Every state change creates a
new version — not an in-place update. This constraint is enforced at the data model layer.

## Dependency Security

- Base images are pinned to specific major versions (no `latest` tag).
- Python dependencies are pinned in `requirements.txt`.
- Node dependencies are locked via `package-lock.json`.
- Planned: automated dependency scanning in CI (optional, not required for on-prem deploys).

## Reporting Vulnerabilities

Open a GitHub issue with the `security` label. Do not include exploit details in public issues.
