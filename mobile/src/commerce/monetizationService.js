import { getBillingProduct, getStoreMetadata } from "./billingCatalog.js";
import { ENTITLEMENT_CACHE_GRACE_HOURS } from "./config.js";
import { createCommerceStateStore } from "./commerceStateStore.js";
import { createDeviceIdentityService } from "./deviceIdentity.js";
import {
  buildQuotaViewModel,
  createInitialCommerceState,
  recordCompletedAnalysisForQuota,
  resolveQuotaState,
} from "./quotaEngine.js";

function nowIso(now) {
  return new Date(now).toISOString();
}

function toDate(value, fallback = new Date()) {
  const text = String(value || "").trim();
  if (!text) {
    return fallback;
  }
  const parsed = new Date(text);
  return Number.isNaN(parsed.getTime()) ? fallback : parsed;
}

function buildPremiumCache(entitlement = {}, now = new Date(), cacheState = "live") {
  return {
    premium_active: Boolean(entitlement.premiumActive),
    entitlement_status: String(entitlement.subscriptionStatus || "inactive").trim() || "inactive",
    source: String(entitlement.source || "apple_app_store").trim(),
    product_id: String(entitlement.productId || "").trim(),
    entitlement_id: String(entitlement.entitlementId || "").trim(),
    expires_at: String(entitlement.expiresAt || "").trim(),
    last_synced_at: String(entitlement.lastSyncedAt || nowIso(now)).trim(),
    cache_state: cacheState,
  };
}

function isCachedPremiumUsable(cache = {}, now = new Date()) {
  if (!cache || !cache.premium_active) {
    return false;
  }
  const expiresAt = toDate(cache.expires_at, null);
  if (expiresAt && now.getTime() <= expiresAt.getTime()) {
    return true;
  }
  const syncedAt = toDate(cache.last_synced_at, null);
  if (!syncedAt) {
    return false;
  }
  const graceMs = ENTITLEMENT_CACHE_GRACE_HOURS * 60 * 60 * 1000;
  return now.getTime() - syncedAt.getTime() <= graceMs;
}

function buildPaywallState({ quotaSnapshot, premiumState, product }) {
  return {
    visible: Boolean(!premiumState.premiumActive && quotaSnapshot.paywall_required),
    premiumActive: Boolean(premiumState.premiumActive),
    blockedReason: !premiumState.premiumActive && quotaSnapshot.paywall_required ? "free_limit_reached" : "",
    productId: product?.productId || "",
    priceDisplay: product?.priceDisplay || "",
    restoreAvailable: true,
  };
}

function buildUnavailableMonetizationState({
  now = new Date(),
  platform = "ios",
  status = "secure_storage_unavailable",
  blockedReason = "secure_storage_unavailable",
} = {}) {
  const fallbackProduct = getBillingProduct(platform);
  const initialState = createInitialCommerceState(now);
  const resolved = resolveQuotaState(initialState, {
    now,
    premiumActive: false,
  });
  return {
    ok: false,
    status,
    blockedReason,
    appUserId: "",
    secureStorageAvailable: false,
    is_bootstrapping: false,
    premiumActive: false,
    premiumState: {
      ok: false,
      status,
      premiumActive: false,
      subscriptionStatus: "inactive",
      productId: "",
      entitlementId: "",
      source: "apple_app_store",
      currentState: resolved.state,
    },
    quota: resolved.snapshot,
    quotaView: buildQuotaViewModel(resolved.snapshot, now, {
      premiumActive: false,
      expiresAt: "",
    }),
    paywall: buildPaywallState({
      quotaSnapshot: resolved.snapshot,
      premiumState: { premiumActive: false },
      product: fallbackProduct,
    }),
    productCatalog: {
      ok: false,
      status: "catalog_unavailable",
      product: { ...fallbackProduct, is_valid: false },
      usesFallback: true,
      storeMetadata: getStoreMetadata(),
    },
    product: { ...fallbackProduct, is_valid: false },
    storeMetadata: getStoreMetadata(),
  };
}

