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
- The release Compose file (`docker-compose.release.yml`) does not publish PostgreSQL or Redis
  ports to the host at all — they're reachable only on the internal Docker network.
- The local dev Compose file (`docker-compose.yml`) binds PostgreSQL and Redis to
  `127.0.0.1` for local debugging, not `0.0.0.0`.
- TLS termination at the reverse proxy (nginx / Caddy / Traefik) — not in the application.
- No ports bound to `0.0.0.0` in production without a firewall or ingress rule.

## Authentication (Future)

The MVP does not enforce authentication. Intended for trusted-network or single-user deployment.

Planned: OIDC/SAML support configurable via environment variables, with no assumption about
a specific identity provider. The API will never hard-code an auth backend.

## Audit Trail

Decision records are mutable in the current data model: `PATCH` updates the row in place and
`updated_at` reflects the last write. Append-only versioning is not implemented yet — treat the
API as a live record store, not a tamper-evident log, until that lands.

## Dependency Security

- Base images are pinned to specific major versions (no `latest` tag).
- Python dependencies are pinned in `requirements.txt`.
- Node dependencies are locked via `package-lock.json`.
- CI runs `pip-audit` against both `requirements.txt` files and `bandit` against the API source
  on every push and pull request. A finding fails the build.

## Reporting Vulnerabilities

Open a GitHub issue with the `security` label. Do not include exploit details in public issues.
