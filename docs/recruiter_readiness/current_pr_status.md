# Current PR Status

Status date: 2026-06-08.

This document is a lightweight PR-hygiene snapshot for reviewer context. It is not legal, privacy, production-readiness, or model-quality approval.

## Baselines

- PR #67 is merged and is the current CEO-demo / recruiter-demo baseline.
- PR #68 is merged and is the current research/control-room baseline.
- PR #56 is merged and requires no action.

## Final Polish Closure Set

The remaining stale PRs were classified as superseded and closed in the final recruiter-readiness polish pass:

| PR | Title | Branch | Observed state before closure | Rationale |
| --- | --- | --- | --- | --- |
| #45 | Allow exact Replit A/B origin for CORS | `codex/allow-replit-ab-cors` | Conflicting | Replit-specific CORS is not part of the active recruiter/demo path; custom-domain CORS remains a separate manual task. |
| #44 | Improve private WhatsApp cue-labeling and weak-label engine workflow | `codex/private-whatsapp-engine-improvement-nightly` | Conflicting | Research-heavy and local-only; future recovery should use a dedicated research-audit branch. |
| #42 | Replit A/B frontend experiment | `replit/ab-minimal-frontend-redesign` | Draft, conflicting | Draft experiment superseded by current main and control-room docs. |
| #41 | Document UI A/B variant governance | `docs/ab-test-variant-governance` | Mergeable docs-only | Variant governance/history is now easier to find through control-room docs. |
| #40 | Document minimal UI merge and Replit A/B plan | `docs/minimal-ui-merge-proof` | Mergeable docs-only | Minimal UI / Replit A/B planning context is preserved at a higher level in control-room docs. |

## Current Branch Position

The final recruiter-readiness branch should stay docs-only. It should not merge, cherry-pick, or depend on unrelated stale branches.

After this cleanup PR is opened, the expected open PR count is one: the final recruiter-readiness polish PR.
