# Cue Taxonomy Accuracy Audit

Status: deterministic cue audit. This does not claim measured accuracy.

## Cue Rules

Every normal cue should define:

- cue_id
- label
- safe category
- rule triggers
- evidence span requirements
- positive synthetic examples
- negative synthetic examples
- false-positive risks
- unsafe interpretations to block
- signal-strength logic
- safe explanation template
- repair suggestion template
- minimum context needed
- fallback behavior

## Current Hardening

- Specificity cues now require concrete dates, times, deadlines, details, or quantities.
- Consent-clarity cues now require consent, check-in, permission, or opt-out context instead of generic yes/no wording.
- Specificity-drop detection suppresses direct acknowledgements and requires a prior direct ask.
- Contradiction matching avoids generic yes/no conflicts that misread phrases like "no pressure."
- Low-signal fallback catches short, sparse, or evidence-empty inputs.
- Evidence compacting carries cue ID, span offsets, safe explanation, signal strength, interpretation limits, and repair suggestion.

## Cue Precedence

| Situation | Expected behavior |
| --- | --- |
| User asks for attraction, deception, diagnosis, hidden motive, or manipulation | Return safe refusal/redirect to observable wording. |
| Input is too short | Return low-signal fallback. |
| No evidence spans exist | Return low-signal fallback. |
| Pressure and boundary cues both fire | Show boundary pressure without labeling the person. |
| Urgency appears without coercive wording | Show urgency, not pressure. |
| Reassurance cue fires | Do not infer insecurity, anxiety, relationship style, or romantic interest. |
| Commitment mismatch appears | Do not infer lying. |
| Conflict escalation appears | Do not infer abuse, intent, or personality. |

## Cue-by-Cue Notes

| Cue | Safe detection | Minimum context | False-positive risk | Fallback |
| --- | --- | --- | --- | --- |
| direct ask | question or directive with clear action item | one message can be enough if action is explicit | command vs request | low signal if no action item |
| indirect ask | softened request phrase plus action | one message plus evidence phrase | politeness misread as uncertainty | label indirect wording only |
| unclear ask | vague pronoun/timing/action | enough words to see missing action item | inside jokes or shared context | ask for clarification |
| unanswered ask | ask followed by non-answer/topic shift | at least two turns | delayed context missing | low/mixed signal |
| vague timing | later/soon/sometime without concrete anchor | one message | casual chat not needing schedule | suggest specific time |
| commitment mismatch | prior commitment and later conflict | at least two turns | changed plans, not deception | phrase as mismatch |
| specificity drop | concrete prior detail followed by vague response | at least two turns | acknowledgement replies | suppress direct answer false positives |
| reassurance seeking | "are we okay", "just checking" | one message | care check-in | do not infer relationship pathology |
| softening language | "maybe", "if you are up for it" | one message | politeness/culture | label softener only |
| urgency language | now/asap/today | one message | real deadline | separate from pressure |
| pressure language | repeated demand/obligation/coercive wording | one message | direct logistical ask | require pressure phrase |
| boundary pressure | pressure after no/boundary | two turns preferred | consent context missing | caution/fallback |
| conflict escalation | blame/accusation/intensity | one message | quoted text | avoid person labels |
| blame language | "you always/never" accusation | one message | legitimate accountability | show wording pattern |
| cognitive overload | multiple asks, long chains, mixed topics | one long message | complex but necessary details | suggest splitting |
| topic shift | reply changes topic after ask | at least two turns | normal conversation drift | low/mixed signal |
| repair opportunity | apology/clarification opening | one or more turns | performative apology assumptions | suggest repair wording |

## Remaining Work

Human-reviewed labels are needed before any precision/recall or accuracy claim. Future evaluation should measure regression pass rate, fixture coverage, unsafe-output block rate, and evidence completeness rate only.
