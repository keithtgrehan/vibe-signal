import { getProviderCatalogEntry } from "./providerCatalog.js";
import { normalizeExternalSummary } from "./externalSummary.js";

export const VALIDATION_MESSAGES = {
  ready: "The provider is ready to use.",
  missing_credentials: "A stored API key is required before continuing.",
  secure_storage_unavailable: "Secure storage is unavailable on this device.",
  invalid_credentials: "The API key was rejected by the provider.",
  provider_timeout: "The provider did not respond in time.",
  rate_limited: "The provider rate limit was hit. Try again later.",
  provider_unavailable: "The provider is unavailable right now.",
  consent_required: "You must confirm provider consent before continuing.",
  unknown_error: "The provider returned an unexpected error.",
};

export const VALIDATION_LIMITS = {
  maxValidationTimeoutMs: 8000,
  defaultValidationTimeoutMs: 4000,
  maxValidationMessageChars: 24,
  maxSummarySignalChars: 8000,
  maxSummaryExcerptChars: 800,
};

function clampTimeout(timeoutMs) {
  const value = Number(timeoutMs || VALIDATION_LIMITS.defaultValidationTimeoutMs);
  if (!Number.isFinite(value) || value <= 0) {
    return VALIDATION_LIMITS.defaultValidationTimeoutMs;
  }
  return Math.min(Math.max(value, 1000), VALIDATION_LIMITS.maxValidationTimeoutMs);
}

function buildResult({
  providerName,
  modelName = "",
  status,
  userMessage = "",
  ready = status === "ready",
  httpStatus = null,
  validationMode = "live",
  consentConfirmed = false,
  secureStorageAvailable = false,
  credentialPresent = false,
  externalProcessingUsed = false,
  outputText = "",
  externalSummary = null,
} = {}) {
  return {
    provider_name: String(providerName || "").trim().toLowerCase(),
    model_name: String(modelName || "").trim(),
    status,
    ready: Boolean(ready),
    user_message: String(userMessage || VALIDATION_MESSAGES[status] || VALIDATION_MESSAGES.unknown_error).trim(),
    http_status: httpStatus,
    validation_mode: validationMode,
    consent_confirmed: Boolean(consentConfirmed),
    secure_storage_available: Boolean(secureStorageAvailable),
    credential_present: Boolean(credentialPresent),
    external_processing_used: Boolean(externalProcessingUsed),
    output_text: String(outputText || "").trim(),
    external_summary: externalSummary,
  };
}

function mapProviderHttpError(statusCode) {
  if (statusCode === 401 || statusCode === 403) {
    return "invalid_credentials";
  }
  if (statusCode === 429) {
    return "rate_limited";
  }
  if (statusCode === 408 || statusCode === 504) {
    return "provider_timeout";
  }
  if (statusCode >= 500) {
    return "provider_unavailable";
  }
  return "unknown_error";
}

function mapProviderException(error) {
  const message = String(error?.message || error || "").toLowerCase();
  if (message.includes("abort") || message.includes("timed out") || message.includes("timeout")) {
    return "provider_timeout";
  }
  if (message.includes("rate limit") || message.includes("too many requests")) {
    return "rate_limited";
  }
  if (message.includes("network") || message.includes("failed to fetch")) {
    return "provider_unavailable";
  }
  return "unknown_error";
}

function normalizeBaseUrl(url) {
  return String(url || "").trim().replace(/\/+$/, "");
}

function truncateText(text, limit) {
  return String(text || "").slice(0, limit);
}

