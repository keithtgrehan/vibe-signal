# Device QA Evidence Template

Use this template after running real-device QA. Keep it metadata-only.

## Metadata

- Date:
- Operator:
- Reviewer:
- Device model:
- OS version:
- Build label:
- Git SHA:
- Backend host label:
- Network condition:

## Results

| Check | Pass/Fail | Notes |
| --- | --- | --- |
| App opens |  |  |
| Synthetic example path |  |  |
| Consent gate blocks private analysis before consent |  |  |
| Sensitive-input warning visible |  |  |
| Match loading state |  |  |
| Match success result hierarchy |  |  |
| Low-signal fallback |  |  |
| Network/backend error state |  |  |
| Feedback duplicate-submit guard |  |  |
| Legal/disclaimer visibility |  |  |
| No unsafe claims observed |  |  |
| No raw content in notes/logs |  |  |

## Allowed Notes

Use route names, status codes, request IDs, coarse error categories, screen names, and build labels only.

## Blocked Notes

Do not paste real messages, names, phone numbers, addresses, tester identity, request bodies, response bodies, screenshots with private text, provider outputs, secrets, raw external dataset rows, vectors, checkpoints, or model artifacts.
