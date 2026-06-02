# Closed-Beta Tester Instructions

Status: closed-beta tester guidance only. This is not production launch, legal advice, GDPR/CCPA compliance, or a model-quality claim.

Vibe Signal is communication-support only. It compares observable communication patterns and returns pattern-based suggestions. It does not determine truth, attraction, hidden intent, cheating, diagnosis, neurotype, attachment style, emotional truth, manipulation, or relationship success.

## Before You Start

- Use the beta only if you understand it is experimental closed-beta software.
- Use synthetic or low-sensitivity examples first.
- Only submit messages you have permission to analyze.
- Do not submit sensitive personal data, secrets, medical data, legal documents, financial data, workplace confidential information, or third-party private messages without permission.
- Do not submit phone numbers, emails, addresses, API keys, passwords, tokens, account numbers, or payment details.
- Do not use the output to pressure someone, optimize a reply to make someone like you, or make claims about another person's motives, identity, health, or feelings.
- Do not include real private chats, realistic private-chat fixtures, provider outputs, or copied dataset rows in bug reports, screenshots, demos, or repo artifacts.

## Synthetic Examples To Try

Use examples like these for first-pass testing:

```text
self: Can you confirm Friday at 3pm?
other: Yes, Friday at 3pm works. No pressure if we need to adjust.
```

```text
self: Can we choose a time before tomorrow?
other: Maybe later, I have some things going on.
```

```text
self: Are you still free Tuesday?
other: I said yes earlier, but I am not free Tuesday now.
```

These are authored test examples, not private chats and not dataset rows.

## What To Test

- App opens and the main analysis/match surfaces are usable.
- Empty input does not submit.
- Loading state appears when a match request is sent.
- Error state is understandable if the backend is unavailable.
- Result state shows compatibility score or band, positive factors, risk factors, evidence safe phrases, and explanation.
- Consent and sensitive-data warnings are visible near match submission.
- Privacy, terms, deletion/export, and match-disclaimer links or routes are reachable when exposed in the build.
- Output wording remains cautious and evidence-based.

## What Not To Test

Do not test with:

- real private chats from someone who has not given permission.
- medical, legal, financial, employment, school, or account-security content.
- secrets, tokens, passwords, API keys, payment details, addresses, phone numbers, or emails.
- content intended to test attraction prediction, hidden intent, cheating, diagnosis, neurotype, attachment style, emotional truth, or manipulation.
- attempts to make the app tell you how to make someone respond, like you, or change their feelings.

## Bug Report Format

Use this format. Keep reports metadata-focused and avoid private message content.

```text
Build:
Device:
OS version:
Backend host label: local / deployed / unknown
Screen or flow:
What you expected:
What happened:
Safe reproduction using synthetic text:
Request ID if shown:
Screenshot attached: yes/no
Sensitive data included: no
```

Attach screenshots only when they contain synthetic text or fully non-sensitive UI state. If the issue only reproduces with real content, do not paste that content into the report and do not attach a screenshot containing it. Instead, describe the problem at a high level and ask for a safer reproduction path.

## Deletion And Export Requests

Closed beta does not add account storage or raw chat persistence by default. Local analyze and match routes do not persist raw chats by default. If you need a deletion or export review for beta records that may exist in support, logs, feedback systems, or other enabled metadata systems, use the support path provided by the beta operator.

Reference docs:

- [data deletion request draft](data_deletion_request_draft.md)
- [data export request draft](data_export_request_draft.md)
- [data deletion/export notes](data_deletion_export.md)

These drafts require legal review before public launch.

## Closed-Beta Limitations

- The beta may be unavailable or rolled back without notice.
- Smoke tests prove connectivity and basic response shape only.
- Synthetic-only evaluation does not prove model quality.
- Legal/privacy drafts are not final.
- Commercial training remains blocked until rights are explicitly approved.
- Real-device behavior may differ from local or simulator behavior.
- Monitoring and incident response may still include manual review by the operator.
