import { buildMatchRequestFromDraft } from "./matchClient.js";
import { parseBackendBaseUrl } from "./backendUrl.js";

const LEGAL_SLUGS = new Set([
  "privacy",
  "terms",
  "data-deletion",
  "data-export",
  "match-disclaimer",
]);

function normalizeText(value) {
  return String(value || "").trim();
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

async function requestJson({ apiUrl, path, method = "GET", body, fetchImpl, timeoutMs }) {
  const response = await withTimeout(
    fetchImpl(`${apiUrl}${path}`, {
      method,
      headers: {
        "content-type": "application/json",
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    }),
    timeoutMs
  );

  if (!response?.ok) {
    let responseBody = "";
    if (typeof response?.text === "function") {
      responseBody = String(await response.text()).slice(0, 400);
    }
    return {
      ok: false,
      status: "backend_request_failed",
      responseStatus: Number(response?.status || 0),
      responseBody,
    };
  }

  const result = typeof response.json === "function" ? await response.json() : {};
  return {
    ok: true,
    status: "backend_request_complete",
    result,
  };
}

export function createVibeBackendClient({
  apiUrl = process.env.EXPO_PUBLIC_API_URL || "",
  fetchImpl = globalThis.fetch,
  timeoutMs = 15000,
} = {}) {
  async function withApi(path, options = {}) {
    const parsedApiUrl = parseBackendBaseUrl(apiUrl);
    if (!parsedApiUrl.ok) {
      return buildClientError(
        parsedApiUrl.status,
        parsedApiUrl.status === "missing_api_url"
          ? "Set EXPO_PUBLIC_API_URL to reach the Vibe Signal backend."
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
      const response = await requestJson({
        apiUrl: parsedApiUrl.apiUrl,
        path,
        fetchImpl,
        timeoutMs,
        ...options,
      });
      if (response.ok) {
        return {
          ok: true,
          status: response.status,
          raw_chat_persisted: false,
          result: response.result,
        };
      }
      return buildClientError(
        "backend_request_failed",
        "The backend could not complete this request.",
        response
      );
    } catch (error) {
      const timedOut = String(error?.message || error || "") === "request_timeout";
      return buildClientError(
        timedOut ? "request_timeout" : "network_error",
        "The backend route could not be reached.",
        {
          error: String(error?.message || error || ""),
        }
      );
    }
  }

  return {
    async submitAnalyzeDraft({ conversationText = "", conversationId = "" } = {}) {
      const request = buildMatchRequestFromDraft({
        conversationText,
        conversationId:
          normalizeText(conversationId) || `mobile_analysis_${Date.now().toString(16)}`,
      });
      if (!request.ok) {
        return buildClientError(
          request.status,
          "Add at least one line of conversation text before surfacing cues.",
          { errors: request.errors }
        );
      }

      return withApi("/api/analyze", {
        method: "POST",
        body: {
          conversation_id: request.payload.conversation_id,
          messages: request.payload.messages,
        },
      });
    },

    async submitFeedbackMetadata({ matchId = "", rating = null, consent = false } = {}) {
      if (consent !== true) {
        return buildClientError(
          "feedback_consent_required",
          "Feedback storage requires explicit consent.",
          { errors: ["feedback_consent_required"] }
        );
      }

      const safeMatchId = normalizeText(matchId);
      if (!safeMatchId) {
        return buildClientError("missing_match_id", "A match result is required before feedback.", {
          errors: ["missing_match_id"],
        });
      }

      return withApi("/api/feedback", {
        method: "POST",
        body: {
          match_id: safeMatchId,
          rating,
          comment: "",
          consent_to_store_feedback: true,
        },
      });
    },

    async fetchLegalDraft(slug = "match-disclaimer") {
      const safeSlug = LEGAL_SLUGS.has(slug) ? slug : "match-disclaimer";
      return withApi(`/legal/${safeSlug}`, {
        method: "GET",
      });
    },
  };
}
