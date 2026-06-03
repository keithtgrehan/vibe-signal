# No-Raw-Content Data-Flow Audit

Date: 2026-06-03.

Status: `PASS_FOR_SOURCE-CONTROLLED STATIC CHECKS`.

## Scanner

Command:

```bash
python scripts/check_no_raw_content_leaks.py
```

Result:

- Raw-content leak findings: `0`.
- Feedback metadata no longer stores a text hash for optional feedback comments.
- No new analytics SDK, raw message persistence, raw external dataset, embeddings, vectors, checkpoints, or model files were added.

## Data-Flow Findings

| Area | Result |
| --- | --- |
| Backend feedback storage | Metadata-only; optional comment text is not stored or hashed. |
| Backend request logging | Existing safe request logging avoids raw request bodies. |
| UI feedback | No raw pasted message content is sent with beta signup or metadata-only feedback paths. |
| Synthetic fixtures | Clearly marked synthetic; not copied from real chats or external datasets. |
| Reports/proof docs | Metadata-only; no request/response bodies or tester content. |

## Remaining Manual Checks

- Confirm Render runtime logs during real beta QA do not contain raw user message bodies.
- Confirm crash-reporting/logging remains disabled or metadata-only before TestFlight.
- Confirm legal/privacy review approves the exact data-flow description before tester invites.
