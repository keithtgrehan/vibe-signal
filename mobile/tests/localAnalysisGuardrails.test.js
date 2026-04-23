import test from "node:test";
import assert from "node:assert/strict";

import { sanitizeLocalAnalysisResult } from "../src/screens/localAnalysisGuardrails.js";

test("local analysis guardrails rewrite certainty and accusation language before render", () => {
  const result = sanitizeLocalAnalysisResult({
    headline: "This proves something",
    signalLabel: "High certainty",
    analysisMode: "fallback",
    pattern: "This shows they are cheating.",
    summary: "This means they are lying.",
    suggestion: "This proves they are manipulative.",
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
    result.suggestion,
    ...result.highlights,
    result.shareText,
  ].join(" ");

  assert.equal(/proves/i.test(combined), false);
  assert.equal(/cheating/i.test(combined), false);
  assert.equal(/lying/i.test(combined), false);
  assert.equal(/manipulative/i.test(combined), false);
  assert.equal(result.analysisMode, "fallback");
});

test("local analysis guardrails keep missing new fields render-safe for older payloads", () => {
  const result = sanitizeLocalAnalysisResult({
    headline: "Tone appears consistent",
    pattern: "Nothing clearly changed here.",
  });

  assert.equal(result.analysisMode, "");
  assert.equal(result.suggestion, "");
  assert.deepEqual(result.highlights, []);
  assert.deepEqual(result.spans, []);
  assert.equal(result.signalLabel, "");
});
