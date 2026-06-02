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

function summarizeVerificationResult(result) {
  return {
    ok: Boolean(result?.ok),
    status: String(result?.status || ""),
    results: Array.isArray(result?.results)
      ? result.results.map((item) => {
          const responseBody = String(item?.responseBody || "");
          return {
            eventType: String(item?.eventType || ""),
            url: String(item?.url || ""),
            ok: Boolean(item?.ok),
            status: Number(item?.status || 0),
            response_body_present: responseBody.length > 0,
            response_body_length: responseBody.length,
          };
        })
      : [],
    errors: Array.isArray(result?.errors) ? result.errors : [],
  };
}

async function main() {
  const eventType = readArg("--event") || "state";
  const apiUrl = readArg("--api-url") || process.env.EXPO_PUBLIC_API_URL || "";
  const verifyAll = eventType === "all" || process.argv.includes("--all");

  if (verifyAll) {
    const result = await verifyBackendConnection({
      apiUrl,
    });
    console.log(JSON.stringify(summarizeVerificationResult(result), null, 2));
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
    payload_field_count: Object.keys(request.payload || {}).length,
  }, null, 2));

  let response;
  let bodyText = "";
  try {
    response = await fetch(request.url, {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify(request.payload),
    });
    bodyText = typeof response.text === "function" ? await response.text() : "";
  } catch (_error) {
    console.log(JSON.stringify({
      ok: false,
      status: 0,
      detail: "transport_error",
    }, null, 2));
    process.exitCode = 1;
    return;
  }

  console.log(JSON.stringify({
    ok: response.ok,
    status: response.status,
    response_body_present: String(bodyText || "").length > 0,
    response_body_length: String(bodyText || "").length,
  }, null, 2));

  if (!response.ok) {
    process.exitCode = 1;
  }
}

void main();
