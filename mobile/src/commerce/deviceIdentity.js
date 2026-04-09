const INSTALLATION_KEY = "vibesignal.device.installation_id";
const SECURE_STORE_OPTIONS = {
  keychainService: "vibesignal.device.identity",
};
const INSTALLATION_ID_PREFIX = "install_";

async function loadSecureStoreModule(explicitModule) {
  if (explicitModule) {
    return explicitModule;
  }
  return import("expo-secure-store");
}

function createInstallationId() {
  if (globalThis.crypto && typeof globalThis.crypto.randomUUID === "function") {
    return `${INSTALLATION_ID_PREFIX}${globalThis.crypto.randomUUID()}`;
  }
  const randomChunk = Math.random().toString(16).slice(2, 10);
  return `${INSTALLATION_ID_PREFIX}${Date.now().toString(16)}_${randomChunk}`;
}

function blockedStorageResult(error = "") {
  return {
    ok: false,
    status: "secure_storage_unavailable",
    blockedReason: "secure_storage_unavailable",
    secureStorageAvailable: false,
    installationId: "",
    error: String(error || ""),
  };
}

async function loadValidatedSecureStore(explicitModule) {
  const secureStore = await loadSecureStoreModule(explicitModule);
  const supportsAvailability = secureStore && typeof secureStore.isAvailableAsync === "function";
  const supportsGet = secureStore && typeof secureStore.getItemAsync === "function";
  const supportsSet = secureStore && typeof secureStore.setItemAsync === "function";
  const supportsDelete = secureStore && typeof secureStore.deleteItemAsync === "function";

  if (!supportsAvailability || !supportsGet || !supportsSet || !supportsDelete) {
    throw new Error("Secure storage module is missing required methods.");
  }
  return secureStore;
}

function normalizeInstallationId(value) {
  const text = String(value || "").trim();
  if (!text.startsWith(INSTALLATION_ID_PREFIX)) {
    return "";
  }
  return text;
}

export function createDeviceIdentityService({ secureStoreModule } = {}) {
  async function secureStorageAvailable() {
    try {
      const secureStore = await loadValidatedSecureStore(secureStoreModule);
      const available = Boolean(await secureStore.isAvailableAsync());
      return {
        available,
        status: available ? "available" : "secure_storage_unavailable",
      };
    } catch (error) {
      return {
        available: false,
        status: "secure_storage_unavailable",
        error: String(error?.message || error || ""),
      };
    }
  }

  async function getOrCreateInstallationId() {
    const availability = await secureStorageAvailable();
    if (!availability.available) {
      return blockedStorageResult(availability.error || "");
    }
    try {
      const secureStore = await loadValidatedSecureStore(secureStoreModule);
      const existing = normalizeInstallationId(
        await secureStore.getItemAsync(INSTALLATION_KEY, SECURE_STORE_OPTIONS)
      );
      if (existing) {
        return {
          ok: true,
          status: "existing_installation_id",
          secureStorageAvailable: true,
          blockedReason: "",
          installationId: existing,
        };
      }
      const installationId = createInstallationId();
      await secureStore.setItemAsync(INSTALLATION_KEY, installationId, SECURE_STORE_OPTIONS);
      return {
        ok: true,
        status: "installation_id_created",
        secureStorageAvailable: true,
        blockedReason: "",
        installationId,
      };
    } catch (error) {
      return blockedStorageResult(String(error?.message || error || ""));
    }
  }

  async function deleteInstallationId() {
    const availability = await secureStorageAvailable();
    if (!availability.available) {
      return blockedStorageResult(availability.error || "");
    }
    try {
      const secureStore = await loadValidatedSecureStore(secureStoreModule);
      await secureStore.deleteItemAsync(INSTALLATION_KEY, SECURE_STORE_OPTIONS);
      return {
        ok: true,
        status: "installation_id_deleted",
        secureStorageAvailable: true,
        blockedReason: "",
      };
    } catch (error) {
      return blockedStorageResult(String(error?.message || error || ""));
    }
  }

  async function clearInstallationIdForTests() {
    return deleteInstallationId();
  }

  return {
    secureStorageAvailable,
    getOrCreateInstallationId,
    deleteInstallationId,
    clearInstallationIdForTests,
  };
}
