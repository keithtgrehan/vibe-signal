#!/usr/bin/env bash
set -euo pipefail

BRANCH="codex/n8n-beta-ops-control-room"

echo "Creating isolated n8n beta-ops control room assets..."

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: run this inside the vibe-signal git repo."
  exit 1
fi

if git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
  git checkout "${BRANCH}"
else
  git checkout -b "${BRANCH}"
fi

mkdir -p \
  ops/n8n/payloads \
  ops/n8n/scripts \
  ops/n8n/docs \
  docs/proof/closed_beta \
  scripts

cat > ops/n8n/payloads/feedback_safe.json <<'JSON'
{
  "source": "web_beta",
  "event_type": "feedback",
  "result_id": "synthetic_001",
  "cue_type": "ambiguity",
  "feedback_category": "useful",
  "severity": "low",
  "notes": "The evidence card helped me understand the result.",
  "raw_message_present": false
}
JSON

cat > ops/n8n/payloads/feedback_unsafe_wording.json <<'JSON'
{
  "source": "web_beta",
  "event_type": "feedback",
  "result_id": "synthetic_002",
  "cue_type": "pressure",
  "feedback_category": "unsafe_wording",
  "severity": "high",
  "notes": "Output sounded too certain.",
  "flagged_phrase": "certainty_claim",
  "raw_message_present": false
}
JSON

cat > ops/n8n/payloads/backend_failure.json <<'JSON'
{
  "source": "web_beta",
  "event_type": "backend_failure",
  "result_id": "synthetic_003",
  "cue_type": null,
  "feedback_category": "bug",
  "severity": "medium",
  "notes": "Synthetic backend failure test.",
  "raw_message_present": false
}
JSON

cat > ops/n8n/scripts/validate_n8n_payloads.js <<'JS'
const fs = require("fs");
const path = require("path");

const payloadDir = path.resolve(__dirname, "../payloads");

const forbiddenFields = [
  "raw_message",
  "message",
  "message_text",
  "private_text",
  "chat_text",
  "transcript",
  "screenshot",
  "conversation",
  "raw_chat",
  "raw_text"
];

const forbiddenText = [
  "they like you",
  "hidden intent",
  "they are lying",
  "this proves",
  "diagnose",
  "manipulate",
  "make them respond",
  "win them back",
  "gdpr compliant",
  "eu ai act compliant"
];

function walk(value, visitor, keyPath = []) {
  visitor(value, keyPath);
  if (Array.isArray(value)) {
    value.forEach((item, index) => walk(item, visitor, [...keyPath, String(index)]));
  } else if (value && typeof value === "object") {
    Object.entries(value).forEach(([key, item]) => walk(item, visitor, [...keyPath, key]));
  }
}

function fail(msg) {
  console.error(`n8n payload validation failed: ${msg}`);
  process.exitCode = 1;
}

if (!fs.existsSync(payloadDir)) {
  fail(`payload dir missing: ${payloadDir}`);
  process.exit(1);
}

const files = fs.readdirSync(payloadDir).filter((file) => file.endsWith(".json"));

if (files.length === 0) {
  fail("no payload JSON files found");
  process.exit(1);
}

for (const file of files) {
  const fullPath = path.join(payloadDir, file);
  let parsed;

  try {
    parsed = JSON.parse(fs.readFileSync(fullPath, "utf8"));
  } catch (err) {
    fail(`${file} is invalid JSON: ${err.message}`);
    continue;
  }

  walk(parsed, (value, keyPath) => {
    const key = keyPath[keyPath.length - 1];

    if (key && forbiddenFields.includes(key)) {
      fail(`${file} contains forbidden raw-text field "${key}" at ${keyPath.join(".")}`);
    }

    if (typeof value === "string") {
      const lower = value.toLowerCase();
      for (const phrase of forbiddenText) {
        if (lower.includes(phrase)) {
          fail(`${file} contains forbidden phrase "${phrase}" at ${keyPath.join(".")}`);
        }
      }
    }
  });

  if (parsed.raw_message_present !== false) {
    fail(`${file} must set raw_message_present=false`);
  }
}

if (process.exitCode) {
  process.exit(process.exitCode);
}

console.log(`Validated ${files.length} metadata-only n8n payload(s).`);
JS

