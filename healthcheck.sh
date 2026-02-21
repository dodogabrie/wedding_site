#!/bin/bash
# Health check script for wedding site (prod stack)
# Run after: docker compose -f docker-compose.prod.yml up -d
#
# Usage:
#   ./healthcheck.sh           (default: localhost:8080)
#   FRONTEND=http://localhost ./healthcheck.sh

set -e

FRONTEND="${FRONTEND:-http://localhost:8080}"
PASS=0
FAIL=0

ok()   { echo "  [OK]  $1"; PASS=$((PASS+1)); }
fail() { echo "  [FAIL] $1"; FAIL=$((FAIL+1)); }

echo ""
echo "=== Frontend (nginx) ==="

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND/")
[ "$STATUS" = "200" ] && ok "Nginx GET / -> 200" || fail "Nginx GET / -> $STATUS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND/some-deep-route")
[ "$STATUS" = "200" ] && ok "Nginx SPA fallback -> 200" || fail "Nginx SPA fallback -> $STATUS"

echo ""
echo "=== Frontend -> Backend proxy (via nginx) ==="

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND/api/families")
[ "$STATUS" = "200" ] && ok "Nginx /api/families proxied -> 200" || fail "Nginx /api/families proxied -> $STATUS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND/api/guests")
[ "$STATUS" = "200" ] && ok "Nginx /api/guests proxied -> 200" || fail "Nginx /api/guests proxied -> $STATUS"

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
