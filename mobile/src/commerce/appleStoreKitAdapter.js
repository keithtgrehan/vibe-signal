import { getBillingProduct } from "./billingCatalog.js";
import { getMonetizationReadiness } from "./monetizationReadiness.js";
import {
  IOS_PREMIUM_ENTITLEMENT_ID,
  IOS_REVENUECAT_API_KEY,
} from "./config.js";

function unavailableResult(message, extra = {}) {
  return {
    ok: false,
    ready: false,
    status: "billing_unavailable",
    platform: "ios",
    store: "apple_app_store",
    canPurchase: false,
    canRestore: false,
    message,
    entitlementConfirmed: false,
    premiumActive: false,
    source: "apple_app_store",
    ...extra,
  };
}

function normalizeStoreProduct(product = {}, fallbackProduct = {}) {
  return {
    productId: String(
      product.identifier || product.productIdentifier || fallbackProduct.productId || ""
    ).trim(),
    displayName: String(product.title || fallbackProduct.displayName || "").trim(),
    priceDisplay: String(
      product.priceString || product.localizedPriceString || fallbackProduct.priceDisplay || ""
    ).trim(),
    billingPeriod: String(
      product.subscriptionPeriod || fallbackProduct.billingPeriod || "P1M"
    ).trim(),
    productType: "auto_renewing_subscription",
    platform: "ios",
    is_valid: true,
  };
}

function findPackage(offerings, productId) {
  const current = offerings?.current;
  const packages = Array.isArray(current?.availablePackages) ? current.availablePackages : [];
  return (
    packages.find((item) => {
      const identifier = String(item?.product?.identifier || "").trim();
      return identifier === productId;
    }) || null
  );
}

function normalizeEntitlement(customerInfo = {}, productId, entitlementId) {
  const active = customerInfo?.entitlements?.active || {};
  const namedEntitlement = active[entitlementId] || null;
  const entitlement = namedEntitlement || null;
  const premiumActive = Boolean(entitlement);

  return {
    premiumActive,
    entitlementId: premiumActive
      ? String(entitlement.identifier || entitlementId).trim()
      : entitlementId,
    subscriptionStatus: premiumActive ? "active" : "inactive",
    productId: premiumActive
      ? String(entitlement.productIdentifier || productId || "").trim()
      : String(productId || "").trim(),
    expiresAt: premiumActive ? String(entitlement.expirationDate || "").trim() : "",
    lastSyncedAt: String(customerInfo.requestDate || new Date().toISOString()).trim(),
    source: "apple_app_store",
    customerInfo,
  };
}

function normalizePurchaseSuccess(customerInfo, productId, entitlementId, message) {
  const entitlement = normalizeEntitlement(customerInfo, productId, entitlementId);
  return {
    ok: true,
    ready: true,
    status: entitlement.premiumActive ? "purchase_completed" : "purchase_unverified",
    platform: "ios",
    store: "apple_app_store",
    canPurchase: true,
    canRestore: true,
    message,
    entitlementConfirmed: entitlement.premiumActive,
    premiumActive: entitlement.premiumActive,
    subscriptionStatus: entitlement.subscriptionStatus,
    productId: entitlement.productId,
    entitlementId: entitlement.entitlementId,
    expiresAt: entitlement.expiresAt,
    lastSyncedAt: entitlement.lastSyncedAt,
    source: entitlement.source,
    customerInfo: entitlement.customerInfo,
  };
}

function normalizePurchasesError(error) {
  const userCancelled = Boolean(error?.userCancelled);
  if (userCancelled) {
    return {
      status: "purchase_cancelled",
      message: "The App Store purchase was cancelled before completion.",
    };
  }
  const message = String(error?.message || error || "").trim();
  return {
    status: "billing_error",
    message: message || "The App Store purchase could not be completed.",
  };
}

async function loadPurchasesModule(explicitModule) {
  if (explicitModule) {
    return explicitModule.default ?? explicitModule;
  }
  const module = await import("react-native-purchases");
  return module.default ?? module;
}

