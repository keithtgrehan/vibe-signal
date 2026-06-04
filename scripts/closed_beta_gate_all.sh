#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/_automation_common.sh"
cd "$ROOT_DIR"

BASE_URL="${1:-$DEFAULT_PROD_BASE_URL}"
EXPECTED_GIT_COMMIT="${EXPECTED_GIT_COMMIT:-$(git rev-parse HEAD 2>/dev/null || true)}"
DEPLOY_STATUS="unverified"
DEFAULT_LATEST_REPORT_OUT="reports/automation/latest/closed_beta_gate_report.md"
TRACKED_REPORT_OUT="docs/proof/closed_beta/closed_beta_gate_report.md"
if [[ "${WRITE_REPORT:-0}" == "1" && -z "${CLOSED_BETA_GATE_REPORT_OUT:-}" ]]; then
  REPORT_OUT="$TRACKED_REPORT_OUT"
else
  REPORT_OUT="${CLOSED_BETA_GATE_REPORT_OUT:-$DEFAULT_LATEST_REPORT_OUT}"
fi

derive_deploy_status() {
  local verifier_output
  verifier_output="$(mktemp)"
  local verifier_status=0
  local parsed_status=""
  local command=("$PYTHON_BIN" scripts/verify_deployed_version.py --base-url "$BASE_URL" --timeout-seconds 30 --format json)

  if [[ -n "$EXPECTED_GIT_COMMIT" ]]; then
    command+=(--expected-git-commit "$EXPECTED_GIT_COMMIT")
  else
    info "Expected git commit unavailable; deployed version proof may be unverified."
  fi

  section "Deployed version verification"
  if "${command[@]}" >"$verifier_output"; then
    verifier_status=0
  else
    verifier_status=$?
  fi
  cat "$verifier_output"

  parsed_status="$(sed -n 's/.*"version_status"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$verifier_output" | head -n 1)"
  rm -f "$verifier_output"

  case "$parsed_status" in
    current|stale|unverified)
      DEPLOY_STATUS="$parsed_status"
      ;;
    *)
      DEPLOY_STATUS="unverified"
      info "Deployed version status could not be parsed; using unverified."
      ;;
  esac

  if [[ "$verifier_status" -ne 0 && "$DEPLOY_STATUS" != "stale" ]]; then
    info "Deployed version verifier exited non-zero; using $DEPLOY_STATUS."
  fi
}

section "Vibe Signal closed-beta gate"
info "Tester invites remain a human decision; this script only assembles repo-side gate evidence."

if require_file "scripts/verify_deployed_version.py"; then
  derive_deploy_status
else
  info "Deployed version verifier unavailable; using unverified."
fi

info "Deploy status: $DEPLOY_STATUS"

mkdir -p "$(dirname "$REPORT_OUT")"

if require_file "scripts/closed_beta_gate_check.py"; then
  run_required "Closed-beta gate checker" "$PYTHON_BIN" scripts/closed_beta_gate_check.py --deploy-status "$DEPLOY_STATUS" --report-out "$REPORT_OUT"
fi

section "Final tester invite decision"
if rg -q "Tester invites remain .*BLOCKED|BLOCKED|MANUAL_REQUIRED" "$REPORT_OUT"; then
  info "Tester invite decision: BLOCKED_OR_MANUAL_REQUIRED. Human/legal/device gates still control release."
else
  info "Tester invite decision: REVIEW_REQUIRED. A human owner must approve any tester invite."
fi

section "Closed-beta gate complete"
info "Report written to $REPORT_OUT"
