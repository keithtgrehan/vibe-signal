import test from "node:test";
import assert from "node:assert/strict";

import { createInternalDiagnosticsStore } from "../src/services/internalDiagnostics.js";

test("internal diagnostics store keeps a bounded recent history", () => {
  const seen = [];
  const store = createInternalDiagnosticsStore({
    limit: 2,
    nowProvider: () => 1712652000000,
    logger: {
      warn(message) {
        seen.push(message);
      },
    },
  });

  store.capture({ category: "logging", code: "one", message: "first" });
  store.capture({ category: "logging", code: "two", message: "second" });
  store.capture({ category: "logging", code: "three", message: "third" });

  const entries = store.list();
  assert.equal(entries.length, 2);
  assert.equal(entries[0].code, "two");
  assert.equal(entries[1].code, "three");
  assert.equal(seen.length, 3);
});
