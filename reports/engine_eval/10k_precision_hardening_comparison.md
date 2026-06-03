# 10k Precision Hardening Comparison

Status: bootstrap-only synthetic regression comparison. These numbers are not accuracy, model-quality, validation, or production-readiness claims.

## Before

- Overall bootstrap micro P/R/F1: `0.5732 / 0.6827 / 0.6232`
- Overall bootstrap macro P/R/F1: `0.6494 / 0.5483 / 0.7223`
- Evidence completeness: `4574/5000`
- Unsafe-output block: `5000/5000`
- Hard-negative unexpected cues: `334`
- Red-team safety: `500/500`

## After

- Overall bootstrap micro P/R/F1: `0.6646 / 0.947 / 0.7811`
- Overall bootstrap macro P/R/F1: `0.7998 / 0.9379 / 0.8278`
- Evidence completeness: `5000/5000`
- Unsafe-output block: `5000/5000`
- Hard-negative unexpected cues: `0`
- Red-team safety: `500/500`

## Per-Split After Metrics

| Split | Precision | Recall | F1 | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: |
| dev | 0.604 | 0.9242 | 0.7306 | 3160 | 395 |
| hard_negative | 1.0 | 1.0 | 1.0 | 0 | 0 |
| heldout | 0.6364 | 1.0 | 0.7778 | 400 | 0 |
| red_team | n/a | n/a | n/a | 0 | 0 |

## Cue Improvements

- Evidence completeness recovered to `5000/5000`.
- `cognitive_load`, `overloaded_message`, `response_timing`, `reassurance`, `unsupported_claim_shift`, `topic_shift`, and `unclear_ask` now show bootstrap precision/recall/F1 of `1.0 / 1.0 / 1.0`.
- Hard-negative false positives were reduced to `0`.
- `specificity_drop` improved by blocking cross-speaker acknowledgement false positives.

## Remaining Worst Cue Families

- `hedging`: precision `0.3125`, recall `1.0`, mostly co-firing with ambiguity-style templates.
- `escalation_risk`: precision `0.3192`, recall `1.0`, mostly co-firing with pressure/conflict templates where expectations may need finer labels.
- `answer_evasion_pattern`: precision `0.4129`, recall `0.75`, still confused with topic-shift and private-eval two-message constraints.
- `urgency`: precision `0.4743`, recall `1.0`, still broad in deadline-bearing pressure examples.
- `specificity`: precision `0.5234`, recall `1.0`, still broad in deadline/directness examples.

## Held-Out Note

Held-out synthetic evaluation improved from `200/500` pass count to `200/500` pass count by runner pass criteria, with split bootstrap F1 moving to `0.7778`. The held-out split still has `400` unexpected cues, so further rule cleanup should avoid direct tuning on held-out examples until the next evaluation sprint.

## Safety

- No external datasets were added.
- No raw chats or private/tester data were used.
- No model training, embeddings, provider complexity, analytics, or paywalls were added.
- Private `cheating_ambiguous` metadata remains synthetic evaluation metadata only and is not a product capability.

