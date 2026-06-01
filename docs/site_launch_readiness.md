# Site Launch Readiness

## Current Status

Vibe Matching Engine v0 is ready as a local deterministic foundation:

- deterministic `/api/match` route exists
- matching request/result schemas exist
- synthetic corpus and validator exist
- research-only sklearn baseline runs on synthetic fixtures
- optional embedding experiment fails safely when no cached model is available
- model card, claims boundaries, and evaluation gates are documented

## Not Launch-Ready Yet

- No consented reviewed-label set exists.
- No commercial-safe external training rights are approved.
- No live backend deployment has been verified.
- Frontend/mobile `/api/match` integration is not wired.
- Privacy, terms, deletion, and export URLs are drafts.
- Production monitoring is not implemented.

## Allowed Launch Copy

- Vibe Signal compares observable communication patterns and highlights fit/friction signals with evidence.
- Vibe Signal can surface specificity drops, answer-evasion patterns, and contradiction cues.
- Confidence reflects input quality and evidence strength.

## Blocked Launch Copy

- Vibe Signal detects lies.
- Vibe Signal knows if someone likes you.
- Vibe Signal predicts cheating.
- Vibe Signal diagnoses attachment style, ADHD, autism, or manipulation.
- Vibe Signal reveals hidden intent.

## Launch Blockers

Any of the following blocks launch:

- unsafe user-facing output
- raw private chat committed
- raw external dataset committed
- provider response committed
- commercial-unsafe source used in commercial mode
- model-quality claim made below reviewed-label thresholds
