#!/usr/bin/env bash

set -o pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON:-python}"
DEFAULT_PROD_BASE_URL="${VIBE_SIGNAL_PROD_BASE_URL:-https://vibe-signal.onrender.com}"

section() {
  printf '\n== %s ==\n' "$1"
}

info() {
  printf '[INFO] %s\n' "$1"
}

skip() {
  printf '[SKIP] %s\n' "$1"
}

run_required() {
  section "$1"
  shift
  "$@"
}

run_optional() {
  section "$1"
  shift
  if "$@"; then
    return 0
  fi
  skip "$1 failed or is unavailable; continuing because this check is optional."
  return 0
}

run_required_with_retry() {
  local label="$1"
  local attempts="$2"
  local delay_seconds="$3"
  shift 3

  section "$label"
  local attempt=1
  while true; do
    if "$@"; then
      return 0
    fi
    if [[ "$attempt" -ge "$attempts" ]]; then
      return 1
    fi
    info "$label failed on attempt $attempt/$attempts; retrying in ${delay_seconds}s."
    sleep "$delay_seconds"
    attempt=$((attempt + 1))
  done
}

require_file() {
  local path="$1"
  if [[ ! -f "$ROOT_DIR/$path" ]]; then
    skip "$path not found."
    return 1
  fi
}

require_dir() {
  local path="$1"
  if [[ ! -d "$ROOT_DIR/$path" ]]; then
    skip "$path not found."
    return 1
  fi
}

has_command() {
  command -v "$1" >/dev/null 2>&1
}
