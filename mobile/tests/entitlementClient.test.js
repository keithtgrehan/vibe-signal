import test from "node:test";
import assert from "node:assert/strict";

import { createEntitlementClient } from "../src/commerce/entitlementClient.js";

test("entitlement client fails clearly without a configured transport", async () => {
  const client = createEntitlementClient();
  const result = await client.fetchEntitlement({
    appUserId: "app_user_test",
    platform: "ios",
  });

  assert.equal(result.ok, false);
  assert.equal(result.status, "transport_unavailable");
});

test("entitlement client forwards structured purchase verification payloads", async () => {
  let captured = null;
  const client = createEntitlementClient({
    transport: {
      async send(request) {
        captured = request;
        return {
          ok: true,
          status: "submitted",
        };
      },
    },
  });

  const result = await client.submitPurchaseVerification({
    appUserId: "app_user_test",
    platform: "ios",
    productId: "vibesignal_pro_monthly_ios",
    purchaseArtifact: {
      artifact_type: "apple_app_store_receipt",
      receipt_data_b64: "receipt-token",
      transaction_id: "tx-123",
    },
    transactionId: "tx-123",
  });

  assert.equal(result.ok, true);
  assert.equal(captured.action, "submit_purchase_verification");
  assert.equal(captured.payload.app_user_id, "app_user_test");
  assert.equal(captured.payload.product_id, "vibesignal_pro_monthly_ios");
  assert.equal(captured.payload.purchase_artifact.artifact_type, "apple_app_store_receipt");
});

test("entitlement client rejects malformed purchase artifacts before transport", async () => {
  const client = createEntitlementClient({
    transport: {
      async send() {
        throw new Error("transport should not be called");
      },
    },
  });
  const result = await client.submitPurchaseVerification({
    appUserId: "app_user_test",
    platform: "android",
    productId: "vibesignal_pro_monthly_android",
    purchaseArtifact: {
      artifact_type: "google_play_purchase_token",
      purchase_token: "",
      package_name: "",
    },
  });

  assert.equal(result.ok, false);
  assert.equal(result.status, "invalid_purchase_artifact");
});
