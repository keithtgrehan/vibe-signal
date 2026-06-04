import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";

import {
  CAN_HELP_WITH,
  CANNOT_TELL,
  ANALYSIS_STYLE_OPTIONS,
  CONTEXT_OPTIONS,
  GOAL_OPTIONS,
  RESULT_EXPLAINABILITY_STEPS,
  HERO_COPY,
  REVIEWER_DEMO_FLOW,
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
    "Try a synthetic demo or paste permissioned text. Vibe Signal shows observable cues, evidence, limits, and a safer next step."
  );
  assert.equal(HERO_COPY.primaryCta, "Run a safe demo");
  assert.equal(HERO_COPY.secondaryCta, "Analyze permissioned text");
  assert.equal(
    HERO_COPY.trustNote,
    "Observable wording only. No mind-reading or relationship verdicts."
  );

  assert.deepEqual(TRUST_STRIP_ITEMS, [
    "Synthetic demo first",
    "Evidence before interpretation",
    "Permissioned text only",
    "Limits stay visible",
    "Metadata-only feedback",
  ]);
});

test("main UI copy exposes demo/analyze modes, context, and analysis style without model wording", () => {
  assert.deepEqual(GOAL_OPTIONS.map((option) => option.label), [
    "Understand what feels unclear",
    "Reduce pressure in my reply",
    "Find the direct ask",
    "Check if I am over-reading",
    "Prepare a clearer response",
  ]);
  assert.deepEqual(CONTEXT_OPTIONS.map((option) => option.label), [
    "General",
    "Relationship",
    "Work",
    "Friends/family",
    "Difficult conversation",
    "Unsure",
  ]);
  assert.deepEqual(ANALYSIS_STYLE_OPTIONS.map((option) => option.label), [
    "Quick read",
    "Evidence-first",
    "Careful",
  ]);
  assert.equal(
    ANALYSIS_STYLE_OPTIONS.find((option) => option.id === "quick")?.description,
    "Fast summary with key evidence and one next step."
  );
  assert.equal(
    ANALYSIS_STYLE_OPTIONS.find((option) => option.id === "evidence")?.description,
    "Quoted cues, pattern labels, limits, and repair options."
  );
  assert.equal(
    ANALYSIS_STYLE_OPTIONS.find((option) => option.id === "careful")?.description,
    "More cautious. Best for sensitive or unclear messages."
  );

  const appText = readFileSync(resolve(ROOT, "src/App.jsx"), "utf8");
  assert.match(appText, /What do you want help with\?/);
  assert.match(appText, /Goal only shapes wording and suggested next steps\./);
  assert.match(appText, /Your goal:/);
  assert.match(appText, /Demo Mode/);
  assert.match(appText, /Analyze Text/);
  assert.match(appText, /Compare two snippets/);
  assert.match(appText, /Remove identifying details/);
  assert.match(appText, /What kind of exchange is this\?/);
  assert.match(appText, /Context only adjusts caution and wording\. It does not infer intent\./);
  assert.match(appText, /Analysis style/);
  assert.match(appText, /Signal strength/);
  assert.match(appText, /Want a clearer reply\?/);
  assert.equal(/\bmodel\b/i.test(appText), false);
});

test("home surface keeps three primary demos and hides extra examples behind disclosure", () => {
  const appText = readFileSync(resolve(ROOT, "src/App.jsx"), "utf8");

  assert.match(appText, /PRIMARY_DEMO_IDS/);
  assert.match(appText, /EXTRA_DEMO_IDS/);
  assert.match(appText, /More examples/);
  assert.deepEqual(SYNTHETIC_DEMOS.slice(0, 3).map((demo) => demo.title), [
    "Unclear ask",
    "Pressure / urgency",
    "Repair opportunity",
  ]);
});

test("synthetic demo cards cover required and reviewer-ready scenarios without private text", () => {
  assert.deepEqual(
    SYNTHETIC_DEMOS.map((demo) => demo.title),
    [
      "Unclear ask",
      "Pressure / urgency",
      "Repair opportunity",
      "Low-signal fallback",
      "Boundary-respecting request",
      "Overloaded message",
    ]
  );

  for (const demo of SYNTHETIC_DEMOS) {
    assert.equal(demo.actionLabel, "Run demo");
    assert.match(demo.exchange, /self:|other:/);
    assert.ok(demo.highlight.length > 20);
    assert.ok(demo.previewPattern.length > 8);
    assert.equal(demo.requiresPrivateConsent, false);
    const result = buildSyntheticResult(demo.id);
    assert.equal(result.synthetic, true);
    assert.equal(result.requiresPrivateConsent, false);
  }
});

