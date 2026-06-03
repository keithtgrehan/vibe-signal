import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";

import {
  CAN_HELP_WITH,
  CANNOT_TELL,
  HERO_COPY,
  SYNTHETIC_DEMOS,
  TRUST_STRIP_ITEMS,
} from "../src/trustContent.js";
import {
  buildLowSignalFallback,
  buildSyntheticResult,
  buildTrustFirstResultView,
  FEEDBACK_OPTIONS,
} from "../src/resultViewModel.js";

const ROOT = resolve(import.meta.dirname, "..");

test("landing content exposes the required trust-first hero and synthetic-first CTA", () => {
  assert.equal(HERO_COPY.title, "Understand message patterns without guessing motives.");
  assert.equal(
    HERO_COPY.subtitle,
    "Vibe Signal highlights observable cues like clarity, ambiguity, pressure, reassurance, and repair opportunities — with evidence, limits, and safe next steps."
  );
  assert.equal(HERO_COPY.primaryCta, "Try a synthetic example");
  assert.equal(HERO_COPY.secondaryCta, "See how it works");
  assert.equal(
    HERO_COPY.trustNote,
    "Use synthetic text first, or only messages you have permission to analyze."
  );

  assert.deepEqual(TRUST_STRIP_ITEMS, [
    "Evidence-first outputs",
    "No hidden-intent claims",
    "Synthetic demo available",
    "Privacy-conscious beta design",
    "Built for clarity, not manipulation",
  ]);
});

test("synthetic demo cards cover unclear asks, pressure, and repair without private text", () => {
  assert.deepEqual(
    SYNTHETIC_DEMOS.map((demo) => demo.title),
    ["Unclear ask", "Pressure / urgency", "Repair opportunity"]
  );

  for (const demo of SYNTHETIC_DEMOS) {
    assert.equal(demo.actionLabel, "Run demo");
    assert.match(demo.exchange, /self:|other:/);
    assert.ok(demo.highlight.length > 20);
    assert.equal(demo.requiresPrivateConsent, false);
    const result = buildSyntheticResult(demo.id);
    assert.equal(result.synthetic, true);
    assert.equal(result.requiresPrivateConsent, false);
  }
});

test("can and cannot sections use the required plain-language boundaries", () => {
  assert.deepEqual(CAN_HELP_WITH, [
    "Spot vague or overloaded messages",
    "Identify unclear asks",
    "Surface pressure or urgency cues",
    "Show reassurance and repair opportunities",
    "Suggest clearer, lower-pressure replies",
  ]);
  assert.deepEqual(CANNOT_TELL, [
    "Whether someone likes you",
    "Whether someone is cheating",
    "Whether someone is lying",
    "What someone secretly means",
    "Someone’s diagnosis, attachment style, neurotype, or personality",
    "Whether a relationship will work",
  ]);
});

test("result view model is evidence-first and hides numeric confidence", () => {
  const view = buildTrustFirstResultView({
    match_id: "vibe_match_123",
    signal_strength: "medium",
    evidence: [
      {
        evidence_id: "ev_1",
        safe_phrase: "maybe later",
        cue_family: "vague_timing",
        explanation: "The reply gives an open-ended timing answer after a direct question.",
        repair_suggestion: "Ask for a specific time or decision point.",
      },
      {
        evidence_id: "ev_2",
        safe_phrase: "not sure yet",
        cue_family: "vague_timing",
      },
    ],
    safe_explanation: "This message gives a vague timing answer after a direct question.",
    safe_next_steps: ["Ask for a specific time or decision point."],
  });

  assert.equal(view.mainRead, "This message gives a vague timing answer after a direct question.");
  assert.equal(
    view.signalStrengthLabel,
    "Medium — there is evidence, but context could change the read."
  );
  assert.deepEqual(view.evidencePhrases, ["maybe later", "not sure yet"]);
  assert.deepEqual(view.patternLabels, ["Vague timing"]);
  assert.equal(
    view.patternExplanation,
    "The reply gives an open-ended timing answer after a direct question."
  );
  assert.equal(
    view.cannotInferText,
    "This does not prove intent, attraction, honesty, or emotional state."
  );
  assert.equal(view.safeNextStep, "Ask for a specific time or decision point.");
  assert.equal(JSON.stringify(view).includes("%"), false);
});

test("short/context-light inputs receive the safe low-signal fallback", () => {
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

test("feedback options are metadata-only and match the requested labels", () => {
  assert.deepEqual(
    FEEDBACK_OPTIONS.map((option) => option.label),
    ["Useful", "Too strong", "Missed context", "Unsafe wording", "Confusing"]
  );
  for (const option of FEEDBACK_OPTIONS) {
    assert.equal(Object.hasOwn(option, "rawMessageText"), false);
    assert.equal(option.comment, "");
  }
});

test("consumer UI does not expose developer-facing backend/API route copy", () => {
  const appText = readFileSync(resolve(ROOT, "src/App.jsx"), "utf8");
  for (const forbidden of ["Current backend", "Backend only", "API detail", "/api/"]) {
    assert.equal(appText.includes(forbidden), false, `App.jsx exposed ${forbidden}`);
  }
});
