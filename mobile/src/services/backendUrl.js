function normalizeText(value) {
  return String(value || "").trim();
}

export function parseBackendBaseUrl(value) {
  const text = normalizeText(value);
  if (!text) {
    return {
      ok: false,
      status: "missing_api_url",
      apiUrl: "",
    };
  }

  try {
    const parsed = new URL(text);
    const hasUnsafeParts =
      parsed.username ||
      parsed.password ||
      parsed.search ||
      parsed.hash ||
      (parsed.pathname && parsed.pathname !== "/");
    if (!["http:", "https:"].includes(parsed.protocol) || hasUnsafeParts) {
      return {
        ok: false,
        status: "invalid_api_url",
        apiUrl: "",
      };
    }

    return {
      ok: true,
      status: "api_url_ready",
      apiUrl: parsed.origin,
      host: parsed.host,
    };
  } catch (_error) {
    return {
      ok: false,
      status: "invalid_api_url",
      apiUrl: "",
    };
  }
}

export function formatBackendUrlStatus(value) {
  const parsed = parseBackendBaseUrl(value);
  if (parsed.ok) {
    return `Backend configured: ${parsed.host}`;
  }
  if (parsed.status === "missing_api_url") {
    return "Set EXPO_PUBLIC_API_URL to use the backend.";
  }
  return "Configured backend URL must be a clean http(s) base URL.";
}
