const SUPPORTED_PROVIDERS = ["openai", "anthropic", "groq"];
const KEY_PREFIX = "vibesignal.provider";
const PROBE_KEY = `${KEY_PREFIX}.availability_probe`;
const SECURE_STORE_OPTIONS = {
  keychainService: "vibesignal.provider.credentials",
};
const WEB_STORAGE_PREFIX = "vibesignal.provider.web";
const WEB_PROBE_KEY = `${WEB_STORAGE_PREFIX}.availability_probe`;

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

function webCredentialKey(provider) {
  return `${WEB_STORAGE_PREFIX}.${normalizeProvider(provider)}`;
}

function canUseWebStorage(platform, webStorage) {
  return (
    platform === "web" &&
    webStorage &&
    typeof webStorage.getItem === "function" &&
    typeof webStorage.setItem === "function" &&
    typeof webStorage.removeItem === "function"
  );
}

function probeWebStorage(webStorage) {
  const probeValue = `probe_${Date.now().toString(16)}`;
  webStorage.setItem(WEB_PROBE_KEY, probeValue);
  const storedValue = webStorage.getItem(WEB_PROBE_KEY);
  webStorage.removeItem(WEB_PROBE_KEY);
  if (storedValue !== probeValue) {
    throw new Error("Web storage probe did not round-trip successfully.");
  }
}

export function createProviderSecureStore({
  secureStoreModule,
  platform = "",
  webStorage = globalThis.localStorage,
} = {}) {
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
    if (canUseWebStorage(platform, webStorage)) {
      try {
        probeWebStorage(webStorage);
        cachedAvailability = {
          available: true,
          status: "available",
          storageType: "web_local_storage",
        };
      } catch (error) {
        cachedAvailability = {
          available: false,
          status: "secure_storage_unavailable",
          error: String(error?.message || error || ""),
        };
      }
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
    if (availability.storageType === "web_local_storage") {
      try {
        webStorage.setItem(webCredentialKey(provider), normalizedCredential);
        return {
          ok: true,
          status: "credential_saved",
          provider: normalizeProvider(provider),
          secureStorageAvailable: true,
          credentialPresent: true,
        };
      } catch (error) {
        return {
          ok: false,
          status: "credential_save_blocked",
          reason: "secure_storage_unavailable",
          provider: normalizeProvider(provider),
          secureStorageAvailable: false,
          credentialPresent: false,
          error: String(error?.message || error || ""),
        };
      }
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
    if (availability.storageType === "web_local_storage") {
      try {
        const credential = webStorage.getItem(webCredentialKey(provider));
        return {
          ok: true,
          status: credential ? "credential_loaded" : "provider_enabled_no_credential",
          provider: normalizeProvider(provider),
          secureStorageAvailable: true,
          credentialPresent: Boolean(credential),
          credential: credential || null,
        };
      } catch (error) {
        return {
          ok: false,
          status: "secure_storage_unavailable",
          provider: normalizeProvider(provider),
          secureStorageAvailable: false,
          credentialPresent: false,
          credential: null,
          error: String(error?.message || error || ""),
        };
      }
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
    if (availability.storageType === "web_local_storage") {
      try {
        webStorage.removeItem(webCredentialKey(provider));
        return {
          ok: true,
          status: "credential_deleted",
          provider: normalizeProvider(provider),
          secureStorageAvailable: true,
          credentialPresent: false,
        };
      } catch (error) {
        return {
          ok: false,
          status: "secure_storage_unavailable",
          provider: normalizeProvider(provider),
          secureStorageAvailable: false,
          credentialPresent: false,
          error: String(error?.message || error || ""),
        };
      }
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
    if (availability.storageType === "web_local_storage") {
      try {
        for (const provider of SUPPORTED_PROVIDERS) {
          webStorage.removeItem(webCredentialKey(provider));
        }
        return {
          ok: true,
          status: "credentials_cleared",
          secureStorageAvailable: true,
          clearedProviders: [...SUPPORTED_PROVIDERS],
        };
      } catch (error) {
        return {
          ok: false,
          status: "secure_storage_unavailable",
          secureStorageAvailable: false,
          clearedProviders: [],
          error: String(error?.message || error || ""),
        };
      }
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
