import test from "node:test";
import assert from "node:assert/strict";

import { createProviderSecureStore } from "../src/secureStorage/providerSecureStore.js";
import { requestProviderSummary, validateStoredProviderCredential } from "../src/providers/providerValidation.js";

function makeMockSecureStore({ available = true } = {}) {
  const items = new Map();
  return {
    async isAvailableAsync() {
      return available;
    },
    async setItemAsync(key, value) {
      items.set(key, value);
    },
    async getItemAsync(key) {
      return items.has(key) ? items.get(key) : null;
    },
    async deleteItemAsync(key) {
      items.delete(key);
    },
  };
}

function makeJsonResponse(status, payload) {
  return {
    ok: status >= 200 && status < 300,
    status,
    async text() {
      return JSON.stringify(payload);
    },
  };
}

test("validation returns consent_required before network use", async () => {
  const secureStorage = createProviderSecureStore({
    secureStoreModule: makeMockSecureStore(),
  });
  await secureStorage.saveProviderCredential("openai", "sk-test");

  const result = await validateStoredProviderCredential({
    providerName: "openai",
    consentConfirmed: false,
    secureStorage,
    fetchImpl: async () => {
      throw new Error("fetch should not be called without consent");
    },
  });

  assert.equal(result.status, "consent_required");
});

test("validation maps invalid credentials from provider response", async () => {
  const secureStorage = createProviderSecureStore({
    secureStoreModule: makeMockSecureStore(),
  });
  await secureStorage.saveProviderCredential("openai", "sk-test");

  const result = await validateStoredProviderCredential({
    providerName: "openai",
    consentConfirmed: true,
    secureStorage,
    fetchImpl: async () => makeJsonResponse(401, { error: { message: "bad key" } }),
  });

  assert.equal(result.status, "invalid_credentials");
  assert.equal(result.user_message, "The API key was rejected by the provider.");
});

test("validation maps rate limit and timeout errors", async () => {
  const secureStorage = createProviderSecureStore({
    secureStoreModule: makeMockSecureStore(),
  });
  await secureStorage.saveProviderCredential("groq", "gsk-test");

  const rateLimited = await validateStoredProviderCredential({
    providerName: "groq",
    consentConfirmed: true,
    secureStorage,
    fetchImpl: async () => makeJsonResponse(429, { error: { message: "Too many requests" } }),
  });
  assert.equal(rateLimited.status, "rate_limited");

  const timedOut = await validateStoredProviderCredential({
    providerName: "groq",
    consentConfirmed: true,
    secureStorage,
    fetchImpl: async () => {
      throw new Error("Request timed out");
    },
  });
  assert.equal(timedOut.status, "provider_timeout");
});

test("summary request uses stored credential and returns ready result", async () => {
  const secureStorage = createProviderSecureStore({
    secureStoreModule: makeMockSecureStore(),
  });
  await secureStorage.saveProviderCredential("anthropic", "anthropic-secret");

  let calls = 0;
  const result = await requestProviderSummary({
    providerName: "anthropic",
    consentConfirmed: true,
    secureStorage,
    signalBundle: { shift_radar: { summary: "Later replies look shorter." } },
    fetchImpl: async () => {
      calls += 1;
      if (calls === 1) {
        return makeJsonResponse(200, { content: [{ text: "OK" }] });
      }
      return makeJsonResponse(200, {
        content: [
          {
            text: JSON.stringify({
              summary: "Later replies look shorter and less detailed than earlier ones.",
              what_changed: [
                "Direct answer style softens after the midpoint.",
                "Later messages carry less detail than the opening replies.",
              ],
              compare_prompts: [
                "Compare earlier replies with later replies for detail.",
                "Compare directness with pacing across the conversation.",
              ],
            }),
          },
        ],
      });
    },
  });

  assert.equal(result.status, "success");
  assert.equal(result.external_processing_used, true);
  assert.match(result.external_summary.summary, /shorter/i);
  assert.equal(result.external_summary.provider, "Claude");
});

test("summary request falls back when provider text is unsafe", async () => {
  const secureStorage = createProviderSecureStore({
    secureStoreModule: makeMockSecureStore(),
  });
  await secureStorage.saveProviderCredential("openai", "sk-test");

  let calls = 0;
  const result = await requestProviderSummary({
    providerName: "openai",
    consentConfirmed: true,
    secureStorage,
    signalBundle: {
      shift_radar: { summary: "Later replies look shorter and less detailed than earlier ones." },
      consistency: { top_reasons: ["Direct answer style weakens after the midpoint."] },
    },
    fetchImpl: async () => {
      calls += 1;
      if (calls === 1) {
        return makeJsonResponse(200, { id: "ok" });
      }
      return makeJsonResponse(200, {
        choices: [
          {
            message: {
              content: JSON.stringify({
                summary: "This proves they are suspicious.",
                what_changed: ["Red flags appear later."],
                compare_prompts: ["Ask whether this means dishonesty."],
              }),
            },
          },
        ],
      });
    },
  });

  assert.equal(result.status, "success");
  assert.equal(result.external_summary.used_fallback, true);
  assert.match(result.external_summary.summary, /later replies/i);
  assert.equal(result.external_summary.summary.includes("suspicious"), false);
});
