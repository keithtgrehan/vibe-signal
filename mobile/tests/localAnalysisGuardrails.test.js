import test from "node:test";
import assert from "node:assert/strict";

import { sanitizeLocalAnalysisResult } from "../src/screens/localAnalysisGuardrails.js";

test("local analysis guardrails rewrite certainty and accusation language before render", () => {
  const result = sanitizeLocalAnalysisResult({
    headline: "This proves something",
    pattern: "This shows they are cheating.",
    summary: "This means they are lying.",
    highlights: ["Red flag", "Suspicious shift"],
    spans: [{ label: "Later", excerpt: "Caught" }],
    disclosure: "Pattern-based only.",
    shareTitle: "VibeSignal",
    shareText: "This proves they are manipulative.",
  });

  const combined = [
    result.headline,
    result.pattern,
    result.summary,
    ...result.highlights,
    result.shareText,
  ].join(" ");

  assert.equal(/proves/i.test(combined), false);
  assert.equal(/cheating/i.test(combined), false);
  assert.equal(/lying/i.test(combined), false);
  assert.equal(/manipulative/i.test(combined), false);
});
