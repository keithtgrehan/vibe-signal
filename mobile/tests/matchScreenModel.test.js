import test from "node:test";
import assert from "node:assert/strict";

import {
  buildMatchComposerState,
  buildMatchResultViewModel,
  buildLowSignalFallback,
  FEEDBACK_OPTIONS,
} from "../src/screens/matchScreenModel.js";

test("match composer exposes loading, empty, and ready states", () => {
  const empty = buildMatchComposerState({
    conversationText: "",
    loading: false,
    apiUrl: "https://example.test",
  });
  assert.equal(empty.submitEnabled, false);
  assert.equal(empty.empty, true);

  const loading = buildMatchComposerState({
    conversationText: "self: Can you confirm?\nother: Yes.",
    loading: true,
    apiUrl: "https://example.test",
  });
  assert.equal(loading.submitEnabled, false);
  assert.equal(loading.statusLabel, "Checking communication fit...");

  const ready = buildMatchComposerState({
    conversationText: "self: Can you confirm?\nother: Yes.",
    loading: false,
    apiUrl: "https://example.test",
  });
  assert.equal(ready.submitEnabled, true);
});

test("match result view model renders score, factors, safe phrases, and explanation", () => {
  const viewModel = buildMatchResultViewModel({
    compatibility_band: "moderate",
    score: 0.68,
    positive_factors: [
      "Specificity and concrete timing cues are present.",
      "Messages include agreement or shared-plan wording.",
    ],
    risk_factors: ["A reply does not directly answer a previous ask."],
    evidence: [
      {
        evidence_id: "ev_1",
        safe_phrase: "message contains direct request wording.",
      },
    ],
    contradiction_against_prior_message: [
      {
        evidence_id: "ev_2",
        safe_phrase: "This reply conflicts with an earlier stated availability/commitment.",
      },
    ],
    safe_explanation:
      "Compatibility is based on explicit cues such as directness, specificity, pressure, and repair wording.",
  });

  assert.equal(viewModel.hasResult, true);
  assert.equal(viewModel.mainRead, "Compatibility is based on explicit cues such as directness, specificity, pressure, and repair wording.");
  assert.equal(
    viewModel.signalStrengthLabel,
    "Medium — there is evidence, but context could change the read."
  );
  assert.equal(viewModel.bandLabel, "Moderate fit");
  assert.equal(viewModel.signalStrength, "medium");
  assert.equal(viewModel.isLowSignal, false);
  assert.deepEqual(viewModel.positiveFactors, [
    "Specificity and concrete timing cues are present.",
    "Messages include agreement or shared-plan wording.",
  ]);
  assert.deepEqual(viewModel.riskFactors, ["A reply does not directly answer a previous ask."]);
  assert.deepEqual(viewModel.evidencePhrases, [
    "message contains direct request wording.",
    "This reply conflicts with an earlier stated availability/commitment.",
  ]);
  assert.deepEqual(viewModel.patternLabels, ["Cue", "Cue"]);
  assert.equal(
    viewModel.cannotInferText,
    "This does not prove intent, attraction, honesty, or emotional state."
  );
  assert.equal(viewModel.safeNextStep, "Clarify one ask in plain language.");
  assert.match(viewModel.explanation, /explicit cues/);
  assert.equal(JSON.stringify(viewModel).includes("%"), false);
});

test("match result view model keeps blocked claims out of UI disclosure", () => {
  const viewModel = buildMatchResultViewModel({
    compatibility_band: "mixed",
    score: 0.49,
    positive_factors: [],
    risk_factors: [],
    evidence: [],
    safe_explanation: "Compatibility is based on explicit cues.",
  });

  const combined = [
    viewModel.disclosure,
    viewModel.emptyPositiveLabel,
    viewModel.emptyRiskLabel,
  ].join(" ").toLowerCase();

  assert.equal(combined.includes("they like you"), false);
  assert.equal(combined.includes("cheat"), false);
  assert.equal(combined.includes("diagnos"), false);
  assert.equal(combined.includes("manipulat"), false);
  assert.match(viewModel.disclosure, /bounded communication-pattern review/);
});

test("match result view model falls back when no safe evidence phrase is available", () => {
  const viewModel = buildMatchResultViewModel({
    match_id: "mobile_no_evidence",
    signal_strength: "medium",
    safe_explanation: "The backend returned a summary without a safe evidence phrase.",
  });

  assert.equal(viewModel.isLowSignal, true);
  assert.equal(viewModel.title, "No safe evidence phrase returned.");
  assert.deepEqual(viewModel.evidenceDetails, []);
  assert.equal(
    viewModel.safeNextStep,
    "Add context or try a synthetic example before relying on this read."
  );
});

test("match composer exposes consent and sensitive-data boundaries", () => {
  const state = buildMatchComposerState({
    conversationText: "self: Can you confirm?\nother: Yes.",
    loading: false,
    apiUrl: "https://example.test",
  });

  const combined = [state.consentLabel, state.privacyNote].join(" ").toLowerCase();
  assert.match(combined, /only submit messages you have permission to analyze/);
  assert.match(combined, /sensitive personal data/);
  assert.match(combined, /medical data/);
  assert.match(combined, /legal documents/);
  assert.match(combined, /financial data/);
  assert.match(combined, /third-party private messages without permission/);
  assert.match(combined, /closed beta/);
  assert.match(combined, /legal review before public launch/);
  assert.equal(combined.includes("they like you"), false);
  assert.equal(combined.includes("hidden intent"), false);
  assert.equal(combined.includes("cheat"), false);
});

test("match composer consent copy is compact and synthetic-first", () => {
  const state = buildMatchComposerState({
    conversationText: "self: Can you confirm?\nother: Yes.",
    loading: false,
    apiUrl: "https://example.test",
  });

  assert.equal(state.consentTitle, "Before you paste");
  assert.deepEqual(state.consentBullets, [
    "Only submit messages you have permission to analyze.",
    "Remove names, phone numbers, addresses, and sensitive details.",
    "Use synthetic examples if you just want to test the app.",
  ]);
  assert.equal(
    state.consentCheckboxLabel,
    "I understand and have permission to analyze this text."
  );
});

test("short/context-light messages get an intentional low-signal fallback", () => {
  for (const text of ["hey", "ok", "lol sure", "fine"]) {
    const fallback = buildLowSignalFallback(text);
    assert.equal(fallback.isLowSignal, true);
    assert.equal(fallback.title, "Not enough context to read safely.");
    assert.equal(
      fallback.body,
      "This message is too short or context-light. Vibe Signal can help with wording patterns, but this would be over-reading it."
    );
    assert.deepEqual(fallback.tryItems, [
      "Add the previous message",
      "Ask for a clearer version",
      "Try a synthetic example",
    ]);
  }
});

test("feedback options are bounded metadata labels only", () => {
  assert.deepEqual(
    FEEDBACK_OPTIONS.map((option) => option.label),
    ["Useful", "Too strong", "Missed context", "Unsafe wording", "Confusing"]
  );
  for (const option of FEEDBACK_OPTIONS) {
    assert.equal(Object.hasOwn(option, "rawMessageText"), false);
    assert.equal(option.comment, "");
  }
});
