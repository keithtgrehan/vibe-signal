import test from "node:test";
import assert from "node:assert/strict";

import { createAnalysisHistoryStore } from "../src/screens/analysisHistoryStore.js";

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

test("analysis history keeps only the last three saved analyses", async () => {
  const store = createAnalysisHistoryStore({
    secureStoreModule: makeMockSecureStore(),
  });

  for (const id of ["a1", "a2", "a3", "a4"]) {
    await store.addAnalysis({
      id,
      inputPreview: id,
      headline: "Local pattern analysis ready",
      pattern: `Pattern ${id}`,
      summary: `Summary ${id}`,
      shareText: `Share ${id}`,
      result: { pattern: `Pattern ${id}` },
    });
  }

  const items = await store.getRecentAnalyses();
  assert.deepEqual(
    items.map((item) => item.id),
    ["a2", "a3", "a4"]
  );
});
