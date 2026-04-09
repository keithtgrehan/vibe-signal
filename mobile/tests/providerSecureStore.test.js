import test from "node:test";
import assert from "node:assert/strict";

import { createProviderSecureStore } from "../src/secureStorage/providerSecureStore.js";

function makeMockSecureStore({ available = true } = {}) {
  const items = new Map();
  const operations = [];
  return {
    operations,
    async isAvailableAsync() {
      operations.push(["available"]);
      return available;
    },
    async setItemAsync(key, value) {
      operations.push(["set", key, value]);
      items.set(key, value);
    },
    async getItemAsync(key) {
      operations.push(["get", key]);
      return items.has(key) ? items.get(key) : null;
    },
    async deleteItemAsync(key) {
      operations.push(["delete", key]);
      items.delete(key);
    },
  };
}

test("secure storage availability awaits the async check and verifies a probe round-trip", async () => {
  const secureStoreModule = makeMockSecureStore();
  const service = createProviderSecureStore({ secureStoreModule });

  const availability = await service.secureStorageAvailable();

  assert.equal(availability.available, true);
  assert.deepEqual(
    secureStoreModule.operations.map(([name]) => name),
    ["available", "set", "get", "delete"]
  );
});

test("secure storage service save/get/delete lifecycle", async () => {
  const service = createProviderSecureStore({
    secureStoreModule: makeMockSecureStore(),
  });

  const saveResult = await service.saveProviderCredential("openai", "sk-test-123");
  assert.equal(saveResult.ok, true);
  assert.equal(saveResult.status, "credential_saved");

  const readResult = await service.getProviderCredential("openai");
  assert.equal(readResult.credentialPresent, true);
  assert.equal(readResult.credential, "sk-test-123");

  const deleteResult = await service.deleteProviderCredential("openai");
  assert.equal(deleteResult.ok, true);
  assert.equal(deleteResult.status, "credential_deleted");

  const afterDelete = await service.getProviderCredential("openai");
  assert.equal(afterDelete.credentialPresent, false);
});

test("secure storage service fails closed when unavailable", async () => {
  const service = createProviderSecureStore({
    secureStoreModule: makeMockSecureStore({ available: false }),
  });

  const saveResult = await service.saveProviderCredential("groq", "gsk-test");
  assert.equal(saveResult.ok, false);
  assert.equal(saveResult.status, "credential_save_blocked");
  assert.equal(saveResult.reason, "secure_storage_unavailable");

  const readResult = await service.getProviderCredential("groq");
  assert.equal(readResult.ok, false);
  assert.equal(readResult.status, "secure_storage_unavailable");
});
