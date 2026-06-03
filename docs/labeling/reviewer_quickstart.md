# Reviewer Quickstart

Use this quickstart only with the synthetic review packet. Do not add real private chats or tester messages.

## Setup

Open:

- `data/review/human_review_packet_v2.jsonl`
- `data/review/human_label_template.csv`
- `docs/labeling/human_labeling_rubric_v2.md`

## What To Label

For each cue row, decide whether the visible wording supports that cue.

Fill:

- `cue_present`: `true` or `false`
- `evidence_text`: exact visible text supporting the cue
- `evidence_start` / `evidence_end`: optional character offsets if available
- `evidence_supports_cue`: `true` or `false`
- `false_positive_reason` / `false_negative_reason`: only when useful
- `unsafe_wording_flag`: `true` only if the output or label text drifts into blocked inference
- `reviewer_confidence`: `high`, `medium`, or `low`
- `reviewer`
- `reviewed_at`

## Do Not Label

- hidden intent
- cheating
- attraction
- diagnosis
- deception certainty
- true emotion
- attachment style
- neurotype

If the text is too short or context-light, prefer a low-signal flag over over-reading.