cat > ops/n8n/scripts/post_feedback_event.js <<'JS'
const fs = require("fs");

const payloadPath = process.argv[2];
const webhookUrl = process.env.N8N_WEBHOOK_URL;

function exitSafe(message, code = 1) {
  console.error(message);
  process.exit(code);
}

if (!payloadPath) {
  exitSafe("Usage: node ops/n8n/scripts/post_feedback_event.js <payload-json>");
}

if (!webhookUrl) {
  exitSafe("Missing N8N_WEBHOOK_URL. No request sent.");
}

if (!/^https?:\/\//.test(webhookUrl)) {
  exitSafe("N8N_WEBHOOK_URL must start with http:// or https://");
}

let payload;

try {
  payload = JSON.parse(fs.readFileSync(payloadPath, "utf8"));
} catch (err) {
  exitSafe(`Invalid payload JSON: ${err.message}`);
}

const forbiddenKeys = [
  "raw_message",
  "message",
  "message_text",
  "private_text",
  "chat_text",
  "transcript",
  "screenshot",
  "conversation",
  "raw_chat",
  "raw_text"
];

for (const key of forbiddenKeys) {
  if (Object.prototype.hasOwnProperty.call(payload, key)) {
    exitSafe(`Refusing to send payload containing forbidden raw-text field: ${key}`);
  }
}

fetch(webhookUrl, {
  method: "POST",
  headers: {
    "content-type": "application/json",
    "user-agent": "vibe-signal-n8n-demo"
  },
  body: JSON.stringify(payload)
})
  .then(async (res) => {
    const text = await res.text();
    console.log(JSON.stringify({
      ok: res.ok,
      status: res.status,
      payload_result_id: payload.result_id || null,
      payload_event_type: payload.event_type || null,
      response_preview: text.slice(0, 500)
    }, null, 2));

    if (!res.ok) process.exit(1);
  })
  .catch((err) => {
    exitSafe(`Request failed: ${err.message}`);
  });
JS

