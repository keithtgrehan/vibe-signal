import { createAppleStoreKitAdapter } from "./appleStoreKitAdapter.js";
import { getBillingProduct, getStoreMetadata, listBillingProducts } from "./billingCatalog.js";
import { createGooglePlayBillingAdapter } from "./googlePlayBillingAdapter.js";

function unsupportedPlatform(platform) {
  return {
    ok: false,
    status: "unsupported_platform",
    platform: String(platform || "").trim().toLowerCase(),
    message: "This billing platform is not supported by the current mobile runtime.",
  };
}

function storageBlockedResult(message = "Secure storage is unavailable on this device.") {
  return {
    ok: false,
    status: "secure_storage_unavailable",
    blockedReason: "secure_storage_unavailable",
    message,
    entitlementConfirmed: false,
    localPurchaseOnly: false,
  };
}

function verificationBlockedResult(message = "Local purchase initiation does not grant entitlement without backend confirmation.") {
  return {
    ok: false,
    status: "purchase_unverified",
    blockedReason: "purchase_unverified",
    message,
    entitlementConfirmed: false,
    localPurchaseOnly: true,
  };
}

export function createBillingService({
  iosAdapter,
  androidAdapter,
  iosNativeBillingModule,
  androidNativeBillingModule,
} = {}) {
  const adapters = {
    ios: iosAdapter || createAppleStoreKitAdapter({ nativeBillingModule: iosNativeBillingModule }),
    android:
      androidAdapter || createGooglePlayBillingAdapter({ nativeBillingModule: androidNativeBillingModule }),
  };
  const catalogFlights = new Map();
  const refreshFlights = new Map();
  const initializeFlights = new Map();
  const mutationFlights = new Map();

  function flightKey(platform, appUserId = "") {
    return `${String(platform || "").trim().toLowerCase()}:${String(appUserId || "").trim()}`;
  }

  function runSingleFlight(store, key, operation) {
    if (store.has(key)) {
      return store.get(key);
    }

    const flight = (async () => operation())().finally(() => {
      if (store.get(key) === flight) {
        store.delete(key);
      }
    });
    store.set(key, flight);
    return flight;
  }

  function getAdapter(platform) {
    const normalizedPlatform = String(platform || "").trim().toLowerCase();
    return adapters[normalizedPlatform] || null;
  }

  async function bootstrapCommerce({
    platform,
    identityService,
    entitlementClient,
  } = {}) {
    if (!identityService || typeof identityService.getOrCreateInstallationId !== "function") {
      return storageBlockedResult("Secure installation identity is not configured for this mobile runtime.");
    }
    const installationResult = await identityService.getOrCreateInstallationId();
    if (!installationResult.ok) {
      return storageBlockedResult("Secure storage is unavailable on this device.");
    }
    if (!entitlementClient || typeof entitlementClient.fetchEntitlement !== "function") {
      return {
        ok: false,
        status: "transport_unavailable",
        blockedReason: "purchase_unverified",
        message: "Entitlement transport is unavailable, so purchase state cannot be confirmed.",
        entitlementConfirmed: false,
        installationId: installationResult.installationId,
      };
    }
    const entitlementResponse = await entitlementClient.fetchEntitlement({
      deviceInstallationId: installationResult.installationId,
      platform,
    });
    return {
      ...entitlementResponse,
      installationId: installationResult.installationId,
      appUserId:
        entitlementResponse.app_user?.app_user_id ||
        entitlementResponse.app_user_id ||
        "",
      secureStorageAvailable: true,
      blockedReason:
        entitlementResponse.ok === false && entitlementResponse.status === "secure_storage_unavailable"
          ? "secure_storage_unavailable"
          : "",
    };
  }

  function evaluateAnalysisGate({
    entitlement,
    providerReady = true,
    consentConfirmed = true,
    secureStorageAvailable = true,
  } = {}) {
    if (!secureStorageAvailable) {
      return {
        allowed: false,
        blockedReason: "secure_storage_unavailable",
      };
    }
    if (!consentConfirmed) {
      return {
        allowed: false,
        blockedReason: "missing_consent",
      };
    }
    if (!providerReady) {
      return {
        allowed: false,
        blockedReason: "provider_not_ready",
      };
    }
    if (!entitlement) {
      return {
        allowed: false,
        blockedReason: "purchase_unverified",
      };
    }
    if (entitlement.entitlement_state === "blocked") {
      return {
        allowed: false,
        blockedReason: entitlement.blocked_reason || "free_limit_reached",
      };
    }
    return {
      allowed: true,
      blockedReason: "",
    };
  }

  async function getCatalog(platform, { appUserId } = {}) {
    const adapter = getAdapter(platform);
    if (!adapter) {
      return unsupportedPlatform(platform);
    }
    return runSingleFlight(catalogFlights, flightKey(platform, appUserId), async () => {
      const catalogResult = await adapter.listProducts({ appUserId });
      return {
        ...catalogResult,
        storeMetadata: getStoreMetadata(),
      };
    });
  }

  async function initializeBilling(platform, { appUserId } = {}) {
    const adapter = getAdapter(platform);
    if (!adapter) {
      return unsupportedPlatform(platform);
    }
    if (typeof adapter.initialize !== "function") {
      return {
        ok: false,
        status: "billing_unavailable",
        platform,
        message: "The selected billing adapter does not expose initialization.",
      };
    }
    return runSingleFlight(initializeFlights, flightKey(platform, appUserId), async () =>
      adapter.initialize({ appUserId })
    );
  }

  async function refreshSubscriptionStatus({ platform, appUserId } = {}) {
    const adapter = getAdapter(platform);
    if (!adapter) {
      return unsupportedPlatform(platform);
    }
    if (typeof adapter.getEntitlement !== "function") {
      return {
        ok: false,
        status: "billing_unavailable",
        platform,
        message: "The selected billing adapter does not expose entitlement refresh.",
      };
    }
    const key = flightKey(platform, appUserId);
    if (mutationFlights.has(key)) {
      await mutationFlights.get(key).catch(() => null);
    }
    return runSingleFlight(refreshFlights, key, async () => adapter.getEntitlement({ appUserId }));
  }

  function getBillingReadiness(platform) {
    const adapter = getAdapter(platform);
    if (!adapter) {
      return unsupportedPlatform(platform);
    }
    if (typeof adapter.getReadiness !== "function") {
      return {
        ok: false,
        status: "billing_unavailable",
        platform,
        message: "The selected billing adapter does not expose readiness.",
      };
    }
    return adapter.getReadiness();
  }

  async function initiatePurchase({ platform, appUserId, productId } = {}) {
    if (!String(appUserId || "").trim()) {
      return verificationBlockedResult(
        "An app user must be registered and confirmed before purchase initiation."
      );
    }
    const adapter = getAdapter(platform);
    if (!adapter) {
      return unsupportedPlatform(platform);
    }
    const product = getBillingProduct(platform);
    const key = flightKey(platform, appUserId);
    return runSingleFlight(mutationFlights, key, async () => {
      const purchaseAttempt = await adapter.purchase({
        appUserId,
        productId: productId || product?.productId || "",
      });
      return {
        ...purchaseAttempt,
        product: product || null,
      };
    });
  }

  async function restorePurchases({ platform, appUserId } = {}) {
    if (!String(appUserId || "").trim()) {
      return verificationBlockedResult(
        "An app user must be registered and confirmed before purchase restore."
      );
    }
    const adapter = getAdapter(platform);
    if (!adapter) {
      return unsupportedPlatform(platform);
    }
    const key = flightKey(platform, appUserId);
    return runSingleFlight(mutationFlights, key, async () =>
      adapter.restore({
        appUserId,
      })
    );
  }

  async function verifyPurchaseWithBackend({
    platform,
    purchaseAttempt,
    appUserId,
    entitlementClient,
  } = {}) {
    if (!purchaseAttempt?.purchaseArtifact) {
      return verificationBlockedResult("No purchase artifact is available to verify.");
    }
    if (!entitlementClient || typeof entitlementClient.submitPurchaseVerification !== "function") {
      return verificationBlockedResult(
        "Entitlement confirmation is unavailable, so local purchase initiation cannot unlock usage."
      );
    }
    const verificationResponse = await entitlementClient.submitPurchaseVerification({
      appUserId,
      platform,
      productId: purchaseAttempt.purchaseArtifact.product_id || "",
      purchaseArtifact: purchaseAttempt.purchaseArtifact,
      transactionId: purchaseAttempt.purchaseArtifact.transaction_id || "",
      originalTransactionId: purchaseAttempt.purchaseArtifact.original_transaction_id || "",
      purchaseId: "",
    });
    const entitlement = verificationResponse.entitlement || null;
    const confirmed =
      entitlement &&
      (entitlement.subscription_status === "active" || entitlement.subscription_status === "grace_period");
    if (!confirmed) {
      return {
        ...verificationBlockedResult(),
        verificationResponse,
      };
    }
    return {
      ok: true,
      status: "entitlement_confirmed",
      blockedReason: "",
      message: "Backend verification confirmed the subscription entitlement.",
      entitlementConfirmed: true,
      entitlement,
      verificationResponse,
    };
  }

  return {
    listBillingProducts,
    bootstrapCommerce,
    evaluateAnalysisGate,
    initializeBilling,
    refreshSubscriptionStatus,
    getBillingReadiness,
    getCatalog,
    initiatePurchase,
    restorePurchases,
    verifyPurchaseWithBackend,
  };
}
