import { getBillingProduct } from "./billingCatalog.js";

function unavailableResult(statusMessage) {
  return {
    ok: false,
    status: "billing_unavailable",
    platform: "android",
    message: statusMessage,
  };
}

export function createGooglePlayBillingAdapter({ nativeBillingModule } = {}) {
  function available() {
    return Boolean(nativeBillingModule && typeof nativeBillingModule.requestSubscription === "function");
  }

  async function listProducts() {
    const product = getBillingProduct("android");
    if (!available()) {
      return {
        ...unavailableResult("Google Play Billing is not wired into this mobile runtime yet."),
        products: product ? [product] : [],
      };
    }
    return {
      ok: true,
      status: "products_ready",
      platform: "android",
      products: product ? [product] : [],
    };
  }

  async function purchase({ appUserId, productId } = {}) {
    if (!available()) {
      return unavailableResult("Google Play purchase support is not wired yet.");
    }
    return nativeBillingModule.requestSubscription({
      appUserId,
      productId,
      platform: "android",
    });
  }

  async function restore({ appUserId } = {}) {
    if (!available()) {
      return unavailableResult("Google Play restore support is not wired yet.");
    }
    return nativeBillingModule.restorePurchases({
      appUserId,
      platform: "android",
    });
  }

  return {
    platform: "android",
    available,
    listProducts,
    purchase,
    restore,
  };
}
