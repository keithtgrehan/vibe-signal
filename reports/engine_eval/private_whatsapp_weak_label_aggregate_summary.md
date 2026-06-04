# Private WhatsApp Weak-Label Aggregate Summary

Aggregate-only summary for the local restricted private WhatsApp cue-labeling workflow. This report contains no raw chat text, no redacted windows, no participant names, and no private examples.

## Ingest

- Parsed private messages: `7278`
- Speaker role counts: `self=4155`, `other=3123`
- Multiline messages: `921`
- Full windows generated locally: `7278`
- Full windows with weak-label candidates: `4687`

## First Review Packet

- Restricted review packet: `data/restricted/private_whatsapp/processed/private_label_review_100.csv`
- Rows selected: `100`
- Window size: `3`
- Sampling seed: `42`
- Rows needing human review: `100`

## Candidate Label Counts In 100-Row Packet

- `ambiguity`: `3`
- `boundary`: `24`
- `direct_ask`: `78`
- `escalation_risk`: `23`
- `pressure_urgency`: `25`
- `reassurance`: `13`
- `repair_attempt`: `13`
- `unanswered_ask_candidate`: `21`
- `unclear_timing`: `19`

## Full Weak-Label Candidate Counts

- `ambiguity`: `214`
- `boundary`: `920`
- `direct_ask`: `3716`
- `escalation_risk`: `628`
- `pressure_urgency`: `851`
- `reassurance`: `102`
- `repair_attempt`: `70`
- `unanswered_ask_candidate`: `605`
- `unclear_timing`: `356`

## Likely Weak Spots Before Human Review

- `direct_ask` is frequent and may need human review for overly broad question/request matching.
- `unanswered_ask_candidate` needs review because weak rules cannot decide whether a reply is contextually adequate.
- `pressure_urgency` and `escalation_risk` need review for deadline-vs-pressure separation.
- `boundary` needs review because refusal wording can be benign context rather than a cue needing action.
- `ambiguity`, `reassurance`, and `repair_attempt` are lower-count in the 100-row packet and may need targeted follow-up sampling after the first review pass.

## Planned Review Scope

Keith reviews `100` restricted windows in `private_label_review_100.csv` tomorrow. The goal is observable cue review only. Human review should not label hidden intent, attraction, deception, diagnosis, neurotype, attachment style, manipulation, dating scores, or relationship outcomes.

## Non-Claims

This is not a validation result, accuracy claim, production-readiness claim, or model-quality claim.
