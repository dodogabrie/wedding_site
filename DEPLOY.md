# Deploy Guide

## Requirements

- Docker + Docker Compose installed on the server
- Git (to clone the repo)
- Ports 8022 and 5173 open (or a reverse proxy in front)

---

## 1. Clone and configure

```bash
git clone <repo-url>
cd wedding_site
```

Make sure `data/invitation.txt` is present — it seeds the database on first start.

---

## 2. Update CORS (before building)

In `backend/main.py`, update `allow_origins` to include your production domain:

```python
allow_origins=["https://yourdomain.com"]
```

---

## 3. Build and run

```bash
docker compose up --build -d
```

- Backend: `http://<server-ip>:8022`
- Frontend (dev server): `http://<server-ip>:5173`

> **Note:** The frontend runs Vite's dev server, which is fine for low-traffic personal use.
> For a production-grade setup, see section 5 below.

---

## 4. Verify

```bash
# Check containers are running
docker compose ps

# Check backend health
curl http://localhost:8022/

# Tail logs
docker compose logs -f
```

---

## 5. Production frontend (optional but recommended)

Instead of running Vite's dev server, build a static bundle and serve it with nginx.

Replace `frontend/Dockerfile` with:

```dockerfile
FROM node:20-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

Update `docker-compose.yml` frontend port to `"80:80"`.

Also update `vite.config.js` so the API base URL points to the backend server instead of using the dev proxy.

---

## 6. Stop / restart

```bash
# Stop
docker compose down

# Restart (re-seeds DB from invitation.txt)
docker compose up -d
```

> The SQLite database is ephemeral inside the container. If you need to persist RSVP data across restarts, add a volume for the DB file in `docker-compose.yml`:
>
> ```yaml
> volumes:
>   - ./backend/wedding.db:/app/wedding.db
> ```
