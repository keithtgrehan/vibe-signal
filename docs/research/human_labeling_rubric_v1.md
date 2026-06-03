# Human Labeling Rubric V1

Status: future reviewer rubric. Do not use labels for public accuracy claims until the review protocol, reviewer training, inter-rater agreement, data rights, and privacy review are complete.

## Reviewer Boundary

Reviewers label observable wording only. Reviewers must not label hidden intent, attraction, private feelings, deception certainty, diagnosis, neurotype, personality, relationship-style labels, or whether a user should influence another person.

## Label Fields

| Field | Description |
| --- | --- |
| fixture_id | Synthetic or rights-approved item ID. |
| cue_id | Candidate observable cue. |
| evidence_text | Exact text span supporting the cue. |
| cue_present | yes/no/unclear. |
| evidence_supports_cue | yes/no/partial. |
| false_positive_reason | Why a fired cue is unsupported. |
| false_negative_reason | Why an expected cue was missed. |
| unsafe_wording_flag | yes/no and reason. |
| low_signal_flag | yes/no. |
| reviewer_confidence | low/medium/high for observable cue only. |
| notes | Metadata-only notes. No private content unless the data source has explicit review approval. |

## Human Review Rules

- Label only text the project has rights to review.
- Prefer low signal when private context is required.
- Mark a cue unsupported if no evidence span exists.
- Mark unsafe wording if output implies private feelings, motive, diagnosis, deception certainty, attraction, manipulation, or relationship outcome.
- Do not use reviewer confidence as model confidence.
- Do not treat synthetic fixtures as real-world validation.