function buildValidationRequest(entry, credential, timeoutMs) {
  if (entry.providerName === "anthropic") {
    return {
      url: `${normalizeBaseUrl(entry.baseUrl)}${entry.validationPath}`,
      headers: {
        "content-type": "application/json",
        "x-api-key": credential,
        "anthropic-version": "2023-06-01",
      },
      body: {
        model: entry.modelName,
        max_tokens: 1,
        temperature: 0,
        messages: [
          {
            role: "user",
            content: [{ type: "text", text: "OK" }],
          },
        ],
      },
      timeoutMs,
    };
  }

  return {
    url: `${normalizeBaseUrl(entry.baseUrl)}${entry.validationPath}`,
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${credential}`,
    },
    body: {
      model: entry.modelName,
      temperature: 0,
      max_tokens: 1,
      messages: [{ role: "user", content: "OK" }],
    },
    timeoutMs,
  };
}

function buildSummaryRequest(entry, credential, signalBundle, selectedExcerpts, timeoutMs) {
  const excerptBundle = (selectedExcerpts || [])
    .map((item) => truncateText(item, VALIDATION_LIMITS.maxSummaryExcerptChars))
    .filter(Boolean)
    .slice(0, 3);
  const safeSignalText = truncateText(
    JSON.stringify(signalBundle || {}, null, 2),
    VALIDATION_LIMITS.maxSummarySignalChars
  );
  const userPrompt = JSON.stringify({
    task: "Return one short descriptive-only summary in strict JSON.",
    signals: safeSignalText,
    excerpts: excerptBundle,
    output_contract: {
      summary: "One short paragraph under 220 characters.",
      what_changed: "Array of up to 3 descriptive bullets.",
      compare_prompts: "Array of up to 2 short comparison prompts.",
    },
  });

  if (entry.providerName === "anthropic") {
    return {
      url: `${normalizeBaseUrl(entry.baseUrl)}${entry.summaryPath}`,
      headers: {
        "content-type": "application/json",
        "x-api-key": credential,
        "anthropic-version": "2023-06-01",
      },
      body: {
        model: entry.modelName,
        max_tokens: 180,
        temperature: 0,
        system:
          "Describe communication patterns only. Do not make accusations, intent claims, truth claims, or pass/fail judgments. Return strict JSON with summary, what_changed, and compare_prompts only.",
        messages: [
          {
            role: "user",
            content: [{ type: "text", text: userPrompt }],
          },
        ],
      },
      timeoutMs,
    };
  }

  return {
    url: `${normalizeBaseUrl(entry.baseUrl)}${entry.summaryPath}`,
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${credential}`,
    },
    body: {
      model: entry.modelName,
      temperature: 0,
      max_tokens: 180,
      response_format: { type: "json_object" },
      messages: [
        {
          role: "system",
          content:
            "Describe communication patterns only. Do not make accusations, intent claims, truth claims, or pass/fail judgments. Return strict JSON with summary, what_changed, and compare_prompts only.",
        },
        {
          role: "user",
          content: userPrompt,
        },
      ],
    },
    timeoutMs,
  };
}

async function performJsonRequest({ url, headers, body, timeoutMs, fetchImpl }) {
  const timeout = clampTimeout(timeoutMs);
  const controller = typeof AbortController !== "undefined" ? new AbortController() : null;
  const timer = controller
    ? setTimeout(() => {
        controller.abort();
      }, timeout)
    : null;

  try {
    const response = await fetchImpl(url, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
      signal: controller ? controller.signal : undefined,
    });
    const text = await response.text();
    let payload = {};
    try {
      payload = text ? JSON.parse(text) : {};
    } catch (_error) {
      payload = { raw_text: text };
    }
    return { ok: response.ok, status: response.status, payload };
  } finally {
    if (timer) {
      clearTimeout(timer);
    }
  }
}

