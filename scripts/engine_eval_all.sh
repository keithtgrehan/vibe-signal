#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/_automation_common.sh"
cd "$ROOT_DIR"

ENGINE_MESSAGES="${ENGINE_EVAL_MESSAGES:-10000}"
ENGINE_SPLITS="${ENGINE_EVAL_SPLITS:-dev=6000,hard_negative=2000,heldout=1000,red_team=1000}"
ENGINE_OUT_DIR="${ENGINE_EVAL_OUT_DIR:-reports/automation/synthetic/whatsapp}"
ENGINE_REPORT_DIR="${ENGINE_EVAL_REPORT_DIR:-reports/automation/engine_eval}"

section "Vibe Signal engine eval"
info "Uses synthetic fixtures only. No external data sources, no ML training, and no production API load by default."
info "Default run is the full manual 10k synthetic suite written under ignored reports/automation paths."
info "Set ENGINE_EVAL_MESSAGES and ENGINE_EVAL_SPLITS to run a smaller local debug set."
mkdir -p "$ENGINE_OUT_DIR" "$ENGINE_REPORT_DIR"

if require_file "tools/generate_synthetic_whatsapp_fixtures.py"; then
  run_required "Synthetic fixture generation and local split-aware regression" \
    "$PYTHON_BIN" tools/generate_synthetic_whatsapp_fixtures.py \
      --messages "$ENGINE_MESSAGES" \
      --splits "$ENGINE_SPLITS" \
      --out-dir "$ENGINE_OUT_DIR" \
      --engine-report-dir "$ENGINE_REPORT_DIR"
fi

if require_file "tools/evaluate_reviewed_cue_labels.py"; then
  run_required "Bootstrap metrics by split and cue" \
    "$PYTHON_BIN" tools/evaluate_reviewed_cue_labels.py \
      --bootstrap \
      --all-splits \
      --synthetic-root "$ENGINE_OUT_DIR" \
      --split-results-root "$ENGINE_REPORT_DIR/splits" \
      --split-report-out "$ENGINE_REPORT_DIR/bootstrap_metrics_by_split.md" \
      --per-cue-out "$ENGINE_REPORT_DIR/bootstrap_metrics_by_cue.json" \
      --per-scenario-out "$ENGINE_REPORT_DIR/bootstrap_metrics_by_scenario.json" \
      --metrics-out "$ENGINE_REPORT_DIR/bootstrap_metrics_automation.json"
fi

if require_file "tools/analyze_cue_confusion_groups.py"; then
  run_required "Cue confusion groups" \
    "$PYTHON_BIN" tools/analyze_cue_confusion_groups.py \
      --all-splits \
      --split-results-root "$ENGINE_REPORT_DIR/splits" \
      --report-out "$ENGINE_REPORT_DIR/cue_confusion_groups.md" \
      --summary-out "$ENGINE_REPORT_DIR/cue_confusion_groups.json"
fi

if require_file "tools/analyze_cue_false_positives.py"; then
  run_required "False-positive and false-negative analysis" \
    "$PYTHON_BIN" tools/analyze_cue_false_positives.py \
      --all-splits \
      --split-results-root "$ENGINE_REPORT_DIR/splits" \
      --report-out "$ENGINE_REPORT_DIR/false_positive_analysis_10k.md" \
      --backlog-out "$ENGINE_REPORT_DIR/next_engine_improvement_backlog.md"
fi

section "Engine eval complete"
info "Reports are bootstrap-only synthetic regression outputs, not human-reviewed accuracy or model-quality claims."
