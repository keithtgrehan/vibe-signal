export function maskProviderCredential(credential) {
  const normalized = String(credential || "").trim();
  if (!normalized) {
    return "";
  }
  return `••••${normalized.slice(-4)}`;
}

export function formatSavedCredentialLabel(credential) {
  const masked = maskProviderCredential(credential);
  return masked ? `Saved key ending in ${masked}` : "No key saved yet.";
}

export function buildProviderActionState({
  busy = false,
  selectedProvider = "",
  draftCredential = "",
  credentialPresent = false,
  consentAcknowledged = false,
  validationStatus = "",
} = {}) {
  const hasProvider = Boolean(String(selectedProvider || "").trim());
  const normalizedDraftCredential = String(draftCredential || "").trim();
  const hasDraftCredential = Boolean(normalizedDraftCredential);
  const credentialLongEnough = normalizedDraftCredential.length > 10;
  return {
    disableSave: busy || !hasProvider || !hasDraftCredential,
    disableRemove: busy || !hasProvider || !credentialPresent,
    disableValidate: busy || !hasProvider || !credentialLongEnough,
    disableRun: busy || !hasProvider || !credentialPresent || !consentAcknowledged || validationStatus !== "ready",
    showRemove: hasProvider && credentialPresent,
    showReplace: hasProvider && credentialPresent,
  };
}

export function deriveProviderFlowState({
  selectedProvider = "",
  draftCredential = "",
  busy = false,
  pendingAction = "",
  credentialPresent = false,
  validationStatus = "",
} = {}) {
  if (!String(selectedProvider || "").trim()) {
    return "no_provider";
  }
  if (busy && pendingAction === "verify") {
    return "verifying";
  }
  if (validationStatus === "ready" && credentialPresent) {
    return "verified";
  }
  if (
    [
      "invalid_credentials",
      "network_error",
      "provider_timeout",
      "rate_limited",
      "provider_unavailable",
      "unknown_error",
      "secure_storage_unavailable",
    ].includes(validationStatus)
  ) {
    return "failed";
  }
  if (String(draftCredential || "").trim()) {
    return "key_entered";
  }
  return "provider_selected";
}

export function buildProviderReadinessCopy({
  storageResolved = false,
  credentialPresent = false,
  validationStatus = "",
  validationMessage = "",
  saveMessage = "",
} = {}) {
  if (saveMessage) {
    return saveMessage;
  }
  if (validationStatus === "ready" || credentialPresent) {
    return "Ready to use";
  }
  if (validationStatus === "missing_credentials") {
    return "No key saved yet";
  }
  if (validationStatus === "secure_storage_unavailable") {
    return "Couldn't save key — try again";
  }
  if (validationStatus && validationMessage) {
    return validationMessage;
  }
  if (storageResolved) {
    return "No key saved yet";
  }
  return "";
}

export function buildProviderVerificationModel({
  selectedProvider = "",
  draftCredential = "",
  credentialPresent = false,
  validationStatus = "",
  validationMessage = "",
  saveMessage = "",
  busy = false,
  pendingAction = "",
} = {}) {
  const flowState = deriveProviderFlowState({
    selectedProvider,
    draftCredential,
    busy,
    pendingAction,
    credentialPresent,
    validationStatus,
  });

  if (flowState === "no_provider") {
    return {
      title: "Choose a provider",
      body: "Local analysis stays primary. External summaries are optional and only run when you enable a provider.",
      helper: "",
      tone: "neutral",
      flowState,
    };
  }

  if (flowState === "verifying") {
    return {
      title: "Checking key...",
      body: "This only checks whether the key works for this provider.",
      helper: "",
      tone: "neutral",
      flowState,
    };
  }

  if (saveMessage && validationStatus !== "ready") {
    return {
      title: "Couldn't save key",
      body: saveMessage,
      helper: "",
      tone: "warning",
      flowState,
    };
  }

  if (flowState === "verified") {
    return {
      title: "Key verified",
      body: "External summaries are now available for this provider.",
      helper: validationMessage || "Key verified and saved",
      tone: "success",
      flowState,
    };
  }

  if (validationStatus === "invalid_credentials") {
    return {
      title: "Couldn't verify key",
      body: "Check the key and try again.",
      helper: validationMessage,
      tone: "warning",
      flowState,
    };
  }

  if (
    ["provider_timeout", "rate_limited", "provider_unavailable", "unknown_error"].includes(
      validationStatus
    )
  ) {
    return {
      title: "Couldn't reach provider",
      body: "Your local analysis still works. Try again in a moment.",
      helper: validationMessage,
      tone: "warning",
      flowState,
    };
  }

  if (validationStatus === "consent_required") {
    return {
      title: "Confirm consent first",
      body: "You must confirm provider consent before external summaries can run.",
      helper: "",
      tone: "neutral",
      flowState,
    };
  }

  if (credentialPresent) {
    return {
      title: "Verify key to enable external summaries",
      body: "The key is saved on this device, but external summaries stay off until verification succeeds.",
      helper: "",
      tone: "neutral",
      flowState,
    };
  }

  return {
    title: "No key saved yet",
    body: "Paste your provider API key to verify it for this provider. Local analysis still stays primary.",
    helper: "",
    tone: "neutral",
    flowState,
  };
}
