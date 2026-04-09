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
  const calls = [];
  const result = await verifyBackendConnection({
    apiUrl: "https://example.test",
    fetchImpl: async (url) => {
      calls.push(url);
      return {
        ok: true,
        status: 200,
        async text() {
          return "accepted";
        },
      };
    },
  });

  assert.equal(result.ok, true);
  assert.equal(result.results.length, 4);
  assert.equal(calls.length, 4);
  assert.equal(result.results[0].responseBody, "accepted");
});
