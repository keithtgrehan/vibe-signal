import test from "node:test";
import assert from "node:assert/strict";

import {
  buildAnalysisComposerState,
  buildLocalAnalysisResult,
  getMobileLayoutMetrics,
  selectHeroHeadline,
} from "../src/screens/providerScreenModel.js";

test("mobile layout metrics stay single-column and bounded for narrow viewports", () => {
  const layout = getMobileLayoutMetrics();

  assert.equal(layout.singleColumn, true);
  assert.equal(layout.noHorizontalOverflow, true);
  assert.equal(layout.maxWidth, 480);
  assert.equal(layout.padding, 20);
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
  assert.equal(readyState.ctaLabel, "See what changed");
  assert.equal(readyState.loadingLabel, "Running analysis...");
});

test("hero headline adapts to first use, drafted text, and result state", () => {
  assert.equal(selectHeroHeadline({ analysisText: "", hasResult: false }), "See what changed in how they’re talking to you");
  assert.equal(selectHeroHeadline({ analysisText: "Draft", hasResult: false }), "This message feels different. Here’s why.");
  assert.equal(selectHeroHeadline({ analysisText: "Draft", hasResult: true }), "Detect tone shifts instantly");
});

test("local analysis result builder returns a stable insight payload", () => {
  const result = buildLocalAnalysisResult("Are you free later?\nI can share more detail after lunch.");

  assert.match(
    result.headline,
    /different|specific|certain|direct|subtle|urgent|pulling back|avoiding|measured/i
  );
  assert.match(result.signalLabel, /subtle|noticeable|clear/i);
  assert.equal(Array.isArray(result.highlights), true);
  assert.equal(result.highlights.length, 3);
  assert.match(result.summary, /tone, intent, and meaning/i);
  assert.match(result.pattern, /may indicate|could suggest|becomes|stays/i);
  assert.equal(Array.isArray(result.spans), true);
  assert.ok(result.spans.every((item) => typeof item.note === "string"));
  assert.match(
    result.shareText,
    /This message reads differently the second time|Something changed in the tone here|Not what it seems at first glance/
  );
  assert.ok(result.shareText.length < 80);
});

test("weak or repetitive input falls back to an honest low-signal result", () => {
  const result = buildLocalAnalysisResult("Okay.\nOkay.\nOkay.");

  assert.equal(result.analysisMode, "fallback");
  assert.match(result.headline, /No strong shift detected|Tone appears consistent|Nothing clearly changed here/i);
  assert.equal(result.signalLabel, "Low-signal input");
  assert.deepEqual(result.highlights.slice(0, 2), [
    "Language stays similar throughout",
    "No clear change in tone or intent",
  ]);
  assert.match(result.suggestion, /longer exchange/i);
  assert.match(result.shareText, /No strong shift detected|Tone appears consistent here/i);
});

test("short but clearly changed input stays in signal mode", () => {
  const result = buildLocalAnalysisResult("I need an answer today.\nMaybe later, I'm not sure.");

  assert.equal(result.analysisMode, "signal");
  assert.notEqual(result.signalLabel, "Low-signal input");
  assert.match(result.headline, /direct|certain|pulling back|avoiding|urgent|measured/i);
});

test("long high-similarity input falls back when nothing materially changes", () => {
  const result = buildLocalAnalysisResult(
    "I can do Friday afternoon. I can do Friday afternoon. I can do Friday afternoon.\nI can do Friday afternoon too, that still works for me."
  );

  assert.equal(result.analysisMode, "fallback");
  assert.match(result.headline, /No strong shift detected|Tone appears consistent|Nothing clearly changed here/i);
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
