# Synthetic WhatsApp 10k Pattern Baseline Report

Research-only sklearn baseline over synthetic WhatsApp fixture rows.

## Non-Claims

Synthetic-only metrics are development signals only. They are not real-world validation, model-quality proof, production-readiness proof, legal/compliance approval, or a claim that Vibe Signal can infer hidden intent, attraction, deception, diagnosis, manipulation, abuse, or relationship outcomes.

## Deterministic Engine Boundary

The deterministic cue engine remains primary. This model is a research-only cue-family baseline. Model output must not be rendered directly in product UI. Future model-assisted output must pass evidence-span validation, the safe-output blocker, blocked-claim sanitizer, low-signal fallback, and a human-reviewed evaluation gate.

## Source

- Source tier: `bronze_synthetic_whatsapp_10k`
- Project mode: `research_only`
- Rows: `5000`
- Synthetic messages represented: `10000`
- Provider calls made: `False`
- External embeddings used: `False`
- Model artifact saved: `False`

## Combined Metrics

- precision: `0.812`
- recall: `0.767`
- F1: `0.7889`

## Split Metrics

- dev: precision=1.0, recall=1.0, F1=1.0, rows=3000
- hard_negative: precision=0.3699, recall=0.3053, F1=0.3345, rows=1000
- heldout: precision=0.6667, recall=0.5, F1=0.5714, rows=500
- red_team: precision=0.0, recall=0.0, F1=0.0, rows=500

## Per-Cue Metrics

- alignment: precision=0.7038, recall=1.0, F1=0.8261, FP=133, FN=0
- ambiguity: precision=1.0, recall=1.0, F1=1.0, FP=0, FN=0
- answer_evasion_pattern: precision=0.8251, recall=1.0, F1=0.9041, FP=67, FN=0
- boundary_pressure: precision=1.0, recall=1.0, F1=1.0, FP=0, FN=0
- cognitive_load: precision=1.0, recall=1.0, F1=1.0, FP=0, FN=0
- conflict: precision=1.0, recall=0.6468, F1=0.7855, FP=0, FN=166
- consent_clarity: precision=0.0, recall=0.0, F1=0.0, FP=0, FN=0
- contradiction_against_prior_message: precision=1.0, recall=1.0, F1=1.0, FP=0, FN=0
- directness: precision=0.678, recall=0.5825, F1=0.6266, FP=332, FN=501
- escalation_risk: precision=0.7022, recall=1.0, F1=0.8251, FP=67, FN=0
- hedging: precision=1.0, recall=0.7022, F1=0.8251, FP=0, FN=67
- low_signal: precision=1.0, recall=0.5336, F1=0.6959, FP=0, FN=500
- neutral: precision=0.0, recall=0.0, F1=0.0, FP=833, FN=0
- overloaded_message: precision=1.0, recall=1.0, F1=1.0, FP=0, FN=0
- pressure: precision=1.0, recall=1.0, F1=1.0, FP=0, FN=0
- reassurance: precision=1.0, recall=0.7257, F1=0.841, FP=0, FN=200
- repair_opportunity: precision=1.0, recall=0.7033, F1=0.8258, FP=0, FN=100
- specificity: precision=1.0, recall=0.5841, F1=0.7374, FP=0, FN=433
- specificity_drop: precision=1.0, recall=1.0, F1=1.0, FP=0, FN=0
- topic_shift: precision=0.7796, recall=1.0, F1=0.8762, FP=67, FN=0
- unclear_ask: precision=1.0, recall=1.0, F1=1.0, FP=0, FN=0
- unsupported_claim_shift: precision=1.0, recall=1.0, F1=1.0, FP=0, FN=0
- urgency: precision=1.0, recall=1.0, F1=1.0, FP=0, FN=0

## Hard Negative And Red Team

- hard-negative overfire rate: `0.732`
- red-team unsafe-output pass rate: `1.0`

## Evidence And Low-Signal Checks

- evidence-span coverage: `1.0`
- low-signal correctness: `0.5336`

## Calibration Buckets

- 0.00-0.25: predictions=0, cue-overlap=0.0
- 0.25-0.50: predictions=0, cue-overlap=0.0
- 0.50-0.75: predictions=477, cue-overlap=0.3501
- 0.75-1.00: predictions=4523, cue-overlap=0.7667
