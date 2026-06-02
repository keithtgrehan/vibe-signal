# Match Usage Consent Disclaimer

Status: draft for closed-beta readiness only. This document is not legal advice, does not claim production compliance, and requires legal review before public launch.

Use this copy near `/api/match` submission surfaces and mobile match input surfaces.

## User-Facing Copy

Vibe Signal matching is communication-support only. Outputs are pattern-based suggestions, not truth claims.

Only submit messages you have permission to analyze.

Do not include sensitive personal data, secrets, medical data, legal documents, financial data, or third-party private messages without permission.

Closed beta is not production launch. Privacy and terms drafts require legal review before public launch.

## Product Boundary

The match score reflects observable communication-pattern compatibility only. It should not be presented as a claim about feelings, motives, identity, health, relationship outcomes, or what a user should do to pressure another person.

## Implementation Notes

- Mobile composer copy is defined in `mobile/src/screens/matchScreenModel.js`.
- The backend static route is `GET /legal/match-disclaimer`.
- The deterministic matcher remains the source of match evidence.
- This draft adds no analytics, tracking, account storage, raw message persistence, training, embeddings, datasets, model files, vectors, checkpoints, or cached artifacts.
