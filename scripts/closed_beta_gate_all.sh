#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/_automation_common.sh"
cd "$ROOT_DIR"

DEPLOY_STATUS="${DEPLOY_STATUS:-unverified}"
REPORT_OUT="${CLOSED_BETA_GATE_REPORT_OUT:-reports/automation/closed_beta_gate_report.md}"

section "Vibe Signal closed-beta gate"
info "Deploy status: $DEPLOY_STATUS"
info "Tester invites remain a human decision; this script only assembles repo-side gate evidence."

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
