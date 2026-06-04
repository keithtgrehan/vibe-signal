#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/_automation_common.sh"
cd "$ROOT_DIR"

section "Vibe Signal agent control-room check"
info "Verifies reusable agent prompts preserve safety boundaries and required operating sections."

run_required "Agent control-room Python check" "$PYTHON_BIN" scripts/agent_control_room_check.py

section "Agent control-room check complete"
info "Agent docs are present and boundary-checked."
