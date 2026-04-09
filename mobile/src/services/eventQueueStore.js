const STATE_KEY = "vibesignal.logging.queue.v1";
const PROBE_KEY = "vibesignal.logging.queue.probe";
const SECURE_STORE_OPTIONS = {
  keychainService: "vibesignal.logging.queue",
};

const DEFAULT_STATE = {
  queue: [],
  seen_event_ids: [],
  next_sequence_number: 1,
  dropped_due_max_attempts: 0,
  dropped_due_expiry: 0,
  dropped_invalid_payload: 0,
  dropped_due_rejection: 0,
  deduped_count: 0,
};

async function loadSecureStoreModule(explicitModule) {
  if (explicitModule) {
    return explicitModule.default ?? explicitModule;
  }
  const module = await import("expo-secure-store");
  return module.default ?? module;
}

function unavailableResult(error = "") {
  return {
    ok: false,
    status: "secure_storage_unavailable",
    secureStorageAvailable: false,
    error: String(error || ""),
  };
}

function normalizeState(rawState = {}) {
  return {
    queue: Array.isArray(rawState.queue) ? rawState.queue : [],
    seen_event_ids: Array.isArray(rawState.seen_event_ids) ? rawState.seen_event_ids : [],
    next_sequence_number: Math.max(1, Number(rawState.next_sequence_number || 1)),
    dropped_due_max_attempts: Math.max(0, Number(rawState.dropped_due_max_attempts || 0)),
    dropped_due_expiry: Math.max(0, Number(rawState.dropped_due_expiry || 0)),
    dropped_invalid_payload: Math.max(0, Number(rawState.dropped_invalid_payload || 0)),
    dropped_due_rejection: Math.max(0, Number(rawState.dropped_due_rejection || 0)),
    deduped_count: Math.max(0, Number(rawState.deduped_count || 0)),
  };
}

export function createEventQueueStore({ secureStoreModule } = {}) {
  let cachedAvailability = null;

  async function validateSecureStore() {
    if (cachedAvailability) {
      return cachedAvailability;
    }

    try {
      const secureStore = await loadSecureStoreModule(secureStoreModule);
      const available =
        secureStore &&
        typeof secureStore.isAvailableAsync === "function" &&
        typeof secureStore.setItemAsync === "function" &&
        typeof secureStore.getItemAsync === "function" &&
        typeof secureStore.deleteItemAsync === "function" &&
        Boolean(await secureStore.isAvailableAsync());

      if (!available) {
        cachedAvailability = unavailableResult();
        return cachedAvailability;
      }

      const probeValue = `probe_${Date.now().toString(16)}`;
      await secureStore.setItemAsync(PROBE_KEY, probeValue, SECURE_STORE_OPTIONS);
      const echoed = await secureStore.getItemAsync(PROBE_KEY, SECURE_STORE_OPTIONS);
      await secureStore.deleteItemAsync(PROBE_KEY, SECURE_STORE_OPTIONS);
      if (echoed !== probeValue) {
        cachedAvailability = unavailableResult("Event queue storage probe failed.");
        return cachedAvailability;
      }

      cachedAvailability = {
        ok: true,
        status: "available",
        secureStorageAvailable: true,
      };
      return cachedAvailability;
    } catch (error) {
      cachedAvailability = unavailableResult(String(error?.message || error || ""));
      return cachedAvailability;
    }
  }

  async function loadState() {
    const availability = await validateSecureStore();
    if (!availability.ok) {
      return availability;
    }
    const secureStore = await loadSecureStoreModule(secureStoreModule);
    const raw = await secureStore.getItemAsync(STATE_KEY, SECURE_STORE_OPTIONS);
    if (!raw) {
      return {
        ok: true,
        status: "state_missing",
        secureStorageAvailable: true,
        state: normalizeState(DEFAULT_STATE),
      };
    }
    try {
      return {
        ok: true,
        status: "state_loaded",
        secureStorageAvailable: true,
        state: normalizeState(JSON.parse(raw)),
      };
    } catch (error) {
      return {
        ok: true,
        status: "state_corrupt",
        secureStorageAvailable: true,
        state: normalizeState(DEFAULT_STATE),
        error: String(error?.message || error || ""),
      };
    }
  }

  async function saveState(state) {
    const availability = await validateSecureStore();
    if (!availability.ok) {
      return availability;
    }
    const secureStore = await loadSecureStoreModule(secureStoreModule);
    const normalized = normalizeState(state);
    await secureStore.setItemAsync(
      STATE_KEY,
      JSON.stringify(normalized),
      SECURE_STORE_OPTIONS
    );
    return {
      ok: true,
      status: "state_saved",
      secureStorageAvailable: true,
      state: normalized,
    };
  }

  async function clearStateForTests() {
    const availability = await validateSecureStore();
    if (!availability.ok) {
      return availability;
    }
    const secureStore = await loadSecureStoreModule(secureStoreModule);
    await secureStore.deleteItemAsync(STATE_KEY, SECURE_STORE_OPTIONS);
    return {
      ok: true,
      status: "state_cleared",
      secureStorageAvailable: true,
    };
  }

  return {
    secureStorageAvailable: validateSecureStore,
    loadState,
    saveState,
    clearStateForTests,
  };
}
