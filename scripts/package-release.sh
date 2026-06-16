#!/usr/bin/env sh
set -eu

version="${1:-}"
if [ -z "$version" ]; then
  version="$(cat VERSION)"
fi

case "$version" in
  v*) package_version="$version" ;;
  *) package_version="v$version" ;;
esac

name="devopsledger-${package_version}-demo-package"
dist_dir="dist/${name}"
archive="dist/${name}.tar.gz"

rm -rf "$dist_dir" "$archive"
mkdir -p "$dist_dir"

cp README.md "$dist_dir/"
cp CHANGELOG.md "$dist_dir/"
cp VERSION "$dist_dir/"
cp .env.example "$dist_dir/env.example"
cp -R docs "$dist_dir/docs"
cp -R deploy "$dist_dir/deploy"

cat > "$dist_dir/RELEASE_NOTES.md" <<EOF
# DevOpsLedger ${package_version}: API + Web Portal Demo Package

This release turns DevOpsLedger into a cleaner evaluation package: one download,
release-tagged images, a runnable web portal, API surface, worker, deployment
manifests, and the docs a platform team needs to judge the product seriously.

DevOpsLedger is for the moment after an infrastructure change ships and someone
asks: why did this happen, what changed, who approved it, how risky was it, and
could we roll it back?

It includes:
- API service release image: ghcr.io/gerardrecinto/devopsledger/api:${package_version#v}
- Web portal release image: ghcr.io/gerardrecinto/devopsledger/web:${package_version#v}
- Worker release image: ghcr.io/gerardrecinto/devopsledger/worker:${package_version#v}
- Docker Compose release file
- Helm chart
- Environment variable reference
- Product, architecture, security, on-prem, and data-model docs
- Demo GIF for the API and web portal flow

Why this matters:
- The API proves the operational-memory model is inspectable and automatable.
- The web portal gives evaluators a fast visual read on records, resources, deployments, and incidents.
- The release Compose file runs pinned images instead of local build contexts.
- The default posture remains self-hosted, offline-friendly, and telemetry-free.

Quick run:

\`\`\`bash
cp env.example .env
docker compose -f deploy/docker-compose/docker-compose.release.yml up -d
\`\`\`

Endpoints:
- API health: http://localhost:8000/health
- API docs when ENABLE_DOCS=true: http://localhost:8000/docs
- Web portal: http://localhost:3000

Best demo path:
1. Open the web portal.
2. Show the changed-resource timeline.
3. Hit API health and API docs.
4. Walk the architecture, security, and on-prem docs.
5. Point out that integrations are optional and disabled by default.
EOF

tar -czf "$archive" -C dist "$name"

echo "$archive"
