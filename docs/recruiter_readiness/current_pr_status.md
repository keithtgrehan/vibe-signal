# Current PR Status

Status date: 2026-06-03.

This document summarizes recent Vibe Signal PRs for merge-order and reviewer context. It is not legal, privacy, production-readiness, or model-quality approval.

| PR | Title | Branch | Status | Adds | Merge/order recommendation | Safe to mention in README now? | Superseded? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| #25 | Verify post-merge engine precision baseline | `codex/postmerge-engine-verification-main` | Merged | Verified main after the 455-conversation precision cleanup; local regression `455/455`; deployed bounded sample passed after warm retry; deployed version was initially unverified. | Already merged before #26. | Yes, as historical post-merge verification. | No |
| #26 | Add safe status deploy metadata | `codex/status-commit-deploy-metadata` | Merged | Adds safe allowlisted `/api/status` metadata fields: `git_commit`, `deploy_version`, `build_timestamp`, `service_revision`. | Already merged after #25. Render must configure metadata env vars for deployed commit proof. | Yes. | No |
| #27 | Expand engine evaluation with 10k synthetic splits and hard negatives | `codex/engine-10k-hard-negative-eval` | Merged | Adds 10k synthetic messages, dev/hard-negative/heldout/red-team splits, bootstrap metrics, confusion groups, and human-review packet scaffolding. | Already merged before #29. #29 hardens its evidence/precision gaps. | Yes, with bootstrap-only caveat. | Partially superseded by #29 reports, but not by functionality |
| #28 | Strengthen trust-first UI and demo experience | `codex/ui-ux-product-design-research-upgrade` | Merged | Improves trust-first landing/demo flow, synthetic examples, result hierarchy, metadata-only feedback, and safe UI copy. | Already merged into `main`; #29 remains mergeable but was branched before #28. | Yes. | No |
| #29 | Harden 10k engine evidence coverage and hard-negative precision | `codex/engine-10k-evidence-precision-hardening` | Open, ready | Restores evidence completeness to `5000/5000`, reduces hard-negative unexpected cues from `334` to `0`, keeps unsafe-output block `5000/5000`, and keeps red-team safety `500/500`. | Should merge after current `main`; GitHub reports it mergeable. This README/status PR is stacked on #29 and should merge after #29. | Yes, only as an active PR / stacked branch until merged. | No |

## Merge/Stacking Recommendation

1. Keep #25, #26, #27, and #28 as merged historical context.
2. Merge #29 next if review and CI stay clean.
3. Merge this README/status PR after #29, because it references #29's generated reports and metrics.
4. Do not close #27; it is merged and provides the base 10k evaluation system. Treat #29 as a hardening follow-up, not a replacement PR.

## Correctness Notes

- #29 does not add ML training, external datasets, raw/private chats, provider complexity, analytics SDKs, paywalls, or UI changes.
- #29 metrics are bootstrap-only synthetic regression metrics, not human-reviewed accuracy claims.
- #29 still leaves human-reviewed labels pending.
- Any deployed-backend version statement depends on `/api/status` metadata environment variables being configured on Render.

