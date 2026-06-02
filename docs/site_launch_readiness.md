# Site Launch Readiness

## Implemented

- deterministic `/api/match` route exists
- mobile `/api/match` integration exists and uses environment-driven backend URL configuration
- matching request/result schemas exist
- synthetic corpus and validator exist
- model card, claims boundaries, and evaluation gates are documented
- draft privacy, terms, match disclaimer, deletion request, and export request documents exist
- static draft legal routes exist for privacy, terms, deletion, export, and match disclaimer
- backend `/healthz` and `/readyz` deployment-readiness checks exist
- backend metadata-only request logging exists with request IDs and no raw body logging
- deployment smoke-test script exists for `/healthz`, `/readyz`, legal draft routes, and synthetic `/api/match`
- closed-beta readiness checklist, tester instructions, and device QA script exist
- final closed-beta launch gate report exists and currently requires manual deployed-backend and real-device QA before tester invites

## Research-Only

- sklearn baseline runs on synthetic fixtures only
- synthetic baseline metrics are harness checks, not public quality claims
- commercial mode fails closed unless source rights explicitly allow commercial training

## Skipped Or Optional

- embedding experiment is optional and writes a `SKIPPED` report when local cached dependencies are unavailable
- no external datasets, provider calls, model downloads, vectors, checkpoints, or embeddings are required
- legal routes are static draft artifacts only and do not implement account, analytics, tracking, deletion, or export storage behavior
- backend deployment readiness docs/config exist, but they do not prove live hosting or production compliance
- deployment smoke tests prove connectivity and response shape only; they do not prove live hosting until run against the final host
- bounded metadata monitoring scaffold exists, but production monitoring provider, alerting, and incident ownership are not complete
- closed-beta checklists are operator runbooks only; they do not prove production readiness, legal compliance, GDPR/CCPA compliance, model quality, or commercial data-rights readiness

## Blocked

- No consented reviewed-label set exists.
- No commercial-safe external training rights are approved.
- No model-quality launch claim is allowed from synthetic-only metrics.
- Privacy and terms drafts require legal review before public launch.
- Deletion/export workflow requires reviewed support channel, identity checks, retention policy, and response timelines.
- Live backend deployment must be verified with the final host and environment values.
- Closed-beta device QA must be completed against the final beta build and backend host before tester invites.
- [final_closed_beta_launch_gate_report.md](final_closed_beta_launch_gate_report.md) must be moved from `READY_FOR_MANUAL_DEPLOY_QA` to `READY_FOR_TESTER_INVITES` using metadata-only evidence before tester invites.
- Any raw user message, provider response, secret, vector, checkpoint, or request body in logs blocks launch.

## Future Work

- No live backend deployment has been verified.
- Final privacy, terms, deletion, and export URLs are not deployed.
- Production monitoring provider, alerting, incident owner assignment, and incident-response process are not complete.
- Closed-beta release tracker entry for backend host, git SHA, mobile build, smoke result, log review, and device QA result is not yet recorded.
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
- raw request body or raw message logged
- commercial-unsafe source used in commercial mode
- model-quality claim made below reviewed-label thresholds
