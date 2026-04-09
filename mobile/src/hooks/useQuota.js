import { AppState } from "react-native";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { getSharedMonetizationService } from "../commerce/mobileCommerce.js";
import { getSharedInternalDiagnosticsStore } from "../services/internalDiagnostics.js";
import { getSharedMobileEventLogger } from "../services/mobileEventLogger.js";
import { buildQuotaHookState } from "./quotaViewModel.js";

const logger = getSharedMobileEventLogger();
const diagnostics = getSharedInternalDiagnosticsStore();

export function useQuota(service = getSharedMonetizationService()) {
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState("");
  const [monetization, setMonetization] = useState(null);
  const [purchaseResult, setPurchaseResult] = useState(null);
  const [restoreResult, setRestoreResult] = useState(null);
  const analysisInFlightRef = useRef(false);
  const readinessSignatureRef = useRef("");

  const safeRefresh = useCallback(async () => {
    try {
      const result = await service.getMonetizationState();
      setMonetization(result);
      return result;
    } catch (_error) {
      const fallback = {
        ok: false,
        status: "monetization_unavailable",
        secureStorageAvailable: false,
        is_bootstrapping: false,
        premiumActive: false,
        premiumState: {
          status: "premium_inactive",
        },
        quota: {
          current_period_type: "",
          remaining_uses: 0,
          uses_in_current_period: 0,
        },
        quotaView: {
          usesLeft: "0 left",
          periodLabel: "",
          resetTiming: "",
          resetAt: "",
        },
        paywall: {
          visible: false,
          restoreAvailable: true,
        },
        product: {
          productId: "",
          priceDisplay: "",
          is_valid: false,
        },
        productCatalog: {
          usesFallback: true,
        },
      };
      setMonetization(fallback);
      return fallback;
    } finally {
      setLoading(false);
      setAction("");
    }
  }, [service]);

  const refresh = useCallback(async () => {
    setAction("refresh");
    return safeRefresh();
  }, [safeRefresh]);

  useEffect(() => {
    let cancelled = false;
    refresh().then((result) => {
      if (cancelled) {
        return;
      }
      setMonetization(result);
    });

    const subscription = AppState.addEventListener("change", (nextState) => {
      if (nextState === "active") {
        void logger.notifyForeground();
        void refresh();
      }
    });
    return () => {
      cancelled = true;
      subscription?.remove?.();
    };
  }, [refresh]);

  const purchasePremium = useCallback(async () => {
    setAction("purchase");
    setPurchaseResult(null);
    void logger.logBilling({
      type: "purchase_attempt",
      status: "started",
      productId: monetization?.product?.productId || "",
      entitlementName: monetization?.premiumState?.entitlementId || "",
    });
    try {
      const result = await service.purchasePremium();
      setPurchaseResult(result);
      void logger.logBilling({
        type: "purchase_result",
        status: result.status || (result.ok ? "purchase_completed" : "purchase_failed"),
        productId: result.productId || monetization?.product?.productId || "",
        entitlementName: result.entitlementId || monetization?.premiumState?.entitlementId || "",
      });
      const refreshed = await service.getMonetizationState();
      setMonetization(refreshed);
      return result;
    } catch (_error) {
      diagnostics.capture({
        category: "monetization",
        code: "purchase_failed_safe_fallback",
        severity: "warn",
        message: "Purchase fell back to a safe local failure state.",
      });
      const fallback = {
        ok: false,
        status: "purchase_failed",
        message: "The premium purchase couldn't be completed right now.",
        entitlementConfirmed: false,
      };
      setPurchaseResult(fallback);
      void logger.logBilling({
        type: "purchase_result",
        status: fallback.status,
        productId: monetization?.product?.productId || "",
        entitlementName: monetization?.premiumState?.entitlementId || "",
      });
      return fallback;
    } finally {
      setAction("");
      setLoading(false);
    }
  }, [monetization, service]);

  const restorePurchases = useCallback(async () => {
    setAction("restore");
    setRestoreResult(null);
    void logger.logBilling({
      type: "restore_attempt",
      status: "started",
      productId: monetization?.product?.productId || "",
      entitlementName: monetization?.premiumState?.entitlementId || "",
    });
    try {
      const result = await service.restorePurchases();
      setRestoreResult(result);
      void logger.logBilling({
        type: "restore_result",
        status: result.status || (result.ok ? "restore_completed" : "restore_failed"),
        productId: result.productId || monetization?.product?.productId || "",
        entitlementName: result.entitlementId || monetization?.premiumState?.entitlementId || "",
      });
      const refreshed = await service.getMonetizationState();
      setMonetization(refreshed);
      return result;
    } catch (_error) {
      diagnostics.capture({
        category: "monetization",
        code: "restore_failed_safe_fallback",
        severity: "warn",
        message: "Restore fell back to a safe local failure state.",
      });
      const fallback = {
        ok: false,
        status: "restore_failed",
        message: "Restore couldn't be completed right now.",
        entitlementConfirmed: false,
      };
      setRestoreResult(fallback);
      void logger.logBilling({
        type: "restore_result",
        status: fallback.status,
        productId: monetization?.product?.productId || "",
        entitlementName: monetization?.premiumState?.entitlementId || "",
      });
      return fallback;
    } finally {
      setAction("");
      setLoading(false);
    }
  }, [monetization, service]);

  const recordSuccessfulAnalysis = useCallback(
    async ({ analysisId, runAnalysis }) => {
      if (analysisInFlightRef.current) {
        return {
          ok: false,
          status: "analysis_in_progress",
          recordedUsage: false,
        };
      }
      analysisInFlightRef.current = true;
      setAction("analysis");
      try {
        const result = await service.runGatedAnalysis({
          analysisId,
          runAnalysis,
        });
        const refreshed = await service.getMonetizationState();
        setMonetization(refreshed);
        void logger.logAnalysis({
          analysisId,
          success: Boolean(result.ok),
          mode: "local_analysis",
          status: result.status || "",
        });
        if (result.recordedUsage) {
          void logger.logQuota({
            type: "analysis_consumed",
            remainingAfter: result.quota?.remaining_uses ?? refreshed?.quota?.remaining_uses ?? 0,
            analysisId,
          });
        }
        return result;
      } catch (_error) {
        diagnostics.capture({
          category: "analysis",
          code: "analysis_failed_safe_fallback",
          severity: "warn",
          message: "Local analysis failure was converted into a safe non-crashing result.",
        });
        void logger.logAnalysis({
          analysisId,
          success: false,
          mode: "local_analysis",
          status: "analysis_failed",
        });
        return {
          ok: false,
          status: "analysis_failed",
          recordedUsage: false,
        };
      } finally {
        analysisInFlightRef.current = false;
        setAction("");
        setLoading(false);
      }
    },
    [service]
  );

  const viewState = useMemo(
    () =>
      buildQuotaHookState({
        monetization,
        loading,
        action,
        purchaseResult,
        restoreResult,
      }),
    [monetization, loading, action, purchaseResult, restoreResult]
  );

  useEffect(() => {
    if (!monetization || viewState.is_bootstrapping) {
      return;
    }
    void logger.logState(viewState);
  }, [
    monetization,
    viewState.current_period_type,
    viewState.paywall_required,
    viewState.premium_active,
    viewState.purchase_in_progress,
    viewState.remaining_uses,
    viewState.restore_in_progress,
    viewState.is_bootstrapping,
  ]);

  useEffect(() => {
    if (!monetization || viewState.is_bootstrapping) {
      return;
    }
    void logger.logEntitlementRefresh({
      premium_active: monetization.premiumActive,
      entitlement_name: monetization.premiumState?.entitlementId || "",
      product_id: monetization.premiumState?.productId || monetization.product?.productId || "",
      subscription_status: monetization.premiumState?.subscriptionStatus || "",
    });
  }, [
    monetization,
    monetization?.premiumActive,
    monetization?.premiumState?.entitlementId,
    monetization?.premiumState?.productId,
    monetization?.premiumState?.subscriptionStatus,
    monetization?.product?.productId,
    viewState.is_bootstrapping,
  ]);

  useEffect(() => {
    const readiness = monetization?.storeMetadata?.monetizationReadiness;
    if (!readiness || viewState.is_bootstrapping) {
      return;
    }
    const signature = JSON.stringify({
      errors: readiness.errors || [],
      warnings: readiness.warnings || [],
    });
    if (signature === readinessSignatureRef.current) {
      return;
    }
    readinessSignatureRef.current = signature;
    for (const code of readiness.errors || []) {
      diagnostics.capture({
        category: "monetization_config",
        code,
        severity: "warn",
        message: "A required monetization configuration value is missing in this build.",
      });
    }
    for (const code of readiness.warnings || []) {
      diagnostics.capture({
        category: "monetization_config",
        code,
        severity: "info",
        message: "A monetization configuration warning is present for this build.",
      });
    }
  }, [monetization, viewState.is_bootstrapping]);

  return {
    ...viewState,
    monetization,
    refresh,
    purchasePremium,
    restorePurchases,
    recordSuccessfulAnalysis,
  };
}
