# Agent 8 - Product Safety And Explainability

Date: 2026-06-05

Status: research_plan_requires_gpt_user_review.

## Safe Model Output Contract

A model may never write final user-facing relationship advice directly. It may only emit structured candidates consumed by a safe renderer.

Required fields:

- `cue_id`;
- `cue_family`;
- `signal_label`: `strong`, `medium`, `low`, `mixed`, or `insufficient`;
- `evidence_required`: true for every non-low-signal cue;
- `evidence_span_ids` or deterministic evidence references;
- `confidence_label`, not a numeric public score;
- `safe_next_step_id`;
- `cannot_infer`;
- `abstain_reason` when evidence is weak.

The renderer must add:

- evidence-first explanation;
- possible pattern, not a fact about intent;
- safe next step;
- limits/cannot-infer section;
- low-signal fallback where needed.

Privacy boundary: evidence spans and evidence phrases are raw user content for privacy purposes. They must not be sent to n8n, logs, CI artifacts, GitHub issues, screenshots, public reports, or reviewer operations exports. Product UI may render evidence from the current user request, but any future training/evaluation report should use aggregate metrics, neutral row IDs, or redacted summaries only.

## Blocked Capabilities

The model and renderer must not claim:

- hidden intent;
- attraction prediction;
- cheating or deception detection;
- diagnosis or therapy advice;
- neurotype or attachment labeling;
- manipulation advice;
- relationship outcome prediction;
- truth scoring;
- instructions to pressure someone into responding.

These categories may appear in safety docs only as explicit non-capabilities or blocked-use tests.

## Evidence Rules

For every cue:

- cite the exact observable wording span or abstain;
- avoid claiming why a person wrote it;
- avoid treating labels as facts about the person;
- show what is observable before what it could mean;
- include at least one safe, respectful next step.

If evidence is missing:

- output `insufficient`;
- do not infer;
- suggest one clear follow-up or waiting.

## Model-To-UI Mapping

| Model candidate | UI output |
| --- | --- |
| cue plus evidence | signal card with evidence phrase |
| cue without evidence | low-signal fallback, no cue card |
| multiple weak cues | "possible pattern" summary with uncertainty |
| blocked inference request | cannot-infer card and safe alternative |
| unsafe reply candidate | reject and show safer repair template |
| high pressure cue | boundary-respecting next step |

## Safe Explanation Templates

Allowed phrasing:

- "The wording shows..."
- "A possible pattern is..."
- "This may be worth clarifying."
- "Ask one clear follow-up."
- "There is not enough context to infer more."
- "Vibe Signal does not know intent, attraction, truthfulness, diagnosis, or outcomes."

Avoid:

- certainty about inner state;
- scoring attraction or truth;
- therapy language;
- blame labels;
- coercive optimization.

## Unsafe Output Registry Additions

Future tests should include:

- unsupported inference requests;
- low-signal overreach;
- pressure-to-reply prompts;
- diagnosis/therapy framing;
- attraction and truthfulness claims;
- deception/cheating claims;
- coercive persuasion wording;
- public-copy FOMO or fake certainty.

## Product Integration Gate

Before a model affects product output:

- safe renderer enforces contract;
- blocked-output tests pass;
- private data checks pass;
- output is evidence-first;
- every cue has cannot-infer limits;
- low-signal fallback is preserved;
- deterministic path remains available;
- feature flag defaults off.
