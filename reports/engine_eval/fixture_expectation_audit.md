# Fixture Expectation Audit

Status: synthetic fixture audit only. This is not model validation, real-world accuracy, legal approval, cheating detection, hidden-intent detection, diagnosis, or production readiness.

## Audit Outcome

- The fixture set still contains `455` conversations and `1000` synthetic messages.
- No raw private chats, tester messages, external dataset rows, screenshots, secrets, embeddings, vectors, checkpoints, or model files were added.
- `cheating_ambiguous` remains private synthetic evaluation metadata only. It must never be described as a product capability.

## Fixture Changes

- Removed `[synthetic fixture N]` from message text because it contaminated cue detection with artificial bare numbers.
- Kept fixture identity in `fixture_id`, `seed`, and metadata fields rather than analyzed text.
- Changed generated timestamps from one-minute increments to five-minute increments so same-author follow-ups do not accidentally trigger `response_timing`.
- Added `allowed_extra_cues` for observable contextual cues that are legitimate but not the target cue contract for a scenario.
- Kept hard scenarios in place; no category was removed to raise pass rate.

## Expected Label Changes

- `unhappy` still targets ambiguity, answer evasion, and conflict. Specificity, hedging, specificity drop, and topic shift are allowed context because the synthetic messages visibly include those patterns.
- `scared` and `boundary_pressure` still target pressure and boundary-pressure cues. Escalation and timing details are allowed context when the visible wording supports them.
- `overloaded_message` still targets directness, cognitive load, and overloaded-message cues. Timing specificity from “tomorrow” is allowed context.
- `cheating_ambiguous` still targets ambiguity, unanswered ask behavior, specificity drop, commitment mismatch, escalation risk, and repair opportunity. Directness, specificity, hedging, topic shift, and conflict are allowed context only.

## Notes For Human Review

- Human reviewers should label observable wording only.
- Reviewers should not label hidden intent, cheating, attraction, true emotion, deception certainty, diagnosis, attachment style, neurotype, or relationship outcome.
- Allowed contextual cues are a review aid, not a human-reviewed label set.
