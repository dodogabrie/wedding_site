# Deploy Guide

## Requirements

- Docker + Docker Compose installed on the server
- Git (to clone the repo)
- Port 80 open (prod) or ports 8022 + 5173 (dev)

---

## Development (local)

Quick start with Vite dev server and backend exposed directly.

```bash
git clone <repo-url>
cd wedding_site
docker compose up --build -d
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8022`

The DB is seeded from `data/invitation.txt` on every start.

---

## Production

Uses `docker-compose.prod.yml`: nginx serves the built static frontend on port 80
and proxies `/api/*` to the backend internally. The backend is not exposed publicly.

### 1. Clone and prepare

```bash
git clone <repo-url>
cd wedding_site
```

Make sure `data/invitation.txt` is present.

### 2. Check CORS

`backend/main.py` already includes `https://caterina.edoardogabrielli.com` in `allow_origins`.
If the domain changes, update that list before building.

### 3. Build and run

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

- Site: `http://<server-ip>` (port 80)
- Backend is internal only, not reachable from outside

### 4. Health check

```bash
./healthcheck.sh
```

Verifies:
- Backend API responds correctly
- nginx serves the frontend and SPA fallback works
- nginx proxies `/api/*` to the backend
- CORS preflight from the production domain is accepted
- DB was seeded and returns families

### 5. Logs and status

```bash
# Container status
docker compose -f docker-compose.prod.yml ps

# Tail all logs
docker compose -f docker-compose.prod.yml logs -f

# Backend only
docker compose -f docker-compose.prod.yml logs -f backend
```

### 6. Stop / restart

```bash
# Stop
docker compose -f docker-compose.prod.yml down

# Restart without rebuilding
docker compose -f docker-compose.prod.yml up -d

# Full rebuild (after code changes)
docker compose -f docker-compose.prod.yml up --build -d
```

> **DB persistence:** RSVP responses are stored in `backend/wedding.db`, which is mounted
> as a volume in the prod compose. Data survives container restarts. The DB is re-seeded
> from `invitation.txt` on every start, but existing RSVP responses are preserved because
> seeding only inserts guests/families, not attendance data.

### 7. Recreate the database

Use this when you want to wipe all RSVP responses and re-seed from `invitation.txt` (e.g. after updating the guest list).

```bash
# Stop containers
docker compose -f docker-compose.prod.yml down

# Delete the database file
rm backend/wedding.db

# Start again — seed_data.py runs automatically on startup
docker compose -f docker-compose.prod.yml up -d
```

> **Warning:** this permanently deletes all recorded RSVP responses. Back up first if needed:
> ```bash
> cp backend/wedding.db backend/wedding.db.bak
> ```

---

### 8. HTTPS (recommended)

Run a reverse proxy (Caddy or nginx) in front of port 80 on the host to terminate TLS.

Example with Caddy (`/etc/caddy/Caddyfile`):

```
caterina.edoardogabrielli.com {
    reverse_proxy localhost:80
}
```

Caddy auto-provisions a Let's Encrypt certificate.
