import {
  buildBackendVerificationRequest,
  verifyBackendConnection,
} from "../src/services/backendVerification.js";

function readArg(flag) {
  const index = process.argv.indexOf(flag);
  if (index === -1) {
    return "";
  }
  return String(process.argv[index + 1] || "").trim();
}

async function main() {
  const eventType = readArg("--event") || "state";
  const apiUrl = readArg("--api-url") || process.env.EXPO_PUBLIC_API_URL || "";
  const verifyAll = eventType === "all" || process.argv.includes("--all");

  if (verifyAll) {
    const result = await verifyBackendConnection({
      apiUrl,
    });
    console.log(JSON.stringify(result, null, 2));
    if (!result.ok) {
      process.exitCode = 1;
    }
    return;
  }

  const request = buildBackendVerificationRequest({
    eventType,
    apiUrl,
  });

  if (!request.ok) {
    console.error(JSON.stringify({
      ok: false,
      status: request.status,
      errors: request.errors,
    }, null, 2));
    process.exitCode = 1;
    return;
  }

  console.log(JSON.stringify({
    ok: true,
    eventType: request.eventType,
    url: request.url,
    payload: request.payload,
  }, null, 2));

  const response = await fetch(request.url, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify(request.payload),
  });

  const bodyText = await response.text();
  console.log(JSON.stringify({
    ok: response.ok,
    status: response.status,
    body: bodyText.slice(0, 2000),
  }, null, 2));

  if (!response.ok) {
    process.exitCode = 1;
  }
}

void main();
