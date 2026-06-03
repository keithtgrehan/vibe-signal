# Synthetic WhatsApp Regression Method

Status: synthetic regression method only. This is not real-world accuracy, model-quality proof, production readiness, legal approval, or permission to use external datasets.

## Purpose

The generator at `tools/generate_synthetic_whatsapp_fixtures.py` creates deterministic WhatsApp-style synthetic conversations for cue-contract and unsafe-output regression checks. It uses hand-authored toy messages only.

API regression is run with `tools/run_synthetic_fixture_regression.py`, which sends synthetic fixture conversations to `/api/analyze` and stores API responses separately from fixture definitions.

## Categories

- `happy`
- `new_in_love`
- `in_love`
- `unhappy`
- `scared`
- `cheating_ambiguous`
- `low_signal`
- `boundary_pressure`
- `conflict_repair`
- `overloaded_message`

`cheating_ambiguous` is private synthetic evaluation metadata only. It exists to stress ambiguity, unanswered asks, specificity drop, commitment mismatch, conflict escalation, and repair-opportunity behavior. Vibe Signal must never claim cheating detection.

## Metrics Names

Use:

- fixture regression pass rate
- synthetic API regression pass rate
- evidence completeness rate
- unsafe-output block rate
- cue contract coverage
- bootstrap-only reviewed-label comparison

Do not use:

- accuracy
- precision
- recall
- model quality
- validation

## Outputs

- `data/synthetic/whatsapp/conversations.jsonl`
- `reports/engine_eval/synthetic_regression_api_responses.jsonl`
- `reports/engine_eval/synthetic_regression_results.jsonl`
- `reports/engine_eval/synthetic_regression_report.md`
- `reports/engine_eval/false_positive_analysis.md`
- `reports/engine_eval/cue_improvement_backlog.md`
- `reports/engine_eval/regression_comparison_after_precision_cleanup.md`

No raw private chats, tester messages, external dataset rows, embeddings, vectors, checkpoints, model files, screenshots, secrets, or provider outputs are included.

## Fixture Contract Notes

- Fixture text does not include fixture IDs or synthetic markers inside the analyzed message body; fixture identity lives in metadata.
- Generated timestamps avoid accidental rapid same-author follow-up cues unless a test intentionally supplies rapid timing.
- `allowed_extra_cues` marks observable context cues that are acceptable but not the scenario's target cue contract.
- `cheating_ambiguous` remains private synthetic evaluation metadata only and must never appear as a product claim.
