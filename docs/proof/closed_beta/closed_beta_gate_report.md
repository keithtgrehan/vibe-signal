# Closed-Beta Gate Report

Generated: `2026-06-03T21:12:54.099416+00:00`

Final tester invite decision: `BLOCKED`

## Gate Matrix

| Gate | Status | Notes |
| --- | --- | --- |
| `safety_scanners` | `PASS` | Public-copy and no-raw-content scanners run by this gate. |
| `restricted_artifacts` | `PASS` | Restricted-artifact scanner result for staged changes. |
| `synthetic_regression_report` | `PASS` | 10k synthetic regression hardening report presence check. |
| `human_reviewed_labels` | `MANUAL_REQUIRED` | Human-reviewed labels are pending; bootstrap labels do not unlock this gate. |
| `legal_privacy_review` | `MANUAL_REQUIRED` | Legal/privacy packet exists for human review; approval is not claimed. |
| `real_device_qa` | `MANUAL_REQUIRED` | Real-device iPhone/TestFlight QA evidence is required before invites. |
| `deployed_backend_version` | `PASS` | Deploy metadata status: current. |
| `metadata_only_monitoring` | `PASS` | Structured metadata-only monitoring contract and docs. |

## Scanner Results

- `public_copy_scanner`: `PASS` via `/Users/keith/.pyenv/versions/3.11.3/bin/python scripts/check_public_copy_safety.py`
- `no_raw_content_scanner`: `PASS` via `/Users/keith/.pyenv/versions/3.11.3/bin/python scripts/check_no_raw_content_leaks.py`
- `restricted_artifact_scanner`: `PASS` via `/Users/keith/.pyenv/versions/3.11.3/bin/python scripts/check_vibe_restricted_artifacts.py --staged`

## Decision Rule

Tester invites remain `BLOCKED` unless real-device QA evidence exists, legal/privacy review is completed by a human reviewer, deployed backend metadata proves the intended commit, P0 metadata-only monitoring is accepted, and safety scanners pass.

This report does not claim production launch, App Store release, legal/GDPR compliance, human-reviewed validation, or real-world accuracy.
