# n8n Beta Ops Demo Proof

## Scope

This proof records the isolated n8n beta-ops demo assets. The demo is limited to synthetic metadata-only events and does not modify production backend or frontend runtime logic.

## Assets Created

- `ops/n8n/README.md`
- `ops/n8n/vibe_signal_beta_ops.workflow.json`
- `ops/n8n/payloads/feedback_safe.json`
- `ops/n8n/payloads/feedback_unsafe_wording.json`
- `ops/n8n/payloads/backend_failure.json`
- `ops/n8n/scripts/post_feedback_event.js`
- `ops/n8n/scripts/validate_n8n_payloads.js`
- `ops/n8n/docs/interview_demo_script.md`
- `ops/n8n/docs/n8n_beta_ops_runbook.md`

## Validation

Run from the repo root:

```bash
node ops/n8n/scripts/validate_n8n_payloads.js
node ops/n8n/scripts/post_feedback_event.js ops/n8n/payloads/feedback_safe.json
git diff --check
```

The post helper requires `N8N_WEBHOOK_URL`. For local smoke tests, use a temporary localhost receiver. For n8n tests, use a test webhook URL supplied through the local shell.

## Boundaries

- No raw chats, tester messages, credentials, or production webhook URLs are included.
- No analytics SDKs are added.
- No n8n calls are added to production app code.
- No legal compliance claims are made.
- No claims are made about hidden intent, emotional truth, attraction prediction, deception certainty, diagnosis, or manipulation ability.
