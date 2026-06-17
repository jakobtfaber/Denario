#!/usr/bin/env bash
set -euo pipefail

# Load environment variables from local .env if present (not committed)
if [ -f .env ]; then
  echo "Loading environment from .env"
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

# Start the proxy in background
echo "Starting TPM/RPM proxy on :${PROXY_PORT:-8080}"
uvicorn --factory proxy.app:create_app --host "${PROXY_HOST:-0.0.0.0}" --port "${PROXY_PORT:-8080}" &
proxy_pid=$!

# Wait for proxy readiness (max ~10s)
proxy_ready=false
for _ in $(seq 1 20); do
  # Check if proxy process is still running
  if ! kill -0 "$proxy_pid" 2>/dev/null; then
    echo "Error: Proxy process failed to start" >&2
    exit 1
  fi
  if curl -fsS "http://127.0.0.1:${PROXY_PORT:-8080}/healthz" >/dev/null 2>&1; then
    echo "Proxy is ready."
    proxy_ready=true
    break
  fi
  sleep 0.5
done

if [ "$proxy_ready" = false ]; then
  echo "Warning: Proxy health check failed, but continuing startup"
fi

# Ensure a writable workspace and temp/cache locations
PRIMARY_RUNTIME_DIR="$HOME/app/exports"
FALLBACK_RUNTIME_DIR="/tmp/denario-exports"
DENARIO_RUNTIME_DIR="$PRIMARY_RUNTIME_DIR"
if ! mkdir -p "$DENARIO_RUNTIME_DIR" 2>/dev/null; then
  echo "Primary runtime dir $PRIMARY_RUNTIME_DIR not writable; falling back to $FALLBACK_RUNTIME_DIR"
  DENARIO_RUNTIME_DIR="$FALLBACK_RUNTIME_DIR"
  if ! mkdir -p "$DENARIO_RUNTIME_DIR"; then
    echo "Error: Failed to create runtime directory $DENARIO_RUNTIME_DIR" >&2
    exit 1
  fi
fi
export TMPDIR="$DENARIO_RUNTIME_DIR"
export XDG_CACHE_HOME="$DENARIO_RUNTIME_DIR/.cache"
export DENARIO_PROJECT_DIR="$DENARIO_RUNTIME_DIR"
export PROJECT_DIR="$DENARIO_RUNTIME_DIR"
cd "$DENARIO_RUNTIME_DIR"

echo "Starting Denario Streamlit app on :${PORT:-7860}"

# Resolve Streamlit app path: prefer bind-mounted in-repo path (absolute), otherwise locate installed package
APP_ROOT="/home/user/app"
APP_PATH="$APP_ROOT/DenarioApp/src/denario_app/app.py"
if [ ! -f "$APP_PATH" ]; then
  echo "App path $APP_PATH not found; resolving installed denario_app module path"
  APP_DIR=$(python - <<'PY'
import os, sys
try:
    import denario_app as m
    d = os.path.dirname(m.__file__)
    print(os.path.join(d, 'app.py'))
except Exception as e:
    print('')
PY
)
  if [ -n "$APP_DIR" ] && [ -f "$APP_DIR" ]; then
    APP_PATH="$APP_DIR"
  elif [ -f "/tmp/DenarioApp/src/denario_app/app.py" ]; then
    echo "Using fallback app at /tmp/DenarioApp/src/denario_app/app.py"
    APP_PATH="/tmp/DenarioApp/src/denario_app/app.py"
  else
    echo "Fatal: Could not resolve denario_app.app.py; exiting" >&2
    exit 2
  fi
fi

exec streamlit run "$APP_PATH" \
  --server.port="${PORT:-7860}" \
  --server.address=0.0.0.0 \
  -- \
  --deploy
