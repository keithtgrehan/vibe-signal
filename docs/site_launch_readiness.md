# Site Launch Readiness

## Implemented

- deterministic `/api/match` route exists
- matching request/result schemas exist
- synthetic corpus and validator exist
- model card, claims boundaries, and evaluation gates are documented

## Research-Only

- sklearn baseline runs on synthetic fixtures only
- synthetic baseline metrics are harness checks, not public quality claims
- commercial mode fails closed unless source rights explicitly allow commercial training

## Skipped Or Optional

- embedding experiment is optional and writes a `SKIPPED` report when local cached dependencies are unavailable
- no external datasets, provider calls, model downloads, vectors, checkpoints, or embeddings are required

## Blocked

- No consented reviewed-label set exists.
- No commercial-safe external training rights are approved.
- No model-quality launch claim is allowed from synthetic-only metrics.

## Future Work

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
