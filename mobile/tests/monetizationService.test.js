import test from "node:test";
import assert from "node:assert/strict";

import { createCommerceStateStore } from "../src/commerce/commerceStateStore.js";
import { createDeviceIdentityService } from "../src/commerce/deviceIdentity.js";
import { createMonetizationService } from "../src/commerce/monetizationService.js";

function makeMockSecureStore({ available = true } = {}) {
  const items = new Map();
  return {
    async isAvailableAsync() {
      return available;
    },
    async setItemAsync(key, value) {
      items.set(key, value);
    },
    async getItemAsync(key) {
      return items.has(key) ? items.get(key) : null;
    },
    async deleteItemAsync(key) {
      items.delete(key);
    },
  };
}

function buildService({
  secureStoreModule = makeMockSecureStore(),
  billingService,
  now = new Date("2026-04-08T10:00:00.000Z"),
} = {}) {
  const identityService = createDeviceIdentityService({ secureStoreModule });
  const stateStore = createCommerceStateStore({ secureStoreModule });
  return createMonetizationService({
    platform: "ios",
    identityService,
    stateStore,
    billingService,
    nowProvider: () => now,
  });
}

test("monetization state shows trial-week usage before premium is active", async () => {
  const service = buildService({
    billingService: {
      async refreshSubscriptionStatus() {
        return { ok: true, status: "premium_inactive", premiumActive: false };
      },
      async initiatePurchase() {
        return { ok: false, status: "billing_unavailable" };
      },
      async restorePurchases() {
        return { ok: false, status: "billing_unavailable" };
      },
    },
  });

  const state = await service.getMonetizationState();
  assert.equal(state.ok, true);
  assert.equal(state.quota.remaining_uses, 10);
  assert.equal(state.paywall.visible, false);
  assert.equal(state.premiumActive, false);
});

test("monetization service records successful analyses and triggers paywall after quota exhaustion", async () => {
  const service = buildService({
    billingService: {
      async refreshSubscriptionStatus() {
        return { ok: true, status: "premium_inactive", premiumActive: false };
      },
      async initiatePurchase() {
        return { ok: false, status: "billing_unavailable" };
      },
      async restorePurchases() {
        return { ok: false, status: "billing_unavailable" };
      },
    },
  });

  for (let index = 0; index < 10; index += 1) {
    const result = await service.runGatedAnalysis({
      analysisId: `analysis_${index}`,
      runAnalysis: async () => ({ ok: true }),
    });
    assert.equal(result.ok, true);
  }

  const blocked = await service.runGatedAnalysis({
    analysisId: "analysis_blocked",
    runAnalysis: async () => ({ ok: true }),
  });

  assert.equal(blocked.ok, false);
  assert.equal(blocked.status, "paywall_required");
  assert.equal(blocked.paywall.visible, true);
});

test("premium cached state preserves access when refresh is temporarily unavailable", async () => {
  const secureStoreModule = makeMockSecureStore();
  const service = buildService({
    secureStoreModule,
    billingService: {
      async refreshSubscriptionStatus() {
        return {
          ok: true,
          status: "premium_active",
          premiumActive: true,
          subscriptionStatus: "active",
          productId: "vibesignal_pro_monthly_ios",
          entitlementId: "vibesignal_pro",
          source: "apple_app_store",
          expiresAt: "2026-05-08T10:00:00.000Z",
          lastSyncedAt: "2026-04-08T10:00:00.000Z",
        };
      },
      async initiatePurchase() {
        return { ok: false, status: "billing_unavailable" };
      },
      async restorePurchases() {
        return { ok: false, status: "billing_unavailable" };
      },
    },
  });

  const active = await service.getMonetizationState();
  assert.equal(active.premiumActive, true);

  const cachedService = createMonetizationService({
    platform: "ios",
    identityService: createDeviceIdentityService({ secureStoreModule }),
    stateStore: createCommerceStateStore({ secureStoreModule }),
    billingService: {
      async refreshSubscriptionStatus() {
        return { ok: false, status: "billing_unavailable" };
      },
      async initiatePurchase() {
        return { ok: false, status: "billing_unavailable" };
      },
      async restorePurchases() {
        return { ok: false, status: "billing_unavailable" };
      },
    },
    nowProvider: () => new Date("2026-04-09T10:00:00.000Z"),
  });

  const cached = await cachedService.getMonetizationState();
  assert.equal(cached.premiumActive, true);
  assert.equal(cached.premiumState.status, "premium_cached");
});

