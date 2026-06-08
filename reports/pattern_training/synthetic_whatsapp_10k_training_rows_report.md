# Synthetic WhatsApp 10k Training Rows Report

Synthetic-only fixture conversion for a research-only pattern-recognition baseline.

## Source Discovery

- Input directory: `data/synthetic/whatsapp`
- Source JSONL: `data/synthetic/whatsapp/conversations.jsonl`
- Source manifest: `data/synthetic/whatsapp/fixture_manifest.json`
- Discovered source conversations: `5000`
- Discovered source messages: `10000`
- Training rows written: `5000`
- Synthetic messages represented: `10000`

## Split Counts

- dev: 3000
- hard_negative: 1000
- heldout: 500
- red_team: 500

## Cue Counts

- alignment: 316
- ambiguity: 574
- answer_evasion_pattern: 316
- boundary_pressure: 258
- cognitive_load: 158
- conflict: 470
- contradiction_against_prior_message: 237
- directness: 1200
- escalation_risk: 158
- hedging: 225
- low_signal: 1072
- overloaded_message: 158
- pressure: 337
- reassurance: 729
- repair_opportunity: 337
- specificity: 1041
- specificity_drop: 158
- topic_shift: 237
- unclear_ask: 79
- unsupported_claim_shift: 79
- urgency: 304

## Unsupported Fixture Cues Excluded From Training Labels

- response_timing: 79

## Safety Boundary

Synthetic-only fixture conversion; not real-world accuracy, model quality, production readiness, legal/compliance approval, or evidence that Vibe Signal can infer private motives or outcomes.

The deterministic cue engine remains primary. This model-training row set is for local research-only cue-family baseline work. Model output must not be rendered directly in the product UI. Future model-assisted output would need evidence-span validation, safe-output blocking, blocked-claim sanitization, low-signal fallback handling, and a human-reviewed evaluation gate.

No human data, semi-synthetic data, private chats, tester messages, provider outputs, external datasets, screenshots, embeddings, vectors, checkpoints, or model artifacts are included.
