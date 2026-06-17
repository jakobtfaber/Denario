#!/usr/bin/env bash
set -euo pipefail

# Simple smoke tests for proxy: healthz, CORS, and cache namespacing
# Usage: bash ./proxy_smoke_tests.sh [BASE_URL] [TOKEN_A] [TOKEN_B]
# Defaults: BASE_URL=http://localhost:8090, tokens empty

BASE_URL=${1:-http://localhost:8090}
TOKEN_A=${2:-}
TOKEN_B=${3:-}

echo "[1/4] Health endpoint"
curl -fsS "$BASE_URL/healthz" | jq . || curl -fsS "$BASE_URL/healthz" | cat

echo "\n[2/4] CORS preflight (OPTIONS /healthz)"
curl -fsS -X OPTIONS -H 'Origin: http://localhost:7870' -H 'Access-Control-Request-Method: GET' \
  -D - "$BASE_URL/healthz" -o /dev/null | sed -n '1,20p'

echo "\n[3/4] Cache namespacing HIT test (same token)"
BODY='{"model":"gpt-4o-mini","messages":[{"role":"user","content":"ping"}],"stream":false}'
curl -fsS -H "Authorization: Bearer $TOKEN_A" -H 'Content-Type: application/json' \
  -d "$BODY" "$BASE_URL/chat/completions" -D /tmp/resp1.h -o /tmp/resp1.b || true
curl -fsS -H "Authorization: Bearer $TOKEN_A" -H 'Content-Type: application/json' \
  -d "$BODY" "$BASE_URL/chat/completions" -D /tmp/resp2.h -o /tmp/resp2.b || true
echo "First X-Proxy-Cache header:"; grep -i '^X-Proxy-Cache' /tmp/resp1.h || true
echo "Second X-Proxy-Cache header (expect HIT):"; grep -i '^X-Proxy-Cache' /tmp/resp2.h || true

echo "\n[4/4] Cache namespacing MISS test (different token)"
curl -fsS -H "Authorization: Bearer $TOKEN_B" -H 'Content-Type: application/json' \
  -d "$BODY" "$BASE_URL/chat/completions" -D /tmp/resp3.h -o /tmp/resp3.b || true
echo "Third X-Proxy-Cache header (expect MISS):"; grep -i '^X-Proxy-Cache' /tmp/resp3.h || true

echo "\nDone."


