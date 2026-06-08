# Current PR Status

Status date: 2026-06-08.

This document is a lightweight open-PR hygiene snapshot for reviewer context. It is not legal, privacy, production-readiness, or model-quality approval.

## Open PR Snapshot

| PR | Title | Branch | Mergeability observed | Demo-readiness relevance | Recommended action |
| --- | --- | --- | --- | --- | --- |
| #66 | Codex/UI ux product design research upgrade | `codex/ui-ux-product-design-research-upgrade` | Conflicting / dirty | High, but broad and not clean | Do not depend on it for this reviewer flow. Rebase and complete separately. |
| #46 | Add safe WhatsApp dynamics research prototype | `codex/whatsapp-dynamics-research-prototype` | Draft, conflicting / dirty | Low for CEO demo | Leave draft; handle as separate research work. |
| #45 | Allow exact Replit A/B origin for CORS | `codex/allow-replit-ab-cors` | Conflicting / dirty | Relevant only if using Replit A/B demo | Ignore unless Replit is the demo target. |
| #44 | Improve private WhatsApp cue-labeling and weak-label engine workflow | `codex/private-whatsapp-engine-improvement-nightly` | Conflicting / dirty | Low for CEO demo | Ignore for demo readiness; handle separately. |
| #42 | Replit A/B frontend experiment | `replit/ab-minimal-frontend-redesign` | Draft, conflicting / dirty | Medium, but draft | Leave draft unless deliberately choosing A/B path. |
| #41 | Document UI A/B variant governance | `docs/ab-test-variant-governance` | Mergeable / clean | Medium docs support | Optional docs-only follow-up. |
| #40 | Document minimal UI merge and Replit A/B plan | `docs/minimal-ui-merge-proof` | Mergeable / clean | Medium docs support | Optional docs-only follow-up. |

## Current Branch Position

The CEO-demo readiness branch should stay self-contained. It should not merge, cherry-pick, or depend on unrelated open PRs.

Open PR hygiene checked. This PR is self-contained and does not depend on unrelated open PRs.
