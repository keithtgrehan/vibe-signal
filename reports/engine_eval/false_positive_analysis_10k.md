# Cue False-Positive / False-Negative Analysis

Status: synthetic API regression analysis only. This is not real-world accuracy, model-quality proof, cheating detection, hidden-intent detection, emotion detection, or diagnosis.

- API result rows: `5000`
- Low-signal failures: `917`
- Evidence missing cases: `426`
- Unsafe-output hits: `0`

## Top Missing Expected Cues

- `specificity`: `280`
- `reassurance`: `280`
- `contradiction_against_prior_message`: `237`
- `urgency`: `225`
- `cognitive_load`: `158`
- `overloaded_message`: `158`
- `specificity_drop`: `158`
- `response_timing`: `158`
- `conflict`: `100`
- `alignment`: `79`
- `unclear_ask`: `79`
- `ambiguity`: `79`
- `unsupported_claim_shift`: `79`
- `answer_evasion_pattern`: `79`
- `hedging`: `67`
- `directness`: `67`

## Top Unexpected Cues

- `specificity`: `936`
- `directness`: `911`
- `hedging`: `416`
- `escalation_risk`: `337`
- `answer_evasion_pattern`: `258`
- `urgency`: `258`
- `specificity_drop`: `146`
- `ambiguity`: `79`
- `boundary_pressure`: `79`
