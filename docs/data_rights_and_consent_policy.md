# Data Rights and Consent Policy

Vibe Signal is local-first by default. Use only user-owned data, consented data, manual local examples, metadata-only references, or synthetic fixtures.

## Allowed Inputs

- User-owned or explicitly consented chats and exports.
- Pasted chats supplied by the operator for local review.
- Manual local files that the operator has rights to process.
- Synthetic fixtures created for tests and demos.
- Metadata-only research or benchmark references.

## Red Lines

- No covert surveillance.
- No scraping private chats.
- No paywall bypassing or login-gated collection.
- No raw personal data commits.
- No raw chats, audio, video, transcripts, provider outputs, or exports in git unless they are synthetic fixtures under approved fixture paths.
- No external provider calls by default.
- No dataset downloads in the hardening scaffold.

## Storage And Commit Rules

Raw user data stays local. Committed artifacts should be docs, schemas, configs, metadata, synthetic fixtures, or validated review outputs that do not expose private raw bodies.

The expected product behavior is that users can export and delete their local data. Implementations should keep raw input paths separate from derived, reviewable metadata so deletion/export can be honored cleanly.

External datasets are benchmark-only by default. Their labels are not product truth and must not become Vibe gold labels automatically.

## Claims Boundary

Vibe Signal describes observable communication patterns. It does not infer true emotion, make deception or cheating detection claims, predict attraction, infer attachment style, diagnose mental health, infer protected traits, perform biometric identity analysis, score manipulation, advise emotional manipulation, train models, or download datasets.

## Matching v0 Data Posture

The only training-ready source for matching v0 is the synthetic fixture corpus under `data/vibe_matching/synthetic/`.

External datasets are metadata-only, manual-review, or blocked until rights, consent, privacy, provenance, and harm review are complete. Commercial training mode must fail closed unless every selected source explicitly allows commercial training.
