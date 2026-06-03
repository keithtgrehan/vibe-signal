# Engine Evaluation Reports

These reports document synthetic engine regression and bootstrap-only cue-label evaluation. They are not human-reviewed accuracy, model-quality proof, validation, or production-readiness claims.

## Current Main / PR Context

- PR #27 added the 10k split-aware synthetic evaluation system.
- PR #29 hardens evidence coverage and hard-negative precision. If #29 is not merged yet, treat its latest metrics as active PR review output.

## Key Reports

- [10k_synthetic_regression_summary.md](10k_synthetic_regression_summary.md): 10k split overview from PR #27.
- [10k_precision_hardening_comparison.md](10k_precision_hardening_comparison.md): PR #29 before/after comparison.
- [metric_calculation_audit.md](metric_calculation_audit.md): metric formula audit and macro F1 explanation.
- [evidence_gap_analysis_10k.md](evidence_gap_analysis_10k.md): evidence completeness recovery analysis.
- [hard_negative_false_positive_reduction.md](hard_negative_false_positive_reduction.md): hard-negative precision report.
- [bootstrap_metrics_by_split.md](bootstrap_metrics_by_split.md): split-level bootstrap metrics.
- [cue_confusion_groups.md](cue_confusion_groups.md): confusion-family analysis.
- [false_positive_analysis_10k.md](false_positive_analysis_10k.md): top missing/unexpected cue summary.
- [next_engine_improvement_backlog.md](next_engine_improvement_backlog.md): next deterministic cue cleanup targets.

## Latest PR #29 Local Regression Snapshot

- Overall bootstrap micro P/R/F1: `0.6646 / 0.947 / 0.7811`
- Overall bootstrap macro P/R/F1: `0.7998 / 0.9379 / 0.8278`
- Evidence completeness: `5000/5000`
- Unsafe-output block: `5000/5000`
- Red-team safety: `500/500`
- Hard-negative unexpected cues: `0`

## Known Limits

- Human-reviewed labels are pending.
- Metrics are fixture-derived bootstrap checks.
- Synthetic fixtures are not real private chats and not external datasets.
- No real-world accuracy claim is made.

