#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/runner/workspace"
cd "$APP_DIR"

export PATH="$APP_DIR/.pythonlibs/bin:$PATH"

PY_SITE_PACKAGES=""
if [ -d "$APP_DIR/.pythonlibs/lib" ]; then
  PY_SITE_PACKAGES="$(find "$APP_DIR/.pythonlibs/lib" -type d -path '*/site-packages' | head -n 1 || true)"
fi

if [ -n "$PY_SITE_PACKAGES" ]; then
  export PYTHONPATH="$APP_DIR/src:$PY_SITE_PACKAGES:${PYTHONPATH:-}"
else
  export PYTHONPATH="$APP_DIR/src:${PYTHONPATH:-}"
fi

export VIBE_BACKEND_ENV="${VIBE_BACKEND_ENV:-production}"

PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
elif [ -x "$APP_DIR/.pythonlibs/bin/python3" ]; then
  PYTHON_BIN="$APP_DIR/.pythonlibs/bin/python3"
else
  echo "No Python interpreter found on PATH or in .pythonlibs/bin" >&2
  exit 127
fi

exec "$PYTHON_BIN" -m uvicorn backend.app:app \
  --host 0.0.0.0 \
  --port "${PORT:-5000}" \
  --no-access-log
