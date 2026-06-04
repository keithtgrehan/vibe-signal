# n8n Beta Ops Runbook

## Purpose

This runbook covers the isolated n8n beta-ops demo under `ops/n8n`. It is for synthetic metadata-only feedback events and operational triage.

## Files

- `ops/n8n/vibe_signal_beta_ops.workflow.json`: n8n import file.
- `ops/n8n/payloads/*.json`: synthetic metadata-only sample events.
- `ops/n8n/scripts/validate_n8n_payloads.js`: payload safety validation.
- `ops/n8n/scripts/post_feedback_event.js`: local helper for posting a sample payload to a webhook URL supplied through the shell.

## Guardrails

- Do not put raw chats, tester messages, screenshots, transcripts, or credentials in this folder.
- Do not commit webhook URLs.
- Do not wire this workflow into backend or frontend runtime code.
- Do not add analytics SDKs.
- Do not describe the workflow as a legal compliance system.
- Do not use it to claim hidden intent, attraction prediction, deception certainty, diagnosis, or manipulation ability.

## Local Checks

```bash
node ops/n8n/scripts/validate_n8n_payloads.js
git diff --check
```

## Posting a Test Event

Use an n8n test webhook URL only while the workflow is listening for a test event:

```bash
export N8N_WEBHOOK_URL="PASTE_N8N_TEST_WEBHOOK_URL"
node ops/n8n/scripts/post_feedback_event.js ops/n8n/payloads/feedback_safe.json
```

Unset the variable when finished:

```bash
unset N8N_WEBHOOK_URL
```

## Expected Routes

| Payload | Expected route |
| --- | --- |
| `feedback_safe.json` | `product_feedback` |
| `feedback_unsafe_wording.json` | `safety_review` |
| `backend_failure.json` | `reliability_queue` |

## Incident Notes

If a payload validation failure occurs, remove the unsafe field or phrase from the synthetic sample. Do not replace sample payloads with real user text.
