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
  const hasDraftCredential = Boolean(String(draftCredential || "").trim());
  const credentialReadyForValidation = hasDraftCredential || credentialPresent;
  return {
    disableSave: busy || !hasProvider || !hasDraftCredential,
    disableRemove: busy || !hasProvider || !credentialPresent,
    disableValidate: busy || !hasProvider || !credentialReadyForValidation,
    disableRun: busy || !hasProvider || !credentialPresent || !consentAcknowledged || validationStatus !== "ready",
    showRemove: hasProvider && credentialPresent,
  };
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
  credentialPresent = false,
  validationStatus = "",
  validationMessage = "",
  saveMessage = "",
  busy = false,
  pendingAction = "",
} = {}) {
  const hasProvider = Boolean(String(selectedProvider || "").trim());
  const isVerifying = busy && pendingAction === "verify";

  if (!hasProvider) {
    return {
      title: "Choose a provider",
      body: "Local analysis stays primary. External summaries are optional and only run when you enable a provider.",
      helper: "",
      tone: "neutral",
    };
  }

  if (isVerifying) {
    return {
      title: "Checking key...",
      body: "This only checks whether the key works for this provider.",
      helper: "",
      tone: "neutral",
    };
  }

  if (saveMessage) {
    return {
      title: "Couldn't save key",
      body: saveMessage,
      helper: "",
      tone: "warning",
    };
  }

  if (validationStatus === "ready" && credentialPresent) {
    return {
      title: "Key verified",
      body: "External summaries are now available for this provider.",
      helper: "",
      tone: "success",
    };
  }

  if (validationStatus === "invalid_credentials") {
    return {
      title: "Couldn't verify key",
      body: "Check the key and try again.",
      helper: validationMessage,
      tone: "warning",
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
    };
  }

  if (validationStatus === "consent_required") {
    return {
      title: "Confirm consent first",
      body: "You must confirm provider consent before external summaries can run.",
      helper: "",
      tone: "neutral",
    };
  }

  if (credentialPresent) {
    return {
      title: "Verify key to enable external summaries",
      body: "The key is saved on this device, but external summaries stay off until verification succeeds.",
      helper: "",
      tone: "neutral",
    };
  }

  return {
    title: "No key saved yet",
    body: "Paste your provider API key to verify it for this provider. Local analysis still stays primary.",
    helper: "",
    tone: "neutral",
  };
}
