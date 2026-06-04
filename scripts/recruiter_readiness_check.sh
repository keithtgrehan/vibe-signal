#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/_automation_common.sh"
cd "$ROOT_DIR"

section "Vibe Signal recruiter readiness"
info "Checks repo presentation, safety copy, and overclaim boundaries without using private data."

run_required "README exists" test -f README.md
run_required "Recruiter project summary exists" test -f docs/recruiter_readiness/project_summary.md
run_required "Recruiter repo tour exists" test -f docs/recruiter_readiness/repo_tour.md
run_required "Current PR status exists" test -f docs/recruiter_readiness/current_pr_status.md
run_required "Demo screenshots README exists" test -f docs/assets/screenshots/README.md

if require_file "scripts/check_public_copy_safety.py"; then
  run_required "Public copy safety" "$PYTHON_BIN" scripts/check_public_copy_safety.py
fi

if require_file "scripts/check_no_raw_content_leaks.py"; then
  run_required "No raw content leaks" "$PYTHON_BIN" scripts/check_no_raw_content_leaks.py
fi

section "README/repo-tour key phrases"
run_required "README has safe product framing" rg -n "observable|synthetic|closed-beta|not production|human-reviewed" README.md docs/recruiter_readiness/project_summary.md docs/recruiter_readiness/repo_tour.md

section "Overclaim scan"
run_required "No unallowlisted public-copy overclaims" "$PYTHON_BIN" scripts/check_public_copy_safety.py

section "Recruiter readiness complete"
info "Repo-facing presentation checks passed with safety caveats intact."
