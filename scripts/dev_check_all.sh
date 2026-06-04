#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/_automation_common.sh"
cd "$ROOT_DIR"

section "Vibe Signal dev check"
info "Runs local compile, tests, builds, safety scanners, and whitespace checks."
info "Inputs are repo fixtures and synthetic examples only; no private chats or secrets are printed."

run_required "Python compile" "$PYTHON_BIN" -m py_compile $(git ls-files '*.py')
run_required "Python tests" "$PYTHON_BIN" -m pytest -q

if require_dir "web"; then
  run_required "Web tests" bash -lc 'cd web && npm test'
  run_required "Web production build" bash -lc 'cd web && npm run build'
fi

if require_dir "mobile"; then
  if [[ -f mobile/package.json ]]; then
    run_required "Mobile tests" bash -lc 'cd mobile && npm test'
    if has_command npx; then
      run_required "Expo public config" bash -lc 'cd mobile && npx expo config --type public'
    else
      skip "npx not found; Expo public config skipped."
    fi
  else
    skip "mobile/package.json not found; mobile checks skipped."
  fi
fi

if require_file "scripts/check_public_copy_safety.py"; then
  run_required "Public copy safety" "$PYTHON_BIN" scripts/check_public_copy_safety.py
fi

if require_file "scripts/check_no_raw_content_leaks.py"; then
  run_required "No raw content leaks" "$PYTHON_BIN" scripts/check_no_raw_content_leaks.py
fi

if require_file "scripts/check_vibe_restricted_artifacts.py"; then
  run_required "Restricted artifacts staged check" "$PYTHON_BIN" scripts/check_vibe_restricted_artifacts.py --staged
fi

run_required "Git diff whitespace check" git diff --check

section "Dev check complete"
info "All required local checks passed."
