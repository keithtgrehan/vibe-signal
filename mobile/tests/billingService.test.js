import test from "node:test";
import assert from "node:assert/strict";

import { createBillingService } from "../src/commerce/billingService.js";

test("billing service exposes the monthly catalog even before native wiring", async () => {
  const service = createBillingService();
  const iosCatalog = await service.getCatalog("ios");
  const androidCatalog = await service.getCatalog("android");

  assert.equal(iosCatalog.products.length, 1);
  assert.equal(iosCatalog.products[0].productId, "vibesignal_pro_monthly_ios");
  assert.equal(androidCatalog.products[0].productId, "vibesignal_pro_monthly_android");
  assert.equal(iosCatalog.storeMetadata.subscriptionDisclosure.priceDisplay, "€1.89/month");
});

test("billing service forwards the app user id into product lookup", async () => {
  let receivedAppUserId = "";
  const service = createBillingService({
    iosAdapter: {
      async listProducts({ appUserId } = {}) {
        receivedAppUserId = appUserId;
        return {
          ok: true,
          status: "products_ready",
          products: [
            {
              productId: "vibesignal_pro_monthly_ios",
              priceDisplay: "€1.89/month",
            },
          ],
        };
      },
    },
  });

  const catalog = await service.getCatalog("ios", { appUserId: "install_abc123" });

  assert.equal(catalog.ok, true);
  assert.equal(receivedAppUserId, "install_abc123");
});

test("billing service reports unavailable purchase path without native store wiring", async () => {
  const service = createBillingService();
  const result = await service.initiatePurchase({
    platform: "ios",
    appUserId: "app_user_test",
  });

  assert.equal(result.ok, false);
  assert.equal(result.status, "billing_unavailable");
});

test("billing service fails closed when secure installation identity is unavailable", async () => {
  const service = createBillingService();
  const result = await service.bootstrapCommerce({
    platform: "ios",
    identityService: {
      async getOrCreateInstallationId() {
        return {
          ok: false,
          status: "secure_storage_unavailable",
        };
      },
    },
    entitlementClient: {
      async fetchEntitlement() {
        return { ok: true };
      },
    },
  });

  assert.equal(result.ok, false);
  assert.equal(result.status, "secure_storage_unavailable");
  assert.equal(result.blockedReason, "secure_storage_unavailable");
});

test("billing service does not grant entitlement from local purchase initiation alone", async () => {
  const service = createBillingService({
    iosAdapter: {
      async listProducts() {
        return { ok: true, status: "products_ready", products: [] };
      },
      async purchase() {
        return {
          ok: true,
          status: "purchase_completed_unverified",
          purchaseArtifact: {
            artifact_type: "apple_app_store_receipt",
            product_id: "vibesignal_pro_monthly_ios",
            receipt_data_b64: "receipt-b64",
            transaction_id: "tx-local",
          },
        };
      },
      async restore() {
        return { ok: true, status: "restore_artifacts_ready", restoredPurchases: [] };
      },
    },
  });

  const purchaseAttempt = await service.initiatePurchase({
    platform: "ios",
    appUserId: "app_user_test",
  });
  const verification = await service.verifyPurchaseWithBackend({
    platform: "ios",
    appUserId: "app_user_test",
    purchaseAttempt,
    entitlementClient: {
      async submitPurchaseVerification() {
        return {
          ok: true,
          status: "verification_unavailable",
          entitlement: {
            subscription_status: "verification_unavailable",
            entitlement_state: "blocked",
            blocked_reason: "purchase_unverified",
          },
        };
      },
    },
  });

  assert.equal(purchaseAttempt.status, "purchase_completed_unverified");
  assert.equal(verification.ok, false);
  assert.equal(verification.status, "purchase_unverified");
  assert.equal(verification.entitlementConfirmed, false);
});

test("billing service can forward a purchase artifact to authoritative entitlement confirmation", async () => {
  const service = createBillingService({
    androidAdapter: {
      async listProducts() {
        return { ok: true, status: "products_ready", products: [] };
      },
      async purchase() {
        return {
          ok: true,
          status: "purchase_completed_unverified",
          purchaseArtifact: {
            artifact_type: "google_play_purchase_token",
            product_id: "vibesignal_pro_monthly_android",
            purchase_token: "token-123",
            package_name: "ai.vibesignal.app",
          },
        };
      },
      async restore() {
        return { ok: true, status: "restore_artifacts_ready", restoredPurchases: [] };
      },
    },
  });

  const purchaseAttempt = await service.initiatePurchase({
    platform: "android",
    appUserId: "app_user_test",
  });
  const verification = await service.verifyPurchaseWithBackend({
    platform: "android",
    appUserId: "app_user_test",
    purchaseAttempt,
    entitlementClient: {
      async submitPurchaseVerification() {
        return {
          ok: true,
          status: "verified_active",
          entitlement: {
            subscription_status: "active",
            entitlement_state: "subscription_active",
            blocked_reason: "",
          },
        };
      },
    },
  });

  assert.equal(verification.ok, true);
  assert.equal(verification.status, "entitlement_confirmed");
  assert.equal(verification.entitlementConfirmed, true);
});

test("billing service can refresh Apple entitlement state from the adapter", async () => {
  const service = createBillingService({
    iosAdapter: {
      async getEntitlement() {
        return {
          ok: true,
          status: "premium_active",
          premiumActive: true,
          subscriptionStatus: "active",
          productId: "vibesignal_pro_monthly_ios",
          entitlementId: "premium",
        };
      },
    },
  });

  const refreshed = await service.refreshSubscriptionStatus({
    platform: "ios",
    appUserId: "install_123",
  });

  assert.equal(refreshed.ok, true);
  assert.equal(refreshed.premiumActive, true);
  assert.equal(refreshed.subscriptionStatus, "active");
});
