#!/usr/bin/env bash
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=========================================================="
echo " Starting NEXUS Local Full-Stack Platform"
echo "=========================================================="

export PYTHONPATH="packages/contracts/src:packages/enforcement/src:packages/workspace/src:packages/discovery/src:packages/intelligence/src:packages/funding/src:services/api/src"
export NEXUS_GRAPH_DATA="$REPO_ROOT/data/nexus_full_graph.json"
export API_URL="http://127.0.0.1:8000"

# Check if nexus-db-1 docker container is running
if docker ps --format '{{.Names}}' | grep -q "nexus-db-1"; then
    echo "✔ Detected active PostgreSQL container: nexus-db-1 (port 5438)"
else
    echo "ℹ Starting nexus-db-1 container..."
    docker run -d --name nexus-db-1 \
      -e POSTGRES_DB=nexus \
      -e POSTGRES_USER=nexus \
      -e POSTGRES_PASSWORD=nexus_dev_password \
      -p 127.0.0.1:5438:5432 \
      postgres:16-alpine 2>/dev/null || docker start nexus-db-1
fi

echo "Starting FastAPI backend on http://127.0.0.1:8000 ..."
python3 -m uvicorn nexus_api.main:app --host 127.0.0.1 --port 8000 --reload &
API_PID=$!

echo "Starting Next.js frontend on http://localhost:3000 ..."
cd "$REPO_ROOT/frontend"
npm run dev -- -p 3000 &
WEB_PID=$!

cleanup() {
    echo "Shutting down Nexus services..."
    kill "$API_PID" "$WEB_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

wait
