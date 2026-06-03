# Synthetic WhatsApp Regression Method

Status: synthetic regression method only. This is not real-world accuracy, model-quality proof, production readiness, legal approval, or permission to use external datasets.

## Purpose

The generator at `tools/generate_synthetic_whatsapp_fixtures.py` creates deterministic WhatsApp-style synthetic conversations for cue-contract and unsafe-output regression checks. It uses hand-authored toy messages only.

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
- evidence completeness rate
- unsafe-output block rate
- cue contract coverage

Do not use:

- accuracy
- precision
- recall
- model quality
- validation

## Outputs

- `data/synthetic/whatsapp/conversations.jsonl`
- `data/synthetic/whatsapp/evaluations.jsonl`
- `reports/synthetic_whatsapp/fixture_regression_report.md`
- `reports/synthetic_whatsapp/unsafe_output_regression_report.md`

No raw private chats, tester messages, external dataset rows, embeddings, vectors, checkpoints, model files, screenshots, secrets, or provider outputs are included.
