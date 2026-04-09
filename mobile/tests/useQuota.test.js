import test from "node:test";
import assert from "node:assert/strict";

import { buildQuotaHookState } from "../src/hooks/quotaViewModel.js";

test("quota hook state exposes the real UI selectors the screen needs", () => {
  const state = buildQuotaHookState({
    loading: false,
    monetization: {
      premiumActive: false,
      quota: {
        current_period_type: "trial_week",
        remaining_uses: 7,
        uses_in_current_period: 3,
      },
      quotaView: {
        usesLeft: "7 left",
        periodLabel: "Trial week",
        resetTiming: "Resets in 6d",
        resetAt: "2026-04-15T10:00:00.000Z",
      },
      paywall: {
        visible: false,
        restoreAvailable: true,
      },
      product: {
        productId: "vibesignal_pro_monthly_ios",
        priceDisplay: "€1.89/month",
        is_valid: true,
      },
      productCatalog: {
        usesFallback: false,
      },
    },
  });

  assert.equal(state.premium_active, false);
  assert.equal(state.current_period_type, "trial_week");
  assert.equal(state.remaining_uses, 7);
  assert.equal(state.paywall_required, false);
  assert.equal(state.price_display, "€1.89/month");
  assert.equal(state.restore_available, true);
  assert.equal(state.purchase_available, true);
});

test("quota hook state keeps premium users unlocked without a false paywall", () => {
  const state = buildQuotaHookState({
    loading: false,
    monetization: {
      premiumActive: true,
      quota: {
        current_period_type: "weekly_free",
        remaining_uses: null,
        uses_in_current_period: 5,
      },
      quotaView: {
        usesLeft: "Unlimited",
        periodLabel: "Weekly free usage",
        resetTiming: "Premium active",
      },
      paywall: {
        visible: false,
        restoreAvailable: true,
      },
      product: {
        productId: "vibesignal_pro_monthly_ios",
        priceDisplay: "€1.89/month",
        is_valid: true,
      },
      productCatalog: {
        usesFallback: false,
      },
    },
  });

  assert.equal(state.premium_active, true);
  assert.equal(state.paywall_required, false);
  assert.equal(state.uses_left_label, "Unlimited");
  assert.equal(state.remaining_uses, Number.POSITIVE_INFINITY);
});

test("quota hook state keeps fallback pricing honest when live metadata is unavailable", () => {
  const state = buildQuotaHookState({
    loading: false,
    monetization: {
      premiumActive: false,
      quota: {
        current_period_type: "weekly_free",
        remaining_uses: 0,
        uses_in_current_period: 5,
      },
      quotaView: {
        usesLeft: "0 left",
        periodLabel: "Weekly free usage",
        resetTiming: "Resets in 7d",
      },
      paywall: {
        visible: true,
        restoreAvailable: true,
      },
      product: {
        productId: "vibesignal_pro_monthly_ios",
        priceDisplay: "€1.89/month",
        is_valid: false,
      },
      productCatalog: {
        usesFallback: true,
      },
    },
  });

  assert.equal(state.catalog_uses_fallback, true);
  assert.match(state.status_message, /fallback price/i);
  assert.equal(state.purchase_available, false);
});

test("quota hook state stays internally consistent for unavailable storage", () => {
  const state = buildQuotaHookState({
    loading: false,
    monetization: {
      ok: false,
      secureStorageAvailable: false,
      premiumActive: false,
      quota: {
        current_period_type: "trial_week",
        remaining_uses: 10,
        uses_in_current_period: 0,
      },
      quotaView: {
        usesLeft: "10 left",
        periodLabel: "Trial week",
        resetTiming: "Resets in 7d",
      },
      paywall: {
        visible: false,
        restoreAvailable: true,
      },
      product: {
        productId: "vibesignal_pro_monthly_ios",
        priceDisplay: "€1.89/month",
        is_valid: false,
      },
      productCatalog: {
        usesFallback: true,
      },
      storeMetadata: {
        privacyPolicyUrl: "",
        termsUrl: "",
        subscriptionDisclosure: {
          priceDisplay: "€1.89/month",
        },
        monetizationReadiness: {
          purchaseReady: false,
        },
      },
    },
  });

  assert.equal(state.paywall_required, false);
  assert.equal(state.premium_active, false);
  assert.match(state.status_message, /secure storage is unavailable/i);
  assert.equal(state.legal_links_configured, false);
});

test("quota hook state suppresses paywall while bootstrapping", () => {
  const state = buildQuotaHookState({
    loading: true,
    monetization: {
      is_bootstrapping: true,
      premiumActive: false,
      quota: {
        current_period_type: "weekly_free",
        remaining_uses: 0,
        uses_in_current_period: 5,
      },
      quotaView: {
        usesLeft: "0 left",
        periodLabel: "Weekly free usage",
        resetTiming: "Resets in 7d",
      },
      paywall: {
        visible: true,
        restoreAvailable: true,
      },
      product: {
        productId: "vibesignal_pro_monthly_ios",
        priceDisplay: "€1.89/month",
        is_valid: false,
      },
      productCatalog: {
        usesFallback: true,
      },
    },
  });

  assert.equal(state.is_bootstrapping, true);
  assert.equal(state.paywall_required, false);
  assert.equal(state.status_message, "");
});

test("quota hook state can show a non-blocking upgrade prompt after repeated successful analyses", () => {
  const state = buildQuotaHookState({
    loading: false,
    monetization: {
      premiumActive: false,
      quota: {
        current_period_type: "trial_week",
        remaining_uses: 7,
        uses_in_current_period: 3,
        paywall_required: false,
      },
      quotaView: {
        usesLeft: "7 left",
        periodLabel: "Trial week",
        resetTiming: "Resets in 6d",
      },
      paywall: {
        visible: false,
        restoreAvailable: true,
      },
      product: {
        productId: "vibesignal_pro_monthly_ios",
        priceDisplay: "€1.89/month",
        is_valid: true,
      },
      productCatalog: {
        usesFallback: false,
      },
    },
  });

  assert.equal(state.paywall_required, false);
  assert.equal(state.upgrade_prompt_visible, true);
  assert.equal(state.upgrade_prompt_stage, "teaser");
});

test("quota hook state surfaces compliance metadata for the paywall", () => {
  const state = buildQuotaHookState({
    loading: false,
    monetization: {
      premiumActive: false,
      quota: {
        current_period_type: "weekly_free",
        remaining_uses: 0,
        uses_in_current_period: 5,
      },
      quotaView: {
        usesLeft: "0 left",
        periodLabel: "Weekly free usage",
        resetTiming: "Resets in 7d",
      },
      paywall: {
        visible: true,
        restoreAvailable: true,
      },
      product: {
        productId: "vibesignal_pro_monthly_ios",
        priceDisplay: "€1.89/month",
        is_valid: true,
      },
      productCatalog: {
        usesFallback: false,
        status: "products_ready",
      },
      storeMetadata: {
        privacyPolicyUrl: "https://example.test/privacy",
        termsUrl: "https://example.test/terms",
        supportContactRef: "support@example.test",
        subscriptionDisclosure: {
          priceDisplay: "€1.89/month",
        },
        monetizationReadiness: {
          purchaseReady: true,
        },
      },
    },
  });

  assert.equal(state.purchase_available, true);
  assert.equal(state.privacy_policy_url, "https://example.test/privacy");
  assert.equal(state.terms_url, "https://example.test/terms");
  assert.equal(state.legal_links_configured, true);
});
