import test from "node:test";
import assert from "node:assert/strict";

import {
  buildBackendVerificationPlan,
  buildBackendVerificationRequest,
  verifyBackendConnection,
} from "../src/services/backendVerification.js";

test("backend verification request builds a backend-safe state payload", () => {
  const request = buildBackendVerificationRequest({
    eventType: "state",
    apiUrl: "https://example.test/",
    now: 1712652000000,
  });

  assert.equal(request.ok, true);
  assert.equal(request.url, "https://example.test/api/events/state");
  assert.equal(request.payload.event_id, "evt_verify_state_1712652000000");
  assert.equal(request.payload.client_timestamp, 1712652000000);
  assert.equal(request.payload.user_id, "install_verification");
  assert.equal(request.payload.paywall_required, false);
});

test("backend verification request rejects invalid API URLs safely", () => {
  const request = buildBackendVerificationRequest({
    eventType: "analysis",
    apiUrl: "javascript:alert(1)",
  });

  assert.equal(request.ok, false);
  assert.equal(request.status, "invalid_api_url");
});

test("backend verification request reports missing API URLs safely", () => {
  for (const apiUrl of ["", "   "]) {
    const request = buildBackendVerificationRequest({
      eventType: "analysis",
      apiUrl,
    });

    assert.equal(request.ok, false);
    assert.equal(request.status, "missing_api_url");
  }
});

test("backend verification request rejects credentials, paths, queries, and fragments", () => {
  const unsafeUrls = [
    "https://user:pass@example.test",
    "https://example.test/api/events/state",
    "https://example.test/api/..",
    "https://example.test/.",
    "https://example.test/foo/%2e%2e/",
    "https://example.test?token=abc",
    "https://example.test#fragment",
    "https://example.test:0",
  ];

  for (const apiUrl of unsafeUrls) {
    const request = buildBackendVerificationRequest({
      eventType: "state",
      apiUrl,
    });

    assert.equal(request.ok, false);
    assert.equal(request.status, "invalid_api_url");
  }
});

test("backend verification returns before fetch when URL is missing or invalid", async () => {
  let called = false;
  const result = await verifyBackendConnection({
    apiUrl: "",
    fetchImpl: async () => {
      called = true;
      throw new Error("fetch should not be called");
    },
  });

  assert.equal(result.ok, false);
  assert.equal(result.status, "missing_api_url");
  assert.equal(called, false);
});

test("backend verification request rejects unsupported event types", () => {
  const request = buildBackendVerificationRequest({
    eventType: "unknown",
    apiUrl: "https://example.test",
  });

  assert.equal(request.ok, false);
  assert.equal(request.status, "unsupported_event_type");
});

test("backend verification plan can prepare all event routes in one pass", () => {
  const plan = buildBackendVerificationPlan({
    apiUrl: "https://example.test",
  });

  assert.equal(plan.ok, true);
  assert.equal(plan.requests.length, 4);
  assert.deepEqual(
    plan.requests.map((item) => item.eventType),
    ["analysis", "quota", "billing", "state"]
  );
});

test("backend verification returns structured per-endpoint results", async () => {
  const rawSecret = "raw-private-message-secret-from-verification";
  const calls = [];
  const result = await verifyBackendConnection({
    apiUrl: "https://example.test",
    fetchImpl: async (url) => {
      calls.push(url);
      return {
        ok: true,
        status: 200,
        async text() {
          return rawSecret;
        },
      };
    },
  });

  assert.equal(result.ok, true);
  assert.equal(result.results.length, 4);
  assert.equal(calls.length, 4);
  assert.equal(result.results[0].responseBodyPresent, true);
  assert.equal(result.results[0].responseBodyLength, rawSecret.length);
  assert.equal(Object.hasOwn(result.results[0], "responseBody"), false);
  assert.equal(JSON.stringify(result).includes(rawSecret), false);
});
