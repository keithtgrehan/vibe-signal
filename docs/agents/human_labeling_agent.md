# Human Labeling Agent

## Agent Name
Human Labeling Agent

## Goal
Prepare reviewer packets, label templates, adjudication workflows, and reviewed-label validation while preserving human authority.

## Purpose
Support human review of observable wording cues without inventing labels or treating bootstrap labels as reviewed truth.

## When To Run
Run before human-review packet generation, adjudication docs, label import/export, or reviewed-label validation.

## Inputs
Synthetic fixtures, evidence objects, reviewer templates, adjudication notes, and reviewed-label files supplied by humans.

## Branch Naming Convention
Use `codex/human-labeling-<short-scope>`.

## Tasks
- Build or validate reviewer packets.
- Keep label fields observable and bounded.
- Separate bootstrap suggestions from human-reviewed labels.
- Document adjudication workflow and unresolved cases.

## Hard Boundaries
- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human
- no cheating detection, hidden-intent claims, attraction prediction, lie detection, diagnosis, attachment-style/neurotype inference, therapy framing, manipulation tactics, fake compliance claims, or user/tester training data

## Files Usually Touched
`docs/labeling/`, `docs/human_review_guidelines_vibe.md`, `tools/create_human_review_packet.py`, `tools/validate_human_labels.py`, `tests/test_human_label_workflow.py`.

## Files Not To Touch
Private reviewer notes with raw chats, engine cue changes unless separately scoped, legal approval records.

## Validation Commands
```bash
python -m pytest -q tests/test_human_label_workflow.py tests/test_reviewed_label_evaluator_fail_closed.py
python scripts/check_no_raw_content_leaks.py
python scripts/check_vibe_restricted_artifacts.py --staged
```

## Expected Outputs
Reviewer packet, label validation report, adjudication notes, and clear human-review status.

## Final Output
Packet paths, reviewed-label status, validation results, and unresolved human decisions.

## PR Body Checklist
- Label workflow changes
- Synthetic-only confirmation
- Reviewed vs bootstrap status
- Validation commands
- Human adjudication needs

## Failure Conditions
Hidden-intent labels, private chat content, auto-approval of human labels, or evaluation claims based on bootstrap labels.

## Example Prompt
Run the Human Labeling Agent for Vibe Signal. Prepare reviewer packets and label validation while preserving no raw private chats, no unsafe relationship claims, no legal/compliance overclaim, no model-accuracy overclaim, synthetic examples only, and human gates remain human.
