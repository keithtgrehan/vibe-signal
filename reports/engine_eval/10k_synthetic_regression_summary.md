# 10k Synthetic Engine Regression Summary

Status: split-aware bootstrap-only synthetic evaluation. These are not human-reviewed accuracy, model-quality, production-readiness, legal, clinical, deception, hidden-intent, attraction, cheating-detection, or relationship-outcome claims.

## Fixture Counts

- Total: `10000` synthetic messages / `5000` conversations
- `dev`: `6000` messages / `3000` conversations
- `hard_negative`: `2000` messages / `1000` conversations
- `heldout`: `1000` messages / `500` conversations
- `red_team`: `1000` messages / `500` conversations

## Regression Results

| Split | Conversations | Cue-contract passes | Evidence complete | Unsafe-output absent | Fallback correct |
| --- | ---: | ---: | ---: | ---: | ---: |
| `dev` | `3000` | `1104/3000` | `2842/3000` | `3000/3000` | `2684/3000` |
| `hard_negative` | `1000` | `332/1000` | `732/1000` | `1000/1000` | `599/1000` |
| `heldout` | `500` | `200/500` | `500/500` | `500/500` | `300/500` |
| `red_team` | `500` | `500/500` | `500/500` | `500/500` | `500/500` |

Overall evidence completeness: `4574/5000`.

Overall unsafe-output block rate: `5000/5000`.

Overall low-signal fallback correctness: `4083/5000`.

Hard-negative false-positive rate: `334` unexpected cues across `1000` hard-negative conversations (`33.4%` conversation-normalized count).

Red-team safety pass rate: `500/500`.

## Bootstrap Metrics

- Micro precision: `0.5732`
- Micro recall: `0.6827`
- Micro F1: `0.6232`
- Macro precision: `0.6494`
- Macro recall: `0.5483`
- Macro F1: `0.7223`

## Per-Split Bootstrap Metrics

| Split | Precision | Recall | F1 | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: |
| `dev` | `0.5595` | `0.7015` | `0.6225` | `2923` | `1580` |
| `hard_negative` | `0.6416` | `0.4979` | `0.5607` | `334` | `603` |
| `heldout` | `0.6` | `0.8571` | `0.7059` | `400` | `100` |
| `red_team` | `null` | `null` | `null` | `0` | `0` |

## Worst Cue Precision

1. `specificity_drop`: precision `0.0`, recall `0.0`, FP `146`, FN `158`
2. `hedging`: precision `0.242`, recall `0.7022`, FP `495`, FN `67`
3. `escalation_risk`: precision `0.3192`, recall `1.0`, FP `337`, FN `0`
4. `urgency`: precision `0.3798`, recall `0.4125`, FP `258`, FN `225`
5. `specificity`: precision `0.4061`, recall `0.7125`, FP `1015`, FN `280`
6. `directness`: precision `0.4632`, recall `0.9215`, FP `911`, FN `67`
7. `answer_evasion_pattern`: precision `0.4788`, recall `0.75`, FP `258`, FN `79`
8. `boundary_pressure`: precision `0.7656`, recall `1.0`, FP `79`, FN `0`
9. `conflict`: precision `0.8241`, recall `0.7872`, FP `79`, FN `100`
10. `ambiguity`: precision `0.8624`, recall `0.8624`, FP `79`, FN `79`

## Worst Cue Recall

1. `cognitive_load`: recall `0.0`, FN `158`
2. `contradiction_against_prior_message`: recall `0.0`, FN `237`
3. `overloaded_message`: recall `0.0`, FN `158`
4. `response_timing`: recall `0.0`, FN `158`
5. `specificity_drop`: recall `0.0`, FN `158`
6. `unclear_ask`: recall `0.0`, FN `79`
7. `unsupported_claim_shift`: recall `0.0`, FN `79`
8. `urgency`: recall `0.4125`, FN `225`
9. `reassurance`: recall `0.6159`, FN `280`
10. `hedging`: recall `0.7022`, FN `67`

## Top Confusion Groups

- `specificity_vs_directness`: directness/specificity co-fired `1036` times; `specificity` had `936` unexpected hits and `directness` had `911`.
- `hedging_vs_softening`: `hedging` had `416` unexpected hits and `reassurance` had `280` missing labels.
- `urgency_vs_pressure`: `boundary_pressure+pressure+urgency` co-fired `337` times; `urgency` had `258` unexpected hits and `225` missing labels.
- `topic_shift_vs_evasion`: `answer_evasion_pattern+topic_shift` co-fired `237` times; `answer_evasion_pattern` had `258` unexpected hits.
- `contradiction_vs_deception`: contradiction-style synthetic labels remain missed; this is a deterministic cue coverage gap, not a deception claim.

## Human Review Status

- Human review packet: `data/review/human_review_packet_v2.jsonl`
- Packet rows: `100`
- Split balance: `40` dev, `25` hard-negative, `20` held-out, `15` red-team
- Bootstrap label suggestions: `data/review/human_review_packet_v2_bootstrap_labels.jsonl`
- Human-reviewed status: `not human-reviewed`

## Next Engine Backlog

- Add or expose deterministic evidence for `cognitive_load`, `overloaded_message`, and `response_timing` in `/api/analyze`.
- Tighten `specificity` and `directness` separation.
- Review `hedging` false positives in hard-negative examples.
- Review `urgency` templates and rule coverage separately from pressure.
- Keep red-team unsafe request handling as a safety gate, not a product capability.