test("purchase and restore flows can activate premium through Apple entitlement state", async () => {
  let entitlementActive = false;
  const service = buildService({
    billingService: {
      async getCatalog() {
        return {
          ok: true,
          status: "products_ready",
          products: [
            {
              productId: "vibesignal_pro_monthly_ios",
              priceDisplay: "€1.89/month",
              is_valid: true,
            },
          ],
        };
      },
      async refreshSubscriptionStatus() {
        return {
          ok: true,
          status: entitlementActive ? "premium_active" : "premium_inactive",
          premiumActive: entitlementActive,
          subscriptionStatus: entitlementActive ? "active" : "inactive",
          productId: entitlementActive ? "vibesignal_pro_monthly_ios" : "",
          entitlementId: entitlementActive ? "vibesignal_pro" : "",
          source: "apple_app_store",
          expiresAt: entitlementActive ? "2026-05-08T10:00:00.000Z" : "",
          lastSyncedAt: "2026-04-08T10:00:00.000Z",
        };
      },
      async initiatePurchase() {
        entitlementActive = true;
        return {
          ok: true,
          status: "purchase_completed",
          entitlementConfirmed: true,
          premiumActive: true,
          subscriptionStatus: "active",
          productId: "vibesignal_pro_monthly_ios",
          entitlementId: "vibesignal_pro",
          source: "apple_app_store",
          expiresAt: "2026-05-08T10:00:00.000Z",
          lastSyncedAt: "2026-04-08T10:05:00.000Z",
        };
      },
      async restorePurchases() {
        entitlementActive = true;
        return {
          ok: true,
          status: "restore_completed",
          entitlementConfirmed: true,
          premiumActive: true,
          subscriptionStatus: "active",
          productId: "vibesignal_pro_monthly_ios",
          entitlementId: "vibesignal_pro",
          source: "apple_app_store",
          expiresAt: "2026-05-08T10:00:00.000Z",
          lastSyncedAt: "2026-04-08T10:06:00.000Z",
        };
      },
    },
  });

  const purchase = await service.purchasePremium();
  const restore = await service.restorePurchases();

  assert.equal(purchase.ok, true);
  assert.equal(purchase.entitlementConfirmed, true);
  assert.equal(restore.ok, true);
  assert.equal(restore.entitlementConfirmed, true);
});

test("restore clears the paywall block after quota exhaustion when premium is recovered", async () => {
  let restoreCalled = false;
  const service = buildService({
    billingService: {
      async refreshSubscriptionStatus() {
        return {
          ok: restoreCalled,
          status: restoreCalled ? "premium_active" : "premium_inactive",
          premiumActive: restoreCalled,
          subscriptionStatus: restoreCalled ? "active" : "inactive",
          productId: restoreCalled ? "vibesignal_pro_monthly_ios" : "",
          entitlementId: restoreCalled ? "vibesignal_pro" : "",
          source: "apple_app_store",
          expiresAt: restoreCalled ? "2026-05-08T10:00:00.000Z" : "",
          lastSyncedAt: "2026-04-08T10:00:00.000Z",
        };
      },
      async getCatalog() {
        return {
          ok: false,
          status: "catalog_unavailable",
          products: [],
        };
      },
      async initiatePurchase() {
        return { ok: false, status: "billing_unavailable" };
      },
      async restorePurchases() {
        restoreCalled = true;
        return {
          ok: true,
          status: "restore_completed",
          entitlementConfirmed: true,
          premiumActive: true,
          subscriptionStatus: "active",
          productId: "vibesignal_pro_monthly_ios",
          entitlementId: "vibesignal_pro",
          source: "apple_app_store",
          expiresAt: "2026-05-08T10:00:00.000Z",
          lastSyncedAt: "2026-04-08T10:06:00.000Z",
        };
      },
    },
  });

  for (let index = 0; index < 10; index += 1) {
    const result = await service.runGatedAnalysis({
      analysisId: `trial_${index}`,
      runAnalysis: async () => ({ ok: true }),
    });
    assert.equal(result.ok, true);
  }

  const blockedBeforeRestore = await service.getMonetizationState();
  assert.equal(blockedBeforeRestore.paywall.visible, true);

  const restore = await service.restorePurchases();
  assert.equal(restore.ok, true);
  assert.equal(restore.entitlementConfirmed, true);

  const afterRestore = await service.getMonetizationState();
  assert.equal(afterRestore.premiumActive, true);
  assert.equal(afterRestore.paywall.visible, false);
});

test("failed analysis does not decrement usage and duplicate ids do not double count", async () => {
  const service = buildService({
    billingService: {
      async refreshSubscriptionStatus() {
        return { ok: true, status: "premium_inactive", premiumActive: false };
      },
      async getCatalog() {
        return {
          ok: false,
          status: "catalog_unavailable",
          products: [],
        };
      },
      async initiatePurchase() {
        return { ok: false, status: "billing_unavailable" };
      },
      async restorePurchases() {
        return { ok: false, status: "billing_unavailable" };
      },
    },
  });

  await assert.rejects(
    service.runGatedAnalysis({
      analysisId: "failed_analysis",
      runAnalysis: async () => {
        throw new Error("analysis boom");
      },
    }),
    /analysis boom/
  );

  const afterFailure = await service.getMonetizationState();
  assert.equal(afterFailure.quota.uses_in_current_period, 0);
  assert.equal(afterFailure.quota.remaining_uses, 10);

  const firstSuccess = await service.runGatedAnalysis({
    analysisId: "dedupe_analysis",
    runAnalysis: async () => ({ ok: true }),
  });
  const duplicateSuccess = await service.runGatedAnalysis({
    analysisId: "dedupe_analysis",
    runAnalysis: async () => ({ ok: true }),
  });

  assert.equal(firstSuccess.ok, true);
  assert.equal(firstSuccess.recordedUsage, true);
  assert.equal(duplicateSuccess.ok, true);
  assert.equal(duplicateSuccess.recordedUsage, false);

  const finalState = await service.getMonetizationState();
  assert.equal(finalState.quota.uses_in_current_period, 1);
  assert.equal(finalState.quota.remaining_uses, 9);
});

