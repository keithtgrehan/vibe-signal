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

test("analysis history strips raw input, previews, share text, and result payloads before persistence", async () => {
  const persisted = new Map();
  const store = createAnalysisHistoryStore({
    platform: "web",
    webStorage: {
      getItem(key) {
        return persisted.get(key) || null;
      },
      setItem(key, value) {
        persisted.set(key, value);
      },
      removeItem(key) {
        persisted.delete(key);
      },
    },
  });

  const rawInput = "self: synthetic alpha message\nother: synthetic beta reply";
  await store.addAnalysis({
    id: "private_case",
    inputText: rawInput,
    inputPreview: rawInput.slice(0, 24),
    headline: "Local pattern analysis ready",
    pattern: "Specificity changed",
    summary: "Metadata-safe summary",
    shareText: `Share text with ${rawInput}`,
    mode: "local",
    cueLabels: ["specificity_drop"],
    syntheticFixtureId: "qa_specificity_drop_001",
    result: {
      spans: [{ excerpt: rawInput }],
    },
  });

  const serialized = [...persisted.values()].join("\n");
  const items = await store.getRecentAnalyses();

  assert.equal(serialized.includes(rawInput), false);
  assert.equal(serialized.includes("synthetic alpha message"), false);
  assert.equal(serialized.includes("Share text with"), false);
  assert.equal(Object.hasOwn(items[0], "inputText"), false);
  assert.equal(Object.hasOwn(items[0], "inputPreview"), false);
  assert.equal(Object.hasOwn(items[0], "shareText"), false);
  assert.equal(Object.hasOwn(items[0], "result"), false);
  assert.deepEqual(items[0].cueLabels, ["specificity_drop"]);
  assert.equal(items[0].syntheticFixtureId, "qa_specificity_drop_001");
});
