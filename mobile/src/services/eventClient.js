import { createDeviceIdentityService } from "../commerce/deviceIdentity.js";
import { validateEventPayload } from "./eventPayloadValidator.js";
import { createEventQueueStore } from "./eventQueueStore.js";
import { getSharedInternalDiagnosticsStore } from "./internalDiagnostics.js";
import { getLoggingConfig } from "./loggingConfig.js";

const QUEUE_LIMIT = 100;
const SEEN_EVENT_LIMIT = 200;
const MAX_ATTEMPTS = 3;
const MAX_EVENT_AGE_MS = 7 * 24 * 60 * 60 * 1000;
const FLUSH_DELAY_MS = 250;
const RETRY_DELAY_MS = 30000;

const ENDPOINTS = {
  analysis: "/api/events/analysis",
  quota: "/api/events/quota",
  billing: "/api/events/billing",
  state: "/api/events/state",
};

function nowMs(nowProvider) {
  return Number(new Date(nowProvider()).getTime());
}

function makeEventId(nowProvider) {
  if (globalThis.crypto && typeof globalThis.crypto.randomUUID === "function") {
    return globalThis.crypto.randomUUID();
  }
  return `evt_${nowMs(nowProvider).toString(16)}_${Math.random().toString(16).slice(2, 10)}`;
}

function normalizeQueueItem(item = {}) {
  return {
    event_id: String(item.event_id || "").trim(),
    event_type: String(item.event_type || "").trim(),
    endpoint: String(item.endpoint || "").trim(),
    payload: item.payload && typeof item.payload === "object" ? item.payload : {},
    attempts: Math.max(0, Number(item.attempts || 0)),
    created_at: Math.max(0, Number(item.created_at || 0)),
    last_attempt_at: Math.max(0, Number(item.last_attempt_at || 0)),
  };
}

function normalizeStateShape(state = {}) {
  return {
    queue: Array.isArray(state.queue) ? state.queue.map(normalizeQueueItem) : [],
    seen_event_ids: Array.isArray(state.seen_event_ids)
      ? state.seen_event_ids.map((item) => String(item || "").trim()).filter(Boolean)
      : [],
    next_sequence_number: Math.max(1, Number(state.next_sequence_number || 1)),
    dropped_due_max_attempts: Math.max(0, Number(state.dropped_due_max_attempts || 0)),
    dropped_due_expiry: Math.max(0, Number(state.dropped_due_expiry || 0)),
    dropped_invalid_payload: Math.max(0, Number(state.dropped_invalid_payload || 0)),
    dropped_due_rejection: Math.max(0, Number(state.dropped_due_rejection || 0)),
    scheduled_retry_count: Math.max(0, Number(state.scheduled_retry_count || 0)),
    deduped_count: Math.max(0, Number(state.deduped_count || 0)),
  };
}

function buildNoopResult(status) {
  return {
    ok: true,
    status,
    noop: true,
  };
}

function buildLoggingGateResult({ loggingEnabled, apiUrl } = {}) {
  if (!loggingEnabled) {
    return buildNoopResult("logging_disabled");
  }
  if (!apiUrl) {
    return buildNoopResult("logging_not_configured");
  }
  return null;
}

