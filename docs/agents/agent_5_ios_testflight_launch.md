# Agent 5 - iOS / TestFlight Launch

## Agent Name
Agent 5 - iOS / TestFlight Launch

## Goal
Prepare iOS/TestFlight configuration, metadata, privacy/support links, and real-device QA packets without implying release approval.

## Purpose
Keep beta app readiness organized and App Store-sensitive copy bounded.

## When To Run
Run before EAS builds, TestFlight metadata edits, iOS QA, support/privacy link changes, or App Review copy updates.

## Inputs
Mobile app config, Expo/EAS notes, TestFlight docs, privacy/support drafts, QA runbooks, and synthetic test cases.

## Branch Naming Convention
Use `codex/ios-testflight-<short-scope>`.

## Tasks
- Review Expo/EAS config and public env handling.
- Update TestFlight metadata drafts and QA checklists.
- Verify privacy/support/delete/export links.
- Keep tester invites blocked until manual gates pass.

## Hard Boundaries
- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human
- no cheating detection, hidden-intent claims, attraction prediction, lie detection, diagnosis, attachment-style/neurotype inference, therapy framing, manipulation tactics, fake compliance claims, unreviewed paywalls, or user/tester training data

## Files Usually Touched
`mobile/`, `docs/ios/`, `docs/device_qa_script.md`, `docs/real_device_qa_runbook.md`, `docs/legal_privacy/`.

## Files Not To Touch
Engine logic, dataset sources, production deployment secrets, final App Store approval claims.

## Validation Commands
```bash
cd mobile && npm test
cd mobile && npx expo config --type public
python scripts/check_public_copy_safety.py
python scripts/check_no_raw_content_leaks.py
```

## Expected Outputs
QA-ready mobile docs, bounded metadata, validation results, and pending human gate list.

## Final Output
iOS/TestFlight changes, validation results, manual QA blockers, and invite status.

## PR Body Checklist
- Mobile config/doc changes
- Privacy/support link status
- TestFlight copy safety
- Real-device QA status
- Remaining manual gates

## Failure Conditions
Unreviewed paywall, unsafe App Store copy, private data exposure, or statement that TestFlight/App Store approval is complete without evidence.

## Example Prompt
Run Agent 5 for Vibe Signal. Prepare iOS/TestFlight launch materials and QA checks while preserving no raw private chats, no unsafe relationship claims, no legal/compliance overclaim, no model-accuracy overclaim, synthetic examples only, and human gates remain human.
