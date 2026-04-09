import test from "node:test";
import assert from "node:assert/strict";

import { createProviderFlowController } from "../src/providers/providerFlowController.js";

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

function makeJsonResponse(status, payload) {
  return {
    ok: status >= 200 && status < 300,
    status,
    async text() {
      return JSON.stringify(payload);
    },
  };
}

test("controller save, validate, and remove flow works end-to-end", async () => {
  const controller = createProviderFlowController({
    secureStoreModule: makeMockSecureStore(),
  });
  let state = controller.buildBaseState();

  const saveStep = await controller.saveCredential({
    providerName: "openai",
    apiKey: "sk-test",
    consentAcknowledged: true,
    currentState: state,
  });
  state = saveStep.state;
  assert.equal(state.credentialPresent, true);
  assert.equal(Boolean(state.maskedCredential), true);

  const validateStep = await controller.validateProvider({
    providerName: "openai",
    consentAcknowledged: true,
    currentState: state,
    fetchImpl: async () => makeJsonResponse(200, { id: "ok" }),
  });
  state = validateStep.state;
  assert.equal(state.validationResult.status, "ready");

  const removeStep = await controller.removeCredential({
    providerName: "openai",
    consentAcknowledged: true,
    currentState: state,
  });
  assert.equal(removeStep.state.credentialPresent, false);
});

test("controller verify flow saves first and keeps the draft on invalid keys", async () => {
  const controller = createProviderFlowController({
    secureStoreModule: makeMockSecureStore(),
  });

  const verifyStep = await controller.verifyCredential({
    providerName: "openai",
    apiKey: "sk-invalid",
    consentAcknowledged: true,
    currentState: controller.buildBaseState(),
    fetchImpl: async () => makeJsonResponse(401, { error: { message: "bad key" } }),
  });

  assert.equal(verifyStep.result.status, "invalid_credentials");
  assert.equal(verifyStep.state.credentialPresent, true);
  assert.equal(verifyStep.state.draftCredential, "sk-invalid");
});

test("controller run flow is gated when validation fails", async () => {
  const controller = createProviderFlowController({
    secureStoreModule: makeMockSecureStore(),
  });
  const saveStep = await controller.saveCredential({
    providerName: "openai",
    apiKey: "sk-test",
    consentAcknowledged: true,
    currentState: controller.buildBaseState(),
  });

  const runStep = await controller.runExternalSummary({
    providerName: "openai",
    consentAcknowledged: true,
    currentState: saveStep.state,
    fetchImpl: async () => makeJsonResponse(401, { error: { message: "bad key" } }),
  });

  assert.equal(runStep.result.status, "invalid_credentials");
  assert.equal(runStep.state.lastRunResult.status, "invalid_credentials");
});

test("controller run flow keeps local-first behavior when the provider is unavailable", async () => {
  const controller = createProviderFlowController({
    secureStoreModule: makeMockSecureStore(),
  });
  const saveStep = await controller.saveCredential({
    providerName: "openai",
    apiKey: "sk-test",
    consentAcknowledged: true,
    currentState: controller.buildBaseState(),
  });

  const runStep = await controller.runExternalSummary({
    providerName: "openai",
    consentAcknowledged: true,
    currentState: {
      ...saveStep.state,
      validationResult: {
        status: "ready",
        ready: true,
      },
    },
    fetchImpl: async () => {
      throw new Error("Network unavailable");
    },
  });

  assert.equal(runStep.result.status, "provider_unavailable");
  assert.equal(runStep.result.external_processing_used, false);
  assert.equal(runStep.result.external_summary, null);
});

test("controller reports secure storage unavailable without insecure fallback", async () => {
  const controller = createProviderFlowController({
    secureStoreModule: makeMockSecureStore({ available: false }),
  });
  const runStep = await controller.validateProvider({
    providerName: "groq",
    consentAcknowledged: true,
    currentState: controller.buildBaseState(),
  });

  assert.equal(runStep.result.status, "secure_storage_unavailable");
});

test("controller does not default storage to unavailable before hydration resolves", async () => {
  const controller = createProviderFlowController({
    secureStoreModule: makeMockSecureStore(),
  });

  const initialState = controller.buildBaseState();
  assert.equal(initialState.secureStorageAvailable, null);
  assert.equal(initialState.storageResolved, false);

  const hydratedState = await controller.hydrateProviderState({
    providerName: "",
    currentState: initialState,
  });

  assert.equal(hydratedState.secureStorageAvailable, true);
  assert.equal(hydratedState.storageResolved, true);
});
