const HISTORY_KEY = "vibesignal.analysis.history.v1";
const SECURE_STORE_OPTIONS = {
  keychainService: "vibesignal.analysis.history",
};
const MAX_HISTORY_ITEMS = 3;

async function loadSecureStoreModule(explicitModule) {
  if (explicitModule) {
    return explicitModule.default ?? explicitModule;
  }
  const module = await import("expo-secure-store");
  return module.default ?? module;
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

function normalizeHistory(items) {
  return Array.isArray(items)
    ? items
        .map((item) => ({
          id: String(item?.id || "").trim(),
          inputText: String(item?.inputText || "").trim(),
          inputPreview: String(item?.inputPreview || "").trim(),
          headline: String(item?.headline || "").trim(),
          pattern: String(item?.pattern || "").trim(),
          summary: String(item?.summary || "").trim(),
          shareText: String(item?.shareText || "").trim(),
          createdAt: String(item?.createdAt || "").trim(),
          result: item?.result && typeof item.result === "object" ? item.result : null,
        }))
        .filter((item) => item.id && item.result)
        .slice(-MAX_HISTORY_ITEMS)
    : [];
}

function safeParse(raw) {
  try {
    return normalizeHistory(JSON.parse(String(raw || "[]")));
  } catch (_error) {
    return [];
  }
}

export function createAnalysisHistoryStore({
  secureStoreModule,
  platform = "",
  webStorage = globalThis.localStorage,
} = {}) {
  async function available() {
    if (canUseWebStorage(platform, webStorage)) {
      try {
        webStorage.setItem(HISTORY_KEY, webStorage.getItem(HISTORY_KEY) || "[]");
        return true;
      } catch (_error) {
        return false;
      }
    }

    try {
      const secureStore = await loadSecureStoreModule(secureStoreModule);
      return Boolean(
        secureStore &&
          typeof secureStore.isAvailableAsync === "function" &&
          typeof secureStore.getItemAsync === "function" &&
          typeof secureStore.setItemAsync === "function" &&
          Boolean(await secureStore.isAvailableAsync())
      );
    } catch (_error) {
      return false;
    }
  }

  async function loadItems() {
    if (canUseWebStorage(platform, webStorage)) {
      return safeParse(webStorage.getItem(HISTORY_KEY));
    }
    const secureStore = await loadSecureStoreModule(secureStoreModule);
    return safeParse(await secureStore.getItemAsync(HISTORY_KEY, SECURE_STORE_OPTIONS));
  }

  async function saveItems(items) {
    const normalized = normalizeHistory(items);
    const serialized = JSON.stringify(normalized);
    if (canUseWebStorage(platform, webStorage)) {
      webStorage.setItem(HISTORY_KEY, serialized);
      return normalized;
    }
    const secureStore = await loadSecureStoreModule(secureStoreModule);
    await secureStore.setItemAsync(HISTORY_KEY, serialized, SECURE_STORE_OPTIONS);
    return normalized;
  }

  return {
    async getRecentAnalyses() {
      if (!(await available())) {
        return [];
      }
      return loadItems();
    },
    async addAnalysis(entry = {}) {
      if (!(await available())) {
        return [];
      }
      const existing = await loadItems();
      const next = [
        ...existing.filter((item) => item.id !== String(entry.id || "").trim()),
        {
          id: String(entry.id || "").trim(),
          inputText: String(entry.inputText || "").trim(),
          inputPreview: String(entry.inputPreview || "").trim(),
          headline: String(entry.headline || "").trim(),
          pattern: String(entry.pattern || "").trim(),
          summary: String(entry.summary || "").trim(),
          shareText: String(entry.shareText || "").trim(),
          createdAt: String(entry.createdAt || new Date().toISOString()).trim(),
          result: entry.result && typeof entry.result === "object" ? entry.result : null,
        },
      ];
      return saveItems(next);
    },
    async clearHistoryForTests() {
      if (canUseWebStorage(platform, webStorage)) {
        webStorage.removeItem(HISTORY_KEY);
        return;
      }
      const secureStore = await loadSecureStoreModule(secureStoreModule);
      await secureStore.deleteItemAsync(HISTORY_KEY, SECURE_STORE_OPTIONS);
    },
  };
}
