function normalizeStatusMessage({
  monetization,
  purchaseResult,
  restoreResult,
  isBootstrapping = false,
} = {}) {
  if (isBootstrapping) {
    return "";
  }
  if (purchaseResult) {
    if (purchaseResult.status === "purchase_cancelled") {
      return "The App Store purchase was cancelled.";
    }
    if (purchaseResult.ok && purchaseResult.entitlementConfirmed) {
      return "Premium is now active on this device.";
    }
    if (purchaseResult.status === "billing_unavailable") {
      return "Premium purchases aren't configured in this build yet.";
    }
    if (purchaseResult.status === "product_unavailable") {
      return "The premium subscription isn't available right now.";
    }
    return "The premium purchase couldn't be completed right now.";
  }

  if (restoreResult) {
    if (restoreResult.ok && restoreResult.entitlementConfirmed) {
      return "Purchases restored successfully.";
    }
    if (restoreResult.status === "restore_no_active_entitlement") {
      return "No active premium subscription was found to restore.";
    }
    return "Restore couldn't be completed right now.";
  }

  if (!monetization) {
    return "";
  }

  if (monetization.secureStorageAvailable === false) {
    return "Secure storage is unavailable on this device.";
  }
  if (monetization.premiumState?.status === "premium_cached") {
    return "Premium is active. Subscription status will refresh again when the connection improves.";
  }
  if (monetization.productCatalog?.status === "billing_unavailable") {
    return "Premium purchases aren't configured in this build yet.";
  }
  if (monetization.productCatalog && monetization.productCatalog.usesFallback) {
    return "Using the current fallback price until App Store product details load.";
  }
  return "";
}

export function buildQuotaHookState({
  monetization = null,
  loading = true,
  action = "",
  purchaseResult = null,
  restoreResult = null,
} = {}) {
  const premiumActive = Boolean(monetization?.premiumActive);
  const isBootstrapping = Boolean(loading || monetization?.is_bootstrapping);
  const quota = monetization?.quota || {};
  const quotaView = monetization?.quotaView || {};
  const paywall = monetization?.paywall || {};
  const product = monetization?.product || {};
  const productCatalog = monetization?.productCatalog || {};
  const storeMetadata = monetization?.storeMetadata || {};
  const monetizationReadiness = storeMetadata.monetizationReadiness || {};
  const premiumProductAvailable = Boolean(product.productId) && product.is_valid === true;

  return {
    loading,
    hydrating: loading,
    is_bootstrapping: isBootstrapping,
    premium_active: premiumActive,
    current_period_type: quota.current_period_type || "",
    remaining_uses: premiumActive
      ? Number.POSITIVE_INFINITY
      : Math.max(0, Number(quota.remaining_uses || 0)),
    uses_in_current_period: quota.uses_in_current_period || 0,
    paywall_required: isBootstrapping ? false : Boolean(paywall.visible),
    reset_timing: quotaView.resetTiming || "",
    reset_at: quotaView.resetAt || "",
    period_label: quotaView.periodLabel || "",
    uses_left_label: quotaView.usesLeft || "",
    price_display: product.priceDisplay || "",
    product_id: product.productId || "",
    premium_product_available: premiumProductAvailable,
    purchase_available:
      premiumProductAvailable && monetizationReadiness.purchaseReady !== false,
    premium_active_label: premiumActive ? "Premium active" : "Free plan",
    restore_available: paywall.restoreAvailable !== false,
    catalog_uses_fallback: Boolean(productCatalog.usesFallback),
    product_status: String(productCatalog.status || "").trim(),
    privacy_policy_url: storeMetadata.privacyPolicyUrl || "",
    terms_url: storeMetadata.termsUrl || "",
    support_contact_ref: storeMetadata.supportContactRef || "",
    subscription_disclosure: {
      ...(storeMetadata.subscriptionDisclosure || {}),
    },
    legal_links_configured:
      Boolean(storeMetadata.privacyPolicyUrl) && Boolean(storeMetadata.termsUrl),
    purchase_in_progress: action === "purchase",
    restore_in_progress: action === "restore",
    refresh_in_progress: action === "refresh",
    usage_in_progress: action === "analysis",
    status_message: normalizeStatusMessage({
      monetization,
      purchaseResult,
      restoreResult,
      isBootstrapping,
    }),
  };
}
