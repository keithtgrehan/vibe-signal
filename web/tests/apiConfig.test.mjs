import assert from "node:assert/strict";
import test from "node:test";

import {
  getApiBaseUrlStatus,
  resolveApiBaseUrl,
  submitAnalyze,
  submitFeedback,
} from "../src/api.js";

test("resolveApiBaseUrl prefers the hosted-web VITE_API_BASE_URL override", () => {
  const resolved = resolveApiBaseUrl({
    VITE_API_URL: "",
    VITE_API_BASE_URL: "https://api.example.test/",
    EXPO_PUBLIC_API_URL: "https://mobile.example.test",
  });

  assert.equal(resolved, "https://api.example.test");
});

test("resolveApiBaseUrl prefers VITE_API_BASE_URL over legacy aliases", () => {
  const resolved = resolveApiBaseUrl({
    VITE_API_URL: "https://vite.example.test/",
    VITE_API_BASE_URL: "https://api.example.test",
    EXPO_PUBLIC_API_URL: "https://mobile.example.test",
  });

  assert.equal(resolved, "https://api.example.test");
});

test("resolveApiBaseUrl falls back to the Render backend when no env override is set", () => {
  assert.equal(resolveApiBaseUrl({}), "https://vibe-signal.onrender.com");
});

test("web API config rejects non-origin backend URLs", () => {
  const unsafeValues = [
    "javascript:alert(1)",
    "https://user:pass@example.test",
    "https://example.test/api",
    "https://example.test?token=secret",
    "https://example.test#fragment",
  ];

  for (const value of unsafeValues) {
    const status = getApiBaseUrlStatus({ VITE_API_BASE_URL: value });
    assert.equal(status.ok, false);
    assert.equal(status.status, "invalid_api_url");
    assert.equal(status.apiUrl, "");
    assert.equal(status.host, "");
  }
});

test("submitFeedback sends bounded metadata without raw message text", async () => {
  const originalFetch = globalThis.fetch;
  const calls = [];
  globalThis.fetch = async (_url, options) => {
    calls.push(JSON.parse(options.body));
    return {
      ok: true,
      json: async () => ({ status: "accepted" }),
    };
  };

  try {
    await submitFeedback({
      matchId: "vibe_match_123",
      feedbackTag: "too_strong",
      consent: true,
    });
  } finally {
    globalThis.fetch = originalFetch;
  }

  assert.equal(calls.length, 1);
  assert.equal(calls[0].feedback_event_id, "evt_feedback_vibe_match_123_too_strong");
  assert.equal(calls[0].match_id, "vibe_match_123");
  assert.equal(calls[0].feedback_tag, "too_strong");
  assert.equal(calls[0].comment, "");
  assert.equal(calls[0].consent_to_store_feedback, true);
  assert.equal(Object.hasOwn(calls[0], "raw_message_text"), false);
  assert.equal(Object.hasOwn(calls[0], "source_text"), false);
});

test("submitAnalyze retries one transient network failure then returns safe result", async () => {
  const originalFetch = globalThis.fetch;
  const retryStates = [];
  const calls = [];
  globalThis.fetch = async (_url, options) => {
    calls.push(JSON.parse(options.body));
    if (calls.length === 1) {
      throw new TypeError("Failed to fetch raw transport detail should stay hidden");
    }
    return {
      ok: true,
      status: 200,
      json: async () => ({
        conversation_id: calls[1].conversation_id,
        analysis_mode: "deterministic_local_only",
        provider_used: false,
        raw_chat_persisted: false,
        evidence: [],
      }),
    };
  };

  try {
    const result = await submitAnalyze(
      "self: Are we still on for Friday?\nother: maybe later, not sure yet",
      {
        onRetry: (state) => retryStates.push(state),
      }
    );

    assert.equal(calls.length, 2);
    assert.equal(result.analysis_mode, "deterministic_local_only");
    assert.deepEqual(retryStates, [
      {
        classification: "backend_waking",
        message: "The backend may be waking up. Trying once more...",
      },
    ]);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("submitAnalyze retries once then classifies a final timeout safely", async () => {
  const originalFetch = globalThis.fetch;
  let attempts = 0;
  globalThis.fetch = async () => {
    attempts += 1;
    throw new DOMException("raw timeout detail should stay hidden", "AbortError");
  };

  try {
    await assert.rejects(
      () => submitAnalyze("self: Friday?\nother: maybe later"),
      (error) => {
        assert.equal(error.classification, "timeout");
        assert.equal(error.message, "The backend did not respond in time. Please try again in a moment.");
        assert.equal(String(error).includes("raw timeout detail"), false);
        return true;
      }
    );
    assert.equal(attempts, 2);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("submitAnalyze classifies CORS or network failures without raw details", async () => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => {
    throw new TypeError("Failed to fetch token=raw-secret");
  };

  try {
    await assert.rejects(
      () => submitAnalyze("self: Friday?\nother: maybe later"),
      (error) => {
        assert.equal(error.classification, "cors_or_network");
        assert.equal(error.message, "The app could not reach the backend. Check deployment configuration.");
        assert.equal(String(error).includes("raw-secret"), false);
        return true;
      }
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("submitAnalyze does not retry backend validation errors", async () => {
  const originalFetch = globalThis.fetch;
  let attempts = 0;
  globalThis.fetch = async () => {
    attempts += 1;
    return {
      ok: false,
      status: 400,
      json: async () => ({ detail: "raw validation detail should stay hidden" }),
    };
  };

  try {
    await assert.rejects(
      () => submitAnalyze("self: Friday?\nother: maybe later"),
      (error) => {
        assert.equal(error.classification, "validation_error");
        assert.equal(
          error.message,
          "The request could not be analyzed. Please try the synthetic example or shorten the text."
        );
        assert.equal(String(error).includes("raw validation detail"), false);
        return true;
      }
    );
    assert.equal(attempts, 1);
  } finally {
    globalThis.fetch = originalFetch;
  }
});
