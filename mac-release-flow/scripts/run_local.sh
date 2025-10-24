#!/usr/bin/env bash
set -euo pipefail

# Start/stop the local docker compose stack that mirrors EC2 deploy.
# Requires Docker Desktop. Uses deploy/compose.local.yml and .env.local.
# Usage:
#   scripts/run_local.sh up|down|logs|clean

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f ".env.local" ]]; then
  set -a; source .env.local; set +a
fi

COMPOSE_FILE="deploy/compose.local.yml"

cmd="${1:-up}"

case "$cmd" in
  up)
    docker volume create supermario_db_data >/dev/null
    docker compose -f "$COMPOSE_FILE" pull || true
    docker compose -f "$COMPOSE_FILE" up -d --no-build
    echo "App is starting. Try: curl -s http://localhost:${FLASK_PORT:-8000}/health || true"
    ;;
  down)
    docker compose -f "$COMPOSE_FILE" down
    ;;
  logs)
    docker compose -f "$COMPOSE_FILE" logs -f
    ;;
  clean)
    docker compose -f "$COMPOSE_FILE" down -v
    docker image prune -f || true
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    exit 1
    ;;
esac
