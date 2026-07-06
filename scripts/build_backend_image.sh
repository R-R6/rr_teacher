#!/usr/bin/env sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Building admin console static assets..."
node admin-web/scripts/build.mjs

if [ ! -f frontend/admin-dist/index.html ]; then
  echo "frontend/admin-dist/index.html not found after admin build" >&2
  exit 1
fi

TAG="${1:-chem-teacher/backend:local}"

echo "==> Building Docker image: $TAG"
docker build -f backend/Dockerfile -t "$TAG" .

echo "==> Done."
echo "Verify locally: docker run --rm -p 8000:8080 -e DEBUG=true -e DB_TYPE=sqlite $TAG"
