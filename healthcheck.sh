#!/bin/bash
# Health check script for wedding site (prod stack)
# Run after: docker compose -f docker-compose.prod.yml up -d

set -e

FRONTEND="http://localhost"
BACKEND="http://localhost:8022"
PASS=0
FAIL=0

ok()   { echo "  [OK]  $1"; PASS=$((PASS+1)); }
fail() { echo "  [FAIL] $1"; FAIL=$((FAIL+1)); }

echo ""
echo "=== Backend direct ==="

# Backend health
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND/")
[ "$STATUS" = "200" ] && ok "Backend root / -> 200" || fail "Backend root / -> $STATUS"

# Backend API families
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND/api/families")
[ "$STATUS" = "200" ] && ok "Backend GET /api/families -> 200" || fail "Backend GET /api/families -> $STATUS"

# Backend API guests
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND/api/guests")
[ "$STATUS" = "200" ] && ok "Backend GET /api/guests -> 200" || fail "Backend GET /api/guests -> $STATUS"

echo ""
echo "=== Frontend (nginx) ==="

# Nginx serves index.html
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND/")
[ "$STATUS" = "200" ] && ok "Nginx GET / -> 200" || fail "Nginx GET / -> $STATUS"

# Nginx SPA fallback (any unknown route should return index.html, not 404)
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND/some-deep-route")
[ "$STATUS" = "200" ] && ok "Nginx SPA fallback -> 200" || fail "Nginx SPA fallback -> $STATUS"

echo ""
echo "=== Frontend -> Backend proxy (via nginx) ==="

# Nginx proxies /api/ to backend
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND/api/families")
[ "$STATUS" = "200" ] && ok "Nginx /api/families proxied -> 200" || fail "Nginx /api/families proxied -> $STATUS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND/api/guests")
[ "$STATUS" = "200" ] && ok "Nginx /api/guests proxied -> 200" || fail "Nginx /api/guests proxied -> $STATUS"

# CORS preflight from production origin
echo ""
echo "=== CORS preflight ==="
CORS=$(curl -s -o /dev/null -w "%{http_code}" \
  -X OPTIONS "$FRONTEND/api/families" \
  -H "Origin: https://caterina.edoardogabrielli.com" \
  -H "Access-Control-Request-Method: GET")
[ "$CORS" = "200" ] || [ "$CORS" = "204" ] \
  && ok "CORS preflight /api/families -> $CORS" \
  || fail "CORS preflight /api/families -> $CORS"

echo ""
echo "=== Data sanity ==="

# Check families response is a non-empty JSON array
BODY=$(curl -s "$FRONTEND/api/families")
echo "$BODY" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if isinstance(data, list) and len(data) > 0:
    print(f'  [OK]  /api/families returned {len(data)} families')
else:
    print(f'  [FAIL] /api/families returned unexpected data: {data}')
    sys.exit(1)
" && PASS=$((PASS+1)) || FAIL=$((FAIL+1))

echo ""
echo "================================"
echo "  Passed: $PASS  |  Failed: $FAIL"
echo "================================"
echo ""

[ "$FAIL" -eq 0 ] && exit 0 || exit 1
