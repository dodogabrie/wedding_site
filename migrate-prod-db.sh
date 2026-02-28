#!/usr/bin/env bash

set -euo pipefail

COMPOSE_FILE="docker-compose.prod.yml"
DB_PATH="backend/wedding.db"
BACKUP_PATH="backend/wedding.db.bak.$(date +%Y%m%d_%H%M%S)"

echo "Backing up ${DB_PATH} to ${BACKUP_PATH}"
cp "${DB_PATH}" "${BACKUP_PATH}"

echo "Building backend image"
docker compose -f "${COMPOSE_FILE}" build backend

echo "Running Alembic migrations"
docker compose -f "${COMPOSE_FILE}" run --rm backend alembic upgrade head

echo "Starting production stack"
docker compose -f "${COMPOSE_FILE}" up -d

echo "Done"
