import { createEventClient } from "./eventClient.js";

const STATE_DEBOUNCE_MS = 400;

function normalizeRemainingUses(value) {
  if (value === Number.POSITIVE_INFINITY) {
    return -1;
  }
  return Math.max(0, Number(value || 0));
}

function normalizeTrackedState(input = {}) {
  return {
    premium_active: Boolean(input.premium_active),
    remaining_uses: normalizeRemainingUses(input.remaining_uses),
    paywall_required: Boolean(input.paywall_required),
    current_period_type: String(input.current_period_type || "").trim(),
    purchase_in_progress: Boolean(input.purchase_in_progress),
    restore_in_progress: Boolean(input.restore_in_progress),
  };
}

export function createMobileEventLogger({
  eventClient = createEventClient(),
  nowProvider = () => Date.now(),
  debounceMs = STATE_DEBOUNCE_MS,
} = {}) {
  let lastStateSignature = "";
  let pendingStateSignature = "";
  let stateTimer = null;
  let pendingStatePayload = null;
  let lastBillingSignature = "";

  async function logAnalysis({
    analysisId = "",
    success = false,
    mode = "local",
    status = "",
    eventOrigin = "mobile_app",
  } = {}) {
    return eventClient.enqueueEvent("analysis", {
      analysis_id: String(analysisId || "").trim(),
      success: Boolean(success),
      mode: String(mode || "").trim(),
      status: String(status || "").trim(),
      event_origin: String(eventOrigin || "").trim(),
      client_timestamp: Number(nowProvider()),
    });
  }

  async function logQuota({
    type = "",
    remainingAfter = 0,
    analysisId = "",
  } = {}) {
    return eventClient.enqueueEvent("quota", {
      type: String(type || "").trim(),
      remaining_after: normalizeRemainingUses(remainingAfter),
      analysis_id: String(analysisId || "").trim(),
      client_timestamp: Number(nowProvider()),
    });
  }

  async function logBilling({
    type = "",
    status = "",
    productId = "",
    entitlementName = "",
    eventOrigin = "mobile_app",
  } = {}) {
    return eventClient.enqueueEvent("billing", {
      type: String(type || "").trim(),
      status: String(status || "").trim(),
      product_id: String(productId || "").trim(),
      entitlement_name: String(entitlementName || "").trim(),
      event_origin: String(eventOrigin || "").trim(),
      client_timestamp: Number(nowProvider()),
    });
  }

  function logState(nextState = {}) {
    const normalized = normalizeTrackedState(nextState);
    const signature = JSON.stringify(normalized);
    if (signature === lastStateSignature || signature === pendingStateSignature) {
      return Promise.resolve({
        ok: true,
        status: "state_unchanged",
      });
    }
    pendingStateSignature = signature;
    pendingStatePayload = {
      ...normalized,
      client_timestamp: Number(nowProvider()),
    };
    if (stateTimer) {
      clearTimeout(stateTimer);
    }
    stateTimer = setTimeout(() => {
      const payload = pendingStatePayload;
      pendingStatePayload = null;
      stateTimer = null;
      if (!payload) {
        return;
      }
      lastStateSignature = JSON.stringify(normalizeTrackedState(payload));
      pendingStateSignature = "";
      void eventClient.enqueueEvent("state", payload);
    }, debounceMs);
    return Promise.resolve({
      ok: true,
      status: "state_scheduled",
    });
  }

  function logEntitlementRefresh(state = {}) {
    const signature = JSON.stringify({
      premium_active: Boolean(state.premium_active),
      entitlement_name: String(state.entitlement_name || "").trim(),
      product_id: String(state.product_id || "").trim(),
      subscription_status: String(state.subscription_status || "").trim(),
    });
    if (signature === lastBillingSignature) {
      return Promise.resolve({
        ok: true,
        status: "billing_unchanged",
      });
    }
    lastBillingSignature = signature;
    return logBilling({
      type: "entitlement_refresh",
      status: String(state.subscription_status || "").trim(),
      productId: state.product_id,
      entitlementName: state.entitlement_name,
    });
  }

  function flush() {
    return eventClient.flushQueue({ reason: "manual" });
  }

  function notifyForeground() {
    return eventClient.notifyForeground();
  }

  async function getDebugState() {
    return eventClient.getDebugState();
  }

  return {
    logAnalysis,
    logQuota,
    logBilling,
    logState,
    logEntitlementRefresh,
    flush,
    notifyForeground,
    getDebugState,
  };
}

let sharedLogger = null;

export function getSharedMobileEventLogger() {
  if (!sharedLogger) {
    sharedLogger = createMobileEventLogger();
  }
  return sharedLogger;
}
