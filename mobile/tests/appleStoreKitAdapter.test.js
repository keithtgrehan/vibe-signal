import test from "node:test";
import assert from "node:assert/strict";

import { createAppleStoreKitAdapter } from "../src/commerce/appleStoreKitAdapter.js";

test("apple adapter reports a clear configuration gap when the RevenueCat key is missing", async () => {
  const adapter = createAppleStoreKitAdapter({
    purchasesModule: {},
    apiKey: "",
  });

  const readiness = adapter.getReadiness();
  const init = await adapter.initialize();

  assert.equal(readiness.ok, false);
  assert.equal(readiness.status, "billing_unavailable");
  assert.match(readiness.message, /RevenueCat is not configured/i);
  assert.equal(init.status, "billing_unavailable");
});

test("apple adapter initializes, lists products, and resolves active premium entitlement", async () => {
  const calls = [];
  const adapter = createAppleStoreKitAdapter({
    apiKey: "appl_test_public_sdk_key",
    purchasesModule: {
      configure(config) {
        calls.push({ type: "configure", config });
      },
      async getOfferings() {
        return {
          current: {
            identifier: "default",
            availablePackages: [
              {
                identifier: "$rc_monthly",
                product: {
                  identifier: "vibesignal_pro_monthly_ios",
                  title: "VibeSignal Pro Monthly",
                  priceString: "€1.89",
                  subscriptionPeriod: "P1M",
                },
              },
            ],
          },
        };
      },
      async getCustomerInfo() {
        return {
          requestDate: "2026-04-08T10:00:00.000Z",
          entitlements: {
            active: {
              vibesignal_pro: {
                identifier: "vibesignal_pro",
                productIdentifier: "vibesignal_pro_monthly_ios",
                expirationDate: "2026-05-08T10:00:00.000Z",
              },
            },
          },
        };
      },
      async purchasePackage(pkg) {
        return {
          customerInfo: {
            requestDate: "2026-04-08T10:05:00.000Z",
            entitlements: {
              active: {
                vibesignal_pro: {
                  identifier: "vibesignal_pro",
                  productIdentifier: pkg.product.identifier,
                  expirationDate: "2026-05-08T10:05:00.000Z",
                },
              },
            },
          },
        };
      },
      async restorePurchases() {
        return {
          requestDate: "2026-04-08T10:06:00.000Z",
          entitlements: {
            active: {
              vibesignal_pro: {
                identifier: "vibesignal_pro",
                productIdentifier: "vibesignal_pro_monthly_ios",
                expirationDate: "2026-05-08T10:06:00.000Z",
              },
            },
          },
        };
      },
    },
  });

  const init = await adapter.initialize({ appUserId: "install_123" });
  const catalog = await adapter.listProducts({ appUserId: "install_123" });
  const entitlement = await adapter.getEntitlement({ appUserId: "install_123" });
  const purchase = await adapter.purchase({
    appUserId: "install_123",
    productId: "vibesignal_pro_monthly_ios",
  });
  const restore = await adapter.restore({ appUserId: "install_123" });

  assert.equal(init.ok, true);
  assert.equal(calls[0].config.appUserID, "install_123");
  assert.equal(catalog.products[0].productId, "vibesignal_pro_monthly_ios");
  assert.equal(catalog.products[0].priceDisplay, "€1.89");
  assert.equal(catalog.products[0].is_valid, true);
  assert.equal(entitlement.premiumActive, true);
  assert.equal(entitlement.status, "premium_active");
  assert.equal(purchase.entitlementConfirmed, true);
  assert.equal(purchase.status, "purchase_completed");
  assert.equal(restore.entitlementConfirmed, true);
  assert.equal(restore.status, "restore_completed");
});
