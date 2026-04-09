import { FREE_ANALYSIS_LIMIT, SUBSCRIPTION_REQUIRED_AFTER_LIMIT } from "./config.js";

function missingTransport(statusMessage) {
  return {
    ok: false,
    status: "transport_unavailable",
    message: statusMessage,
  };
}

function invalidArtifact(statusMessage) {
  return {
    ok: false,
    status: "invalid_purchase_artifact",
    message: statusMessage,
  };
}

export function createEntitlementClient({ transport } = {}) {
  async function send(action, payload) {
    if (!transport || typeof transport.send !== "function") {
      return missingTransport("No entitlement transport is configured for this mobile shell.");
    }
    return transport.send({
      action,
      payload,
    });
  }

  function normalizePurchaseArtifact(platform, purchaseArtifact = {}) {
    const normalizedPlatform = String(platform || "").trim().toLowerCase();
    if (normalizedPlatform === "ios") {
      if (!purchaseArtifact || purchaseArtifact.artifact_type !== "apple_app_store_receipt") {
        return invalidArtifact("An Apple receipt artifact is required before verification.");
      }
      const receiptData = String(purchaseArtifact.receipt_data_b64 || "").trim();
      if (!receiptData) {
        return invalidArtifact("The Apple receipt payload is missing receipt_data_b64.");
      }
      return {
        ok: true,
        payload: {
          purchase_artifact: {
            artifact_type: "apple_app_store_receipt",
            receipt_data_b64: receiptData,
            transaction_id: String(purchaseArtifact.transaction_id || "").trim(),
            original_transaction_id: String(purchaseArtifact.original_transaction_id || "").trim(),
            environment: String(purchaseArtifact.environment || "").trim(),
            bundle_id: String(purchaseArtifact.bundle_id || "").trim(),
          },
        },
      };
    }
    if (normalizedPlatform === "android") {
      if (!purchaseArtifact || purchaseArtifact.artifact_type !== "google_play_purchase_token") {
        return invalidArtifact("A Google Play purchase token artifact is required before verification.");
      }
      const purchaseToken = String(purchaseArtifact.purchase_token || "").trim();
      const packageName = String(purchaseArtifact.package_name || "").trim();
      if (!purchaseToken || !packageName) {
        return invalidArtifact("The Google Play purchase artifact is missing token or package details.");
      }
      return {
        ok: true,
        payload: {
          purchase_artifact: {
            artifact_type: "google_play_purchase_token",
            purchase_token: purchaseToken,
            package_name: packageName,
            order_id: String(purchaseArtifact.order_id || "").trim(),
            purchase_state: String(purchaseArtifact.purchase_state || "").trim(),
            acknowledged: Boolean(purchaseArtifact.acknowledged),
            obfuscated_account_id: String(purchaseArtifact.obfuscated_account_id || "").trim(),
          },
        },
      };
    }
    return invalidArtifact("Unsupported billing platform for purchase verification.");
  }

  return {
    freeAnalysisLimit: FREE_ANALYSIS_LIMIT,
    subscriptionRequiredAfterLimit: SUBSCRIPTION_REQUIRED_AFTER_LIMIT,
    fetchEntitlement({ appUserId, deviceInstallationId, platform } = {}) {
      return send("fetch_entitlement", {
        app_user_id: appUserId,
        device_installation_id: deviceInstallationId,
        platform,
      });
    },
    submitPurchaseVerification({
      appUserId,
      platform,
      productId,
      purchaseArtifact,
      transactionId = "",
      originalTransactionId = "",
      purchaseId = "",
    } = {}) {
      const normalizedArtifact = normalizePurchaseArtifact(platform, purchaseArtifact);
      if (!normalizedArtifact.ok) {
        return normalizedArtifact;
      }
      return send("submit_purchase_verification", {
        app_user_id: appUserId,
        platform,
        product_id: productId,
        transaction_id: transactionId,
        original_transaction_id: originalTransactionId,
        purchase_id: purchaseId,
        ...normalizedArtifact.payload,
      });
    },
    restorePurchases({ appUserId, platform } = {}) {
      return send("restore_purchases", {
        app_user_id: appUserId,
        platform,
      });
    },
    recordCompletedAnalysis({ appUserId, analysisId, conversationId } = {}) {
      return send("record_completed_analysis", {
        app_user_id: appUserId,
        analysis_id: analysisId,
        conversation_id: conversationId,
      });
    },
    normalizePurchaseArtifact,
  };
}
