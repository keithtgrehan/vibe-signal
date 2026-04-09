import test from "node:test";
import assert from "node:assert/strict";
import { setTimeout as delay } from "node:timers/promises";

import { createDeviceIdentityService } from "../src/commerce/deviceIdentity.js";
import { createEventClient } from "../src/services/eventClient.js";
import { createEventQueueStore } from "../src/services/eventQueueStore.js";

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

function makeFetchResponse(ok = true) {
  return {
    ok,
    status: ok ? 200 : 500,
  };
}

function buildClient({
  apiUrl = "https://example.test",
  loggingEnabled = true,
  fetchImpl = async () => makeFetchResponse(true),
  nowSequence = [1712652000000, 1712652001000, 1712652002000],
  flushDelayMs = 5,
  secureStoreModule = makeMockSecureStore(),
} = {}) {
  let index = 0;
  const nowProvider = () => {
    const value = nowSequence[Math.min(index, nowSequence.length - 1)];
    index += 1;
    return value;
  };
  const identityService = createDeviceIdentityService({ secureStoreModule });
  const queueStore = createEventQueueStore({ secureStoreModule });
  const client = createEventClient({
    apiUrl,
    loggingEnabled,
    fetchImpl,
    identityService,
    queueStore,
    nowProvider,
    appVersion: "1.2.3",
    sessionId: "session_test",
    flushDelayMs,
  });
  return {
    client,
    queueStore,
    identityService,
    secureStoreModule,
  };
}

test("event client adds event id, client timestamp, user id, and sequence number to outbound events", async () => {
  const requests = [];
  const { client } = buildClient({
    fetchImpl: async (url, options) => {
      requests.push({
        url,
        body: JSON.parse(options.body),
      });
      return makeFetchResponse(true);
    },
  });

  const first = await client.enqueueEvent("analysis", {
    analysis_id: "analysis_1",
    success: true,
    mode: "relationship_chat",
  });
  const second = await client.enqueueEvent("quota", {
    type: "analysis_consumed",
    remaining_after: 8,
    analysis_id: "analysis_1",
  });
  await client.flushQueue({ reason: "test" });
  await delay(10);

  assert.equal(first.ok, true);
  assert.equal(second.ok, true);
  assert.equal(first.payload.sequence_number, 1);
  assert.equal(second.payload.sequence_number, 2);
  assert.equal(typeof first.payload.event_id, "string");
  assert.equal(first.payload.client_timestamp, 1712652000000);
  assert.equal(first.payload.app_version, "1.2.3");
  assert.equal(first.payload.session_id, "session_test");
  assert.equal(requests.length, 2);
  assert.equal(requests[0].url, "https://example.test/api/events/analysis");
  assert.equal(requests[1].url, "https://example.test/api/events/quota");
  assert.match(requests[0].body.user_id, /^install_/);
});

test("event client dedupes repeated event ids before and after successful flush", async () => {
  const requests = [];
  const { client } = buildClient({
    fetchImpl: async (_url, options) => {
      requests.push(JSON.parse(options.body));
      return makeFetchResponse(true);
    },
  });

  const first = await client.enqueueEvent("analysis", {
    event_id: "evt_same",
    analysis_id: "analysis_dup",
    success: true,
    mode: "relationship_chat",
  });
  const second = await client.enqueueEvent("analysis", {
    event_id: "evt_same",
    analysis_id: "analysis_dup",
    success: true,
    mode: "relationship_chat",
  });
  await client.flushQueue({ reason: "test" });
  const third = await client.enqueueEvent("analysis", {
    event_id: "evt_same",
    analysis_id: "analysis_dup",
    success: true,
    mode: "relationship_chat",
  });
  await delay(10);

  assert.equal(first.status, "event_enqueued");
  assert.equal(second.status, "event_deduped");
  assert.equal(third.status, "event_deduped");
  assert.equal(requests.length, 1);
});

test("event client persists failed events, retries them, and drops them after max attempts", async () => {
  const { client } = buildClient({
    fetchImpl: async () => makeFetchResponse(false),
  });

  await client.enqueueEvent("billing", {
    type: "purchase_attempt",
    status: "started",
  });

  const firstFlush = await client.flushQueue({ reason: "retry-1" });
  const firstState = await client.getDebugState();
  const secondFlush = await client.flushQueue({ reason: "retry-2" });
  const secondState = await client.getDebugState();
  const thirdFlush = await client.flushQueue({ reason: "retry-3" });
  const finalState = await client.getDebugState();

  assert.equal(firstFlush.queue_length, 1);
  assert.equal(firstState.queue[0].attempts, 1);
  assert.equal(firstState.scheduled_retry_count, 1);
  assert.equal(secondFlush.queue_length, 1);
  assert.equal(secondState.queue[0].attempts, 2);
  assert.equal(secondState.scheduled_retry_count, 2);
  assert.equal(thirdFlush.queue_length, 0);
  assert.equal(finalState.queue.length, 0);
  assert.equal(finalState.dropped_due_max_attempts, 1);
});

