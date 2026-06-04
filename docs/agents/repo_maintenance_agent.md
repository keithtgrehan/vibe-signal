# Repo Maintenance Agent

## Agent Name
Repo Maintenance Agent

## Goal
Keep root files, stale docs, generated artifact policy, command freshness, and dependency notes maintainable.

## Purpose
Reduce repo clutter and keep repeatable commands discoverable without deleting user work.

## When To Run
Run after large PRs, generated report churn, dependency updates, docs drift, or root cleanup tasks.

## Inputs
Git status, file inventory, README, automation docs, dependency files, generated report policy, and validation outputs.

## Branch Naming Convention
Use `codex/repo-maintenance-<short-scope>`.

## Tasks
- Identify stale docs and duplicate generated artifacts.
- Refresh command references.
- Keep generated clutter out of PRs unless intentional.
- Update dependency notes without committing secrets.

## Hard Boundaries
- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human
- no cheating detection, hidden-intent claims, attraction prediction, lie detection, diagnosis, attachment-style/neurotype inference, therapy framing, manipulation tactics, fake compliance claims, destructive git cleanup, or user/tester training data

## Files Usually Touched
`README.md`, `docs/automation/`, `docs/recruiter_readiness/`, `.gitignore`, `package.json`, `pyproject.toml`, command docs.

## Files Not To Touch
User work, raw data, generated reports from another active branch, secrets, engine behavior unless scoped.

## Validation Commands
```bash
bash scripts/dev_check_all.sh
python scripts/check_vibe_restricted_artifacts.py --staged
git diff --check
```

## Expected Outputs
Cleanup summary, command updates, stale-doc notes, and validation results.

## Final Output
Files cleaned or documented, skipped cleanup with reasons, validation results, and remaining maintenance backlog.

## PR Body Checklist
- Maintenance scope
- Files moved/updated
- Generated artifact handling
- Validation results
- User work preserved

## Failure Conditions
Reverting unrelated user changes, deleting needed reports, committing secrets, raw data exposure, or broad unreviewable churn.

## Example Prompt
Run the Repo Maintenance Agent for Vibe Signal. Clean up stale docs and command references while preserving no raw private chats, no unsafe relationship claims, no legal/compliance overclaim, no model-accuracy overclaim, synthetic examples only, and human gates remain human.
