import { validateEventPayload } from "./eventPayloadValidator.js";

const EVENT_ENDPOINTS = {
  analysis: "/api/events/analysis",
  quota: "/api/events/quota",
  billing: "/api/events/billing",
  state: "/api/events/state",
};

function parseApiUrl(value) {
  const text = String(value || "").trim();
  if (!text) {
    return {
      ok: false,
      status: "missing_api_url",
      apiUrl: "",
    };
  }

  try {
    const parsed = new URL(text);
    if (!["http:", "https:"].includes(parsed.protocol)) {
      return {
        ok: false,
        status: "invalid_api_url",
        apiUrl: text,
      };
    }
    return {
      ok: true,
      status: "api_url_ready",
      apiUrl: parsed.toString().replace(/\/$/, ""),
    };
  } catch (_error) {
    return {
      ok: false,
      status: "invalid_api_url",
      apiUrl: text,
    };
  }
}

function buildSamplePayload(eventType, {
  now = Date.now(),
  userId = "install_verification",
  sessionId = "session_verification",
  sequenceNumber = 1,
  platform = "ios",
  appVersion = "",
} = {}) {
  const timestamp = Number(now);
  const envelope = {
    event_id: `evt_verify_${eventType}_${timestamp}`,
    client_timestamp: timestamp,
    user_id: String(userId || "").trim(),
    sequence_number: Number(sequenceNumber || 1),
    session_id: String(sessionId || "").trim(),
    platform: String(platform || "ios").trim(),
    app_version: String(appVersion || "").trim(),
  };

  if (eventType === "analysis") {
    return {
      ...envelope,
      analysis_id: "analysis_verification",
      success: true,
      mode: "local_analysis",
      status: "analysis_completed",
      event_origin: "mobile_verification",
    };
  }

  if (eventType === "quota") {
    return {
      ...envelope,
      type: "analysis_consumed",
      remaining_after: 4,
      analysis_id: "analysis_verification",
    };
  }

  if (eventType === "billing") {
    return {
      ...envelope,
      type: "entitlement_refresh",
      status: "inactive",
      product_id: "vibesignal_pro_monthly_ios",
      entitlement_name: "vibesignal_pro",
      event_origin: "mobile_verification",
    };
  }

  if (eventType === "state") {
    return {
      ...envelope,
      premium_active: false,
      remaining_uses: 5,
      paywall_required: false,
      current_period_type: "trial_week",
      purchase_in_progress: false,
      restore_in_progress: false,
    };
  }

  return envelope;
}

export function buildBackendVerificationRequest({
  eventType = "state",
  apiUrl = process.env.EXPO_PUBLIC_API_URL || "",
  now = Date.now(),
  userId = "install_verification",
  sessionId = "session_verification",
  sequenceNumber = 1,
  platform = "ios",
  appVersion = process.env.EXPO_PUBLIC_APP_VERSION || "",
} = {}) {
  const normalizedType = String(eventType || "").trim().toLowerCase();
  const endpoint = EVENT_ENDPOINTS[normalizedType] || "";
  if (!endpoint) {
    return {
      ok: false,
      status: "unsupported_event_type",
      endpoint: "",
      payload: {},
      errors: ["unsupported_event_type"],
    };
  }

  const parsedApiUrl = parseApiUrl(apiUrl);
  if (!parsedApiUrl.ok) {
    return {
      ok: false,
      status: parsedApiUrl.status,
      endpoint,
      payload: {},
      errors: [parsedApiUrl.status],
    };
  }

  const payload = buildSamplePayload(normalizedType, {
    now,
    userId,
    sessionId,
    sequenceNumber,
    platform,
    appVersion,
  });
  const validation = validateEventPayload(normalizedType, payload);
  if (!validation.ok) {
    return {
      ok: false,
      status: "invalid_event_payload",
      endpoint,
      payload,
      errors: validation.errors,
    };
  }

  return {
    ok: true,
    status: "verification_request_ready",
    eventType: normalizedType,
    endpoint,
    url: `${parsedApiUrl.apiUrl}${endpoint}`,
    payload,
    errors: [],
  };
}

export function buildBackendVerificationPlan({
  apiUrl = process.env.EXPO_PUBLIC_API_URL || "",
  eventTypes = Object.keys(EVENT_ENDPOINTS),
  now = Date.now(),
  userId = "install_verification",
  sessionId = "session_verification",
  platform = "ios",
  appVersion = process.env.EXPO_PUBLIC_APP_VERSION || "",
} = {}) {
  const requests = eventTypes.map((eventType, index) =>
    buildBackendVerificationRequest({
      eventType,
      apiUrl,
      now: Number(now) + index,
      userId,
      sessionId,
      sequenceNumber: index + 1,
      platform,
      appVersion,
    })
  );

  const failures = requests.filter((item) => !item.ok);
  return {
    ok: failures.length === 0,
    status: failures.length === 0 ? "verification_plan_ready" : failures[0].status,
    requests,
    errors: failures.flatMap((item) => item.errors || []),
  };
}

export async function verifyBackendConnection({
  apiUrl = process.env.EXPO_PUBLIC_API_URL || "",
  eventTypes = Object.keys(EVENT_ENDPOINTS),
  fetchImpl = globalThis.fetch,
  now = Date.now(),
  userId = "install_verification",
  sessionId = "session_verification",
  platform = "ios",
  appVersion = process.env.EXPO_PUBLIC_APP_VERSION || "",
} = {}) {
  const plan = buildBackendVerificationPlan({
    apiUrl,
    eventTypes,
    now,
    userId,
    sessionId,
    platform,
    appVersion,
  });

  if (!plan.ok) {
    return {
      ok: false,
      status: plan.status,
      results: [],
      errors: plan.errors,
    };
  }

  if (typeof fetchImpl !== "function") {
    return {
      ok: false,
      status: "transport_unavailable",
      results: [],
      errors: ["transport_unavailable"],
    };
  }

  const results = [];
  for (const request of plan.requests) {
    let responseStatus = 0;
    let responseBody = "";
    let responseOk = false;
    try {
      const response = await fetchImpl(request.url, {
        method: "POST",
        headers: {
          "content-type": "application/json",
        },
        body: JSON.stringify(request.payload),
      });
      responseStatus = Number(response?.status || 0);
      responseOk = Boolean(response?.ok);
      if (typeof response?.text === "function") {
        responseBody = String(await response.text()).slice(0, 1000);
      }
    } catch (error) {
      responseBody = String(error?.message || error || "");
    }

    results.push({
      eventType: request.eventType,
      url: request.url,
      ok: responseOk,
      status: responseStatus || (responseOk ? 200 : 0),
      responseBody,
    });
  }

  return {
    ok: results.every((item) => item.ok),
    status: results.every((item) => item.ok)
      ? "backend_verification_passed"
      : "backend_verification_failed",
    results,
    errors: results.filter((item) => !item.ok).map((item) => `${item.eventType}:${item.status}`),
  };
}
