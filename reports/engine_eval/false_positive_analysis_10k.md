# Cue False-Positive / False-Negative Analysis

Status: synthetic API regression analysis only. This is not real-world accuracy, model-quality proof, cheating detection, hidden-intent detection, emotion detection, or diagnosis.

- API result rows: `5000`
- Low-signal failures: `625`
- Evidence missing cases: `0`
- Unsafe-output hits: `0`

## Top Missing Expected Cues

- `contradiction_against_prior_message`: `158`
- `alignment`: `79`
- `ambiguity`: `79`
- `answer_evasion_pattern`: `79`

## Top Unexpected Cues

- `specificity`: `869`
- `directness`: `790`
- `hedging`: `416`
- `answer_evasion_pattern`: `337`
- `urgency`: `337`
- `escalation_risk`: `337`
- `specificity_drop`: `79`
- `ambiguity`: `79`
- `boundary_pressure`: `79`