test("event client flushes queued events on startup and on app foreground", async () => {
  const startupRequests = [];
  const startupBuild = buildClient({
    fetchImpl: async (_url, options) => {
      startupRequests.push(JSON.parse(options.body));
      return makeFetchResponse(true);
    },
    flushDelayMs: 5,
  });
  await startupBuild.queueStore.saveState({
    queue: [
      {
        event_id: "evt_startup",
        event_type: "state",
        endpoint: "/api/events/state",
        payload: {
          event_id: "evt_startup",
          user_id: "install_existing",
          client_timestamp: 1712652000000,
          sequence_number: 1,
          session_id: "session_startup",
          platform: "ios",
          app_version: "1.2.3",
          premium_active: false,
          remaining_uses: 5,
          paywall_required: false,
          current_period_type: "trial_week",
          purchase_in_progress: false,
          restore_in_progress: false,
        },
        attempts: 0,
        created_at: 1712652000000,
        last_attempt_at: 0,
      },
    ],
    seen_event_ids: [],
    next_sequence_number: 2,
  });
  const startupClient = createEventClient({
    apiUrl: "https://example.test",
    loggingEnabled: true,
    fetchImpl: async (_url, options) => {
      startupRequests.push(JSON.parse(options.body));
      return makeFetchResponse(true);
    },
    identityService: startupBuild.identityService,
    queueStore: startupBuild.queueStore,
    flushDelayMs: 5,
  });
  assert.ok(startupClient);
  await delay(25);

  const foregroundRequests = [];
  const { client } = buildClient({
    fetchImpl: async (_url, options) => {
      foregroundRequests.push(JSON.parse(options.body));
      return makeFetchResponse(true);
    },
    flushDelayMs: 100,
  });
  await client.enqueueEvent("state", {
    premium_active: false,
    remaining_uses: 4,
    paywall_required: false,
  });
  assert.equal(foregroundRequests.length, 0);
  await client.notifyForeground();
  await delay(10);

  assert.equal(startupRequests.length, 1);
  assert.equal(foregroundRequests.length, 1);
});

test("event client is a safe no-op when logging is disabled or missing configuration", async () => {
  const disabledClient = buildClient({
    loggingEnabled: false,
  }).client;
  const missingUrlClient = buildClient({
    apiUrl: "",
  }).client;

  const disabled = await disabledClient.enqueueEvent("analysis", {
    success: true,
  });
  const missingUrl = await missingUrlClient.enqueueEvent("analysis", {
    success: true,
  });
  const disabledFlush = await disabledClient.flushQueue();
  const missingUrlFlush = await missingUrlClient.flushQueue();

  assert.equal(disabled.status, "logging_disabled");
  assert.equal(missingUrl.status, "logging_not_configured");
  assert.equal(disabledFlush.status, "logging_disabled");
  assert.equal(missingUrlFlush.status, "logging_not_configured");
});

test("event client never throws into callers when enqueueing fails", async () => {
  const client = createEventClient({
    apiUrl: "https://example.test",
    loggingEnabled: true,
    identityService: {
      async getOrCreateInstallationId() {
        throw new Error("boom");
      },
    },
    queueStore: createEventQueueStore({ secureStoreModule: makeMockSecureStore() }),
    fetchImpl: async () => makeFetchResponse(true),
  });

  const result = await client.enqueueEvent("analysis", {
    success: true,
  });

  assert.equal(result.ok, true);
  assert.equal(result.status, "logging_enqueue_failed");
});

test("event client drops malformed payloads safely before enqueue", async () => {
  const { client } = buildClient();

  const result = await client.enqueueEvent("quota", {
    type: "",
    remaining_after: "not-a-number",
  });
  const state = await client.getDebugState();

  assert.equal(result.ok, false);
  assert.equal(result.status, "invalid_event_payload");
  assert.equal(result.dropped, true);
  assert.equal(state.queue.length, 0);
  assert.equal(state.dropped_invalid_payload, 1);
});

test("event client drops non-retryable backend rejections instead of looping forever", async () => {
  const { client } = buildClient({
    fetchImpl: async () => ({
      ok: false,
      status: 422,
      async text() {
        return JSON.stringify({ detail: "bad payload" });
      },
    }),
  });

  await client.enqueueEvent("billing", {
    type: "purchase_result",
    status: "purchase_failed",
  });
  const flush = await client.flushQueue({ reason: "rejected" });
  const state = await client.getDebugState();

  assert.equal(flush.queue_length, 0);
  assert.equal(state.queue.length, 0);
  assert.equal(state.dropped_due_rejection, 1);
});
