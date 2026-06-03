const DEFAULT_API_URL = "https://vibe-signal.onrender.com";
const REQUEST_TIMEOUT_MS = 30000;
const MAX_TRANSIENT_ATTEMPTS = 2;
const RETRY_DELAY_MS = 500;

export const API_RETRYING_BACKEND_MESSAGE = "The backend may be waking up. Trying once more...";

const USER_FACING_ERROR_MESSAGES = {
  configuration_error:
    "The backend URL is misconfigured. Set VITE_API_BASE_URL to a clean http(s) backend origin.",
  backend_waking: API_RETRYING_BACKEND_MESSAGE,
  timeout: "The backend did not respond in time. Please try again in a moment.",
  cors_or_network: "The app could not reach the backend. Check deployment configuration.",
  backend_error: "The backend could not complete the request. Please try again in a moment.",
  validation_error:
    "The request could not be analyzed. Please try the synthetic example or shorten the text.",
};

function normalizeText(value) {
  return String(value || "").trim();
}

export function parseApiBaseUrl(value) {
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

    if (!["http:", "https:"].includes(parsed.protocol) || hasUnsafeParts) {
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
  return parseApiBaseUrl(candidate);
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
  if (error?.name === "AbortError") {
    return "timeout";
  }
  return "cors_or_network";
}

function sleep(ms) {
  return new Promise((resolve) => {
    globalThis.setTimeout(resolve, ms);
  });
}

async function fetchWithTimeout(path, options) {
  const controller = new AbortController();
  const timer = globalThis.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    return await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });
  } finally {
    globalThis.clearTimeout(timer);
  }
}

async function requestJson(path, options = {}, clientOptions = {}) {
  if (!API_CONFIG.ok) {
    throw buildApiRequestError("configuration_error");
  }

  let lastTransientError = null;
  for (let attempt = 1; attempt <= MAX_TRANSIENT_ATTEMPTS; attempt += 1) {
    let response;
    try {
      response = await fetchWithTimeout(path, options);
    } catch (error) {
      const classification = classifyFetchFailure(error);
      lastTransientError = buildApiRequestError(classification);
      if (attempt < MAX_TRANSIENT_ATTEMPTS) {
        clientOptions.onRetry?.({
          classification: "backend_waking",
          message: USER_FACING_ERROR_MESSAGES.backend_waking,
        });
        await sleep(RETRY_DELAY_MS);
        continue;
      }
      throw lastTransientError;
    }

    if (!response.ok) {
      throw buildApiRequestError(classifyHttpStatus(response.status), { status: response.status });
    }

    try {
      return await response.json();
    } catch (_error) {
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

export async function submitFeedback({ matchId, rating, feedbackTag, consent }, clientOptions = {}) {
  const safeMatchId = normalizeText(matchId);
  const safeTag = safeFeedbackTag(feedbackTag, rating);
  const normalizedRating = safeTag === "useful" ? 1 : 0;
  return requestJson("/api/feedback", {
    method: "POST",
    body: JSON.stringify({
      feedback_event_id: buildFeedbackEventId(safeMatchId, safeTag),
      match_id: safeMatchId,
      rating: normalizedRating,
      feedback_tag: safeTag,
      comment: "",
      consent_to_store_feedback: consent === true,
    }),
  }, clientOptions);
}

export async function fetchLegalPage(slug, clientOptions = {}) {
  return requestJson(`/legal/${slug}`, {
    method: "GET",
  }, clientOptions);
}
