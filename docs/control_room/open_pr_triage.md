# Open PR Triage

Status date: 2026-06-08.

Purpose: classify currently open PRs and recommend safe action. This document is a control-room snapshot, not a merge instruction. Do not merge stale branches wholesale.

Inspection command:

```bash
gh pr list --state open --json number,title,headRefName,baseRefName,isDraft,mergeable,updatedAt,url
```

Additional filename-only inspections were run for PR #46 and PR #66. No raw/private data, generated artifacts, or implementation diff content was copied.

## Summary

PR #67 is merged and is the current recruiter/CEO-demo baseline. PR #56 is merged and requires no action.

PR #46 and PR #66 were closed as superseded in this control-room run after useful direction was documented. All other PRs should be left alone unless Keith gives a new instruction.

## Current Open PRs At Inspection

| PR | Title | Branch | Draft/open | Mergeability observed | Changed area | Value | Risk | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #66 | Codex/UI ux product design research upgrade | `codex/ui-ux-product-design-research-upgrade` | Open | `CONFLICTING` from `gh pr view`; `UNKNOWN` from list snapshot | UI/UX docs, web/mobile UI files, tests | Contains trust-first UI and reviewer-flow research ideas | Broad diff, conflicts, incomplete template body, overlaps with PR #67 | Close as superseded. Recover any remaining useful UI/UX ideas later through a small clean branch from current `main`. |
| #46 | Add safe WhatsApp dynamics research prototype | `codex/whatsapp-dynamics-research-prototype` | Draft | `CONFLICTING` | Private WhatsApp/local-only research tooling, synthetic private-inspired fixture concept, weak-label scaffolding, web variants | Useful research direction for aggregate-only local evaluator and synthetic hard-negative planning | 30 files, research-heavy, conflicts, private-data/model-training adjacency, no direct merge path | Close as superseded. Recover useful ideas through a future research-audit branch only. |
| #45 | Allow exact Replit A/B origin for CORS | `codex/allow-replit-ab-cors` | Open | `CONFLICTING` | Deployment/CORS docs and tests for Replit A/B origin | Narrow CORS idea if Replit preview remains needed | Not part of current custom-domain CORS fix; may conflict with current production origin posture | Leave alone. Revisit only after custom-domain CORS is fixed; close/supersede later if Replit A/B is no longer needed. |
| #44 | Improve private WhatsApp cue-labeling and weak-label engine workflow | `codex/private-whatsapp-engine-improvement-nightly` | Open | `CONFLICTING` | Private WhatsApp cue-label workflow, local weak-label baseline, reports/tools/tests | Potential local-only evaluator and deterministic cue-rule research | Private-data/model-risk adjacency; broad conflicted branch | Research-only. Do not merge without a separate audit, no raw private data, and no training/runtime changes. |
| #42 | Replit A/B frontend experiment | `replit/ab-minimal-frontend-redesign` | Draft | `CONFLICTING` | Replit A/B web experiment and variants | Historical A/B UI direction | Draft, conflicts, superseded by current Scanner/CEO-demo flow unless explicitly revived | Leave draft or close later if no longer useful. Do not merge over current web UI. |
| #41 | Document UI A/B variant governance | `docs/ab-test-variant-governance` | Open | `MERGEABLE` | A/B governance docs | May contain docs-only experiment governance language | Could imply active A/B workflow if merged without cleanup | Likely superseded by control-room docs. Leave alone in this run; close later if safe. |
| #40 | Document minimal UI merge and Replit A/B plan | `docs/minimal-ui-merge-proof` | Open | `MERGEABLE` | Minimal UI/Replit A/B docs | Historical context | Likely stale after PR #67 and current control-room index | Likely superseded by control-room docs. Leave alone in this run; close later if safe. |

## Required Closure Decisions For This Run

### PR #46

Recommendation: close as superseded; recover useful ideas through a future research-audit branch.

Rationale:

- Draft and conflicted.
- Research-heavy with 30 changed files.
- Adjacent to private WhatsApp workflows, weak-label scaffolding, synthetic exports, and local model experimentation.
- Not appropriate for direct merge into current `main`.
- Useful direction is captured in `docs/control_room/research_recovery_log.md` and `docs/control_room/research_to_execution_roadmap.md`.

### PR #66

Recommendation: close as superseded by PR #67 and this control-room consolidation.

Rationale:

- Conflicted.
- PR body was incomplete/vague.
- Broad UI/UX and mobile/web diff.
- PR #67 already shipped the clean recruiter/CEO-demo subset.
- Any remaining research should be reintroduced later from a current `main` branch with a complete PR body.

## Do Not Touch In This Run

- Do not close PR #45, #44, #42, #41, or #40 without a new instruction.
- Do not delete local or remote branches.
- Do not inspect or apply stashes.
- Do not resolve conflicts on stale PR branches.
- Do not merge private-data, Replit, model-training, or broad UI research branches wholesale.
