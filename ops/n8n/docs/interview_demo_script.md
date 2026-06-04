# Interview Demo Script: n8n Beta Ops Control Room

## Setup

- Import `ops/n8n/vibe_signal_beta_ops.workflow.json` into n8n.
- Use only the n8n test webhook URL during the interview.
- Keep `N8N_WEBHOOK_URL` in the local shell only. Do not commit it.
- Confirm sample payloads are synthetic metadata-only events before posting.

## Demo Flow

1. Open the workflow and show the Webhook, sanitization, backend health check, metadata row, and response nodes.
2. Run `node ops/n8n/scripts/validate_n8n_payloads.js`.
3. Post `feedback_safe.json` and show it routes to `product_feedback`.
4. Post `feedback_unsafe_wording.json` and show it routes to `safety_review`.
5. Post `backend_failure.json` and show it routes to `reliability_queue`.
6. Point out that the response includes route, result ID, raw-text removal status, and backend status.

## Talk Track

- "This is an isolated beta-ops workflow. It is not wired into production app code."
- "The payloads are synthetic and metadata-only."
- "The workflow removes raw/private text fields before routing."
- "This demo supports review queues and reliability triage without adding analytics SDKs."

## Avoid Saying

- Do not say this proves legal compliance.
- Do not say the system reads hidden meaning or emotional truth.
- Do not say the system predicts attraction, deception, or intent.
- Do not say raw private chats are stored or reviewed in this workflow.
