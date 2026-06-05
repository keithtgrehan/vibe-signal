# Agent 2 - Public Dataset Landscape

Date: 2026-06-05

Status: research_plan_requires_gpt_user_review. No datasets were downloaded for this research sprint.

## Scouting Rule

Every public dataset is metadata-only until a source-specific rights, privacy, provenance, and harm review approves a specific use. This document records candidate fit; it does not approve training.

Not Approval note: license compatibility, privacy permissibility, and product-training approval are separate gates. A permissive or observed license does not approve benchmark use, product training, provider upload, redistribution, or public claims.

## Dataset Landscape Matrix

| Dataset/source | URL | Data type | Useful cues | License/status found | Training status | Benchmark status | Vibe recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Vibe synthetic fixtures | local repo fixtures | synthetic dialogue snippets | all cue families, hard negatives, safe replies | repo-authored | yes after product review | yes | Immediate primary path. Expand first. |
| Private gold labels | local restricted path only | human-reviewed rows from local-only private source pending documented lawful-basis and purpose-specific rights review | cue QA, evaluator, weak-label calibration | private/local-only | not now | local aggregate only after review | Use 30 rows for QA and evaluator smoke only. |
| GoEmotions | https://github.com/google-research/google-research/tree/master/goemotions | Reddit comments with emotion labels | low-signal, affect-label pitfalls, calibration caveats | Google repo says datasets CC BY 4.0; dataset contains Reddit/comments and bias warnings | not_approved_metadata_only | not_approved_metadata_only | Do not train product cues from emotion labels. |
| Civil Comments | https://www.tensorflow.org/datasets/catalog/civil_comments | public comments with toxicity labels | unsafe wording, harassment boundary tests | TFDS says CC0 | not_approved_metadata_only | not_approved_metadata_only | Candidate for future safety benchmark/red-team design, not cue training. |
| Wikipedia Detox | https://meta.wikimedia.org/wiki/Research:Detox/Data_Release | Wikipedia talk comments and annotations | toxic/attack/aggression safety eval | CC0 public domain dedication | not_approved_metadata_only | not_approved_metadata_only | Candidate for future unsafe-output tests. |
| Stanford Politeness Corpus/API | https://github.com/sudhof/politeness | requests with politeness strategies | directness, softened asks, request detection | code Apache-2.0; corpus rights need review | not_approved_metadata_only | not_approved_metadata_only | Use strategy taxonomy; do not ingest rows yet. |
| Switchboard Dialog Act Corpus | https://convokit.cornell.edu/documentation/switchboard.html | speech transcripts with dialogue acts | question, answer, agreement, backchannel | CC BY-NC-SA 3.0 | not_approved_metadata_only | not_approved_metadata_only | Dialogue-act mapping reference. |
| DailyDialog | https://parl.ai/docs/tasks.html | multi-turn daily dialogue, act/topic/emotion labels | dialogue acts, topic shifts, low-signal turns | non-commercial/research in common distributions | not_approved_metadata_only | not_approved_metadata_only | Useful for literature and evaluator design only. |
| EmpatheticDialogues | https://parl.ai/docs/tasks.html | emotional-situation conversations | supportive language, repair tone | CC BY-NC | not_approved_metadata_only | not_approved_metadata_only | Reference supportive phrasing cautiously. |
| TweetEval | https://github.com/cardiffnlp/tweeteval | tweet classification tasks | sentiment/stance/toxicity benchmark shape | repo warns task/Twitter restrictions may apply | not_approved_metadata_only | not_approved_metadata_only | Do not train; source-specific review required. |
| Taskmaster | https://github.com/google-research-datasets/Taskmaster | task-oriented spoken/written dialogs | clarification, repair, error handling, constraints | Google dataset repo; license observed separately from Vibe use approval | not_approved_metadata_only | not_approved_metadata_only | Requires registry/legal/privacy/harm review. |
| MultiWOZ | https://parl.ai/docs/tasks.html | task-oriented wizard-of-oz dialogues | constraints, booking repair, user goal shifts | license varies by version/mirror | not_approved_metadata_only | not_approved_metadata_only | Low product fit; review before use. |
| ConvAI2/PersonaChat | https://parl.ai/projects/convai2/ | persona-grounded open dialogue | persona/adaptation risks | ParlAI availability; license needs source review | not_approved_metadata_only | not_approved_metadata_only | Avoid persona inference patterns. |
| Blended Skill Talk | https://parl.ai/docs/tasks.html | open-domain dialogue blending skills | empathy/knowledge/persona blending | license unclear across mirrors | not_approved_metadata_only | not_approved_metadata_only | Not needed early; high copy-style drift risk. |
| ProsocialDialog | https://github.com/skywalker023/prosocial-dialog | safety-oriented dialogues | unsafe prompt response patterns | official repo; license observed separately from Vibe use approval | not_approved_metadata_only | not_approved_metadata_only | Consider later for blocked-output tests, not product cue model. |
| ReDial | https://redialdata.github.io/website/ | movie recommendation dialogue | ask/answer, recommendation flow | CC BY 4.0 | not_approved_metadata_only | not_approved_metadata_only | Weak fit; benchmark/reference only after review. |
| Commonsense-Dialogues | https://github.com/alexa/Commonsense-Dialogues | social-context dialogues | everyday context and response coherence | CC BY-NC 4.0 | not_approved_metadata_only | not_approved_metadata_only | Reference only. |
| Negotiation datasets | papers/repos vary | bargaining conversations | pressure, concession, boundary language | often unclear | not_approved_metadata_only | not_approved_metadata_only | Block product training unless safe-output purpose is tightly scoped. |
| Persuasion datasets | papers/repos vary | persuasion conversations | persuasion tactics, refusal pressure | often sensitive | not_approved_metadata_only | not_approved_metadata_only | High risk of coercive optimization. |
| Customer support/chat datasets | varies | support dialogs | clarification, repair, issue resolution | often platform-specific/unclear | not_approved_metadata_only | not_approved_metadata_only | Potentially useful only if permissive and non-sensitive after review. |
| Mental-health/support forums | varies | sensitive support conversations | support phrasing | sensitive/unclear | not_approved_metadata_only | not_approved_metadata_only | Product is not therapy; avoid. |
| Reddit/forum dumps | varies | scraped public posts/comments | broad language | platform/TOS/privacy issues | not_approved_metadata_only | not_approved_metadata_only | Do not use raw dumps. |

## Cue Fit Notes

Best fit for Vibe Signal:

- dialogue acts: questions, answers, refusals, acknowledgements, repair;
- request/directness/politeness strategies;
- toxicity/boundary pressure red-team cases;
- synthetic counterfactuals for clarity/ambiguity/pressure/reassurance.

Weak or risky fit:

- emotion labels, because Vibe Signal must not infer internal states;
- personality/persona data, because it can drift toward identity inference;
- mental-health and support forums, because the product is not therapy;
- persuasion/negotiation data, because it can optimize coercive behavior;
- scraped private-feeling conversations without clear consent.

## Practical Recommendation

For the next implementation sprint, do not download any public dataset. Add a fail-closed metadata registry extension first, then review one source at a time. The first useful external candidates are not for product cue training; they are for safety benchmarks and taxonomy calibration:

1. Civil Comments or Wikipedia Detox for unsafe-output tests.
2. Stanford politeness concepts for request/directness features, without importing corpus rows.
3. GoEmotions only as a warning case and taxonomy reference, not as emotion-truth training.
