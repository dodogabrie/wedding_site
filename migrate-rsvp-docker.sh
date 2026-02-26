#!/usr/bin/env bash
set -euo pipefail

# Quick usage:
#   ./migrate-rsvp-docker.sh                 # migrate using docker-compose.prod.yml (recommended)
#   ./migrate-rsvp-docker.sh --dry-run       # preview backup/stamp/upgrade steps
#   ./migrate-rsvp-docker.sh --env prod      # explicit prod compose
#   ./migrate-rsvp-docker.sh --env dev --exec  # run in already-running dev backend container
#
# Prerequisites:
#   - Docker + docker compose
#   - backend image contains `scripts/migrate_rsvp_db.py` (this script builds by default)
#
# Backups:
#   - Stored in ./data/db-backups on the host (via /data/db-backups in the container)
#
# Migrate the RSVP SQLite DB inside the backend Docker container.
# Defaults to prod compose because it bind-mounts /app/wedding.db.
#
# Examples:
#   ./migrate-rsvp-docker.sh
#   ./migrate-rsvp-docker.sh --dry-run
#   ./migrate-rsvp-docker.sh --env dev --exec

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENVIRONMENT="prod"
DRY_RUN=0
USE_EXEC=0
SKIP_BUILD=0

usage() {
  cat <<'EOF'
Usage: ./migrate-rsvp-docker.sh [options]

Options:
  --env {prod|dev}   Compose environment to use (default: prod)
  --dry-run          Show what the migration script would do
  --exec             Run inside an already-running backend container (docker compose exec)
  --no-build         Skip backend image build step
  -h, --help         Show this help

Notes:
  - Prod mode is recommended because docker-compose.prod.yml bind-mounts ./backend/wedding.db -> /app/wedding.db.
  - Backups are written to /data/db-backups inside the container, which maps to ./data on the host.
  - Dev mode without a bind-mounted /app/wedding.db may migrate a non-persistent container-local DB.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      ENVIRONMENT="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --exec)
      USE_EXEC=1
      shift
      ;;
    --no-build)
      SKIP_BUILD=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$ENVIRONMENT" != "prod" && "$ENVIRONMENT" != "dev" ]]; then
  echo "Invalid --env value: $ENVIRONMENT (expected prod or dev)" >&2
  exit 2
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "docker compose (or docker-compose) not found" >&2
  exit 2
fi

if [[ "$ENVIRONMENT" == "prod" ]]; then
  COMPOSE_FILES=(-f docker-compose.prod.yml)
else
  COMPOSE_FILES=(-f docker-compose.yml)
  echo "WARNING: dev compose does not bind-mount /app/wedding.db in the current config." >&2
  echo "         Prefer --env prod, or use --exec on the running dev backend container." >&2
fi

MIGRATE_ARGS=(
  python
  /app/scripts/migrate_rsvp_db.py
  --backend-dir /app
  --db-path /app/wedding.db
  --backup-dir /data/db-backups
)

if [[ "$DRY_RUN" -eq 1 ]]; then
  MIGRATE_ARGS+=(--dry-run)
fi

echo "Environment: $ENVIRONMENT"
echo "Compose: ${COMPOSE_CMD[*]} ${COMPOSE_FILES[*]}"
echo "Mode: $([[ "$USE_EXEC" -eq 1 ]] && echo exec || echo run)"
echo "Migration command: ${MIGRATE_ARGS[*]}"

cd "$ROOT_DIR"

if [[ "$SKIP_BUILD" -eq 0 ]]; then
  echo "Building backend image..."
  "${COMPOSE_CMD[@]}" "${COMPOSE_FILES[@]}" build backend
fi

if [[ "$USE_EXEC" -eq 1 ]]; then
  echo "Running migration in existing backend container..."
  "${COMPOSE_CMD[@]}" "${COMPOSE_FILES[@]}" exec backend "${MIGRATE_ARGS[@]}"
else
  echo "Running migration in one-off backend container..."
  "${COMPOSE_CMD[@]}" "${COMPOSE_FILES[@]}" run --rm backend "${MIGRATE_ARGS[@]}"
fi

echo "Done."
