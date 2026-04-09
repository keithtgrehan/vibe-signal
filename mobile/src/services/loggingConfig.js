function parseEnabled(value) {
  const text = String(value ?? "").trim().toLowerCase();
  if (!text) {
    return false;
  }
  return text === "1" || text === "true" || text === "yes" || text === "on";
}

function parseHttpUrl(value) {
  const text = String(value || "").trim();
  if (!text) {
    return {
      value: "",
      valid: false,
    };
  }
  try {
    const parsed = new URL(text);
    const valid = parsed.protocol === "http:" || parsed.protocol === "https:";
    return {
      value: valid ? parsed.toString().replace(/\/$/, "") : text,
      valid,
    };
  } catch (_error) {
    return {
      value: text,
      valid: false,
    };
  }
}

export function getLoggingConfig() {
  const enabled = parseEnabled(process.env.EXPO_PUBLIC_ENABLE_LOGGING);
  const parsedApiUrl = parseHttpUrl(process.env.EXPO_PUBLIC_API_URL || "");
  const warnings = [];
  if (enabled && !parsedApiUrl.value) {
    warnings.push("logging_enabled_without_api_url");
  }
  if (enabled && parsedApiUrl.value && !parsedApiUrl.valid) {
    warnings.push("logging_api_url_invalid");
  }
  return {
    apiUrl: parsedApiUrl.valid ? parsedApiUrl.value : "",
    rawApiUrl: parsedApiUrl.value,
    enabled,
    appVersion: String(process.env.EXPO_PUBLIC_APP_VERSION || "").trim(),
    warnings,
    ready: enabled && parsedApiUrl.valid,
  };
}
