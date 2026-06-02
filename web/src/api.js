const DEFAULT_API_URL = "https://vibe-signal.onrender.com";
const REQUEST_TIMEOUT_MS = 15000;

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
    normalizeText(env.VITE_API_URL) ||
    normalizeText(env.VITE_API_BASE_URL) ||
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

function buildFeedbackEventId(matchId, rating) {
  const safeMatchId = normalizeText(matchId).replace(/[^A-Za-z0-9_.:-]/g, "_").slice(0, 48);
  const safeRating = String(rating === 1 ? 1 : 0);
  return `evt_feedback_${safeMatchId || "unknown"}_${safeRating}`;
}

function buildSafeRequestError(path, status) {
  const routeLabel =
    path === "/api/match"
      ? "The match request"
      : path === "/api/analyze"
        ? "The cue-evidence request"
        : path === "/api/feedback"
          ? "Feedback metadata"
          : path.startsWith("/legal/")
            ? "The legal draft"
            : "The backend request";
  const statusLabel = status ? ` Status ${status}.` : "";
  return new Error(
    `${routeLabel} could not be completed by the backend.${statusLabel} Check the backend URL and CORS configuration, then try again with synthetic or permissioned text.`
  );
}

async function requestJson(path, options = {}) {
  if (!API_CONFIG.ok) {
    throw new Error(
      "The backend URL is misconfigured. Set VITE_API_BASE_URL to a clean http(s) backend origin."
    );
  }

  const controller = new AbortController();
  const timer = globalThis.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        "content-type": "application/json",
        ...(options.headers || {}),
      },
    });
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new Error("The backend request timed out. Check the backend URL and CORS configuration.");
    }
    throw new Error("The backend route could not be reached. Check the backend URL and CORS configuration.");
  } finally {
    globalThis.clearTimeout(timer);
  }

  if (!response.ok) {
    throw buildSafeRequestError(path, response.status);
  }

  return response.json();
}

export async function submitMatch(conversationText) {
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
  });
}

export async function submitAnalyze(conversationText) {
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
  });
}

export async function submitFeedback({ matchId, rating, consent }) {
  const safeMatchId = normalizeText(matchId);
  return requestJson("/api/feedback", {
    method: "POST",
    body: JSON.stringify({
      feedback_event_id: buildFeedbackEventId(safeMatchId, rating),
      match_id: safeMatchId,
      rating,
      comment: "",
      consent_to_store_feedback: consent === true,
    }),
  });
}

export async function fetchLegalPage(slug) {
  return requestJson(`/legal/${slug}`, {
    method: "GET",
  });
}
