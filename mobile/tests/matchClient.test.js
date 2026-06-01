import test from "node:test";
import assert from "node:assert/strict";

import {
  buildMatchRequestFromDraft,
  createMatchClient,
} from "../src/services/matchClient.js";

test("match request builder parses self and other lines into backend contract messages", () => {
  const request = buildMatchRequestFromDraft({
    conversationText: "self: Can you confirm Friday at 3pm?\nother: Yes, Friday at 3pm works.",
    conversationId: "mobile_match_test",
  });

  assert.equal(request.ok, true);
  assert.equal(request.payload.conversation_id, "mobile_match_test");
  assert.deepEqual(
    request.payload.messages.map((message) => ({
      id: message.id,
      author: message.author,
      text: message.text,
    })),
    [
      {
        id: "m1",
        author: "self",
        text: "Can you confirm Friday at 3pm?",
      },
      {
        id: "m2",
        author: "other",
        text: "Yes, Friday at 3pm works.",
      },
    ]
  );
  assert.equal(request.payload.user_preferences.prefers_directness, true);
  assert.equal(request.payload.user_preferences.max_message_load, "medium");
});

test("match request builder returns an empty state for blank input", () => {
  const request = buildMatchRequestFromDraft({
    conversationText: "   \n  ",
  });

  assert.equal(request.ok, false);
  assert.equal(request.status, "empty_match_input");
});

test("match client posts to /api/match and returns backend JSON without persisting chat text", async () => {
  const calls = [];
  const client = createMatchClient({
    apiUrl: "https://example.test/",
    fetchImpl: async (url, options) => {
      calls.push({
        url,
        body: JSON.parse(options.body),
      });
      return {
        ok: true,
        status: 200,
        async json() {
          return {
            compatibility_band: "moderate",
            score: 0.68,
            positive_factors: ["Specificity and concrete timing cues are present."],
            risk_factors: ["No major deterministic friction cue is visible from the current text."],
            evidence: [
              {
                evidence_id: "ev_1",
                safe_phrase: "message contains direct request wording.",
              },
            ],
            safe_explanation: "Compatibility is based on explicit cues.",
            safe_summary: "The match score reflects observable communication-pattern compatibility.",
          };
        },
      };
    },
  });

  const result = await client.submitMatchDraft({
    conversationText: "self: Can you confirm Friday?\nother: Yes, Friday works.",
    conversationId: "mobile_match_test",
  });

  assert.equal(result.ok, true);
  assert.equal(result.status, "match_complete");
  assert.equal(result.raw_chat_persisted, false);
  assert.equal(result.result.score, 0.68);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "https://example.test/api/match");
  assert.equal(calls[0].body.conversation_id, "mobile_match_test");
  assert.equal(calls[0].body.messages.length, 2);
});

test("match client fails safely when backend URL is missing", async () => {
  const client = createMatchClient({
    apiUrl: "",
    fetchImpl: async () => {
      throw new Error("fetch should not run");
    },
  });

  const result = await client.submitMatchDraft({
    conversationText: "self: Can you confirm Friday?\nother: Yes.",
  });

  assert.equal(result.ok, false);
  assert.equal(result.status, "missing_api_url");
  assert.match(result.userMessage, /EXPO_PUBLIC_API_URL/);
});
