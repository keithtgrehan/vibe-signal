# Regression Failure Triage

Status: synthetic API regression triage only. This is not real-world accuracy, model-quality proof, production readiness, cheating detection, hidden-intent detection, emotion detection, diagnosis, or legal review.

## Baseline Reviewed

- Baseline local API regression: `189/455`.
- Baseline evidence completeness: `455/455`.
- Baseline unsafe-output block rate: `455/455`.
- Baseline low-signal fallback correctness: `455/455`.
- Baseline reviewed-label status: `bootstrap`, not human-reviewed.

## Top Unexpected Cues Before Cleanup

1. `specificity`: `237`
2. `hedging`: `91`
3. `specificity_drop`: `91`
4. `topic_shift`: `91`
5. `unclear_ask`: `91`
6. `directness`: `91`
7. `escalation_risk`: `91`
8. `response_timing`: `83`
9. `urgency`: `45`
10. `answer_evasion_pattern`: `45`

## Top Missing Expected Cues Before Cleanup

- None locally. The deployed sample from PR #21 missed `answer_evasion_pattern`, `contradiction_against_prior_message`, `specificity_drop`, and `unsupported_claim_shift`, but that sample was from a backend version that did not include the current branch.

## Top Cue / Scenario Failure Pairs

- `unhappy` unexpectedly carried `hedging`, `specificity`, `specificity_drop`, `topic_shift`, and `unclear_ask`.
- `scared` unexpectedly carried `directness`, `escalation_risk`, and `specificity`.
- `boundary_pressure` unexpectedly carried `escalation_risk`, `specificity`, and `urgency`.
- `overloaded_message` unexpectedly carried `answer_evasion_pattern`, `specificity`, and `specificity_drop`.
- `cheating_ambiguous` unexpectedly carried multiple contextual cues from fixture suffix contamination and broad exact-set expectations.
- `conflict_repair` unexpectedly carried `response_timing` from synthetic one-minute same-author timestamps.

## Root Causes

- Synthetic message text included `[synthetic fixture N]`, which introduced bare numbers into analyzed text.
- The specificity regex treated bare numbers as time details.
- The generated timestamps made same-author fixture replies look like rapid follow-ups.
- `unclear_ask` fired on vague replies that were not actually asks.
- `topic_shift` fired from a standalone marker rather than requiring the previous relevant ask.
- `answer_evasion_pattern` treated clarification replies such as “send one request first” as non-answers.
- Scenario target cues were too strict for context-rich fixtures, so legitimate contextual cues were counted as failures.

## Precision Actions Taken

- Removed synthetic fixture suffixes from analyzed text and kept fixture identity in metadata.
- Spaced generated timestamps five minutes apart so `response_timing` only fires when a test intentionally supplies rapid timing.
- Tightened time regexes so bare numbers do not count as specificity.
- Removed permission-preserving wording from hedging.
- Made `topic_shift` contextual to a previous ask.
- Made `unclear_ask` require an actual vague ask.
- Suppressed directness when pressure wording is the matched directive.
- Added clarification guards for `answer_evasion_pattern` and `specificity_drop`.
- Added `allowed_extra_cues` metadata for observable context cues that are not the scenario’s target contract.

## Cues That Need Ongoing Review

- `specificity`: still appears as a bootstrap-only extra where target labels omit contextual timing details.
- `hedging`: still appears as a bootstrap-only extra in scenarios with “maybe” replies.
- `topic_shift`: still appears as a bootstrap-only extra where “Anyway” is used as observable deflection context.
- `escalation_risk`: still appears as a bootstrap-only extra in pressure/boundary scenarios.

## Highest-Impact Next Fixes

1. Add human-reviewed labels to decide whether allowed contextual cues should be target labels or reviewer-visible supporting labels.
2. Add fixture variants where dates/times are incidental rather than actionable.
3. Add topic-shift variants with normal transitions that should not fire.
4. Add pressure without urgency, urgency without pressure, and boundary-respecting urgency fixtures.
5. Keep deployed regression separate until Render is updated with the current branch.
