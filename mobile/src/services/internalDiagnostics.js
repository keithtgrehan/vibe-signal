const DEFAULT_LIMIT = 100;

function normalizeSeverity(value) {
  const text = String(value || "").trim().toLowerCase();
  if (["info", "warn", "error"].includes(text)) {
    return text;
  }
  return "warn";
}

function normalizeEntry(entry = {}, nowProvider = () => Date.now()) {
  return {
    category: String(entry.category || "general").trim() || "general",
    code: String(entry.code || "unspecified").trim() || "unspecified",
    message: String(entry.message || "").trim(),
    severity: normalizeSeverity(entry.severity),
    details: entry.details && typeof entry.details === "object" ? { ...entry.details } : {},
    timestamp: Number(entry.timestamp || nowProvider()),
  };
}

export function createInternalDiagnosticsStore({
  limit = DEFAULT_LIMIT,
  nowProvider = () => Date.now(),
  logger = console,
} = {}) {
  let entries = [];

  function capture(entry = {}) {
    const normalized = normalizeEntry(entry, nowProvider);
    entries = [...entries, normalized].slice(-Math.max(1, Number(limit || DEFAULT_LIMIT)));
    const logMethod =
      normalized.severity === "error"
        ? logger?.error
        : normalized.severity === "info"
        ? logger?.info
        : logger?.warn;
    if (typeof logMethod === "function") {
      try {
        logMethod(`[vibesignal:${normalized.category}:${normalized.code}] ${normalized.message}`);
      } catch (_error) {
        // Diagnostics must never throw into app flows.
      }
    }
    return normalized;
  }

  function list() {
    return entries.map((entry) => ({
      ...entry,
      details: { ...entry.details },
    }));
  }

  function clearForTests() {
    entries = [];
  }

  return {
    capture,
    list,
    clearForTests,
  };
}

let sharedDiagnosticsStore = null;

export function getSharedInternalDiagnosticsStore() {
  if (!sharedDiagnosticsStore) {
    sharedDiagnosticsStore = createInternalDiagnosticsStore();
  }
  return sharedDiagnosticsStore;
}
