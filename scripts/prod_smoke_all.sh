#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/_automation_common.sh"
cd "$ROOT_DIR"

BASE_URL="${1:-$DEFAULT_PROD_BASE_URL}"
EXPECTED_GIT_COMMIT="${EXPECTED_GIT_COMMIT:-$(git rev-parse HEAD 2>/dev/null || true)}"

section "Vibe Signal production smoke"
info "Base URL: $BASE_URL"
info "Runs bounded metadata-only deployed checks with synthetic payloads only. Does not run the 10k suite against production."

if require_file "scripts/verify_deployed_version.py"; then
  if [[ -n "$EXPECTED_GIT_COMMIT" ]]; then
    run_required_with_retry "Deployed version verification" 2 2 "$PYTHON_BIN" scripts/verify_deployed_version.py --base-url "$BASE_URL" --timeout-seconds 30 --expected-git-commit "$EXPECTED_GIT_COMMIT"
  else
    info "Expected git commit unavailable; deployed version proof may be unverified."
    run_required_with_retry "Deployed version verification" 2 2 "$PYTHON_BIN" scripts/verify_deployed_version.py --base-url "$BASE_URL" --timeout-seconds 30
  fi
fi

if require_file "scripts/smoke_test_production_analyze.py"; then
  run_required "Production analyze smoke" "$PYTHON_BIN" scripts/smoke_test_production_analyze.py --base-url "$BASE_URL"
fi

section "Production smoke complete"
info "Synthetic, bounded deployment checks passed."
