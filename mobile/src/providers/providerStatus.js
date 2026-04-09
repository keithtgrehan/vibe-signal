const STATUS_COPY = {
  local_only: {
    statusLabel: "Local-only default",
    statusMessage:
      "Local deterministic analysis is active and no external provider will be called.",
  },
  provider_disabled: {
    statusLabel: "Provider disabled",
    statusMessage: "This provider path is off, so summaries stay local-only.",
  },
  provider_not_configured: {
    statusLabel: "Provider not configured",
    statusMessage:
      "This provider path is enabled in concept, but the provider details are not fully configured yet.",
  },
  secure_storage_unavailable: {
    statusLabel: "Secure storage unavailable",
    statusMessage:
      "Secure on-device storage is required before a BYOK credential can be saved for this provider.",
  },
  provider_enabled_no_credential: {
    statusLabel: "Credential needed",
    statusMessage:
      "Secure storage is available, but no provider credential is currently stored on-device.",
  },
  provider_ready: {
    statusLabel: "Provider ready",
    statusMessage:
      "This provider can be requested explicitly, while local analysis still remains the default path.",
  },
  provider_error: {
    statusLabel: "Provider error",
    statusMessage:
      "The provider path hit an error and no external summary should be treated as available.",
  },
};

export function determineProviderStatus({
  providerMode = "local_only",
  providerName = "none",
  enabled = false,
  authMode = "disabled",
  secureStorageAvailable = false,
  credentialPresent = false,
  errorMessage = "",
} = {}) {
  const normalizedMode = String(providerMode || "local_only").trim() || "local_only";
  const normalizedName = String(providerName || "none").trim().toLowerCase() || "none";
  const normalizedAuth = String(authMode || "disabled").trim() || "disabled";

  if (errorMessage) {
    return "provider_error";
  }
  if (normalizedMode === "local_only") {
    return "local_only";
  }
  if (normalizedMode === "provider_disabled" || !enabled || normalizedAuth === "disabled") {
    return "provider_disabled";
  }
  if (normalizedName === "none") {
    return "provider_not_configured";
  }
  if (normalizedAuth === "byok" && !secureStorageAvailable) {
    return "secure_storage_unavailable";
  }
  if (normalizedAuth === "byok" && !credentialPresent) {
    return "provider_enabled_no_credential";
  }
  if (normalizedAuth === "byok" || normalizedAuth === "backend_proxy") {
    return "provider_ready";
  }
  return "provider_not_configured";
}

export function buildProviderStatusPayload({
  providerName,
  displayName,
  enabled,
  authMode,
  providerMode = "local_only",
  modelName = "",
  secureStorageAvailable = false,
  credentialPresent = false,
  requiresSecureStorage = authMode === "byok",
  localFirstDefault = true,
  externalProcessingUsed = false,
  errorMessage = "",
  statusOverride = "",
} = {}) {
  const status =
    String(statusOverride || "").trim() ||
    determineProviderStatus({
      providerMode,
      providerName,
      enabled,
      authMode,
      secureStorageAvailable,
      credentialPresent,
    });
  const copy = STATUS_COPY[status] || STATUS_COPY.provider_not_configured;
  return {
    provider_name: String(providerName || "none").trim().toLowerCase() || "none",
    display_name: String(displayName || providerName || "Provider").trim() || "Provider",
    enabled: Boolean(enabled),
    auth_mode: String(authMode || "disabled").trim() || "disabled",
    status,
    status_label: copy.statusLabel,
    status_message: String(errorMessage || copy.statusMessage).trim() || copy.statusMessage,
    secure_storage_available: Boolean(secureStorageAvailable),
    credential_present: Boolean(credentialPresent),
    requires_secure_storage: Boolean(requiresSecureStorage),
    local_first_default: Boolean(localFirstDefault),
    external_processing_used: Boolean(externalProcessingUsed),
    model_name: String(modelName || "").trim(),
    can_request_summary: status === "provider_ready",
    safe_to_render: true,
  };
}
