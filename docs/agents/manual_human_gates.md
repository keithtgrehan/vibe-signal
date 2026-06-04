# Manual Human Gates

Status: list of gates agents must not self-approve.

## Gates Agents Cannot Complete

- Legal/privacy approval.
- Real-device iPhone/TestFlight QA.
- Human-reviewed labels.
- Tester invite decision.
- App Store metadata final approval.
- Public marketing claims.

## Agent Role

Agents can prepare checklists, collect metadata-only evidence, run synthetic validation, and identify blockers. They must mark these gates as pending unless a named human owner supplies review evidence.

## Evidence Rules

- Use metadata-only records.
- Use synthetic examples for QA unless a human-approved process says otherwise.
- Do not paste private chats into issues, PRs, docs, screenshots, or logs.
- Do not convert bootstrap metrics into human-reviewed accuracy statements.

## Reporting Template

| Gate | Status | Evidence | Human owner |
| --- | --- | --- | --- |
| Legal/privacy approval | Pending | Review packet prepared | TBD |
| Real-device QA | Pending | QA checklist available | TBD |
| Human-reviewed labels | Pending | Review packet available | TBD |
| Tester invite decision | Blocked or pending | Gate report | TBD |
| App Store metadata | Pending | Draft metadata | TBD |
| Public marketing claims | Pending | Claims matrix | TBD |