export async function validateStoredProviderCredential({
  providerName,
  consentConfirmed = false,
  secureStorage,
  fetchImpl = globalThis.fetch,
  timeoutMs,
} = {}) {
  const entry = getProviderCatalogEntry(providerName);
  if (!entry) {
    return buildResult({
      providerName,
      status: "unknown_error",
      userMessage: "Choose a supported provider before continuing.",
      validationMode: "gated",
    });
  }
  if (!consentConfirmed) {
    return buildResult({
      providerName: entry.providerName,
      modelName: entry.modelName,
      status: "consent_required",
      validationMode: "gated",
    });
  }

  const availability = await secureStorage.secureStorageAvailable();
  if (!availability.available) {
    return buildResult({
      providerName: entry.providerName,
      modelName: entry.modelName,
      status: "secure_storage_unavailable",
      validationMode: "gated",
      consentConfirmed,
    });
  }
  const credentialResult = await secureStorage.getProviderCredential(entry.providerName);
  if (!credentialResult.credentialPresent || !credentialResult.credential) {
    return buildResult({
      providerName: entry.providerName,
      modelName: entry.modelName,
      status: "missing_credentials",
      validationMode: "gated",
      consentConfirmed,
      secureStorageAvailable: true,
    });
  }
  if (typeof fetchImpl !== "function") {
    return buildResult({
      providerName: entry.providerName,
      modelName: entry.modelName,
      status: "provider_unavailable",
      validationMode: "gated",
      consentConfirmed,
      secureStorageAvailable: true,
      credentialPresent: true,
    });
  }

  try {
    const request = buildValidationRequest(entry, credentialResult.credential, timeoutMs);
    const response = await performJsonRequest({
      ...request,
      fetchImpl,
    });
    if (!response.ok) {
      const mappedStatus = mapProviderHttpError(response.status);
      return buildResult({
        providerName: entry.providerName,
        modelName: entry.modelName,
        status: mappedStatus,
        httpStatus: response.status,
        consentConfirmed,
        secureStorageAvailable: true,
        credentialPresent: true,
      });
    }
    return buildResult({
      providerName: entry.providerName,
      modelName: entry.modelName,
      status: "ready",
      consentConfirmed,
      secureStorageAvailable: true,
      credentialPresent: true,
    });
  } catch (error) {
    const mappedStatus = mapProviderException(error);
    return buildResult({
      providerName: entry.providerName,
      modelName: entry.modelName,
      status: mappedStatus,
      consentConfirmed,
      secureStorageAvailable: true,
      credentialPresent: true,
    });
  }
}

export async function requestProviderSummary({
  providerName,
  consentConfirmed = false,
  secureStorage,
  signalBundle = {},
  selectedExcerpts = [],
  fetchImpl = globalThis.fetch,
  timeoutMs,
} = {}) {
  const validation = await validateStoredProviderCredential({
    providerName,
    consentConfirmed,
    secureStorage,
    fetchImpl,
    timeoutMs,
  });
  if (validation.status !== "ready") {
    return validation;
  }

  const entry = getProviderCatalogEntry(providerName);
  const credentialResult = await secureStorage.getProviderCredential(entry.providerName);
  try {
    const request = buildSummaryRequest(
      entry,
      credentialResult.credential,
      signalBundle,
      selectedExcerpts,
      timeoutMs
    );
    const response = await performJsonRequest({
      ...request,
      fetchImpl,
    });
    if (!response.ok) {
      const mappedStatus = mapProviderHttpError(response.status);
      return buildResult({
        providerName: entry.providerName,
        modelName: entry.modelName,
        status: mappedStatus,
        httpStatus: response.status,
        consentConfirmed,
        secureStorageAvailable: true,
        credentialPresent: true,
      });
    }
    const externalSummary = normalizeExternalSummary({
      providerName: entry.providerName,
      modelName: entry.modelName,
      payload: response.payload,
      signalBundle,
    });

    return buildResult({
      providerName: entry.providerName,
      modelName: entry.modelName,
      status: "success",
      ready: true,
      userMessage: "External summary ready.",
      consentConfirmed,
      secureStorageAvailable: true,
      credentialPresent: true,
      externalProcessingUsed: true,
      outputText: externalSummary.summary,
      externalSummary,
    });
  } catch (error) {
    const mappedStatus = mapProviderException(error);
    return buildResult({
      providerName: entry.providerName,
      modelName: entry.modelName,
      status: mappedStatus,
      consentConfirmed,
      secureStorageAvailable: true,
      credentialPresent: true,
    });
  }
}
