import test from "node:test";
import assert from "node:assert/strict";

import {
  buildMatchComposerState,
  buildMatchResultViewModel,
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
  assert.equal(viewModel.compatibilityScoreLabel, "68% cue-weight score");
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
  assert.match(viewModel.explanation, /explicit cues/);
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
