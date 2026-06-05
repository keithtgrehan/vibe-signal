const DEFAULT_API_URL = "https://vibe-signal.onrender.com";
const REQUEST_TOTAL_TIMEOUT_MS = 25000;
const REQUEST_ATTEMPT_TIMEOUT_MS = 12000;
const MAX_TRANSIENT_ATTEMPTS = 2;
const RETRY_DELAY_MS = 500;

export const API_RETRYING_BACKEND_MESSAGE = "The backend may be waking up. Trying once more...";
export const MAX_ANALYZE_INPUT_CHARS = 2000;
export const ANALYZE_INPUT_LIMIT_MESSAGE =
  "This beta works best with short excerpts. Try 2-8 messages or under 2,000 characters.";

const USER_FACING_ERROR_MESSAGES = {
  configuration_error:
    "The backend URL is misconfigured. Set VITE_API_BASE_URL to a clean http(s) backend origin.",
  backend_waking: API_RETRYING_BACKEND_MESSAGE,
  timeout: "The backend did not respond in time. Please try again in a moment.",
  cancelled: "Analysis cancelled.",
  input_too_long: ANALYZE_INPUT_LIMIT_MESSAGE,
  cors_or_network: "The app could not reach the backend. Check deployment configuration.",
  backend_error: "The backend could not complete the request. Please try again in a moment.",
  validation_error:
    "The request could not be analyzed. Please try the synthetic example or shorten the text.",
};

function normalizeText(value) {
  return String(value || "").trim();
}

function isProductionEnv(env = {}) {
  return (
    env.PROD === true ||
    String(env.PROD || "").toLowerCase() === "true" ||
    String(env.MODE || "").toLowerCase() === "production"
  );
}

export function parseApiBaseUrl(value, options = {}) {
  const text = normalizeText(value);
  if (!text) {
    return {
      ok: false,
      status: "missing_api_url",
      apiUrl: "",
      host: "",
    };
  }

  try {
    const parsed = new URL(text);
    const hasUnsafeParts =
      parsed.username ||
      parsed.password ||
      parsed.search ||
      parsed.hash ||
      (parsed.pathname && parsed.pathname !== "/");

    if (
      !["http:", "https:"].includes(parsed.protocol) ||
      (options.requireHttps === true && parsed.protocol !== "https:") ||
      hasUnsafeParts
    ) {
      return {
        ok: false,
        status: "invalid_api_url",
        apiUrl: "",
        host: "",
      };
    }

    return {
      ok: true,
      status: "api_url_ready",
      apiUrl: parsed.origin,
      host: parsed.host,
    };
  } catch (_error) {
    return {
      ok: false,
      status: "invalid_api_url",
      apiUrl: "",
      host: "",
    };
  }
}

export function getApiBaseUrlStatus(env = {}) {
  const candidate =
    normalizeText(env.VITE_API_BASE_URL) ||
    normalizeText(env.VITE_API_URL) ||
    normalizeText(env.EXPO_PUBLIC_API_URL) ||
    DEFAULT_API_URL;
  return parseApiBaseUrl(candidate, { requireHttps: isProductionEnv(env) });
}

export function resolveApiBaseUrl(env = {}) {
  return getApiBaseUrlStatus(env).apiUrl;
}

export const API_CONFIG = getApiBaseUrlStatus(import.meta.env || {});
export const API_BASE_URL = API_CONFIG.apiUrl;

const AUTHOR_ALIASES = {
  self: "self",
  me: "self",
  mine: "self",
  other: "other",
  them: "other",
  they: "other",
  unknown: "unknown",
};

function parseMessageLine(line, index) {
  const trimmed = String(line || "").trim();
  const prefixed = trimmed.match(/^([a-zA-Z]+)\s*[:\-]\s*(.+)$/);
  if (!prefixed) {
    return {
      id: `m${index + 1}`,
      author: "unknown",
      text: trimmed,
    };
  }

  return {
    id: `m${index + 1}`,
    author: AUTHOR_ALIASES[prefixed[1].toLowerCase()] || "unknown",
    text: prefixed[2].trim(),
  };
}

export function buildMessagesFromText(conversationText) {
  return String(conversationText || "")
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map(parseMessageLine)
    .filter((message) => message.text);
}

function buildConversationId(prefix) {
  return `${prefix}_${Date.now().toString(16)}`;
}

function safeFeedbackTag(value, rating) {
  const fallback = rating === 1 ? "useful" : "not_useful";
  return normalizeText(value || fallback)
    .toLowerCase()
    .replace(/[^a-z0-9_.:-]/g, "_")
    .slice(0, 32);
}

function buildFeedbackEventId(matchId, feedbackTag) {
  const safeMatchId = normalizeText(matchId).replace(/[^A-Za-z0-9_.:-]/g, "_").slice(0, 48);
  return `evt_feedback_${safeMatchId || "unknown"}_${feedbackTag}`;
}