test("secure storage failure returns a consistent unavailable monetization shape", async () => {
  const secureStoreModule = makeMockSecureStore({ available: false });
  const service = buildService({
    secureStoreModule,
    billingService: {
      async refreshSubscriptionStatus() {
        return { ok: true, status: "premium_inactive", premiumActive: false };
      },
    },
  });

  const state = await service.getMonetizationState();

  assert.equal(state.ok, false);
  assert.equal(state.status, "secure_storage_unavailable");
  assert.equal(state.secureStorageAvailable, false);
  assert.equal(state.premiumActive, false);
  assert.equal(state.paywall.visible, false);
  assert.equal(state.product.priceDisplay, "€1.89/month");
});

test("concurrent purchase and restore collapse into one entitlement-confirmed mutation", async () => {
  let purchaseCalls = 0;
  let restoreCalls = 0;
  let premiumActive = false;
  const service = buildService({
    billingService: {
      async getCatalog() {
        return {
          ok: true,
          status: "products_ready",
          products: [
            {
              productId: "vibesignal_pro_monthly_ios",
              priceDisplay: "€1.89/month",
              is_valid: true,
            },
          ],
        };
      },
      async refreshSubscriptionStatus() {
        return {
          ok: true,
          status: premiumActive ? "premium_active" : "premium_inactive",
          premiumActive,
          subscriptionStatus: premiumActive ? "active" : "inactive",
          productId: premiumActive ? "vibesignal_pro_monthly_ios" : "",
          entitlementId: premiumActive ? "vibesignal_pro" : "",
          source: "apple_app_store",
          expiresAt: premiumActive ? "2026-05-08T10:00:00.000Z" : "",
          lastSyncedAt: "2026-04-08T10:00:00.000Z",
        };
      },
      async initiatePurchase() {
        purchaseCalls += 1;
        await new Promise((resolve) => setTimeout(resolve, 5));
        premiumActive = true;
        return {
          ok: true,
          status: "purchase_completed",
          entitlementConfirmed: false,
        };
      },
      async restorePurchases() {
        restoreCalls += 1;
        premiumActive = true;
        return {
          ok: true,
          status: "restore_completed",
          entitlementConfirmed: false,
        };
      },
    },
  });

  const [purchase, restore] = await Promise.all([
    service.purchasePremium(),
    service.restorePurchases(),
  ]);
  const finalState = await service.getMonetizationState();

  assert.equal(purchaseCalls, 1);
  assert.equal(restoreCalls, 0);
  assert.equal(purchase.ok, true);
  assert.equal(restore.ok, true);
  assert.equal(finalState.premiumActive, true);
  assert.equal(finalState.paywall.visible, false);
});

test("analysis idempotency persists across service restarts", async () => {
  const secureStoreModule = makeMockSecureStore();
  const billingService = {
    async refreshSubscriptionStatus() {
      return { ok: true, status: "premium_inactive", premiumActive: false };
    },
    async getCatalog() {
      return {
        ok: false,
        status: "catalog_unavailable",
        products: [],
      };
    },
    async initiatePurchase() {
      return { ok: false, status: "billing_unavailable" };
    },
    async restorePurchases() {
      return { ok: false, status: "billing_unavailable" };
    },
  };

  const firstService = buildService({ secureStoreModule, billingService });
  const secondService = buildService({ secureStoreModule, billingService });

  const firstRun = await firstService.runGatedAnalysis({
    analysisId: "persisted_analysis",
    runAnalysis: async () => ({ ok: true }),
  });
  const secondRun = await secondService.runGatedAnalysis({
    analysisId: "persisted_analysis",
    runAnalysis: async () => ({ ok: true }),
  });
  const finalState = await secondService.getMonetizationState();

  assert.equal(firstRun.recordedUsage, true);
  assert.equal(secondRun.recordedUsage, false);
  assert.equal(finalState.quota.uses_in_current_period, 1);
  assert.equal(finalState.quota.remaining_uses, 9);
});

test("fallback catalog blocks premium purchase attempts safely", async () => {
  let purchaseCalls = 0;
  const service = buildService({
    billingService: {
      async refreshSubscriptionStatus() {
        return { ok: true, status: "premium_inactive", premiumActive: false };
      },
      async getCatalog() {
        return {
          ok: false,
          status: "catalog_unavailable",
          products: [],
        };
      },
      async initiatePurchase() {
        purchaseCalls += 1;
        return { ok: true, status: "purchase_completed", entitlementConfirmed: false };
      },
      async restorePurchases() {
        return { ok: false, status: "billing_unavailable" };
      },
    },
  });

  const purchase = await service.purchasePremium();

  assert.equal(purchase.ok, false);
  assert.equal(purchase.status, "product_unavailable");
  assert.equal(purchaseCalls, 0);
});
