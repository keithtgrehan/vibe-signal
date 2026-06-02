import assert from "node:assert/strict";
import test from "node:test";

import { createVibeBackendClient } from "../src/services/vibeBackendClient.js";

test("submitAnalyzeDraft posts structured messages to current analyze route", async () => {
  const calls = [];
  const client = createVibeBackendClient({
    apiUrl: "https://example.test/",
    fetchImpl: async (url, options) => {
      calls.push({ url, options });
      return {
        ok: true,
        json: async () => ({
          raw_chat_persisted: false,
          evidence: [],
        }),
      };
    },
  });

  const response = await client.submitAnalyzeDraft({
    conversationText: "self: Can you confirm Friday?\nother: Friday works.",
    conversationId: "synthetic_mobile_analysis",
  });

  assert.equal(response.ok, true);
  assert.equal(calls[0].url, "https://example.test/api/analyze");
  const body = JSON.parse(calls[0].options.body);
  assert.equal(body.conversation_id, "synthetic_mobile_analysis");
  assert.deepEqual(body.messages.map((message) => message.author), ["self", "other"]);
});

test("submitFeedbackMetadata fails closed without explicit consent", async () => {
  let called = false;
  const client = createVibeBackendClient({
    apiUrl: "https://example.test",
    fetchImpl: async () => {
      called = true;
      return { ok: true, json: async () => ({}) };
    },
  });

  const response = await client.submitFeedbackMetadata({
    matchId: "vibe_match_123",
    rating: 1,
    consent: false,
  });

  assert.equal(response.ok, false);
  assert.equal(response.status, "feedback_consent_required");
  assert.equal(called, false);
});

test("fetchLegalDraft allows only known backend legal slugs", async () => {
  const calls = [];
  const client = createVibeBackendClient({
    apiUrl: "https://example.test",
    fetchImpl: async (url) => {
      calls.push(url);
      return { ok: true, json: async () => ({ title: "Draft" }) };
    },
  });

  await client.fetchLegalDraft("privacy");
  await client.fetchLegalDraft("unexpected");

  assert.deepEqual(calls, [
    "https://example.test/legal/privacy",
    "https://example.test/legal/match-disclaimer",
  ]);
});

test("backend client rejects non-base URLs before analyze, feedback, or legal fetch", async () => {
  let called = false;
  const client = createVibeBackendClient({
    apiUrl: "https://user:pass@example.test/api?token=secret",
    fetchImpl: async () => {
      called = true;
      throw new Error("fetch should not run");
    },
  });

  const analyze = await client.submitAnalyzeDraft({
    conversationText: "self: Can you confirm Friday?\nother: Yes.",
  });
  const feedback = await client.submitFeedbackMetadata({
    matchId: "vibe_match_123",
    rating: 1,
    consent: true,
  });
  const legal = await client.fetchLegalDraft("privacy");

  for (const response of [analyze, feedback, legal]) {
    assert.equal(response.ok, false);
    assert.equal(response.status, "invalid_api_url");
    assert.match(response.userMessage, /clean http\(s\) backend base URL/);
  }
  assert.equal(called, false);
});
