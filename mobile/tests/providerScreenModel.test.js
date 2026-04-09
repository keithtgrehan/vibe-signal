import test from "node:test";
import assert from "node:assert/strict";

import {
  buildAnalysisComposerState,
  buildLocalAnalysisResult,
  getMobileLayoutMetrics,
} from "../src/screens/providerScreenModel.js";

test("mobile layout metrics stay single-column and bounded for narrow viewports", () => {
  const layout = getMobileLayoutMetrics();

  assert.equal(layout.singleColumn, true);
  assert.equal(layout.noHorizontalOverflow, true);
  assert.equal(layout.maxWidth, 480);
  assert.equal(layout.padding, 16);
});

test("analysis input stays visible and analyze enables only when text exists", () => {
  const emptyState = buildAnalysisComposerState({
    analysisText: "",
    loading: false,
    uploadInProgress: false,
    analysisInProgress: false,
    paywallRequired: false,
  });

  assert.equal(emptyState.inputVisible, true);
  assert.equal(emptyState.multiline, true);
  assert.equal(emptyState.analyzeEnabled, false);

  const readyState = buildAnalysisComposerState({
    analysisText: "A visible text sample",
    loading: false,
    uploadInProgress: false,
    analysisInProgress: false,
    paywallRequired: false,
  });

  assert.equal(readyState.inputVisible, true);
  assert.equal(readyState.analyzeEnabled, true);
});

test("local analysis result builder returns a stable descriptive payload", () => {
  const result = buildLocalAnalysisResult("Are you free later?\nI can share more detail after lunch.");

  assert.equal(result.headline, "Local pattern analysis ready");
  assert.equal(Array.isArray(result.highlights), true);
  assert.equal(result.highlights.length, 3);
  assert.match(result.summary, /tone and specificity/i);
  assert.match(result.pattern, /may indicate|can suggest|reads/i);
  assert.equal(Array.isArray(result.spans), true);
  assert.ok(result.shareText.includes("It can read differently the second time"));
  assert.ok(result.shareText.length < 220);
});

test("local analysis result stays inside guardrail language", () => {
  const result = buildLocalAnalysisResult(
    "Maybe later.\nWhatever works, I guess.\nI need a direct answer now."
  );

  const combined = [result.pattern, result.summary, ...result.highlights].join(" ").toLowerCase();
  assert.equal(combined.includes("this proves"), false);
  assert.equal(combined.includes("cheating"), false);
  assert.equal(combined.includes("liar"), false);
});
