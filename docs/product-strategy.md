# DevOpsLedger Product Strategy

## Model: Open-Core

DevOpsLedger is open-core. The Community Edition (CE) is fully open source,
genuinely useful, and includes core platform engineering integrations. Premium
features are reserved for hosted convenience, governance, compliance, enterprise
scale, advanced identity, AI assistance, and support — not for gating the core
product value.

**Payment and subscription features are not implemented yet.**
This document defines the intended split, not the current implementation.

---

## Community Edition (Free, Open Source, Self-Hosted)

The CE must be useful enough for a real platform engineering team to run in
production without any upgrade. The core value — operational memory for GitOps
teams — must be fully available for free.

### Core Features (CE)

**Decision Records**
- Infra decision records (intent, risk, approval, rollback, deployment, learning)
- Changed resource timeline
- Append-only audit trail

**Integrations (planned, all optional, all free)**
- GitHub PR ingestion (open source and GitHub Enterprise basic)
- Terraform / OpenTofu plan parsing
- Argo CD basic deployment and sync events
- PagerDuty basic incident and change webhook
- Generic incident webhook (any incident tool)
- Jira issue link parsing
- CODEOWNERS approval checks

**Risk and Readiness**
- Risk scoring (rules-based)
- Rollback readiness scoring
- YAML-configurable custom risk rules
- Basic incident correlation

**Platform**
- Self-hosted deployment via Docker Compose
- Helm chart (planned)
- Environment-variable configuration
- Local / offline mode — no required outbound SaaS calls
- No telemetry by default
- Basic dashboard

---

## Premium (Future — Not Implemented)

Premium targets teams and organizations that need hosted convenience, compliance
depth, enterprise identity, advanced analytics, AI assistance, or commercial support.
It does not restrict core DevOps functionality.

### Hosted Cloud
- DevOpsLedger Cloud (managed hosting)
- Managed upgrades and backups
- Team workspaces

### Identity and Access
- SSO / SAML / OIDC advanced auth
- SCIM provisioning
- RBAC (role-based access control)

### Compliance and Audit
- Advanced compliance and audit exports
- SOC 2 evidence reports
- Change window enforcement
- Policy enforcement and merge gates

### Analytics and Intelligence
- Advanced analytics
- Team maturity dashboards
- Advanced graph queries
- AI-generated change narratives
- AI-generated postmortem drafts

### Enterprise Integrations
- Advanced Jira / ServiceNow / PagerDuty bidirectional sync
- AWS / GCP / Azure cost integrations

### Enterprise Deployment
- Air-gapped enterprise install bundles
- Private registry images
- Custom integrations
- Long-term managed data retention

### Support
- Enterprise support SLA

---

## Why Core Integrations Are Free

Platform engineering teams already run GitHub, Terraform/OpenTofu, Argo CD,
and PagerDuty. DevOpsLedger is only useful if it connects to those tools.
Putting those integrations behind a paywall would make the free version useless
and undermine the product's reason to exist.

The free CE must be usable in production for a real team without upgrading.

---

## Why Premium Focuses on Scale, Governance, and Hosted Convenience

Most platform teams at small to mid-size companies can operate DevOpsLedger CE
without premium. Premium adds value at the organizational layer:

- Large teams need RBAC, SCIM, and SSO.
- Regulated industries need SOC 2 evidence and compliance exports.
- Teams that don't want to operate their own infrastructure need managed hosting.
- Teams that want AI-assisted postmortems and narratives need LLM integration.
- Enterprise procurement needs SLA-backed support.

None of these restrict the core product. A team running 50 infrastructure changes
a week can get full value from CE.

---

## What We Will Never Do

- Gate core DevOps integrations (GitHub, Terraform, Argo CD, PagerDuty, Jira) behind premium.
- Add artificial limitations to CE to force upgrades.
- Add telemetry without explicit opt-in.
- Require outbound SaaS calls in local/offline mode.
- Embed payment or subscription checks into the open-source core.

---

## Implementation Status

| Area | Status |
|---|---|
| Scaffold / health endpoint | Done |
| Data model | Planned (next slice) |
| Decision record CRUD | Planned |
| Risk scoring | Planned |
| GitHub ingestion (CE) | Planned |
| Terraform/OpenTofu parsing (CE) | Planned |
| Argo CD events (CE) | Planned |
| PagerDuty webhook (CE) | Planned |
| Generic incident webhook (CE) | Planned |
| Jira link parsing (CE) | Planned |
| CODEOWNERS support (CE) | Planned |
| Helm chart | Planned |
| Premium features | Not started — not yet designed |
| Payment / subscriptions | Not implemented — not in scope yet |