test("landing page exposes a short reviewer-safe demo path", () => {
  assert.deepEqual(REVIEWER_DEMO_FLOW, [
    "Open with a synthetic card",
    "Show evidence before interpretation",
    "Point to limits and the safe next step",
    "Use metadata-only feedback",
  ]);
  assert.deepEqual(RESULT_EXPLAINABILITY_STEPS, [
    "Evidence",
    "Pattern",
    "Limits",
    "Next step",
  ]);
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

test("no-evidence match results fall back instead of rendering summary-only analysis", () => {
  const view = buildTrustFirstResultView({
    match_id: "vibe_match_no_evidence",
    signal_strength: "medium",
    safe_explanation: "The summary exists, but no safe evidence phrase was returned.",
  });

  assert.equal(view.isLowSignal, true);
  assert.equal(view.title, "No safe evidence phrase returned.");
  assert.equal(view.evidenceDetails.length, 0);
  assert.equal(view.safeNextStep, "Add context or try a synthetic example before relying on this read.");
});

test("low-signal synthetic demo routes to the intentional fallback", () => {
  const result = buildSyntheticResult("low_signal_fallback");
  const view = buildTrustFirstResultView(result);

  assert.equal(result.requiresPrivateConsent, false);
  assert.equal(view.isLowSignal, true);
  assert.equal(view.title, "Not enough context to read safely.");
  assert.equal(
    view.body,
    "This message is too short or context-light. Add context or try a synthetic demo."
  );
  assert.deepEqual(view.tryItems, [
    "Add the previous message",
    "Add the question this replied to",
    "Add what decision you need to make",
    "Add timing if timing matters",
    "Try a synthetic demo",
  ]);
});

test("short/context-light inputs receive the safe low-signal fallback", () => {
  for (const text of ["hey", "ok", "lol sure", "fine"]) {
    const fallback = buildLowSignalFallback(text);
    assert.equal(fallback.isLowSignal, true);
    assert.equal(fallback.title, "Not enough context to read safely.");
    assert.equal(
      fallback.body,
      "This message is too short or context-light. Add context or try a synthetic demo."
    );
    assert.deepEqual(fallback.tryItems, [
      "Add the previous message",
      "Add the question this replied to",
      "Add what decision you need to make",
      "Add timing if timing matters",
      "Try a synthetic demo",
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

test("major controls expose focus and live-state affordances", () => {
  const appText = readFileSync(resolve(ROOT, "src/App.jsx"), "utf8");
  const stylesText = readFileSync(resolve(ROOT, "src/styles.css"), "utf8");

  assert.match(appText, /aria-live="polite"/);
  assert.match(appText, /role="status"/);
  assert.match(appText, /role="alert"/);
  assert.match(appText, /aria-describedby="conversation-helper consent-helper"/);
  assert.equal(appText.includes('role="tablist"'), false);
  assert.match(stylesText, /:focus-visible/);
  assert.match(stylesText, /feedback-option-selected/);
});

test("analyze form keeps synthetic CTA, consent gate, and safe backend error copy", () => {
  const appText = readFileSync(resolve(ROOT, "src/App.jsx"), "utf8");
  const apiText = readFileSync(resolve(ROOT, "src/api.js"), "utf8");

  assert.match(appText, /Try safe synthetic examples first\. No private messages needed\./);
  assert.match(appText, /Confirm permission before private text analysis\./);
  assert.match(
    appText,
    /Only submit messages you have permission to analyze\. Remove names, phone numbers, addresses, and sensitive details\./
  );
  assert.match(appText, /I have permission to review this text\./);
  assert.match(appText, /onRetry/);
  assert.match(appText, /API_RETRYING_BACKEND_MESSAGE/);
  assert.match(apiText, /The backend may be waking up\. Trying once more\.\.\./);
  assert.match(appText, /The backend may be waking up\. Please try again in a moment\./);
  assert.equal(appText.includes("The backend request timed out. Check the backend URL and CORS configuration."), false);
});
