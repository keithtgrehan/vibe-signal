const AUTHOR_ALIASES = {
  self: "self",
  me: "self",
  mine: "self",
  other: "other",
  them: "other",
  they: "other",
  unknown: "unknown",
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

export function createMatchClient({
  apiUrl = process.env.EXPO_PUBLIC_API_URL || "",
  fetchImpl = globalThis.fetch,
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

      const parsedApiUrl = parseApiUrl(apiUrl);
      if (!parsedApiUrl.ok) {
        return buildClientError(
          parsedApiUrl.status,
          "Set EXPO_PUBLIC_API_URL to run the local backend match route.",
          { errors: [parsedApiUrl.status] }
        );
      }

      if (typeof fetchImpl !== "function") {
        return buildClientError("transport_unavailable", "Network transport is unavailable.", {
          errors: ["transport_unavailable"],
        });
      }

      try {
        const response = await fetchImpl(`${parsedApiUrl.apiUrl}/api/match`, {
          method: "POST",
          headers: {
            "content-type": "application/json",
          },
          body: JSON.stringify(request.payload),
        });

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
        return buildClientError("network_error", "The backend match route could not be reached.", {
          error: String(error?.message || error || ""),
        });
      }
    },
  };
}
