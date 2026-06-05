# Agent 6 - Synthetic Data And Augmentation Plan

Date: 2026-06-05

Status: research_plan_requires_gpt_user_review. Synthetic examples only.

## Role Of Synthetic Data

Synthetic data is the immediate safe expansion path because it can be committed, tested, reviewed, and used in CI without exposing private content. It should be treated as regression coverage and cue coverage, not proof of model accuracy.

## Generation Rules

Allowed:

- hand-authored short excerpts;
- LLM-generated excerpts from cue specs only, with no private examples in prompts;
- counterfactual pairs that change one cue at a time;
- hard negatives that resemble unsafe or ambiguous cases but should abstain;
- synthetic evidence spans.

Blocked:

- paraphrasing private rows;
- using private row wording as seed text;
- including private source IDs, private file names, or private metadata;
- generating therapy/diagnosis or attraction-prediction tasks;
- generating coercive reply optimization.

## Cue Coverage Plan

Target synthetic counts before model work:

- clarity: 100 examples;
- ambiguity: 100 examples;
- pressure: 100 examples;
- reassurance: 80 examples;
- directness: 80 examples;
- cognitive load: 80 examples;
- boundary pressure: 80 examples;
- repair opportunity: 100 examples;
- low signal: 150 examples;
- hard negatives: 200 examples;
- unsafe prompt/output red-team: 150 examples.

These should be balanced across short, medium, and multi-turn excerpts.

## Counterfactual Pairs

Create pairs where only one property changes:

- clear timing vs vague timing;
- direct ask vs indirect ask;
- urgent logistics vs pressure after boundary;
- reassurance vs reassurance request;
- repair attempt vs blame escalation;
- one ask vs multiple stacked asks;
- enough context vs low-signal fragment.

Each pair should define:

- expected cue label;
- expected evidence span;
- expected safe next step;
- cannot-infer limits;
- blocked interpretations.

## Hard Negatives

Hard negatives should include:

- short acknowledgements that should not be over-read;
- polite softeners that are not ambiguity by themselves;
- urgency that is logistics, not pressure;
- a refusal that should not be treated as hostility;
- a topic shift that may be normal context management;
- supportive language that should not be therapy output;
- mention of feelings without diagnosing a person.

## Red-Team Scenarios

Create synthetic tests for:

- requests to infer intent, attraction, truthfulness, diagnosis, or outcomes;
- requests for coercive replies;
- requests to pressure someone into responding;
- attempts to turn uncertainty into certainty;
- unsafe certainty from weak evidence;
- privacy-sensitive input warnings.

Expected behavior:

- refuse the unsupported inference;
- show observable wording only when available;
- offer a safe clarification or boundary-respecting next step;
- use low-signal fallback when evidence is weak.

## Human Review Of Synthetic Sets

Synthetic fixtures still need review:

- ensure they are not copied from private rows;
- check labels are unambiguous;
- check hard negatives are truly negative;
- check safe next step is respectful and non-coercive;
- check no public copy overclaims.

Synthetic rows can be committed only after this review.

