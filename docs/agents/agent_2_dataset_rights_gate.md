# Agent 2 - Dataset Rights Gate

## Agent Name
Agent 2 - Dataset Rights Gate

## Goal
Keep dataset use, source registries, and training paths fail-closed unless rights, privacy, provenance, and safety gates are explicitly approved.

## Purpose
Prevent accidental external dataset ingestion, user/tester chat training, or attribution gaps.

## When To Run
Run before adding data sources, changing training scripts, updating registries, or discussing benchmark use.

## Inputs
Dataset registry entries, source docs, scripts, config files, attribution notes, and proposed evaluation/training plans.

## Branch Naming Convention
Use `codex/dataset-rights-<short-scope>`.

## Tasks
- Verify external datasets remain metadata-only unless approved.
- Confirm training paths reject unapproved sources.
- Update attribution and blocked-use docs.
- Check no user/tester chats are used for training or eval.

## Hard Boundaries
- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human
- no cheating detection, hidden-intent claims, attraction prediction, lie detection, diagnosis, attachment-style/neurotype inference, therapy framing, manipulation tactics, fake compliance claims, or user/tester training data

## Files Usually Touched
`configs/`, `docs/datasets_rights.md`, `docs/dataset_attribution.md`, `docs/vibe_training_rights_gates.md`, `scripts/validate_vibe_training_sources.py`, related tests.

## Files Not To Touch
Raw dataset dumps, provider secrets, production logs, engine cue behavior unless separately scoped.

## Validation Commands
```bash
python scripts/validate_vibe_training_sources.py
python scripts/validate_vibe_resource_registry.py
python scripts/check_no_raw_content_leaks.py
python scripts/check_vibe_restricted_artifacts.py --staged
```

## Expected Outputs
Rights-gate summary, registry changes, attribution notes, and fail-closed validation.

## Final Output
Source decisions, allowed/blocked uses, validation results, and remaining human legal/privacy approvals.

## PR Body Checklist
- Sources added or reviewed
- Rights and attribution status
- Raw-content risk
- Training/eval gate impact
- Human approval still required

## Failure Conditions
External rows committed, raw private text introduced, training path opened without approval, or compliance approval implied by documentation.

## Example Prompt
Run Agent 2 for Vibe Signal. Review this dataset or training-source change for rights, privacy, provenance, and fail-closed behavior while preserving no raw private chats, no unsafe relationship claims, no legal/compliance overclaim, no model-accuracy overclaim, synthetic examples only, and human gates remain human.
