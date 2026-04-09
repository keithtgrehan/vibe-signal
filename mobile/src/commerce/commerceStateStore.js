const STATE_KEY = "vibesignal.commerce.state.v1";
const PROBE_KEY = "vibesignal.commerce.state.probe";
const SECURE_STORE_OPTIONS = {
  keychainService: "vibesignal.commerce.state",
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

export function createCommerceStateStore({ secureStoreModule } = {}) {
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
        cachedAvailability = unavailableResult("Commerce state storage probe failed.");
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
        state: null,
      };
    }
    try {
      return {
        ok: true,
        status: "state_loaded",
        secureStorageAvailable: true,
        state: JSON.parse(raw),
      };
    } catch (error) {
      return {
        ok: true,
        status: "state_corrupt",
        secureStorageAvailable: true,
        state: null,
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
    await secureStore.setItemAsync(
      STATE_KEY,
      JSON.stringify(state || {}),
      SECURE_STORE_OPTIONS
    );
    return {
      ok: true,
      status: "state_saved",
      secureStorageAvailable: true,
      state,
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
