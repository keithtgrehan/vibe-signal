# Synthetic WhatsApp Regression Method

Status: synthetic regression method only. This is not real-world accuracy, model-quality proof, production readiness, legal approval, or permission to use external datasets.

## Purpose

The generator at `tools/generate_synthetic_whatsapp_fixtures.py` creates deterministic WhatsApp-style synthetic conversations for cue-contract and unsafe-output regression checks. It uses hand-authored toy messages only.

API regression is run with `tools/run_synthetic_fixture_regression.py`, which sends synthetic fixture conversations to `/api/analyze` and stores API responses separately from fixture definitions.

## 10k Split-Aware Evaluation

The split-aware generator command is:

```bash
python tools/generate_synthetic_whatsapp_fixtures.py --messages 10000 --splits dev=6000,hard_negative=2000,heldout=1000,red_team=1000 --no-api
```

It writes:

- `data/synthetic/whatsapp/fixture_manifest.json`
- `data/synthetic/whatsapp/dev/conversations.jsonl`
- `data/synthetic/whatsapp/hard_negative/conversations.jsonl`
- `data/synthetic/whatsapp/heldout/conversations.jsonl`
- `data/synthetic/whatsapp/red_team/conversations.jsonl`
- `data/synthetic/whatsapp/conversations.jsonl`

The held-out split is generated separately and should not be used for rule tuning in the same sprint. Hard-negative fixtures are intentionally difficult and should remain visible even when they lower bootstrap metrics.

## Legacy 1k Categories

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

## Split Scenario Families

- Core positive / normal: happy, new-in-love metadata, in-love metadata, warm reassurance, repair success, clear asks/answers, boundary-respecting requests.
- Ambiguity / clarity: vague timing, unclear ask, unanswered ask, soft yes, indirect ask, topic shift, mixed signal, overloaded messages.
- Multi-message context: specificity drop, commitment mismatch, contradiction, answer evasion, unsupported claim shift, response timing delay/stacking.
- Pressure / conflict: urgency without pressure, pressure with urgency, boundary pressure, repeated request after no, conflict escalation, repair, blame language.
- Private eval only: cheating-ambiguous private labels. These are never product outputs.
- Low signal: short/contextless text.
- Red-team safety: unsafe inference requests that should be blocked or redirected safely.

## Metrics Names

Use:

- fixture regression pass rate
- synthetic API regression pass rate
- evidence completeness rate
- unsafe-output block rate
- cue contract coverage
- bootstrap-only reviewed-label comparison
- bootstrap-only micro/macro precision, recall, and F1
- split-aware hard-negative false-positive rate
- red-team safety pass rate

Do not use:

- accuracy without human-reviewed labels
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
- `reports/engine_eval/10k_synthetic_regression_summary.md`
- `reports/engine_eval/dev_regression_report.md`
- `reports/engine_eval/hard_negative_regression_report.md`
- `reports/engine_eval/heldout_regression_report.md`
- `reports/engine_eval/red_team_regression_report.md`
- `reports/engine_eval/bootstrap_metrics_by_split.md`
- `reports/engine_eval/bootstrap_metrics_by_cue.json`
- `reports/engine_eval/bootstrap_metrics_by_scenario.json`
- `reports/engine_eval/cue_confusion_groups.md`
- `reports/engine_eval/false_positive_analysis_10k.md`
- `reports/engine_eval/next_engine_improvement_backlog.md`

No raw private chats, tester messages, external dataset rows, embeddings, vectors, checkpoints, model files, screenshots, secrets, or provider outputs are included.

## Fixture Contract Notes

- Fixture text does not include fixture IDs or synthetic markers inside the analyzed message body; fixture identity lives in metadata.
- Generated timestamps avoid accidental rapid same-author follow-up cues unless a test intentionally supplies rapid timing.
- `allowed_extra_cues` marks observable context cues that are acceptable but not the scenario's target cue contract.
- `cheating_ambiguous` remains private synthetic evaluation metadata only and must never appear as a product claim.
