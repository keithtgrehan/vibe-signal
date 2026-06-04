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
