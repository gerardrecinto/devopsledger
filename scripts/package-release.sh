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

# Pull this version's section out of the changelog so release notes track the
# actual release instead of repeating a fixed blurb.
changelog_section="$(awk -v ver="$package_version" '
  index($0, "## " ver) == 1 { flag = 1; next }
  /^## / { flag = 0 }
  flag { print }
' CHANGELOG.md)"

if [ -z "$changelog_section" ]; then
  changelog_section="See CHANGELOG.md for details."
fi

cat > "$dist_dir/RELEASE_NOTES.md" <<EOF
# DevOpsLedger ${package_version}

## What's in this release
${changelog_section}

## Demo package

- API service release image: ghcr.io/gerardrecinto/devopsledger/api:${package_version#v}
- Web portal release image: ghcr.io/gerardrecinto/devopsledger/web:${package_version#v}
- Worker release image: ghcr.io/gerardrecinto/devopsledger/worker:${package_version#v}
- Docker Compose release file, Helm chart, env reference, docs, demo GIF

\`\`\`bash
cp env.example .env
docker compose -f deploy/docker-compose/docker-compose.release.yml up -d
\`\`\`

- API health: http://localhost:8000/health
- API docs when ENABLE_DOCS=true: http://localhost:8000/docs
- Web portal: http://localhost:3000
EOF

tar -czf "$archive" -C dist "$name"

echo "$archive"
