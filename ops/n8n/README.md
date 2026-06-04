# Vibe Signal n8n Beta Ops Control Room

This folder contains an isolated n8n demo for Vibe Signal beta operations.

## What it does

- Receives synthetic beta feedback via n8n Webhook
- Removes raw/private text fields
- Routes metadata-only events to:
  - safety_review
  - bug_queue
  - reliability_queue
  - product_feedback
- Checks `https://vibe-signal.onrender.com/healthz`
- Returns a clean webhook response

## What it does not do

- It does not analyze messages
- It does not store raw chats
- It does not connect to production users
- It does not add analytics SDKs
- It does not make legal compliance claims
- It does not infer hidden intent, attraction, deception, diagnosis, or emotional truth

## Import into n8n

1. Open n8n Cloud.
2. Import `ops/n8n/vibe_signal_beta_ops.workflow.json`.
3. Open the Webhook node.
4. Use the Test URL first.
5. Click **Listen for test event**.
6. Run:

```bash
export N8N_WEBHOOK_URL="PASTE_N8N_TEST_WEBHOOK_URL"
node ops/n8n/scripts/post_feedback_event.js ops/n8n/payloads/feedback_safe.json
node ops/n8n/scripts/post_feedback_event.js ops/n8n/payloads/feedback_unsafe_wording.json
node ops/n8n/scripts/post_feedback_event.js ops/n8n/payloads/backend_failure.json
```

## Local validation

```bash
node ops/n8n/scripts/validate_n8n_payloads.js
```

All sample payloads are synthetic metadata-only events. Do not replace them with real private chats, tester messages, credentials, or production webhook URLs.
