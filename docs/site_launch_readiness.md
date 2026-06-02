# Site Launch Readiness

## Implemented

- deterministic `/api/match` route exists
- mobile `/api/match` integration exists and uses environment-driven backend URL configuration
- matching request/result schemas exist
- synthetic corpus and validator exist
- model card, claims boundaries, and evaluation gates are documented
- draft privacy, terms, match disclaimer, deletion request, and export request documents exist
- static draft legal routes exist for privacy, terms, deletion, export, and match disclaimer

## Research-Only

- sklearn baseline runs on synthetic fixtures only
- synthetic baseline metrics are harness checks, not public quality claims
- commercial mode fails closed unless source rights explicitly allow commercial training

## Skipped Or Optional

- embedding experiment is optional and writes a `SKIPPED` report when local cached dependencies are unavailable
- no external datasets, provider calls, model downloads, vectors, checkpoints, or embeddings are required
- legal routes are static draft artifacts only and do not implement account, analytics, tracking, deletion, or export storage behavior

## Blocked

- No consented reviewed-label set exists.
- No commercial-safe external training rights are approved.
- No model-quality launch claim is allowed from synthetic-only metrics.
- Privacy and terms drafts require legal review before public launch.
- Deletion/export workflow requires reviewed support channel, identity checks, retention policy, and response timelines.

## Future Work

- No live backend deployment has been verified.
- Final privacy, terms, deletion, and export URLs are not deployed.
- Production monitoring is not implemented.
- GDPR, CCPA, App Store, and platform-policy review are not complete and are not claimed.

## Allowed Launch Copy

- Vibe Signal compares observable communication patterns and highlights fit/friction signals with evidence.
- Vibe Signal can surface specificity drops, answer-evasion patterns, and contradiction cues.
- Confidence reflects input quality and evidence strength.
- Vibe Signal matching is communication-support only, with pattern-based suggestions rather than truth claims.

## Blocked Launch Copy

- Vibe Signal detects lies.
- Vibe Signal knows if someone likes you.
- Vibe Signal predicts cheating.
- Vibe Signal diagnoses attachment style, ADHD, autism, or manipulation.
- Vibe Signal reveals hidden intent.
- Vibe Signal is production-compliant.
- Vibe Signal is GDPR-compliant.

## Launch Blockers

Any of the following blocks launch:

- unsafe user-facing output
- raw private chat committed
- raw external dataset committed
- provider response committed
- commercial-unsafe source used in commercial mode
- model-quality claim made below reviewed-label thresholds
