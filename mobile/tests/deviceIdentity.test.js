import test from "node:test";
import assert from "node:assert/strict";

import { createDeviceIdentityService } from "../src/commerce/deviceIdentity.js";

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

test("device identity persists securely when storage is available", async () => {
  const service = createDeviceIdentityService({
    secureStoreModule: makeMockSecureStore(),
  });
  const first = await service.getOrCreateInstallationId();
  const second = await service.getOrCreateInstallationId();

  assert.equal(first.ok, true);
  assert.equal(second.ok, true);
  assert.equal(Boolean(first.installationId), true);
  assert.equal(first.installationId, second.installationId);
});

test("device identity fails closed when secure storage is unavailable", async () => {
  const service = createDeviceIdentityService({
    secureStoreModule: makeMockSecureStore({ available: false }),
  });
  const result = await service.getOrCreateInstallationId();

  assert.equal(result.ok, false);
  assert.equal(result.status, "secure_storage_unavailable");
});

test("device identity does not fall back when the secure store module is incomplete", async () => {
  const service = createDeviceIdentityService({
    secureStoreModule: {
      async isAvailableAsync() {
        return true;
      },
    },
  });
  const result = await service.getOrCreateInstallationId();

  assert.equal(result.ok, false);
  assert.equal(result.status, "secure_storage_unavailable");
  assert.equal(result.installationId, "");
});

test("device identity can be cleared explicitly for tests", async () => {
  const service = createDeviceIdentityService({
    secureStoreModule: makeMockSecureStore(),
  });
  const first = await service.getOrCreateInstallationId();
  await service.clearInstallationIdForTests();
  const second = await service.getOrCreateInstallationId();

  assert.equal(first.ok, true);
  assert.equal(second.ok, true);
  assert.notEqual(first.installationId, second.installationId);
});
