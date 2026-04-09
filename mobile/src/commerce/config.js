function readEnv(name, fallback = "") {
  const value = String(process.env[name] || "").trim();
  return value || fallback;
}

export const TRIAL_WEEK_FREE_USES = 10;
export const WEEKLY_FREE_USES = 5;
export const TRIAL_PERIOD_DAYS = 7;
export const WEEKLY_PERIOD_DAYS = 7;
export const SUBSCRIPTION_REQUIRED_AFTER_LIMIT = true;
export const SUBSCRIPTION_PRICE_DISPLAY = readEnv("EXPO_PUBLIC_SUBSCRIPTION_PRICE_DISPLAY", "€1.89/month");
export const IOS_MONTHLY_PRODUCT_ID = readEnv("EXPO_PUBLIC_IOS_MONTHLY_PRODUCT_ID", "vibesignal_pro_monthly_ios");
export const ANDROID_MONTHLY_PRODUCT_ID = readEnv(
  "EXPO_PUBLIC_ANDROID_MONTHLY_PRODUCT_ID",
  "vibesignal_pro_monthly_android"
);
export const IOS_PREMIUM_ENTITLEMENT_ID = readEnv(
  "EXPO_PUBLIC_IOS_PREMIUM_ENTITLEMENT_ID",
  "vibesignal_pro"
);
export const IOS_REVENUECAT_API_KEY = readEnv("EXPO_PUBLIC_REVENUECAT_IOS_API_KEY", "");
export const ENTITLEMENT_CACHE_GRACE_HOURS = 72;
export const FREE_ANALYSIS_LIMIT = TRIAL_WEEK_FREE_USES;

export const BILLING_PRODUCTS = [
  {
    productId: IOS_MONTHLY_PRODUCT_ID,
    platform: "ios",
    displayName: "VibeSignal Pro Monthly",
    priceDisplay: SUBSCRIPTION_PRICE_DISPLAY,
    billingPeriod: "P1M",
    productType: "auto_renewing_subscription",
    billingProvider: "revenuecat_app_store",
    entitlementId: IOS_PREMIUM_ENTITLEMENT_ID,
    is_valid: false,
  },
  {
    productId: ANDROID_MONTHLY_PRODUCT_ID,
    platform: "android",
    displayName: "VibeSignal Pro Monthly",
    priceDisplay: SUBSCRIPTION_PRICE_DISPLAY,
    billingPeriod: "P1M",
    productType: "auto_renewing_subscription",
    is_valid: false,
  },
];

export const STORE_METADATA = {
  supportContactRef: readEnv("EXPO_PUBLIC_SUPPORT_CONTACT_REF", "support-contact-placeholder"),
  privacyPolicyRouteRef: readEnv("EXPO_PUBLIC_PRIVACY_POLICY_ROUTE_REF", "/legal/privacy-policy"),
  termsRouteRef: readEnv("EXPO_PUBLIC_TERMS_ROUTE_REF", "/legal/terms"),
  privacyPolicyUrl: readEnv("EXPO_PUBLIC_PRIVACY_POLICY_URL", ""),
  termsUrl: readEnv("EXPO_PUBLIC_TERMS_URL", ""),
  subscriptionDisclosure: {
    priceDisplay: SUBSCRIPTION_PRICE_DISPLAY,
    planName: "VibeSignal Pro Monthly",
    billingFrequency: "Monthly subscription",
    renewalType: "auto_renewing",
    cancellationInfo: "Cancel anytime in your Apple account subscription settings.",
    appStorePricingNote:
      "The displayed monthly price must match the final App Store Connect price point.",
  },
};
