# Human Labeling Rubric V2

Status: future reviewer rubric for synthetic and eventual permissioned review. Current packet labels are bootstrap suggestions only and are not human reviewed.

## Reviewer Task

Label observable wording only. A cue is present only when the visible message text supports it with a concrete evidence span.

## Required Fields

- `review_id`
- `conversation_id`
- `split`
- `scenario`
- `message_id` or `span_id`
- `cue_id`
- `cue_present`
- `evidence_text`
- `evidence_start`
- `evidence_end`
- `evidence_supports_cue`
- `false_positive_reason`
- `false_negative_reason`
- `unsafe_wording_flag`
- `low_signal_flag`
- `reviewer_confidence`: `high`, `medium`, or `low`
- `reviewer`
- `reviewed_at`
- `notes`

## Do Not Label

Reviewers must not label:

- hidden intent
- cheating
- attraction
- deception certainty
- diagnosis
- neurotype
- attachment style
- true emotion
- manipulation effectiveness
- relationship outcome

## Evidence Rules

- Evidence text must be copied from the synthetic fixture text.
- If a cue depends on context that is not visible, mark the cue absent or low signal.
- If two cue families overlap, prefer the narrower observable wording cue and note the confusion group.
- Bootstrap suggestions are hints for review workflow testing, not ground truth.
