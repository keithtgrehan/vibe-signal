import assert from "node:assert/strict";
import test from "node:test";

import { getApiBaseUrlStatus, resolveApiBaseUrl, submitFeedback } from "../src/api.js";

test("resolveApiBaseUrl prefers the hosted-web VITE_API_BASE_URL override", () => {
  const resolved = resolveApiBaseUrl({
    VITE_API_URL: "",
    VITE_API_BASE_URL: "https://api.example.test/",
    EXPO_PUBLIC_API_URL: "https://mobile.example.test",
  });

  assert.equal(resolved, "https://api.example.test");
});

test("resolveApiBaseUrl keeps existing VITE_API_URL precedence", () => {
  const resolved = resolveApiBaseUrl({
    VITE_API_URL: "https://vite.example.test/",
    VITE_API_BASE_URL: "https://api.example.test",
    EXPO_PUBLIC_API_URL: "https://mobile.example.test",
  });

  assert.equal(resolved, "https://vite.example.test");
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