export class ApiRequestError extends Error {
  constructor(classification, message, details = {}) {
    super(message);
    this.name = "ApiRequestError";
    this.classification = classification;
    this.status = details.status;
  }
}

function buildApiRequestError(classification, details = {}) {
  return new ApiRequestError(
    classification,
    USER_FACING_ERROR_MESSAGES[classification] || USER_FACING_ERROR_MESSAGES.backend_error,
    details
  );
}

function classifyHttpStatus(status) {
  if (status === 400 || status === 422) {
    return "validation_error";
  }
  return "backend_error";
}

function classifyFetchFailure(error) {
  if (error?.vibeClassification === "cancelled") {
    return "cancelled";
  }
  if (error?.vibeClassification === "timeout") {
    return "timeout";
  }
  if (error?.name === "AbortError") {
    return "timeout";
  }
  return "cors_or_network";
}

function positiveNumberOrFallback(value, fallback) {
  const numeric = Number(value);
  return Number.isFinite(numeric) && numeric > 0 ? numeric : fallback;
}

function createAbortLikeError(classification) {
  if (typeof DOMException === "function") {
    const error = new DOMException(classification, "AbortError");
    error.vibeClassification = classification;
    return error;
  }
  const error = new Error(classification);
  error.name = "AbortError";
  error.vibeClassification = classification;
  return error;
}

function sleep(ms, signal) {
  if (ms <= 0) {
    return Promise.resolve();
  }
  if (signal?.aborted) {
    return Promise.reject(createAbortLikeError("cancelled"));
  }
  return new Promise((resolve, reject) => {
    let timer;
    const cleanup = () => {
      globalThis.clearTimeout(timer);
      if (signal) {
        signal.removeEventListener("abort", abort);
      }
    };
    const abort = () => {
      cleanup();
      reject(createAbortLikeError("cancelled"));
    };
    timer = globalThis.setTimeout(() => {
      cleanup();
      resolve();
    }, ms);
    if (signal) {
      signal.addEventListener("abort", abort, { once: true });
    }
  });
}

function withTimeout(factory, timeoutMs, signal) {
  if (signal?.aborted) {
    return Promise.reject(createAbortLikeError("cancelled"));
  }
  return new Promise((resolve, reject) => {
    let settled = false;
    const cleanupCallbacks = [];
    const settle = (callback, value) => {
      if (settled) {
        return;
      }
      settled = true;
      for (const cleanup of cleanupCallbacks) {
        cleanup();
      }
      callback(value);
    };

    const timer = globalThis.setTimeout(() => {
      settle(reject, createAbortLikeError("timeout"));
    }, Math.max(1, timeoutMs));
    cleanupCallbacks.push(() => globalThis.clearTimeout(timer));

    if (signal) {
      const abort = () => settle(reject, createAbortLikeError("cancelled"));
      signal.addEventListener("abort", abort, { once: true });
      cleanupCallbacks.push(() => signal.removeEventListener("abort", abort));
    }

    Promise.resolve()
      .then(factory)
      .then((value) => settle(resolve, value))
      .catch((error) => settle(reject, error));
  });
}

async function fetchWithTimeout(path, options, clientOptions = {}) {
  if (clientOptions.signal?.aborted) {
    throw createAbortLikeError("cancelled");
  }
  const controller = new AbortController();
  let timeoutExpired = false;
  const timer = globalThis.setTimeout(() => {
    timeoutExpired = true;
    controller.abort();
  }, Math.max(1, clientOptions.timeoutMs));
  const abortFromClient = () => controller.abort();
  if (clientOptions.signal) {
    clientOptions.signal.addEventListener("abort", abortFromClient, { once: true });
  }
  try {
    return await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });
  } catch (error) {
    if (clientOptions.signal?.aborted) {
      throw createAbortLikeError("cancelled");
    }
    if (timeoutExpired && error?.name === "AbortError") {
      error.vibeClassification = "timeout";
    }
    throw error;
  } finally {
    globalThis.clearTimeout(timer);
    if (clientOptions.signal) {
      clientOptions.signal.removeEventListener("abort", abortFromClient);
    }
  }
}

