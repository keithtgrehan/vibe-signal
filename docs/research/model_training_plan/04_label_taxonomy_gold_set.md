# Agent 4 - Label Taxonomy And Gold Set Design

Date: 2026-06-05

Status: research_plan_requires_gpt_user_review. Synthetic examples only.

## Goal

Create a human-review schema that supports observable wording cues, evidence spans, safe next steps, and explicit limits without turning labels into claims about a speaker's inner state.

## Row-Level Schema

Recommended fields:

- `row_id`: neutral local ID.
- `source_id`: neutral source ID only, never real-person-derived.
- `excerpt_hash_local`: optional local-only hash if needed; do not publish.
- `review_status`: `reviewed`, `needs_second_review`, `reject`, `low_signal`, `needs_more_context`.
- `primary_cue`: one primary cue or `none`.
- `secondary_cues`: list of additional cues.
- `severity`: `low`, `medium`, `high`, `not_applicable`.
- `confidence`: `low`, `medium`, `high`.
- `evidence_span_text_local`: local-only; never committed.
- `evidence_span_start`: local-only offset.
- `evidence_span_end`: local-only offset.
- `safe_next_step`: controlled label, not free-form private text.
- `cannot_infer_flags`: list of unsupported interpretations.
- `unsafe_model_output`: boolean.
- `needs_more_context`: boolean.
- `review_notes_local`: local-only and optional; no public export.
- `reviewer_id`: neutral reviewer code.
- `reviewed_at`: date.

## Cue Labels

Primary cue families:

- clarity: clear ask, explicit answer, concrete timing, concrete constraint;
- ambiguity: vague timing, unclear ask, hedged commitment, unclear yes/no;
- pressure: urgency pressure, repeated request after boundary, multi-ask overload;
- reassurance: reassurance wording, reassurance request, warmth signal;
- directness: direct ask, indirect ask, softened ask, refusal;
- cognitive load: multiple requests, topic stacking, long conditional phrasing;
- boundary pressure: continued push after no/not now/stop, guilt-loaded urgency;
- repair opportunity: apology, clarification opening, de-escalation, reframe;
- low signal: too short, missing context, single-word reply, ambiguous fragment;
- safety boundary: blocked inference request or unsafe suggested output.

## Safe Next Step Labels

Use controlled labels:

- `ask_clear_follow_up`;
- `offer_time_window`;
- `reduce_pressure`;
- `acknowledge_boundary`;
- `name_uncertainty`;
- `repair_and_reset`;
- `pause_and_wait`;
- `choose_low_stakes_check_in`;
- `do_not_send_coercive_reply`;
- `not_enough_context`.

## Synthetic Examples

These examples are synthetic and should not be copied from private rows.

| Synthetic excerpt | Label | Evidence | Safer next step |
| --- | --- | --- | --- |
| Person A: Can we pick a time for Friday? Person B: I can do 6. | clarity | "I can do 6" | Confirm the plan briefly. |
| Person A: Are you coming tonight? Person B: Maybe later, not sure yet. | ambiguity | "Maybe later" | Ask one concrete follow-up. |
| Person A: Please answer now, I need this settled. Person B: I said not now. | boundary pressure | "answer now" and "not now" | Pause and respect the boundary. |
| Person A: I get it. We can talk tomorrow if that is easier. | repair opportunity | "talk tomorrow" | Keep the lower-pressure option. |
| Person B: ok | low signal | "ok" | Do not over-interpret. |

## Reject Rules

Reject a row when:

- the excerpt is not conversation text;
- it contains content the reviewer is not permitted to handle;
- the label would require knowing intent, attraction, truthfulness, diagnosis, or outcomes;
- the safe next step would pressure someone to respond;
- the excerpt is too long or mixed to label reliably;
- the model output is unsafe or unsupported.

## Low-Signal Rules

Mark low-signal when:

- fewer than two meaningful turns are present;
- the cue depends on missing prior context;
- all candidate cues are weak;
- evidence span is not clearly tied to the label;
- the safest output is a limit statement and one low-pressure follow-up.

## Disagreement Handling

Use a second review when:

- primary cue differs between reviewers;
- severity differs by more than one level;
- evidence spans do not overlap;
- one reviewer marks unsafe output;
- one reviewer marks low-signal and another assigns a confident cue.

Resolution should record the final label and a neutral reason category, not private text.

## Row Ranking For Active Learning

Prioritize:

- under-covered cue families;
- high disagreement rows;
- deterministic false positives;
- deterministic false negatives;
- model uncertainty;
- unsafe output near misses;
- hard negatives that resemble a cue but should abstain.

## Label Counts

Planning targets:

- 50-100 reviewed rows: schema sanity and evaluator smoke.
- 250-400 reviewed rows: weak-label calibration and confusion analysis.
- 600-1,000 reviewed rows: first classical baseline at broad cue-family level only.
- 80-100 positive examples per primary cue family: minimum for first local baseline.
- 150-200 positives per high-impact cue family: product-consideration threshold.
- Leaf sub-cues need their own support counts before training at leaf level; do not assume the family-level row target is enough for every sub-cue.
- 200+ low-signal/hard-negative rows: abstention and false-positive control.
