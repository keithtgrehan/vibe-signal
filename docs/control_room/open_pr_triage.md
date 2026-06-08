# Open PR Triage

Status date: 2026-06-08.

Purpose: classify stale PRs and record why they were closed or left alone. This document is a control-room snapshot, not a merge instruction. Do not merge stale branches wholesale.

## Baselines

- PR #67 is merged and is the current recruiter/CEO-demo baseline.
- PR #68 is merged and is the current research/control-room baseline.
- PR #56 is merged and requires no action.

## Final Stale PR Closure Set

These PRs were still open before the final recruiter-readiness polish pass and were approved for closure in that prompt.

| PR | Title | Branch | State before closure | Mergeability observed | Changed area | Value | Risk | Final action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #45 | Allow exact Replit A/B origin for CORS | `codex/allow-replit-ab-cors` | Open | `CONFLICTING` | Replit-specific CORS docs/tests | Narrow historical CORS note | Not the active custom-domain CORS path | Closed as superseded; handle custom-domain CORS separately. |
| #44 | Improve private WhatsApp cue-labeling and weak-label engine workflow | `codex/private-whatsapp-engine-improvement-nightly` | Open | `CONFLICTING` | Private WhatsApp/local-only research workflow | Useful aggregate-only research direction | Private-data/model-risk adjacency; broad conflicted branch | Closed as superseded; future recovery through research-audit branch only. |
| #42 | Replit A/B frontend experiment | `replit/ab-minimal-frontend-redesign` | Draft | `CONFLICTING` | Replit A/B web experiment and variants | Historical A/B UI direction | Draft, conflicts, superseded by current main | Closed as superseded. |
| #41 | Document UI A/B variant governance | `docs/ab-test-variant-governance` | Open | `MERGEABLE` | A/B governance docs | Some historical governance language | Superseded by control-room docs | Closed as superseded. |
| #40 | Document minimal UI merge and Replit A/B plan | `docs/minimal-ui-merge-proof` | Open | `MERGEABLE` | Minimal UI/Replit A/B docs | Historical context | Superseded by recruiter/control-room baseline | Closed as superseded. |

## Previously Closed Superseded PRs

| PR | Title | Final action |
| --- | --- | --- |
| #66 | Codex/UI ux product design research upgrade | Closed as superseded by PR #67 and control-room consolidation. |
| #46 | Add safe WhatsApp dynamics research prototype | Closed as superseded; recover useful ideas only through future research-audit branch. |

## Expected Open PR State

After the final recruiter-readiness polish PR is opened, the expected open PR list should contain only that new PR.

## Guardrails

- Do not delete local or remote branches.
- Do not inspect, apply, pop, or merge stashes.
- Do not resolve conflicts on stale PR branches.
- Do not merge private-data, Replit, model-training, or broad UI research branches wholesale.
- Do not fix custom-domain CORS in this docs-only cleanup pass.