export function createMonetizationService({
  platform = "ios",
  identityService = createDeviceIdentityService(),
  stateStore = createCommerceStateStore(),
  billingService,
  nowProvider = () => new Date(),
} = {}) {
  let syncInFlight = null;
  let purchaseRestoreInFlight = null;

  async function getProductCatalog({ appUserId = "" } = {}) {
    const fallbackProduct = getBillingProduct(platform);
    if (!billingService || typeof billingService.getCatalog !== "function") {
      return {
        ok: false,
        status: "catalog_unavailable",
        product: { ...fallbackProduct, is_valid: false },
        usesFallback: true,
        storeMetadata: getStoreMetadata(),
      };
    }

    const catalog = await billingService.getCatalog(platform, { appUserId });
    const liveProduct = Array.isArray(catalog?.products) ? catalog.products[0] || null : null;
    const product = liveProduct
      ? { ...liveProduct, is_valid: liveProduct.is_valid !== false }
      : { ...fallbackProduct, is_valid: false };
    return {
      ok: Boolean(catalog?.ok),
      status: catalog?.status || "catalog_unavailable",
      product,
      usesFallback: !liveProduct,
      storeMetadata: catalog?.storeMetadata || getStoreMetadata(),
      catalog,
    };
  }

  async function loadOrCreateState(now = nowProvider()) {
    const stored = await stateStore.loadState();
    if (!stored.ok) {
      return stored;
    }
    const state = stored.state || createInitialCommerceState(now);
    if (!stored.state) {
      await stateStore.saveState(state);
    }
    return {
      ok: true,
      status: stored.state ? "state_loaded" : "state_initialized",
      state,
    };
  }

  async function refreshPremiumState({
    appUserId,
    now = nowProvider(),
    currentState = null,
  } = {}) {
    const stateResult = currentState
      ? { ok: true, state: currentState }
      : await loadOrCreateState(now);
    if (!stateResult.ok) {
      return buildUnavailableMonetizationState({ now, platform });
    }
    const state = stateResult.state;

    if (!billingService || typeof billingService.refreshSubscriptionStatus !== "function") {
      const cached = state.cached_premium_state || {};
      return {
        ok: true,
        status: isCachedPremiumUsable(cached, now) ? "premium_cached" : "premium_inactive",
        premiumActive: isCachedPremiumUsable(cached, now),
        subscriptionStatus: cached.entitlement_status || "inactive",
        productId: cached.product_id || "",
        entitlementId: cached.entitlement_id || "",
        source: cached.source || "",
        lastSyncedAt: cached.last_synced_at || "",
        expiresAt: cached.expires_at || "",
        currentState: state,
      };
    }

    const refreshed = await billingService.refreshSubscriptionStatus({
      platform,
      appUserId,
    });

    if (refreshed.ok) {
      const nextState = {
        ...state,
        cached_premium_state: buildPremiumCache(
          {
            premiumActive: refreshed.premiumActive,
            subscriptionStatus: refreshed.subscriptionStatus,
            productId: refreshed.productId,
            entitlementId: refreshed.entitlementId,
            source: refreshed.source,
            expiresAt: refreshed.expiresAt,
            lastSyncedAt: refreshed.lastSyncedAt || nowIso(now),
          },
          now,
          "live"
        ),
      };
      await stateStore.saveState(nextState);
      return {
        ok: true,
        status: refreshed.status,
        premiumActive: Boolean(refreshed.premiumActive),
        subscriptionStatus: refreshed.subscriptionStatus || "inactive",
        productId: refreshed.productId || "",
        entitlementId: refreshed.entitlementId || "",
        source: refreshed.source || "apple_app_store",
        lastSyncedAt: refreshed.lastSyncedAt || nowIso(now),
        expiresAt: refreshed.expiresAt || "",
        currentState: nextState,
      };
    }

    const cached = state.cached_premium_state || {};
    if (isCachedPremiumUsable(cached, now)) {
      return {
        ok: true,
        status: "premium_cached",
        premiumActive: true,
        subscriptionStatus: cached.entitlement_status || "active",
        productId: cached.product_id || "",
        entitlementId: cached.entitlement_id || "",
        source: cached.source || "apple_app_store",
        lastSyncedAt: cached.last_synced_at || "",
        expiresAt: cached.expires_at || "",
        currentState: {
          ...state,
          cached_premium_state: {
            ...cached,
            cache_state: "cached",
          },
        },
      };
    }

    const nextState = {
      ...state,
      cached_premium_state: buildPremiumCache(
        {
          premiumActive: false,
          subscriptionStatus: "inactive",
          source: "apple_app_store",
        },
        now,
        "live"
      ),
    };
    await stateStore.saveState(nextState);
    return {
      ok: false,
      status: refreshed.status || "premium_refresh_failed",
      premiumActive: false,
      subscriptionStatus: "inactive",
      productId: "",
      entitlementId: "",
      source: "apple_app_store",
      lastSyncedAt: "",
      expiresAt: "",
      currentState: nextState,
    };
  }

  async function resolveMonetizationState({ now = nowProvider() } = {}) {
    const installation = await identityService.getOrCreateInstallationId();
    if (!installation.ok) {
      return buildUnavailableMonetizationState({ now, platform });
    }

    const premiumState = await refreshPremiumState({
      appUserId: installation.installationId,
      now,
    });
    const stateResult = premiumState.currentState
      ? { ok: true, state: premiumState.currentState }
      : await loadOrCreateState(now);
    if (!stateResult.ok) {
      return buildUnavailableMonetizationState({ now, platform });
    }
    const state = stateResult.state;
    const resolved = resolveQuotaState(state, {
      now,
      premiumActive: premiumState.premiumActive,
    });
    if (resolved.state !== state) {
      await stateStore.saveState(resolved.state);
    }

    const productCatalog = await getProductCatalog({
      appUserId: installation.installationId,
    });
    const product = productCatalog.product;
    return {
      ok: true,
      status: "monetization_ready",
      appUserId: installation.installationId,
      secureStorageAvailable: true,
      is_bootstrapping: false,
      premiumActive: Boolean(premiumState.premiumActive),
      premiumState,
      quota: resolved.snapshot,
      quotaView: buildQuotaViewModel(resolved.snapshot, now, premiumState),
      paywall: buildPaywallState({
        quotaSnapshot: resolved.snapshot,
        premiumState,
        product,
      }),
      productCatalog,
      product,
      storeMetadata: productCatalog.storeMetadata || getStoreMetadata(),
    };
  }

  async function getMonetizationState({ now = nowProvider(), waitForMutation = true } = {}) {
    if (waitForMutation && purchaseRestoreInFlight) {
      await purchaseRestoreInFlight.catch(() => null);
    }
    if (syncInFlight) {
      return syncInFlight;
    }
    syncInFlight = (async () => resolveMonetizationState({ now }))().finally(() => {
      syncInFlight = null;
    });
    return syncInFlight;
  }

  async function runGatedAnalysis({
    analysisId,
    runAnalysis,
    now = nowProvider(),
  } = {}) {
    const monetization = await getMonetizationState({ now });
    if (!monetization.ok) {
      return monetization;
    }
    if (monetization.paywall.visible) {
      return {
        ok: false,
        status: "paywall_required",
        blockedReason: "free_limit_reached",
        premiumActive: monetization.premiumActive,
        quota: monetization.quota,
        paywall: monetization.paywall,
      };
    }

    try {
      const result = await runAnalysis();
      if (!monetization.premiumActive) {
        const recorded = recordCompletedAnalysisForQuota(monetization.premiumState.currentState, {
          analysisId,
          now,
          premiumActive: false,
        });
        await stateStore.saveState(recorded.state);
        return {
          ok: true,
          status: "analysis_completed",
          recordedUsage: recorded.recorded,
          result,
          quota: recorded.snapshot,
          paywall: buildPaywallState({
            quotaSnapshot: recorded.snapshot,
            premiumState: monetization.premiumState,
            product: monetization.product,
          }),
        };
      }
      return {
        ok: true,
        status: "analysis_completed",
        recordedUsage: false,
        result,
        quota: monetization.quota,
        paywall: monetization.paywall,
      };
    } catch (error) {
      return Promise.reject(error);
    }
  }

  async function purchasePremium({ now = nowProvider() } = {}) {
    if (purchaseRestoreInFlight) {
      return purchaseRestoreInFlight;
    }
    purchaseRestoreInFlight = (async () => {
      const installation = await identityService.getOrCreateInstallationId();
      if (!installation.ok) {
        return buildUnavailableMonetizationState({ now, platform });
      }
      const productCatalog = await getProductCatalog({
        appUserId: installation.installationId,
      });
      if (!productCatalog.product?.is_valid) {
        return {
          ok: false,
          status: "product_unavailable",
          message: "The premium subscription is not available in this build yet.",
          entitlementConfirmed: false,
          premiumActive: false,
          paywallVisible: false,
        };
      }
      if (!billingService || typeof billingService.initiatePurchase !== "function") {
        return {
          ok: false,
          status: "billing_unavailable",
          message: "The Apple billing layer is not configured in this mobile runtime yet.",
          paywallVisible: false,
          entitlementConfirmed: false,
          premiumActive: false,
        };
      }
      const purchaseResult = await billingService.initiatePurchase({
        platform,
        appUserId: installation.installationId,
        productId: productCatalog.product.productId,
      });
      const monetization = await getMonetizationState({ now, waitForMutation: false });
      const entitlementConfirmed = Boolean(monetization.premiumActive);
      return {
        ...purchaseResult,
        ok: purchaseResult.ok && entitlementConfirmed,
        status: purchaseResult.ok
          ? entitlementConfirmed
            ? "purchase_completed"
            : "purchase_unverified"
          : purchaseResult.status,
        entitlementConfirmed,
        premiumActive: entitlementConfirmed,
        subscriptionStatus: monetization.premiumState?.subscriptionStatus || "inactive",
        productId: monetization.premiumState?.productId || productCatalog.product.productId || "",
        entitlementId: monetization.premiumState?.entitlementId || "",
        expiresAt: monetization.premiumState?.expiresAt || "",
        lastSyncedAt: monetization.premiumState?.lastSyncedAt || "",
        source: monetization.premiumState?.source || "apple_app_store",
        paywallVisible: Boolean(monetization.paywall?.visible),
      };
    })().finally(() => {
      purchaseRestoreInFlight = null;
    });
    return purchaseRestoreInFlight;
  }

  async function restorePurchases({ now = nowProvider() } = {}) {
    if (purchaseRestoreInFlight) {
      return purchaseRestoreInFlight;
    }
    purchaseRestoreInFlight = (async () => {
      const installation = await identityService.getOrCreateInstallationId();
      if (!installation.ok) {
        return buildUnavailableMonetizationState({ now, platform });
      }
      if (!billingService || typeof billingService.restorePurchases !== "function") {
        return {
          ok: false,
          status: "billing_unavailable",
          message: "The Apple billing layer is not configured in this mobile runtime yet.",
          paywallVisible: false,
          entitlementConfirmed: false,
          premiumActive: false,
        };
      }
      const restoreResult = await billingService.restorePurchases({
        platform,
        appUserId: installation.installationId,
      });
      const monetization = await getMonetizationState({ now, waitForMutation: false });
      const entitlementConfirmed = Boolean(monetization.premiumActive);
      return {
        ...restoreResult,
        ok: restoreResult.ok && entitlementConfirmed,
        status: restoreResult.ok
          ? entitlementConfirmed
            ? "restore_completed"
            : "restore_no_active_entitlement"
          : restoreResult.status,
        entitlementConfirmed,
        premiumActive: entitlementConfirmed,
        subscriptionStatus: monetization.premiumState?.subscriptionStatus || "inactive",
        productId: monetization.premiumState?.productId || "",
        entitlementId: monetization.premiumState?.entitlementId || "",
        expiresAt: monetization.premiumState?.expiresAt || "",
        lastSyncedAt: monetization.premiumState?.lastSyncedAt || "",
        source: monetization.premiumState?.source || "apple_app_store",
        paywallVisible: Boolean(monetization.paywall?.visible),
      };
    })().finally(() => {
      purchaseRestoreInFlight = null;
    });
    return purchaseRestoreInFlight;
  }

  async function resetStateForTests() {
    return stateStore.clearStateForTests();
  }

  return {
    getMonetizationState,
    getProductCatalog,
    refreshPremiumState,
    runGatedAnalysis,
    purchasePremium,
    restorePurchases,
    resetStateForTests,
  };
}
