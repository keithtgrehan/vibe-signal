function isSafeExternalUrl(value) {
  const text = String(value || "").trim();
  if (!text) {
    return false;
  }
  try {
    const parsed = new URL(text);
    return parsed.protocol === "https:";
  } catch (_error) {
    return false;
  }
}

export function buildPaywallViewModel({
  premiumActive = false,
  softPrompt = false,
  priceDisplay = "",
  purchaseAvailable = false,
  restoreAvailable = true,
  storeMetadata = {},
  statusMessage = "",
} = {}) {
  const disclosure = storeMetadata.subscriptionDisclosure || {};
  const effectivePrice = String(priceDisplay || disclosure.priceDisplay || "").trim();
  const privacyPolicyUrl = String(storeMetadata.privacyPolicyUrl || "").trim();
  const termsUrl = String(storeMetadata.termsUrl || "").trim();

  return {
    title: premiumActive
      ? "Premium unlocked"
      : softPrompt
      ? "Unlock deeper pattern detection"
      : "Keep reading the full signal",
    body: premiumActive
      ? "Unlimited analyses are active on this device."
      : softPrompt
      ? "You've started spotting the shift. Premium keeps local analysis available without weekly limits and makes repeat checks feel instant."
      : "Free usage is exhausted for the current period. Premium keeps local analysis available without weekly limits and unlocks a smoother repeat-use loop.",
    priceDisplay: effectivePrice,
    purchaseEnabled: !premiumActive && purchaseAvailable,
    restoreEnabled: Boolean(restoreAvailable),
    disclosureLines: premiumActive
      ? []
      : [
          disclosure.planName || "VibeSignal Pro Monthly",
          disclosure.billingFrequency || "Monthly subscription",
          effectivePrice
            ? `${effectivePrice} · Auto-renewing subscription`
            : "Price unavailable until App Store product metadata is available.",
          disclosure.cancellationInfo || "Cancel anytime in your Apple account subscription settings.",
        ],
    legalLinks: [
      isSafeExternalUrl(privacyPolicyUrl) ? { label: "Privacy Policy", url: privacyPolicyUrl } : null,
      isSafeExternalUrl(termsUrl) ? { label: "Terms of Service", url: termsUrl } : null,
    ].filter(Boolean),
    legalLinksConfigured: isSafeExternalUrl(privacyPolicyUrl) && isSafeExternalUrl(termsUrl),
    legalLinksMessage:
      isSafeExternalUrl(privacyPolicyUrl) && isSafeExternalUrl(termsUrl)
        ? ""
        : "Privacy Policy and Terms links must be configured with secure HTTPS URLs before App Store submission.",
    statusMessage: String(statusMessage || "").trim(),
  };
}
