# NLP Engine Deep Research

Status: research summary for deterministic, evidence-first cue hardening. This is not model validation, production-readiness evidence, legal advice, or approval to train on external datasets.

## Research-Backed Design Direction

Vibe Signal should focus on observable speech acts and discourse patterns: direct asks, indirect asks, commitments, refusals, confirmations, apologies, repair attempts, topic shifts, unresolved adjacency pairs, urgency, pressure, and overloaded wording.

The safest engine pattern is:

1. detect a small number of transparent cues;
2. require evidence spans;
3. show evidence before interpretation;
4. show signal strength as a bounded label, not a percentage;
5. state what cannot be inferred;
6. suggest repair, clarification, boundary, or lower-pressure next steps;
7. fallback when context is weak or the user asks for a blocked inference.

## Top 20 Engine Changes

1. Reject unknown public match-request fields.
2. Remove public debug summary override.
3. Require low-signal fallback for very short/context-light text.
4. Require evidence spans for normal cue rendering.
5. Separate urgency from pressure.
6. Separate ambiguity from avoidance.
7. Separate reassurance wording from anxiety or relationship-style labels.
8. Separate commitment mismatch from deception claims.
9. Separate conflict escalation from diagnosis or abuse labels.
10. Tighten consent-clarity triggers to consent/check-in wording.
11. Tighten specificity triggers to concrete time/date/detail changes.
12. Suppress specificity-drop false positives after direct acknowledgements.
13. Add user-facing `cannot_infer` blocks.
14. Add safe next-step repair suggestions.
15. Demote numeric score to API/detail context in UI.
16. Add signal-strength enum: strong, medium, low, mixed, insufficient.
17. Run blocked-claim sanitizer after summary/explanation construction.
18. Scan UI copy for coercive or unsupported claims.
19. Keep dataset registry metadata-only for external sources.
20. Treat synthetic fixture results as regression coverage only.

## Top 20 False-Positive Risks

1. One-word acknowledgement interpreted as specificity drop.
2. Polite softener interpreted as uncertainty.
3. Urgent scheduling interpreted as pressure.
4. A refusal interpreted as hostility.
5. Topic change interpreted as avoidance.
6. A mixed-topic message interpreted as manipulation.
7. Reassurance-seeking interpreted as relationship pathology.
8. Commitment mismatch interpreted as lying.
9. Direct ask interpreted as coercion.
10. Boundary statement interpreted as rejection motive.
11. Short message interpreted as low interest.
12. All-caps acronym interpreted as escalation.
13. Punctuation intensity interpreted as anger.
14. A joke or quote interpreted literally.
15. Medical/legal/financial text interpreted without domain caution.
16. Third-party references interpreted as private facts.
17. Multiple asks interpreted as pressure when they are logistics.
18. Apology interpreted as guilt.
19. Delayed reply mention interpreted as avoidance.
20. Synthetic fixture performance interpreted as accuracy.

## Top 20 Unsafe Wording Patterns To Block

1. private-feeling certainty
2. hidden-motive certainty
3. attraction prediction
4. deception verdicts
5. relationship outcome prediction
6. diagnosis
7. neurotype inference
8. personality labeling
9. relationship-style labeling
10. manipulation advice
11. coercive persuasion
12. reply-pressure loops
13. shame copy
14. scarcity/FOMO copy
15. streak pressure
16. addictive/compulsive framing
17. overconfident accuracy claims
18. legal/compliance claims
19. therapy/medical advice framing
20. raw-user-data retention claims that are not implemented

## Top 20 Synthetic Fixtures To Add First

1. clear direct ask
2. vague ask
3. indirect ask
4. unanswered question
5. soft yes / unclear yes
6. vague timing
7. commitment mismatch
8. specificity drop
9. urgency without pressure
10. pressure with urgency
11. boundary-respecting request
12. boundary pressure after no
13. reassurance-seeking language
14. warm reassurance
15. emotional support without therapy framing
16. conflict escalation
17. de-escalation / repair
18. overloaded multi-ask message
19. topic shift
20. low-signal short text

## Top 10 Cue Definitions To Simplify Or Merge

1. specificity vs specificity drop
2. uncertainty vs ambiguity
3. urgency vs pressure
4. boundary pressure vs general pressure
5. conflict escalation vs blame language
6. reassurance vs reassurance-seeking
7. directness vs direct ask
8. unclear ask vs indirect ask
9. unanswered ask vs topic shift
10. commitment mismatch vs contradiction

## After Implementation

The sprint hardened low-signal fallback, unknown-field rejection, safer signal labels, evidence detail propagation, cannot-infer blocks, repair suggestions, UI consent gates, and blocked-copy tests. It remains unvalidated against human-reviewed labels and is appropriate only for cautious closed-beta feedback after real-device/legal gates pass.
