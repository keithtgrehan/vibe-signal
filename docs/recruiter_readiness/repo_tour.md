# Repo Tour

This tour is for reviewers who want to understand the current Vibe Signal implementation quickly without reading every generated report.

## Product Surface

- `web/`: hosted web frontend and synthetic demo flow.
- `mobile/`: Expo mobile app, onboarding, analysis, results, legal screens, and backend URL configuration.
- `backend/`: FastAPI backend routes for health, status, analysis, matching, feedback, legal copy, and events.

## Deterministic Engine

- `src/vibesignal_ai/features/`: cue taxonomy and deterministic feature detection.
- `src/vibesignal_ai/matching/`: match/analyze contracts, deterministic result builder, explanation logic, confidence/low-signal handling, and evidence compaction.
- `src/vibesignal_ai/evidence/`: evidence-object helpers and validation.
- `configs/vibe_cue_taxonomy.yml`: observable cue taxonomy and safe wording.

## Safety And Rights Gates

- `scripts/check_public_copy_safety.py`: blocks unsafe public copy outside allowlisted safety contexts.
- `scripts/check_no_raw_content_leaks.py`: checks for raw-content logging/persistence risks.
- `scripts/check_vibe_restricted_artifacts.py`: blocks restricted model/data artifacts.
- `configs/vibe_training_sources.example.yml`: dataset/source registry example.
- `scripts/validate_vibe_training_sources.py` and `tools/validate_training_sources.py`: rights-gate validation.
- `docs/legal_safe_output_policy.md`: public safety wording policy.
- `docs/datasets_rights.md`: dataset-rights posture.

## Engine Evaluation

- `tools/generate_synthetic_whatsapp_fixtures.py`: deterministic synthetic fixture generator.
- `tools/run_synthetic_fixture_regression.py`: actual `/api/analyze` regression runner.
- `tools/evaluate_reviewed_cue_labels.py`: fail-closed bootstrap/human-label evaluator.
- `tools/analyze_cue_false_positives.py`: false-positive and false-negative report builder.
- `tools/analyze_cue_confusion_groups.py`: confusion-family report builder.
- `data/synthetic/whatsapp/`: synthetic-only fixtures and split manifest.
- `reports/engine_eval/`: generated synthetic regression reports.

## Best Review Path

1. Read [README.md](../../README.md).
2. Read [docs/recruiter_readiness/current_pr_status.md](current_pr_status.md).
3. Inspect the web app and run a synthetic demo.
4. Review [reports/engine_eval/10k_precision_hardening_comparison.md](../../reports/engine_eval/10k_precision_hardening_comparison.md).
5. Review [reports/engine_eval/metric_calculation_audit.md](../../reports/engine_eval/metric_calculation_audit.md).
6. Review [docs/proof/closed_beta/closed_beta_go_no_go.md](../proof/closed_beta/closed_beta_go_no_go.md).

## Review Caveat

Synthetic reports are regression and contract coverage. They are not real-world validation, model-quality proof, or production-readiness evidence.

