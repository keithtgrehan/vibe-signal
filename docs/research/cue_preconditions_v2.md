# Cue Preconditions V2

Status: deterministic engine evaluation guidance. This is not a model-quality, accuracy, validation, production-readiness, legal, clinical, deception, hidden-intent, attraction, or relationship-outcome claim.

## Scope

The cue system must describe observable wording only. If the visible text does not provide enough context, the engine should prefer low-signal fallback or a cautious missing-context note over a stronger cue.

## Single-Message Allowed

These cues may fire from one message when there is direct evidence:

- `directness`: explicit ask, answer, decision, or commitment
- `unclear_ask`: an actual ask/request is present but lacks action, owner, timing, or decision point
- `pressure`: obligation, constrained-choice, repeated demand, or reduced response space
- `urgency`: deadline or time-pressure wording in a request/need context without assuming motive
- `reassurance`: low-pressure or permission-preserving wording such as no pressure, no stress, no worries, if you can, or when you can
- `cognitive_load`: dense or multi-part wording, including long comma-separated lists that benefit from splitting
- `conflict`: observable tension or disagreement wording
- `low_signal_fallback`: short/context-light text without enough evidence-backed cues

## Multi-Message Required

These cues require at least two relevant messages or two observable statements:

- `specificity_drop`: same-speaker earlier concrete detail plus later materially vague replacement, or a direct concrete ask followed by a vague non-answer
- `contradiction_against_prior_message`: two observable statements conflict; never infer lying
- `answer_evasion_pattern`: direct question followed by non-answer, topic change, vague response, or deflection
- `response_timing`: same-speaker follow-up inside the short timestamp window; current synthetic regression uses a three-minute window
- `unsupported_claim_shift`: claim changes without evidence or explanation; never infer deception
- `topic_shift`: only when tied to an immediately relevant prior ask

## Hard Boundaries

- Urgency alone is not pressure.
- Reassurance is not anxiety, attachment style, attraction, or insecurity.
- Ambiguity is not hidden intent.
- Contradiction is not lying or deception certainty.
- Conflict escalation is not abuse, diagnosis, or personality labeling.
- Private evaluation labels must never become product output.

## Evaluation Implications

- Hard-negative fixtures should expose over-broad cue firing without being removed to improve numbers.
- Fixture expectations should be patched when they contradict cue preconditions, for example expecting response timing without same-speaker timestamp evidence.
- Held-out synthetic fixtures should stay separate from dev/regression fixtures.
- Red-team fixtures should verify safe blocking or redirection of unsafe inference requests.
- Human-reviewed labels are required before any accuracy or quality claim.
