import assert from "node:assert/strict";
import test from "node:test";

import {
  buildComparisonResult,
  buildDraftReplyOptions,
  buildFeedbackMetadata,
  goalAwareNextStep,
  redactIdentifyingDetails,
} from "../src/guidedInteraction.js";
import {
  buildLowSignalFallback,
  buildTrustFirstResultView,
  EVIDENCE_QUALITY_LABELS,
} from "../src/resultViewModel.js";

const BLOCKED_REPLY_PATTERNS = [
  /\bsend this\b/i,
  /\bmake them\b/i,
  /\bwin them\b/i,
  /\bguaranteed\b/i,
  /\bhidden intent\b/i,
  /\bperfect reply\b/i,
  /\bcatch a lie\b/i,
];

test("goal-aware next steps stay local, safe, and specific to the selected goal", () => {
  const overReading = goalAwareNextStep(
    "Ask for a specific time or decision point.",
    "over_reading",
    "evidence"
  );
  assert.equal(
    overReading,
    "Based on the evidence shown, avoid treating this as proof. Ask a clarifying question instead."
  );

  const reducePressure = goalAwareNextStep(
    "Ask for a specific time or decision point.",
    "reduce_pressure",
    "careful"
  );
  assert.match(reducePressure, /lower-pressure/);
  assert.match(reducePressure, /Keep the limits visible before acting\./);
  assert.equal(/hidden intent|emotional truth|guaranteed/i.test(reducePressure), false);
});

test("evidence rows expose evidence quality labels without numeric confidence", () => {
  assert.deepEqual(Object.keys(EVIDENCE_QUALITY_LABELS), [
    "strong",
    "mixed",
    "low",
    "insufficient",
  ]);

  const view = buildTrustFirstResultView({
    match_id: "vibe_match_quality",
    signal_strength: "high",
    evidence: [
      {
        evidence_id: "ev_quality_1",
        safe_phrase: "maybe later",
        cue_family: "vague_timing",
        explanation: "The reply gives no clear time or decision point.",
      },
    ],
    safe_explanation: "This message gives a vague timing answer after a direct question.",
  });

  assert.equal(view.evidenceDetails[0].qualityLabel, "Strong");
  assert.match(view.evidenceDetails[0].qualityDescription, /clear wording/);
  assert.equal(JSON.stringify(view).includes("%"), false);
});

test("low-signal fallback explains what context is missing", () => {
  const fallback = buildLowSignalFallback("ok");
  assert.equal(fallback.isLowSignal, true);
  assert.deepEqual(fallback.contextSuggestions, [
    "Add the previous message",
    "Add the question this replied to",
    "Add what decision you need to make",
    "Add timing if timing matters",
    "Try a synthetic demo",
  ]);
  assert.equal(fallback.evidenceDetails.length, 0);
});

test("draft reply helper returns safe editable options shaped by the selected goal", () => {
  const drafts = buildDraftReplyOptions({
    goalId: "reduce_pressure",
    patternLabels: ["Urgency pressure", "Boundary pressure"],
  });

  assert.ok(drafts.length >= 1 && drafts.length <= 3);
  assert.equal(drafts[0].label, "Draft option");
  assert.deepEqual(
    drafts.map((draft) => draft.type),
    ["lower_pressure", "set_boundary", "ask_for_timing"]
  );

  for (const draft of drafts) {
    assert.match(draft.text, /No rush|I need|Could you/i);
    for (const pattern of BLOCKED_REPLY_PATTERNS) {
      assert.equal(pattern.test(draft.text), false, `${draft.text} matched ${pattern}`);
    }
  }
});

test("client redaction helper removes obvious identifiers without claiming anonymization", () => {
  const input =
    "Email alex@example.com or call +1 (555) 123-4567. See https://example.com/a and @alex at 123 Main St.";
  const result = redactIdentifyingDetails(input);

  assert.match(result.text, /\[email\]/);
  assert.match(result.text, /\[phone\]/);
  assert.match(result.text, /\[link\]/);
  assert.match(result.text, /\[handle\]/);
  assert.match(result.text, /\[address\]/);
  assert.equal(result.text.includes("alex@example.com"), false);
  assert.equal(result.text.includes("555"), false);
  assert.equal(result.note, "Helps remove obvious identifiers. This runs in your browser before analysis.");
  assert.equal(/guaranteed anonymous|anonymizes/i.test(result.note), false);
});

test("comparison mode stays neutral and handles low-context snippets", () => {
  const comparison = buildComparisonResult({
    earlierText: "other: Friday at 7 works.",
    laterText: "other: maybe later",
  });

  assert.equal(comparison.comparison, true);
  assert.equal(comparison.result_state, "comparison");
  assert.match(comparison.safe_explanation, /What changed/);
  assert.match(comparison.evidence[0].explanation, /earlier wording/);
  assert.match(comparison.evidence[1].explanation, /later wording/);
  assert.equal(/lying|hidden intent|cheating/i.test(JSON.stringify(comparison)), false);

  const low = buildComparisonResult({ earlierText: "ok", laterText: "maybe" });
  assert.equal(low.low_signal_fallback, true);
  assert.equal(low.signal_strength, "insufficient");
});

test("feedback metadata contains cue ids and context, never raw text or draft output", () => {
  const metadata = buildFeedbackMetadata({
    matchId: "vibe_match_123",
    feedbackTag: "cue_too_strong",
    cueId: "unclear_1",
    cueFamily: "vague_timing",
    evidenceQuality: "mixed",
    goalId: "unclear",
    contextId: "work",
    styleId: "careful",
    lowSignal: false,
    synthetic: true,
  });

  assert.equal(metadata.matchId, "vibe_match_123");
  assert.equal(metadata.feedbackTag, "cue_too_strong");
  assert.equal(metadata.cueId, "unclear_1");
  assert.equal(metadata.cueFamily, "vague_timing");
  assert.equal(metadata.evidenceQuality, "mixed");
  assert.equal(metadata.goalId, "unclear");
  assert.equal(metadata.contextId, "work");
  assert.equal(metadata.styleId, "careful");
  assert.equal(metadata.lowSignal, false);
  assert.equal(metadata.synthetic, true);
  assert.match(metadata.clientEventId, /^evt_feedback_/);
  assert.equal(Object.hasOwn(metadata, "evidenceText"), false);
  assert.equal(Object.hasOwn(metadata, "rawMessageText"), false);
  assert.equal(Object.hasOwn(metadata, "draftReplyText"), false);
});
