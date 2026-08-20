# Changelog

## v1.3.0 - Learning notes + more null-tolerance fixes

- Added a learning notes endpoint (`POST /api/v1/decision-records/{id}/learning-notes`) so postmortem follow-ups can be attached to a decision record. The `LearningNote` model and table already existed but were never wired to a router or included in the record response; they're now created through the API and returned in `learning_notes` on the decision record detail payload.
- The GitHub PR parser 500'd when `pull_request`, `repository`, or `head` were sent as explicit `null` instead of omitted.
- The Terraform plan parser 500'd when `resource_changes` or a `change` block was `null`.
- The PagerDuty webhook parser 500'd when `events` was `null` instead of omitted or an empty list.
- The Argo CD ingest endpoint returned a 500 instead of a 404 when `decision_record_id` was not a valid UUID.

## v1.2.1 - Bugfix release

- Fixed PATCH on decision records: `null` for a nullable field (say, clearing a stale description) was silently dropped instead of clearing it. Explicitly nulling a required field like `title` now returns a 422 instead of attempting a broken write.
- The Argo CD ingest endpoint no longer 500s when a payload has `spec`, `status`, or `operationState` set to `null` — Argo notification templates do emit these as null in some states.
- Incident webhooks with a malformed `started_at` timestamp no longer crash the correlation pass; the timestamp is dropped and the incident still correlates.
- The release compose file defaulted to the 1.1.0 images even in the 1.2.0 package. It now defaults to the version it ships with.
- Release notes in the demo package are now generated from this changelog instead of repeating the same v1.1.0 marketing blurb on every release.
- The release workflow can be run manually with a version input; it cuts the tag itself instead of requiring a tag push.

## v1.2.0 - Hardening pass

- CI now actually lints (ruff) and gates on test failures instead of swallowing them with `|| true`. Added pip-audit and bandit as blocking checks, plus a web build job and a worker lint job — none of those ran before.
- Bumped fastapi to 0.139.0 / starlette to 1.3.1, fixing several starlette CVEs that were sitting unpatched in requirements.txt. Bumped pytest and pytest-asyncio to match.
- Fixed a moderate PostCSS XSS advisory pulled in transitively through Next.js by pinning postcss via npm overrides. Full test/build suite verified green after both bumps.
- API, web, and worker Dockerfiles now run as a non-root user instead of root. Verified each image builds and starts correctly under the new user.
- docker-compose.release.yml no longer publishes Postgres or Redis ports to the host — they were reachable from outside the Docker network by default, which contradicted the documented security model. The local dev compose file now binds them to 127.0.0.1 instead of 0.0.0.0.
- Added a real MIT LICENSE file — the README and badge claimed MIT but the repo had no license file.
- Corrected docs/security-model.md: it claimed decision records were "immutable, append-only" when the actual CRUD layer does in-place updates. Also updated the CI dependency-scanning line since it's no longer "planned."
- Fixed the Helm chart, which pointed at a nonexistent devopsledger/api Docker Hub image instead of the actual ghcr.io/gerardrecinto/devopsledger publish target. Bumped chart and appVersion to match this release.
- Replaced the README demo GIF, which was a marketing pitch-deck animation, with a real terminal recording of the API running end to end (health check, create a decision record, dashboard, list). Removed an unused second demo.gif that nothing referenced.
- Ran ruff --fix across the API codebase (57 findings, ordering/import-sort/UP017 datetime.UTC fixes) — the configured linter had never actually been run in CI.

## v1.1.0 - Demo package release

- Publish API, web portal, and worker container images from release tags.
- Add a self-hosted demo package with Docker Compose, Helm chart, env reference, docs, and demo GIF.
- Document the API, web portal, and release bundle path for evaluators and operators.

## v1.0.0 - Initial release

- Initial Community Edition release with FastAPI API, Next.js web portal, worker, Docker Compose, Helm chart, and core operational-memory docs.