cat > ops/n8n/vibe_signal_beta_ops.workflow.json <<'JSON'
{
  "name": "Vibe Signal Beta Ops Control Room",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "vibe-signal-beta-ops",
        "responseMode": "responseNode",
        "options": {}
      },
      "id": "Webhook_Beta_Feedback",
      "name": "Webhook - Beta Feedback Event",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [240, 300],
      "webhookId": "vibe-signal-beta-ops-demo"
    },
    {
      "parameters": {
        "jsCode": "const forbiddenRawFields = ['raw_message','message','message_text','private_text','chat_text','transcript','screenshot','conversation','raw_chat','raw_text'];\nconst forbiddenPhrases = ['they like you','hidden intent','they are lying','this proves','diagnose','manipulate','make them respond','win them back'];\nconst input = $json.body || $json;\nconst clean = {};\nlet rawTextRemoved = false;\nfor (const [key, value] of Object.entries(input)) {\n  if (forbiddenRawFields.includes(key)) {\n    rawTextRemoved = true;\n    continue;\n  }\n  clean[key] = value;\n}\nconst textForReview = JSON.stringify(clean).toLowerCase();\nconst blockedPhraseHit = forbiddenPhrases.find((phrase) => textForReview.includes(phrase)) || null;\nlet route = 'product_feedback';\nif (blockedPhraseHit || clean.feedback_category === 'unsafe_wording' || clean.severity === 'high') route = 'safety_review';\nelse if (clean.event_type === 'backend_failure') route = 'reliability_queue';\nelse if (clean.feedback_category === 'bug') route = 'bug_queue';\nreturn [{ json: { ...clean, route, raw_text_removed: rawTextRemoved || clean.raw_message_present === false, blocked_phrase_hit: blockedPhraseHit, processed_at: new Date().toISOString() } }];"
      },
      "id": "Code_Sanitize_And_Route",
      "name": "Code - Sanitize + Route",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [520, 300]
    },
    {
      "parameters": {
        "url": "https://vibe-signal.onrender.com/healthz",
        "options": {
          "timeout": 5000
        }
      },
      "id": "HTTP_Backend_Healthz",
      "name": "HTTP - Vibe Signal Healthz",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [800, 300]
    },
    {
      "parameters": {
        "jsCode": "const event = $('Code - Sanitize + Route').first().json;\nconst health = $json || {};\nreturn [{ json: { timestamp: event.processed_at, source: event.source || null, event_type: event.event_type || null, result_id: event.result_id || null, cue_type: event.cue_type || null, feedback_category: event.feedback_category || null, severity: event.severity || null, route: event.route || 'product_feedback', raw_text_removed: event.raw_text_removed === true, backend_status: health.ok === true ? 'ok' : 'unknown_or_failed', notes: event.notes || null, blocked_phrase_hit: event.blocked_phrase_hit || null } }];"
      },
      "id": "Code_Metadata_Row",
      "name": "Code - Build Metadata Row",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1080, 300]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ { ok: true, route: $json.route, result_id: $json.result_id, raw_text_removed: $json.raw_text_removed, backend_status: $json.backend_status } }}",
        "options": {
          "responseCode": 200
        }
      },
      "id": "Respond_To_Webhook",
      "name": "Respond - Clean Demo Result",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [1360, 300]
    }
  ],
  "connections": {
    "Webhook - Beta Feedback Event": {
      "main": [
        [
          {
            "node": "Code - Sanitize + Route",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Code - Sanitize + Route": {
      "main": [
        [
          {
            "node": "HTTP - Vibe Signal Healthz",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "HTTP - Vibe Signal Healthz": {
      "main": [
        [
          {
            "node": "Code - Build Metadata Row",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Code - Build Metadata Row": {
      "main": [
        [
          {
            "node": "Respond - Clean Demo Result",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "settings": {
    "executionOrder": "v1",
    "saveDataSuccessExecution": "none",
    "saveDataErrorExecution": "all"
  },
  "staticData": null,
  "pinData": {},
  "versionId": "vibe-signal-n8n-demo-v1",
  "triggerCount": 0,
  "tags": []
}
JSON

cat > ops/n8n/README.md <<'MD'
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
MD

cat > ops/n8n/docs/interview_demo_script.md <<'MD'
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
MD

cat > ops/n8n/docs/n8n_beta_ops_runbook.md <<'MD'
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
MD

cat > docs/proof/closed_beta/n8n_beta_ops_demo.md <<'MD'
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
MD


chmod +x ops/n8n/scripts/*.js

node ops/n8n/scripts/validate_n8n_payloads.js

mock_log="$(mktemp)"
node <<'JS' > "${mock_log}" &
const http = require("http");

const server = http.createServer((req, res) => {
  let body = "";
  req.on("data", (chunk) => {
    body += chunk;
  });
  req.on("end", () => {
    let payload = {};
    try {
      payload = JSON.parse(body || "{}");
    } catch {
      res.writeHead(400, { "content-type": "application/json" });
      res.end(JSON.stringify({ ok: false, error: "invalid_json" }));
      server.close(() => process.exit(1));
      return;
    }

    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify({
      ok: true,
      route: "product_feedback",
      result_id: payload.result_id || null,
      raw_text_removed: payload.raw_message_present === false,
      backend_status: "mock_ok"
    }));
    server.close(() => process.exit(0));
  });
});

const timeout = setTimeout(() => {
  console.error("mock webhook timed out");
  server.close(() => process.exit(1));
}, 15000);

server.listen(0, "127.0.0.1", () => {
  clearTimeout(timeout);
  console.log(server.address().port);
});
JS
mock_pid="$!"

mock_port=""
for _ in $(seq 1 100); do
  if [ -s "${mock_log}" ]; then
    mock_port="$(head -n 1 "${mock_log}")"
    break
  fi
  sleep 0.1
done

if [ -z "${mock_port}" ]; then
  echo "Error: local mock webhook did not start."
  kill "${mock_pid}" >/dev/null 2>&1 || true
  rm -f "${mock_log}"
  exit 1
fi

export N8N_WEBHOOK_URL="http://127.0.0.1:${mock_port}/vibe-signal-beta-ops-test"
node ops/n8n/scripts/post_feedback_event.js ops/n8n/payloads/feedback_safe.json
unset N8N_WEBHOOK_URL
wait "${mock_pid}"
rm -f "${mock_log}"

git diff --check

echo "n8n beta-ops control room bootstrap complete."