export function createEventClient({
  apiUrl = getLoggingConfig().apiUrl,
  loggingEnabled = getLoggingConfig().enabled,
  fetchImpl = globalThis.fetch,
  identityService = createDeviceIdentityService(),
  queueStore = createEventQueueStore(),
  diagnostics = getSharedInternalDiagnosticsStore(),
  nowProvider = () => Date.now(),
  platform = "ios",
  appVersion = getLoggingConfig().appVersion,
  sessionId = `session_${Date.now().toString(16)}`,
  flushDelayMs = FLUSH_DELAY_MS,
  retryDelayMs = RETRY_DELAY_MS,
} = {}) {
  let flushInFlight = null;
  let flushTimer = null;
  let retryTimer = null;

  if (loggingEnabled && !apiUrl) {
    diagnostics.capture({
      category: "logging_config",
      code: "missing_api_url",
      severity: "warn",
      message: "Mobile logging is enabled but EXPO_PUBLIC_API_URL is missing or invalid.",
    });
  }

  function clearRetryTimer() {
    if (retryTimer) {
      clearTimeout(retryTimer);
      retryTimer = null;
    }
  }

  function scheduleFlush() {
    if (buildLoggingGateResult({ loggingEnabled, apiUrl })) {
      return;
    }
    if (flushTimer) {
      clearTimeout(flushTimer);
    }
    flushTimer = setTimeout(() => {
      flushTimer = null;
      void flushQueue({ reason: "scheduled" });
    }, flushDelayMs);
  }

  function scheduleRetry() {
    if (buildLoggingGateResult({ loggingEnabled, apiUrl })) {
      return;
    }
    clearRetryTimer();
    retryTimer = setTimeout(() => {
      retryTimer = null;
      void flushQueue({ reason: "retry" });
    }, retryDelayMs);
  }

  async function loadState() {
    const stored = await queueStore.loadState();
    if (!stored.ok) {
      return stored;
    }
    return {
      ok: true,
      status: stored.status,
      state: normalizeStateShape(stored.state),
    };
  }

  async function saveState(state) {
    const normalized = normalizeStateShape(state);
    return queueStore.saveState({
      ...normalized,
      queue: normalized.queue.slice(-QUEUE_LIMIT),
      seen_event_ids: normalized.seen_event_ids.slice(-SEEN_EVENT_LIMIT),
    });
  }

  async function enqueueEvent(eventType, payload = {}) {
    try {
      const gateResult = buildLoggingGateResult({ loggingEnabled, apiUrl });
      if (gateResult) {
        return gateResult;
      }
      if (!ENDPOINTS[eventType]) {
        return {
          ok: false,
          status: "unsupported_event_type",
        };
      }

      const identity = await identityService.getOrCreateInstallationId();
      if (!identity.ok) {
        return buildNoopResult("logging_identity_unavailable");
      }

      const loaded = await loadState();
      if (!loaded.ok) {
        return buildNoopResult("logging_storage_unavailable");
      }

      const eventId = String(payload.event_id || "").trim() || makeEventId(nowProvider);
      const sequenceNumber = Number(payload.sequence_number || loaded.state.next_sequence_number);
      const clientTimestamp = Number(payload.client_timestamp || nowMs(nowProvider));

      if (
        loaded.state.seen_event_ids.includes(eventId) ||
        loaded.state.queue.some((item) => item.event_id === eventId)
      ) {
        const dedupedState = {
          ...loaded.state,
          deduped_count: loaded.state.deduped_count + 1,
        };
        await saveState(dedupedState);
        return {
          ok: true,
          status: "event_deduped",
          event_id: eventId,
        };
      }

      const envelope = {
        event_id: eventId,
        client_timestamp: clientTimestamp,
        user_id: identity.installationId,
        sequence_number: sequenceNumber,
        session_id: sessionId,
        platform,
        app_version: String(appVersion || "").trim(),
        ...payload,
        event_id: eventId,
        client_timestamp: clientTimestamp,
        user_id: identity.installationId,
        sequence_number: sequenceNumber,
        session_id: sessionId,
        platform,
        app_version: String(appVersion || "").trim(),
      };

      const validation = validateEventPayload(eventType, envelope);
      if (!validation.ok) {
        diagnostics.capture({
          category: "event_client",
          code: "invalid_payload",
          severity: "warn",
          message: `Dropped malformed ${eventType} event before enqueue.`,
          details: {
            eventType,
            errors: validation.errors,
            eventId,
          },
        });
        await saveState({
          ...loaded.state,
          dropped_invalid_payload: loaded.state.dropped_invalid_payload + 1,
        });
        return {
          ok: false,
          status: "invalid_event_payload",
          dropped: true,
          errors: validation.errors,
          event_id: eventId,
        };
      }

      const nextState = {
        ...loaded.state,
        next_sequence_number: sequenceNumber + 1,
        queue: [
          ...loaded.state.queue,
          normalizeQueueItem({
            event_id: eventId,
            event_type: eventType,
            endpoint: ENDPOINTS[eventType],
            payload: envelope,
            attempts: 0,
            created_at: clientTimestamp,
            last_attempt_at: 0,
          }),
        ].slice(-QUEUE_LIMIT),
      };
      await saveState(nextState);
      scheduleFlush();
      return {
        ok: true,
        status: "event_enqueued",
        event_id: eventId,
        payload: envelope,
      };
    } catch (_error) {
      diagnostics.capture({
        category: "event_client",
        code: "enqueue_failed",
        severity: "warn",
        message: "Event enqueue failed and was converted into a safe no-op.",
      });
      return buildNoopResult("logging_enqueue_failed");
    }
  }

  async function flushQueue({ reason = "manual" } = {}) {
    const gateResult = buildLoggingGateResult({ loggingEnabled, apiUrl });
    if (gateResult) {
      return gateResult;
    }
      if (typeof fetchImpl !== "function") {
        return buildNoopResult("logging_transport_unavailable");
      }
    if (flushInFlight) {
      return flushInFlight;
    }

    flushInFlight = (async () => {
      const loaded = await loadState();
      if (!loaded.ok) {
        diagnostics.capture({
          category: "event_client",
          code: "queue_storage_unavailable",
          severity: "warn",
          message: "Event queue storage is unavailable during flush.",
        });
        return buildNoopResult("logging_storage_unavailable");
      }

      const now = nowMs(nowProvider);
      let queue = [...loaded.state.queue];
      let seen = [...loaded.state.seen_event_ids];
      let droppedDueMaxAttempts = loaded.state.dropped_due_max_attempts;
      let droppedDueExpiry = loaded.state.dropped_due_expiry;
      let droppedInvalidPayload = loaded.state.dropped_invalid_payload;
      let droppedDueRejection = loaded.state.dropped_due_rejection;
      let scheduledRetryCount = loaded.state.scheduled_retry_count;
      let hadRetryableFailure = false;

      for (const item of [...queue]) {
        const tooOld = now - Number(item.created_at || 0) > MAX_EVENT_AGE_MS;
        if (tooOld) {
          queue = queue.filter((queued) => queued.event_id !== item.event_id);
          droppedDueExpiry += 1;
          diagnostics.capture({
            category: "event_client",
            code: "event_expired",
            severity: "info",
            message: "Dropped queued event after the maximum local age window.",
            details: {
              eventId: item.event_id,
              eventType: item.event_type,
            },
          });
          continue;
        }

        if (item.attempts >= MAX_ATTEMPTS) {
          queue = queue.filter((queued) => queued.event_id !== item.event_id);
          droppedDueMaxAttempts += 1;
          diagnostics.capture({
            category: "event_client",
            code: "event_max_attempts",
            severity: "warn",
            message: "Dropped queued event after the maximum retry count.",
            details: {
              eventId: item.event_id,
              eventType: item.event_type,
            },
          });
          continue;
        }

        const validation = validateEventPayload(item.event_type, item.payload);
        if (!validation.ok) {
          queue = queue.filter((queued) => queued.event_id !== item.event_id);
          droppedInvalidPayload += 1;
          diagnostics.capture({
            category: "event_client",
            code: "queued_payload_invalid",
            severity: "warn",
            message: "Dropped queued event because the payload no longer matches the expected schema.",
            details: {
              eventId: item.event_id,
              eventType: item.event_type,
              errors: validation.errors,
            },
          });
          continue;
        }

        let responseOk = false;
        let responseStatus = 0;
        let responseBody = "";
        try {
          const response = await fetchImpl(`${apiUrl}${item.endpoint}`, {
            method: "POST",
            headers: {
              "content-type": "application/json",
            },
            body: JSON.stringify(item.payload),
          });
          responseStatus = Number(response?.status || 0);
          if (typeof response?.text === "function") {
            try {
              responseBody = String(await response.text()).slice(0, 500);
            } catch (_error) {
              responseBody = "";
            }
          }
          responseOk = Boolean(response?.ok);
        } catch (_error) {
          responseOk = false;
        }

        if (responseOk) {
          queue = queue.filter((queued) => queued.event_id !== item.event_id);
          seen = [...seen, item.event_id].slice(-SEEN_EVENT_LIMIT);
          continue;
        }

        if (responseStatus === 409) {
          queue = queue.filter((queued) => queued.event_id !== item.event_id);
          seen = [...seen, item.event_id].slice(-SEEN_EVENT_LIMIT);
          diagnostics.capture({
            category: "event_client",
            code: "backend_duplicate_ack",
            severity: "info",
            message: "Backend reported the event as already recorded.",
            details: {
              eventId: item.event_id,
              eventType: item.event_type,
            },
          });
          continue;
        }

        if ([400, 401, 403, 404, 422].includes(responseStatus)) {
          queue = queue.filter((queued) => queued.event_id !== item.event_id);
          droppedDueRejection += 1;
          diagnostics.capture({
            category: "event_client",
            code: "backend_rejected_event",
            severity: "warn",
            message: "Backend rejected an event payload, so it was dropped locally.",
            details: {
              eventId: item.event_id,
              eventType: item.event_type,
              responseStatus,
              responseBody,
            },
          });
        } else {
          const nextAttempts = item.attempts + 1;
          if (nextAttempts >= MAX_ATTEMPTS) {
            queue = queue.filter((queued) => queued.event_id !== item.event_id);
            droppedDueMaxAttempts += 1;
            diagnostics.capture({
              category: "event_client",
              code: "event_retry_exhausted",
              severity: "warn",
              message: "A queued event exhausted all retry attempts after backend or transport failures.",
              details: {
                eventId: item.event_id,
                eventType: item.event_type,
                responseStatus,
              },
            });
          } else {
            queue = queue.map((queued) =>
              queued.event_id === item.event_id
                ? normalizeQueueItem({
                    ...queued,
                    attempts: nextAttempts,
                    last_attempt_at: now,
                  })
                : queued
            );
            hadRetryableFailure = true;
            scheduledRetryCount += 1;
            diagnostics.capture({
              category: "event_client",
              code: "event_send_retry_scheduled",
              severity: "info",
              message: "A queued event send failed and will be retried.",
              details: {
                eventId: item.event_id,
                eventType: item.event_type,
                responseStatus,
              },
            });
          }
        }
      }

      await saveState({
        ...loaded.state,
        queue,
        seen_event_ids: seen,
        dropped_due_max_attempts: droppedDueMaxAttempts,
        dropped_due_expiry: droppedDueExpiry,
        dropped_invalid_payload: droppedInvalidPayload,
        dropped_due_rejection: droppedDueRejection,
        scheduled_retry_count: scheduledRetryCount,
      });
      if (queue.length > 0 && hadRetryableFailure) {
        scheduleRetry();
      } else if (queue.length === 0) {
        clearRetryTimer();
      }
      return {
        ok: true,
        status: "flush_completed",
        reason,
        queue_length: queue.length,
        dropped_due_max_attempts: droppedDueMaxAttempts,
        dropped_due_expiry: droppedDueExpiry,
        dropped_invalid_payload: droppedInvalidPayload,
        dropped_due_rejection: droppedDueRejection,
        scheduled_retry_count: scheduledRetryCount,
      };
    })().finally(() => {
      flushInFlight = null;
    });

    return flushInFlight;
  }

  function notifyForeground() {
    if (flushTimer) {
      clearTimeout(flushTimer);
      flushTimer = null;
    }
    clearRetryTimer();
    scheduleFlush();
    return flushQueue({ reason: "foreground" });
  }

  async function getDebugState() {
    const loaded = await loadState();
    return loaded.ok
      ? {
          ...loaded.state,
          diagnostics: diagnostics.list(),
        }
      : null;
  }

  scheduleFlush();

  return {
    enqueueEvent,
    flushQueue,
    notifyForeground,
    getDebugState,
    isEnabled: () => Boolean(loggingEnabled && apiUrl),
  };
}
