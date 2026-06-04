# Closed Beta Gate Agent

## Agent Name
Closed Beta Gate Agent

## Goal
Run closed-beta gates, legal/privacy packet checks, TestFlight QA evidence review, monitoring readiness, and final tester-invite blocker reporting.

## Purpose
Keep beta readiness explicit without claiming launch approval.

## When To Run
Run before release-candidate review, tester-invite discussion, deployment verification, or gate report updates.

## Inputs
Gate checker output, legal/privacy docs, real-device QA evidence, deployment smoke results, monitoring notes, and known blockers.

## Branch Naming Convention
Use `codex/closed-beta-gate-<short-scope>`.

## Tasks
- Run closed-beta gate checker.
- Verify required evidence docs exist.
- Summarize manual gates and blocker state.
- Keep tester invite decision assigned to human owner.

## Hard Boundaries
- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human
- no cheating detection, hidden-intent claims, attraction prediction, lie detection, diagnosis, attachment-style/neurotype inference, therapy framing, manipulation tactics, fake compliance claims, or user/tester training data

## Files Usually Touched
`docs/proof/closed_beta/`, `docs/final_closed_beta_launch_gate_report.md`, `scripts/closed_beta_gate_check.py`, `.github/workflows/closed-beta-gate-manual.yml`.

## Files Not To Touch
Legal approval signoff, App Store final approval, human-reviewed label truth, raw tester feedback.

## Validation Commands
```bash
bash scripts/closed_beta_gate_all.sh
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
```

## Expected Outputs
Gate report, invite blocker summary, manual evidence list, and deployment/manual QA status.

## Final Output
Gate state, pass/fail/manual-required table, tester-invite status, validation results, and manual gates remaining.

## PR Body Checklist
- Gate status
- Legal/privacy status
- Real-device QA status
- Monitoring readiness
- Invite decision caveat

## Failure Conditions
Tester invite marked approved without human evidence, legal/privacy approval implied, raw tester data committed, or P0 gate skipped silently.

## Example Prompt
Run the Closed Beta Gate Agent for Vibe Signal. Generate the release gate report and tester-invite blocker summary while preserving no raw private chats, no unsafe relationship claims, no legal/compliance overclaim, no model-accuracy overclaim, synthetic examples only, and human gates remain human.
