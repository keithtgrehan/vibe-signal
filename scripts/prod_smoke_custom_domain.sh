#!/usr/bin/env bash
set -euo pipefail

WEB_PRIMARY="https://www.vibe-signal.com"
WEB_APEX="https://vibe-signal.com"
ORIGIN="https://www.vibe-signal.com"
ORIGIN_HEADER="Origin: https://www.vibe-signal.com"
HEALTHZ_URL="https://vibe-signal.onrender.com/healthz"
STATUS_URL="https://vibe-signal.onrender.com/api/status"
ANALYZE_URL="https://vibe-signal.onrender.com/api/analyze"
LEGAL_PRIVACY_URL="https://vibe-signal.onrender.com/legal/privacy"
API_LEGAL_PRIVACY_URL="https://vibe-signal.onrender.com/api/legal/privacy"
TMP_DIR="$(mktemp -d)"

trap 'rm -rf "$TMP_DIR"' EXIT

pass() {
  printf 'PASS %s\n' "$1"
}

warn() {
  printf 'WARN %s\n' "$1"
}

fail() {
  printf 'FAIL %s\n' "$1" >&2
  exit 1
}

require_curl() {
  command -v curl >/dev/null 2>&1 || fail "curl is required"
}

http_status() {
  local method="$1"
  local url="$2"
  local output="$3"
  shift 3
  curl -sS -X "$method" -o "$output" -w '%{http_code}' "$@" "$url"
}

expect_status_class() {
  local label="$1"
  local status="$2"
  local classes="$3"
  if [[ "$classes" == *"2"* && "$status" == 2* ]]; then
    pass "$label ($status)"
    return
  fi
  if [[ "$classes" == *"3"* && "$status" == 3* ]]; then
    pass "$label ($status)"
    return
  fi
  fail "$label returned HTTP $status"
}

check_head() {
  local label="$1"
  local url="$2"
  local output="$TMP_DIR/${label// /_}.headers"
  local status
  status="$(curl -sS -I -o "$output" -w '%{http_code}' "$url")"
  expect_status_class "$label" "$status" '2*|3*'
}

check_get_json() {
  local label="$1"
  local url="$2"
  local output="$TMP_DIR/${label// /_}.json"
  local status
  status="$(http_status GET "$url" "$output" -H 'Accept: application/json')"
  expect_status_class "$label" "$status" '2*'
}

check_analyze_post() {
  local output="$TMP_DIR/analyze.json"
  local payload
  payload='{"text":"Alex: Are you still up for talking tonight?\n\nSam: Maybe, I am pretty drained."}'
  local status
  status="$(
    http_status POST "$ANALYZE_URL" "$output" \
      -H 'Content-Type: application/json' \
      -d "$payload"
  )"
  expect_status_class "POST /api/analyze synthetic text" "$status" '2*'
}

check_cors_options() {
  local output="$TMP_DIR/cors.headers"
  local status
  status="$(
    curl -sS -i -X OPTIONS "$ANALYZE_URL" \
      -H "$ORIGIN_HEADER" \
      -H 'Access-Control-Request-Method: POST' \
      -H 'Access-Control-Request-Headers: Content-Type' \
      -o "$output" \
      -w '%{http_code}'
  )"
  expect_status_class "CORS OPTIONS /api/analyze from www" "$status" '2*'
  grep -qi "access-control-allow-origin: $ORIGIN" "$output" ||
    fail "CORS OPTIONS did not allow $ORIGIN"
}

check_optional_api_legal() {
  local output="$TMP_DIR/api_legal_privacy.json"
  local status
  status="$(http_status GET "$API_LEGAL_PRIVACY_URL" "$output" -H 'Accept: application/json')"
  if [[ "$status" == 2* ]]; then
    pass "GET /api/legal/privacy backend parity ($status)"
  else
    warn "GET /api/legal/privacy returned $status; Render may be stale. The frontend legal pages are static-first."
  fi
}

main() {
  require_curl
  printf 'Vibe Signal custom-domain production smoke\n'
  printf 'Synthetic text only. Do not paste personal content into this script.\n'

  check_head "curl -I https://www.vibe-signal.com" "$WEB_PRIMARY"
  check_head "curl -I https://vibe-signal.com" "$WEB_APEX"
  check_get_json "GET /healthz" "$HEALTHZ_URL"
  check_get_json "GET /api/status" "$STATUS_URL"
  check_cors_options
  check_analyze_post
  check_get_json "GET /legal/privacy" "$LEGAL_PRIVACY_URL"
  check_optional_api_legal

  pass "custom-domain smoke complete"
}

main "$@"
