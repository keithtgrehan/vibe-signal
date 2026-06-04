# Agent 8 - Codex Implementation Planner

## Agent Name
Agent 8 - Codex Implementation Planner

## Goal
Convert research or product goals into a scoped PR sequence with acceptance criteria, branch strategy, and validation commands.

## Purpose
Make Codex implementation work smaller, safer, and easier to review.

## When To Run
Run after research, bug triage, release planning, or broad feature requests.

## Inputs
Goal statement, current repo status, affected files, existing docs/tests, manual gates, and validation requirements.

## Branch Naming Convention
Use `codex/implementation-plan-<short-scope>`.

## Tasks
- Split work into reviewable PRs.
- Assign branch/worktree boundaries.
- Define acceptance criteria and do-not-touch lists.
- List validation commands and manual gates.

## Hard Boundaries
- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human
- no cheating detection, hidden-intent claims, attraction prediction, lie detection, diagnosis, attachment-style/neurotype inference, therapy framing, manipulation tactics, fake compliance claims, or user/tester training data

## Files Usually Touched
`docs/agents/`, `docs/control_room/`, sprint docs, PR descriptions.

## Files Not To Touch
Production code, engine logic, raw/generated reports, legal approvals unless explicitly assigned.

## Validation Commands
```bash
git status --short
python scripts/check_public_copy_safety.py
git diff --check
```

## Expected Outputs
Implementation plan, PR sequence, acceptance criteria, and validation list.

## Final Output
Recommended PR order, branch names, owners/agents, validation commands, blocked decisions, and manual gates.

## PR Body Checklist
- Plan scope
- Branch sequence
- Do-not-touch boundaries
- Validation commands
- Manual gates

## Failure Conditions
Plan mixes unrelated domains, omits safety/privacy boundaries, relies on raw data, or treats a human gate as automatable.

## Example Prompt
Run Agent 8 for Vibe Signal. Turn this goal into a scoped PR sequence with branch strategy, acceptance criteria, validation commands, and do-not-touch boundaries while preserving no raw private chats, no unsafe relationship claims, no legal/compliance overclaim, no model-accuracy overclaim, synthetic examples only, and human gates remain human.
