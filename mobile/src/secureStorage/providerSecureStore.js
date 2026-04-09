const SUPPORTED_PROVIDERS = ["openai", "anthropic", "groq"];
const KEY_PREFIX = "vibesignal.provider";
const PROBE_KEY = `${KEY_PREFIX}.availability_probe`;
const SECURE_STORE_OPTIONS = {
  keychainService: "vibesignal.provider.credentials",
};

function normalizeProvider(provider) {
  return String(provider || "").trim().toLowerCase();
}

function credentialKey(provider) {
  const normalized = normalizeProvider(provider);
  if (!SUPPORTED_PROVIDERS.includes(normalized)) {
    throw new Error(`Unsupported provider: ${provider}`);
  }
  return `${KEY_PREFIX}.${normalized}`;
}

async function loadSecureStoreModule(explicitModule) {
  if (explicitModule) {
    return explicitModule.default ?? explicitModule;
  }
  const module = await import("expo-secure-store");
  return module.default ?? module;
}

export function createProviderSecureStore({ secureStoreModule } = {}) {
  let cachedAvailability = null;

  async function probeSecureStorage(secureStore) {
    const probeValue = `probe_${Date.now().toString(16)}`;
    await secureStore.setItemAsync(PROBE_KEY, probeValue, SECURE_STORE_OPTIONS);
    const storedValue = await secureStore.getItemAsync(PROBE_KEY, SECURE_STORE_OPTIONS);
    await secureStore.deleteItemAsync(PROBE_KEY, SECURE_STORE_OPTIONS);
    if (storedValue !== probeValue) {
      throw new Error("Secure storage probe did not round-trip successfully.");
    }
  }

  async function availabilityResult() {
    if (cachedAvailability) {
      return cachedAvailability;
    }
    try {
      const secureStore = await loadSecureStoreModule(secureStoreModule);
      const hasAvailabilityCheck =
        secureStore && typeof secureStore.isAvailableAsync === "function";
      const hasReadWriteSurface =
        secureStore &&
        typeof secureStore.setItemAsync === "function" &&
        typeof secureStore.getItemAsync === "function" &&
        typeof secureStore.deleteItemAsync === "function";

      const available = Boolean(
        hasAvailabilityCheck && hasReadWriteSurface
          ? await secureStore.isAvailableAsync()
          : false
      );

      if (available) {
        await probeSecureStorage(secureStore);
      }

      cachedAvailability = {
        available,
        status: available ? "available" : "secure_storage_unavailable",
      };
      return cachedAvailability;
    } catch (error) {
      cachedAvailability = {
        available: false,
        status: "secure_storage_unavailable",
        error: String(error?.message || error || ""),
      };
      return cachedAvailability;
    }
  }

  async function secureStorageAvailable() {
    return availabilityResult();
  }

  async function saveProviderCredential(provider, credential) {
    const availability = await availabilityResult();
    if (!availability.available) {
      return {
        ok: false,
        status: "credential_save_blocked",
        reason: "secure_storage_unavailable",
        provider: normalizeProvider(provider),
        secureStorageAvailable: false,
        credentialPresent: false,
      };
    }
    const normalizedCredential = String(credential || "").trim();
    if (!normalizedCredential) {
      return {
        ok: false,
        status: "credential_save_blocked",
        reason: "missing_credential",
        provider: normalizeProvider(provider),
        secureStorageAvailable: true,
        credentialPresent: false,
      };
    }
    const secureStore = await loadSecureStoreModule(secureStoreModule);
    await secureStore.setItemAsync(
      credentialKey(provider),
      normalizedCredential,
      SECURE_STORE_OPTIONS
    );
    return {
      ok: true,
      status: "credential_saved",
      provider: normalizeProvider(provider),
      secureStorageAvailable: true,
      credentialPresent: true,
    };
  }

  async function getProviderCredential(provider) {
    const availability = await availabilityResult();
    if (!availability.available) {
      return {
        ok: false,
        status: "secure_storage_unavailable",
        provider: normalizeProvider(provider),
        secureStorageAvailable: false,
        credentialPresent: false,
        credential: null,
      };
    }
    const secureStore = await loadSecureStoreModule(secureStoreModule);
    const credential = await secureStore.getItemAsync(credentialKey(provider), SECURE_STORE_OPTIONS);
    return {
      ok: true,
      status: credential ? "credential_loaded" : "provider_enabled_no_credential",
      provider: normalizeProvider(provider),
      secureStorageAvailable: true,
      credentialPresent: Boolean(credential),
      credential: credential || null,
    };
  }

  async function deleteProviderCredential(provider) {
    const availability = await availabilityResult();
    if (!availability.available) {
      return {
        ok: false,
        status: "secure_storage_unavailable",
        provider: normalizeProvider(provider),
        secureStorageAvailable: false,
        credentialPresent: false,
      };
    }
    const secureStore = await loadSecureStoreModule(secureStoreModule);
    await secureStore.deleteItemAsync(credentialKey(provider), SECURE_STORE_OPTIONS);
    return {
      ok: true,
      status: "credential_deleted",
      provider: normalizeProvider(provider),
      secureStorageAvailable: true,
      credentialPresent: false,
    };
  }

  async function clearAllProviderCredentials() {
    const availability = await availabilityResult();
    if (!availability.available) {
      return {
        ok: false,
        status: "secure_storage_unavailable",
        secureStorageAvailable: false,
        clearedProviders: [],
      };
    }
    const secureStore = await loadSecureStoreModule(secureStoreModule);
    for (const provider of SUPPORTED_PROVIDERS) {
      await secureStore.deleteItemAsync(credentialKey(provider), SECURE_STORE_OPTIONS);
    }
    return {
      ok: true,
      status: "credentials_cleared",
      secureStorageAvailable: true,
      clearedProviders: [...SUPPORTED_PROVIDERS],
    };
  }

  return {
    supportedProviders: [...SUPPORTED_PROVIDERS],
    secureStorageAvailable,
    saveProviderCredential,
    getProviderCredential,
    deleteProviderCredential,
    clearAllProviderCredentials,
  };
}

export { SUPPORTED_PROVIDERS };
