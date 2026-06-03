# Cue False-Positive / False-Negative Analysis

Status: synthetic API regression analysis only. This is not real-world accuracy, model-quality proof, cheating detection, hidden-intent detection, emotion detection, or diagnosis.

- API result rows: `100`
- Low-signal failures: `10`
- Evidence missing cases: `0`
- Unsafe-output hits: `0`

## Top Missing Expected Cues

- `answer_evasion_pattern`: `20`
- `contradiction_against_prior_message`: `10`
- `specificity_drop`: `10`
- `unsupported_claim_shift`: `10`

## Top Unexpected Cues

- `specificity`: `51`
- `directness`: `20`
- `escalation_risk`: `20`
- `hedging`: `20`
- `topic_shift`: `20`
- `unclear_ask`: `20`
- `response_timing`: `19`
- `boundary_pressure`: `10`
- `cognitive_load`: `10`
- `conflict`: `10`
- `overloaded_message`: `10`
- `pressure`: `10`
- `urgency`: `10`
