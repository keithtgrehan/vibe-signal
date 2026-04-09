import test from "node:test";
import assert from "node:assert/strict";

import { createProviderCredentialService } from "../src/providers/providerCredentialService.js";

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

test("provider state reflects credential presence", async () => {
  const service = createProviderCredentialService({
    secureStoreModule: makeMockSecureStore(),
  });

  const initialState = await service.getProviderCredentialState({
    providerName: "anthropic",
    displayName: "Anthropic",
    enabled: true,
    authMode: "byok",
    providerMode: "external_summary_optional",
  });
  assert.equal(initialState.status, "provider_enabled_no_credential");

  await service.saveProviderCredential("anthropic", "anthropic-secret");

  const readyState = await service.getProviderCredentialState({
    providerName: "anthropic",
    displayName: "Anthropic",
    enabled: true,
    authMode: "byok",
    providerMode: "external_summary_optional",
  });
  assert.equal(readyState.status, "provider_ready");
  assert.equal(readyState.credential_present, true);
});

test("disconnect deletes the secure credential", async () => {
  const service = createProviderCredentialService({
    secureStoreModule: makeMockSecureStore(),
  });

  await service.saveProviderCredential("openai", "sk-delete-me");
  const disconnectResult = await service.disconnectProvider("openai");
  assert.equal(disconnectResult.ok, true);

  const state = await service.getProviderCredentialState({
    providerName: "openai",
    displayName: "OpenAI",
    enabled: true,
    authMode: "byok",
    providerMode: "external_summary_optional",
  });
  assert.equal(state.status, "provider_enabled_no_credential");
});

test("masked saved-state is returned without exposing the raw key", async () => {
  const service = createProviderCredentialService({
    secureStoreModule: makeMockSecureStore(),
  });

  await service.saveProviderCredential("groq", "gsk_1234567890");
  const masked = await service.getMaskedProviderCredential("groq");
  assert.equal(masked.credentialPresent, true);
  assert.equal(masked.maskedCredential.includes("1234567890"), false);
  assert.equal(masked.maskedCredential, "••••7890");
});
