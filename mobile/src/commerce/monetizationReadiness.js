import {
  IOS_MONTHLY_PRODUCT_ID,
  IOS_PREMIUM_ENTITLEMENT_ID,
  IOS_REVENUECAT_API_KEY,
  STORE_METADATA,
} from "./config.js";

function nonEmpty(value) {
  return String(value || "").trim();
}

export function getMonetizationReadiness() {
  const warnings = [];
  const errors = [];

  const revenueCatKeyConfigured = Boolean(nonEmpty(IOS_REVENUECAT_API_KEY));
  const productIdConfigured = Boolean(nonEmpty(IOS_MONTHLY_PRODUCT_ID));
  const entitlementConfigured = Boolean(nonEmpty(IOS_PREMIUM_ENTITLEMENT_ID));
  const privacyPolicyConfigured = Boolean(nonEmpty(STORE_METADATA.privacyPolicyUrl));
  const termsConfigured = Boolean(nonEmpty(STORE_METADATA.termsUrl));

  if (!revenueCatKeyConfigured) {
    errors.push("missing_revenuecat_api_key");
  }
  if (!productIdConfigured) {
    errors.push("missing_ios_product_id");
  }
  if (!entitlementConfigured) {
    errors.push("missing_ios_entitlement_id");
  }
  if (!privacyPolicyConfigured) {
    warnings.push("missing_privacy_policy_url");
  }
  if (!termsConfigured) {
    warnings.push("missing_terms_url");
  }

  return {
    ok: errors.length === 0,
    purchaseReady: errors.length === 0,
    restoreReady: revenueCatKeyConfigured,
    revenueCatKeyConfigured,
    productIdConfigured,
    entitlementConfigured,
    privacyPolicyConfigured,
    termsConfigured,
    warnings,
    errors,
  };
}