export function createAppleStoreKitAdapter({
  purchasesModule,
  apiKey = IOS_REVENUECAT_API_KEY,
  entitlementId = IOS_PREMIUM_ENTITLEMENT_ID,
} = {}) {
  const product = getBillingProduct("ios");
  let configuredAppUserId = "";
  let resolvedModulePromise = null;

  async function getPurchasesModule() {
    if (!resolvedModulePromise) {
      resolvedModulePromise = loadPurchasesModule(purchasesModule);
    }
    return resolvedModulePromise;
  }

  async function runtimeReady() {
    const readinessCheck = getMonetizationReadiness();
    const trimmedApiKey = String(apiKey || "").trim();
    if (!readinessCheck.productIdConfigured || !readinessCheck.entitlementConfigured || !trimmedApiKey) {
      return unavailableResult(
        "RevenueCat is not configured for iOS yet. Add the public iOS SDK key before enabling premium purchases."
      );
    }

    try {
      const purchases = await getPurchasesModule();
      const ready =
        purchases &&
        typeof purchases.configure === "function" &&
        typeof purchases.getOfferings === "function" &&
        typeof purchases.getCustomerInfo === "function" &&
        typeof purchases.purchasePackage === "function" &&
        typeof purchases.restorePurchases === "function";
      if (!ready) {
        return unavailableResult(
          "The iOS purchase runtime is not available in this build yet.",
          {
            developerMessage:
              "react-native-purchases is not fully available. Use an iOS development build or App Store build for real purchase flows.",
          }
        );
      }
      return {
        ok: true,
        ready: true,
        status: "billing_ready",
        platform: "ios",
        store: "apple_app_store",
        canPurchase: true,
        canRestore: true,
        product,
        entitlementId,
      };
    } catch (error) {
      return unavailableResult(
        "The iOS purchase runtime is not available in this build yet.",
        {
          developerMessage: String(error?.message || error || ""),
        }
      );
    }
  }

  async function configureIfNeeded(appUserId = "") {
    const readiness = await runtimeReady();
    if (!readiness.ok) {
      return readiness;
    }
    const purchases = await getPurchasesModule();
    const normalizedAppUserId = String(appUserId || "").trim();

    if (!configuredAppUserId) {
      purchases.configure({
        apiKey: String(apiKey || "").trim(),
        appUserID: normalizedAppUserId || undefined,
      });
      configuredAppUserId = normalizedAppUserId;
      return readiness;
    }

    if (
      normalizedAppUserId &&
      normalizedAppUserId !== configuredAppUserId &&
      typeof purchases.logIn === "function"
    ) {
      await purchases.logIn(normalizedAppUserId);
      configuredAppUserId = normalizedAppUserId;
    }
    return readiness;
  }

  function getReadiness() {
    const readinessCheck = getMonetizationReadiness();
    if (
      !readinessCheck.productIdConfigured ||
      !readinessCheck.entitlementConfigured ||
      !String(apiKey || "").trim()
    ) {
      return unavailableResult(
        "RevenueCat is not configured for iOS yet. Add the public iOS SDK key before enabling premium purchases."
      );
    }
    return {
      ok: true,
      ready: true,
      status: "billing_ready",
      platform: "ios",
      store: "apple_app_store",
      canPurchase: true,
      canRestore: true,
      product,
      entitlementId,
      readiness: readinessCheck,
      message: "The Apple billing layer is configured for iOS premium purchases.",
    };
  }

  async function initialize({ appUserId } = {}) {
    const readiness = await configureIfNeeded(appUserId);
    if (!readiness.ok) {
      return readiness;
    }
    return {
      ...readiness,
      message: "The Apple billing layer initialized for this device.",
    };
  }

  async function listProducts({ appUserId } = {}) {
    const readiness = await configureIfNeeded(appUserId);
    if (!readiness.ok) {
      return {
        ...readiness,
        products: product ? [product] : [],
      };
    }
    const purchases = await getPurchasesModule();
    const offerings = await purchases.getOfferings();
    const packageForProduct = findPackage(offerings, product?.productId || "");
    const storeProducts = packageForProduct
      ? [normalizeStoreProduct(packageForProduct.product, product)]
      : product
      ? [{ ...product, is_valid: false }]
      : [];

    return {
      ...readiness,
      status: "products_ready",
      products: storeProducts,
      currentOfferingIdentifier: String(offerings?.current?.identifier || "").trim(),
    };
  }

  async function purchase({ appUserId, productId } = {}) {
    const readiness = await configureIfNeeded(appUserId);
    if (!readiness.ok) {
      return readiness;
    }
    const purchases = await getPurchasesModule();
    const offerings = await purchases.getOfferings();
    const productIdentifier = String(productId || product?.productId || "").trim();
    const matchedPackage = findPackage(offerings, productIdentifier);
    if (!matchedPackage) {
      return unavailableResult(
        "The monthly premium subscription is not available in the current offering.",
        {
          status: "product_unavailable",
          ready: true,
          canPurchase: true,
          canRestore: true,
        }
      );
    }

    try {
      const result = await purchases.purchasePackage(matchedPackage);
      const customerInfo = result?.customerInfo || result?.purchaserInfo || {};
      return normalizePurchaseSuccess(
        customerInfo,
        productIdentifier,
        entitlementId,
        "The App Store purchase completed and premium access is ready."
      );
    } catch (error) {
      const normalized = normalizePurchasesError(error);
      return {
        ok: false,
        ready: true,
        platform: "ios",
        store: "apple_app_store",
        canPurchase: true,
        canRestore: true,
        entitlementConfirmed: false,
        premiumActive: false,
        source: "apple_app_store",
        ...normalized,
      };
    }
  }

  async function restore({ appUserId } = {}) {
    const readiness = await configureIfNeeded(appUserId);
    if (!readiness.ok) {
      return readiness;
    }
    const purchases = await getPurchasesModule();
    try {
      const customerInfo = await purchases.restorePurchases();
      const normalized = normalizePurchaseSuccess(
        customerInfo,
        product?.productId || "",
        entitlementId,
        "Restore completed. Premium access has been refreshed for this device."
      );
      return {
        ...normalized,
        status: normalized.premiumActive ? "restore_completed" : "restore_no_active_entitlement",
      };
    } catch (error) {
      const normalized = normalizePurchasesError(error);
      return {
        ok: false,
        ready: true,
        platform: "ios",
        store: "apple_app_store",
        canPurchase: true,
        canRestore: true,
        entitlementConfirmed: false,
        premiumActive: false,
        source: "apple_app_store",
        ...normalized,
      };
    }
  }

  async function getEntitlement({ appUserId } = {}) {
    const readiness = await configureIfNeeded(appUserId);
    if (!readiness.ok) {
      return readiness;
    }
    const purchases = await getPurchasesModule();
    const customerInfo = await purchases.getCustomerInfo();
    const normalized = normalizeEntitlement(customerInfo, product?.productId || "", entitlementId);
    return {
      ok: true,
      ready: true,
      status: normalized.premiumActive ? "premium_active" : "premium_inactive",
      platform: "ios",
      store: "apple_app_store",
      entitlementConfirmed: normalized.premiumActive,
      premiumActive: normalized.premiumActive,
      subscriptionStatus: normalized.subscriptionStatus,
      productId: normalized.productId,
      entitlementId: normalized.entitlementId,
      expiresAt: normalized.expiresAt,
      lastSyncedAt: normalized.lastSyncedAt,
      source: normalized.source,
      customerInfo: normalized.customerInfo,
      message: normalized.premiumActive
        ? "Premium access is active for this Apple account."
        : "No active premium Apple entitlement was found.",
    };
  }

  return {
    platform: "ios",
    available: () => Boolean(String(apiKey || "").trim()),
    getReadiness,
    initialize,
    listProducts,
    purchase,
    restore,
    getEntitlement,
  };
}
