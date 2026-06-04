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
