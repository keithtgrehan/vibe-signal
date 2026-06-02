import { parseBackendBaseUrl } from "./backendUrl.js";

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

  const author = AUTHOR_ALIASES[prefixed[1].toLowerCase()] || "unknown";
  return {
    id: `m${index + 1}`,
    author,
    text: prefixed[2].trim(),
  };
}

export function buildMatchRequestFromDraft({
  conversationText = "",
  conversationId = "",
  userPreferences = {},
} = {}) {
  const lines = String(conversationText || "")
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);

  if (!lines.length) {
    return {
      ok: false,
      status: "empty_match_input",
      payload: null,
      errors: ["empty_match_input"],
    };
  }

  const messages = lines
    .map((line, index) => parseMessageLine(line, index))
    .filter((message) => message.text);

  if (!messages.length) {
    return {
      ok: false,
      status: "empty_match_input",
      payload: null,
      errors: ["empty_match_input"],
    };
  }

  return {
    ok: true,
    status: "match_request_ready",
    payload: {
      conversation_id:
        String(conversationId || "").trim() || `mobile_match_${Date.now().toString(16)}`,
      messages,
      user_preferences: {
        prefers_directness: userPreferences.prefers_directness ?? true,
        prefers_low_pressure: userPreferences.prefers_low_pressure ?? true,
        prefers_explicit_plans: userPreferences.prefers_explicit_plans ?? true,
        max_message_load: userPreferences.max_message_load || "medium",
      },
    },
    errors: [],
  };
}

function buildClientError(status, userMessage, extra = {}) {
  return {
    ok: false,
    status,
    userMessage,
    raw_chat_persisted: false,
    result: null,
    ...extra,
  };
}

function withTimeout(promise, timeoutMs) {
  const timeout = Number(timeoutMs || 0);
  if (!Number.isFinite(timeout) || timeout <= 0) {
    return promise;
  }

  let timer;
  return Promise.race([
    promise,
    new Promise((_, reject) => {
      timer = setTimeout(() => {
        reject(new Error("request_timeout"));
      }, timeout);
    }),
  ]).finally(() => {
    clearTimeout(timer);
  });
}

export function createMatchClient({
  apiUrl = process.env.EXPO_PUBLIC_API_URL || "",
  fetchImpl = globalThis.fetch,
  timeoutMs = 15000,
} = {}) {
  return {
    async submitMatchDraft({
      conversationText = "",
      conversationId = "",
      userPreferences = {},
    } = {}) {
      const request = buildMatchRequestFromDraft({
        conversationText,
        conversationId,
        userPreferences,
      });
      if (!request.ok) {
        return buildClientError(
          request.status,
          "Add at least one line of conversation text before checking communication fit.",
          { errors: request.errors }
        );
      }

      const parsedApiUrl = parseBackendBaseUrl(apiUrl);
      if (!parsedApiUrl.ok) {
        return buildClientError(
          parsedApiUrl.status,
          parsedApiUrl.status === "missing_api_url"
            ? "Set EXPO_PUBLIC_API_URL to run the backend match route."
            : "EXPO_PUBLIC_API_URL must be a clean http(s) backend base URL.",
          { errors: [parsedApiUrl.status] }
        );
      }

      if (typeof fetchImpl !== "function") {
        return buildClientError("transport_unavailable", "Network transport is unavailable.", {
          errors: ["transport_unavailable"],
        });
      }

      try {
        const response = await withTimeout(
          fetchImpl(`${parsedApiUrl.apiUrl}/api/match`, {
            method: "POST",
            headers: {
              "content-type": "application/json",
            },
            body: JSON.stringify(request.payload),
          }),
          timeoutMs
        );

        if (!response?.ok) {
          let responseBody = "";
          if (typeof response?.text === "function") {
            responseBody = String(await response.text()).slice(0, 400);
          }
          return buildClientError(
            "backend_match_failed",
            "The backend could not complete the match check.",
            {
              responseStatus: Number(response?.status || 0),
              responseBody,
            }
          );
        }

        const result = typeof response.json === "function" ? await response.json() : {};
        return {
          ok: true,
          status: "match_complete",
          raw_chat_persisted: false,
          result,
        };
      } catch (error) {
        const timedOut = String(error?.message || error || "") === "request_timeout";
        return buildClientError(
          timedOut ? "request_timeout" : "network_error",
          "The backend match route could not be reached.",
          {
            error: String(error?.message || error || ""),
          }
        );
      }
    },
  };
}
