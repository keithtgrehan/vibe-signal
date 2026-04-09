import test from "node:test";
import assert from "node:assert/strict";
import { setTimeout as delay } from "node:timers/promises";

import { createMobileEventLogger } from "../src/services/mobileEventLogger.js";

function createMockEventClient() {
  const calls = [];
  return {
    calls,
    async enqueueEvent(eventType, payload) {
      calls.push({
        eventType,
        payload,
      });
      return {
        ok: true,
        status: "event_enqueued",
      };
    },
    async flushQueue() {
      return {
        ok: true,
        status: "flush_completed",
      };
    },
    async notifyForeground() {
      return {
        ok: true,
        status: "foreground_flush",
      };
    },
    async getDebugState() {
      return {
        queue: [],
      };
    },
  };
}

test("mobile event logger only sends state when tracked fields change", async () => {
  const eventClient = createMockEventClient();
  const logger = createMobileEventLogger({
    eventClient,
    nowProvider: () => 1712652000000,
    debounceMs: 5,
  });

  await logger.logState({
    premium_active: false,
    remaining_uses: 5,
    paywall_required: false,
    current_period_type: "trial_week",
    purchase_in_progress: false,
    restore_in_progress: false,
  });
  await delay(15);
  await logger.logState({
    premium_active: false,
    remaining_uses: 5,
    paywall_required: false,
    current_period_type: "trial_week",
    purchase_in_progress: false,
    restore_in_progress: false,
    status_message: "ignored",
  });
  await delay(15);
  await logger.logState({
    premium_active: false,
    remaining_uses: 4,
    paywall_required: false,
    current_period_type: "trial_week",
    purchase_in_progress: false,
    restore_in_progress: false,
  });
  await delay(15);

  const stateCalls = eventClient.calls.filter((item) => item.eventType === "state");
  assert.equal(stateCalls.length, 2);
  assert.equal(stateCalls[0].payload.remaining_uses, 5);
  assert.equal(stateCalls[1].payload.remaining_uses, 4);
});

test("mobile event logger debounces rapid state updates and keeps the latest tracked payload", async () => {
  const eventClient = createMockEventClient();
  const logger = createMobileEventLogger({
    eventClient,
    nowProvider: () => 1712652000100,
    debounceMs: 10,
  });

  await logger.logState({
    premium_active: false,
    remaining_uses: 5,
    paywall_required: false,
    current_period_type: "trial_week",
    purchase_in_progress: false,
    restore_in_progress: false,
  });
  await logger.logState({
    premium_active: false,
    remaining_uses: 3,
    paywall_required: true,
    current_period_type: "trial_week",
    purchase_in_progress: false,
    restore_in_progress: false,
  });
  await delay(25);

  const stateCalls = eventClient.calls.filter((item) => item.eventType === "state");
  assert.equal(stateCalls.length, 1);
  assert.equal(stateCalls[0].payload.remaining_uses, 3);
  assert.equal(stateCalls[0].payload.paywall_required, true);
});

test("mobile event logger forwards structured analysis, quota, and billing payloads", async () => {
  const eventClient = createMockEventClient();
  const logger = createMobileEventLogger({
    eventClient,
    nowProvider: () => 1712652000200,
  });

  await logger.logAnalysis({
    analysisId: "analysis_123",
    success: true,
    mode: "local_analysis",
    status: "analysis_completed",
  });
  await logger.logQuota({
    type: "analysis_consumed",
    remainingAfter: 8,
    analysisId: "analysis_123",
  });
  await logger.logBilling({
    type: "purchase_result",
    status: "purchase_completed",
    productId: "vibesignal_pro_monthly_ios",
    entitlementName: "vibesignal_pro",
  });
  await logger.logEntitlementRefresh({
    premium_active: true,
    entitlement_name: "vibesignal_pro",
    product_id: "vibesignal_pro_monthly_ios",
    subscription_status: "active",
  });
  await logger.logEntitlementRefresh({
    premium_active: true,
    entitlement_name: "vibesignal_pro",
    product_id: "vibesignal_pro_monthly_ios",
    subscription_status: "active",
  });

  const analysisCall = eventClient.calls.find((item) => item.eventType === "analysis");
  const quotaCall = eventClient.calls.find((item) => item.eventType === "quota");
  const billingCalls = eventClient.calls.filter((item) => item.eventType === "billing");

  assert.equal(analysisCall.payload.analysis_id, "analysis_123");
  assert.equal(analysisCall.payload.status, "analysis_completed");
  assert.equal(quotaCall.payload.remaining_after, 8);
  assert.equal(billingCalls.length, 2);
  assert.equal(billingCalls[1].payload.type, "entitlement_refresh");
});