async function requestJson(path, options = {}, clientOptions = {}) {
  if (!API_CONFIG.ok) {
    throw buildApiRequestError("configuration_error");
  }

  const timeoutMs = positiveNumberOrFallback(clientOptions.timeoutMs, REQUEST_TOTAL_TIMEOUT_MS);
  const attemptTimeoutMs = positiveNumberOrFallback(
    clientOptions.attemptTimeoutMs,
    REQUEST_ATTEMPT_TIMEOUT_MS
  );
  const retryDelayMs = positiveNumberOrFallback(clientOptions.retryDelayMs, RETRY_DELAY_MS);
  const deadline = Date.now() + timeoutMs;
  let lastTransientError = null;
  for (let attempt = 1; attempt <= MAX_TRANSIENT_ATTEMPTS; attempt += 1) {
    const remainingMs = deadline - Date.now();
    if (remainingMs <= 0) {
      throw buildApiRequestError("timeout");
    }
    let response;
    try {
      response = await fetchWithTimeout(path, options, {
        signal: clientOptions.signal,
        timeoutMs: Math.min(attemptTimeoutMs, remainingMs),
      });
    } catch (error) {
      const classification = classifyFetchFailure(error);
      if (classification === "cancelled") {
        throw buildApiRequestError("cancelled");
      }
      lastTransientError = buildApiRequestError(classification);
      if (attempt < MAX_TRANSIENT_ATTEMPTS && Date.now() < deadline) {
        clientOptions.onRetry?.({
          classification: "backend_waking",
          message: USER_FACING_ERROR_MESSAGES.backend_waking,
        });
        try {
          await sleep(Math.min(retryDelayMs, Math.max(0, deadline - Date.now())), clientOptions.signal);
        } catch (delayError) {
          throw buildApiRequestError(classifyFetchFailure(delayError));
        }
        continue;
      }
      throw lastTransientError;
    }

    if (!response.ok) {
      throw buildApiRequestError(classifyHttpStatus(response.status), { status: response.status });
    }

    try {
      return await withTimeout(
        () => response.json(),
        Math.max(1, deadline - Date.now()),
        clientOptions.signal
      );
    } catch (error) {
      const classification = classifyFetchFailure(error);
      if (classification === "cancelled" || classification === "timeout") {
        throw buildApiRequestError(classification);
      }
      throw buildApiRequestError("backend_error");
    }
  }

  throw lastTransientError || buildApiRequestError("backend_error");
}

export async function submitMatch(conversationText, clientOptions = {}) {
  const messages = buildMessagesFromText(conversationText);
  if (!messages.length) {
    throw new Error("Add at least one line of conversation text.");
  }

  return requestJson("/api/match", {
    method: "POST",
    body: JSON.stringify({
      conversation_id: buildConversationId("web_match"),
      messages,
      user_preferences: {
        prefers_directness: true,
        prefers_low_pressure: true,
        prefers_explicit_plans: true,
        max_message_load: "medium",
      },
    }),
  }, clientOptions);
}

export async function submitAnalyze(conversationText, clientOptions = {}) {
  if (normalizeText(conversationText).length > MAX_ANALYZE_INPUT_CHARS) {
    throw buildApiRequestError("input_too_long");
  }
  const messages = buildMessagesFromText(conversationText);
  if (!messages.length) {
    throw new Error("Add at least one line of conversation text.");
  }

  return requestJson("/api/analyze", {
    method: "POST",
    body: JSON.stringify({
      conversation_id: buildConversationId("web_analysis"),
      messages,
    }),
  }, clientOptions);
}

export async function submitFeedback({
  matchId,
  rating,
  feedbackTag,
  consent,
  cueId = "",
  cueFamily = "",
  evidenceQuality = "",
  goalId = "",
  contextId = "",
  styleId = "",
  lowSignal = false,
  synthetic = false,
  clientEventId = "",
  clientTimestamp = "",
}, clientOptions = {}) {
  const safeMatchId = normalizeText(matchId);
  const safeTag = safeFeedbackTag(feedbackTag, rating);
  const normalizedRating = rating === 1 || safeTag === "useful" || safeTag === "cue_fits" ? 1 : 0;
  const feedbackEventId =
    normalizeText(clientEventId).replace(/[^A-Za-z0-9_.:-]/g, "_").slice(0, 80) ||
    buildFeedbackEventId(safeMatchId, safeTag);
  return requestJson("/api/feedback", {
    method: "POST",
    body: JSON.stringify({
      feedback_event_id: feedbackEventId,
      match_id: safeMatchId,
      rating: normalizedRating,
      feedback_tag: safeTag,
      comment: "",
      consent_to_store_feedback: consent === true,
      cue_id: normalizeText(cueId).replace(/[^A-Za-z0-9_.:-]/g, "_").slice(0, 48),
      cue_family: normalizeText(cueFamily).replace(/[^A-Za-z0-9_.:-]/g, "_").slice(0, 48),
      evidence_quality: normalizeText(evidenceQuality).replace(/[^A-Za-z0-9_.:-]/g, "_").slice(0, 24),
      goal_id: normalizeText(goalId).replace(/[^A-Za-z0-9_.:-]/g, "_").slice(0, 32),
      context_id: normalizeText(contextId).replace(/[^A-Za-z0-9_.:-]/g, "_").slice(0, 32),
      analysis_style_id: normalizeText(styleId).replace(/[^A-Za-z0-9_.:-]/g, "_").slice(0, 32),
      low_signal: lowSignal === true,
      synthetic: synthetic === true,
      client_timestamp: normalizeText(clientTimestamp).replace(/[^0-9.]/g, "").slice(0, 24),
    }),
  }, clientOptions);
}

export async function fetchLegalPage(slug, clientOptions = {}) {
  return requestJson(`/api/legal/${slug}`, {
    method: "GET",
  }, clientOptions);
}
