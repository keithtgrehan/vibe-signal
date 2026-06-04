import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";

import {
  CAN_HELP_WITH,
  CANNOT_TELL,
  HERO_COPY,
  HOW_IT_WORKS_STEPS,
  RESULT_EXPLAINABILITY_STEPS,
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
import { buildVariantSections, VARIANTS } from "../src/variants.js";

const ROOT = resolve(import.meta.dirname, "..");

test("landing hero exposes the minimal human product promise and clear demo CTA", () => {
  assert.equal(
    HERO_COPY.title,
    "See what a message is doing - without guessing what someone feels."
  );
  assert.match(HERO_COPY.title, /See what a message is doing/);
  assert.match(HERO_COPY.title, /without guessing what someone feels/);
  assert.equal(
    HERO_COPY.subtitle,
    "Paste text you’re allowed to use, or run a synthetic demo. Vibe Signal highlights clarity, pressure, unanswered asks, and safer replies."
  );
  assert.equal(HERO_COPY.primaryCta, "Run a demo");
  assert.equal(HERO_COPY.secondaryCta, "Analyze text");
  assert.equal(HERO_COPY.trustNote, "No mind-reading. No relationship verdicts. Just observable wording.");
  assert.equal(VARIANTS.a.hero.title, HERO_COPY.title);
  assert.equal(VARIANTS.a.hero.navCta, "Run demo");

  const appText = readFileSync(resolve(ROOT, "src/App.jsx"), "utf8");
  assert.match(appText, /Demo/);
  assert.match(appText, /How it works/);
  assert.match(appText, /Privacy/);
  assert.match(appText, /variant\.hero\.navCta/);
});

test("home page follows the chosen minimal information architecture", () => {
  const appText = readFileSync(resolve(ROOT, "src/App.jsx"), "utf8");

  assert.match(appText, /function Hero/);
  assert.match(appText, /function FeaturedDemo/);
  assert.match(appText, /function ResultCard/);
  assert.match(appText, /function AnalyzeText/);
  assert.match(appText, /function HowItWorks/);
  assert.match(appText, /function TrustFooter/);
  assert.match(appText, /demo-result-grid/);

  for (const removed of [
    "GoalSelector",
    "ChipSelector",
    "Compare two snippets",
    "Analysis style",
    "What kind of exchange is this?",
    "Signal strength",
    "Can help with",
    "Cannot tell you",
  ]) {
    assert.equal(appText.includes(removed), false, `App.jsx still includes ${removed}`);
  }
});

test("featured synthetic demo is a single understandable first run", () => {
  const featured = SYNTHETIC_DEMOS.find((demo) => demo.id === "unclear_ask");

  assert.equal(featured?.title, "Unclear timing");
  assert.equal(featured?.exchange, "self: Are we still on for Friday?\nother: maybe later, not sure yet");
  assert.equal(featured?.requiresPrivateConsent, false);
  assert.equal(featured?.actionLabel, "Run demo");
  assert.deepEqual(TRUST_STRIP_ITEMS, [
    "No private chats stored for this demo",
    "The exact words that triggered it",
    "What it can’t know",
  ]);
});

test("result view remains evidence-first with the required result-card structure", () => {
  const view = buildTrustFirstResultView(buildSyntheticResult("unclear_ask"));

  assert.deepEqual(RESULT_EXPLAINABILITY_STEPS, [
    "What stands out",
    "Evidence",
    "What it could mean",
    "Safer reply",
    "Limits",
  ]);
  assert.equal(view.mainRead, "The reply answers loosely, but does not confirm Friday.");
  assert.deepEqual(view.evidencePhrases, ["maybe later, not sure yet"]);
  assert.equal(
    view.interpretation,
    "There may not be a clear decision yet. The safest read is that timing is still open."
  );
  assert.equal(
    view.safeNextStep,
    "No worries - can you confirm by Thursday evening so I know whether to keep Friday free?"
  );
  assert.equal(view.cannotInferText, "This does not tell you what they feel or intend.");

  assert.deepEqual(buildVariantSections(view, "a").map((section) => section.label), [
    "What stands out",
    "Evidence",
    "What it could mean",
    "Safer reply",
    "Limits",
  ]);
});

test("analyze flow keeps consent required before pasted text analysis", () => {
  const appText = readFileSync(resolve(ROOT, "src/App.jsx"), "utf8");

  assert.match(appText, /I have permission to analyze this text\./);
  assert.match(appText, /Check the permission box before analyzing\./);
  assert.match(appText, /disabled=\{!canSubmit\}/);
  assert.match(appText, /Avoid sensitive, legal, medical, workplace, or third-party private content/);
  assert.match(appText, /onRetry/);
  assert.match(appText, /API_RETRYING_BACKEND_MESSAGE/);
  assert.match(appText, /API_BACKEND_CONNECTION_ERROR_MESSAGE/);
});

test("feedback stays result-metadata only and avoids raw text fields", () => {
  const appText = readFileSync(resolve(ROOT, "src/App.jsx"), "utf8");

  assert.match(appText, /Feedback stores only result metadata, never the message text\./);
  assert.deepEqual(
    FEEDBACK_OPTIONS.map((option) => option.label),
    ["Useful", "Too strong", "Missed context", "Unsafe wording", "Confusing"]
  );
  for (const option of FEEDBACK_OPTIONS) {
    assert.equal(Object.hasOwn(option, "rawMessageText"), false);
    assert.equal(option.comment, "");
  }
});

test("mobile and small viewport CSS keeps the page single-column and bounded", () => {
  const stylesText = readFileSync(resolve(ROOT, "src/styles.css"), "utf8");

  assert.match(stylesText, /@media \(max-width: 920px\)/);
  assert.match(stylesText, /\.demo-result-grid,\n  \.steps-grid \{\n    grid-template-columns: 1fr;/);
  assert.match(stylesText, /\.result-card \{\n    position: static;/);
  assert.match(stylesText, /@media \(max-width: 640px\)/);
  assert.match(stylesText, /\.button \{\n    width: 100%;/);
});

test("supporting trust content stays short and safe", () => {
  assert.deepEqual(HOW_IT_WORKS_STEPS.map((step) => step.title), [
    "Paste or run a demo",
    "See the evidence",
    "Choose a clearer next step",
  ]);
  assert.deepEqual(REVIEWER_DEMO_FLOW, [
    "Open with a synthetic card",
    "Show evidence before interpretation",
    "Point to limits and the safe next step",
    "Use metadata-only feedback",
  ]);
  assert.deepEqual(CAN_HELP_WITH, [
    "Spot vague or overloaded messages",
    "Identify unclear asks",
    "Surface pressure or urgency cues",
    "Show reassurance and repair opportunities",
    "Suggest clearer, lower-pressure replies",
  ]);
  assert.deepEqual(CANNOT_TELL, [
    "What someone feels",
    "What someone intends",
    "Whether a statement is true",
    "Health, personality, or identity labels",
    "What will happen next",
  ]);
});

test("fallbacks still avoid rendering summary-only analysis", () => {
  const noEvidence = buildTrustFirstResultView({
    match_id: "vibe_match_no_evidence",
    signal_strength: "medium",
    safe_explanation: "The summary exists, but no safe evidence phrase was returned.",
  });

  assert.equal(noEvidence.isLowSignal, true);
  assert.equal(noEvidence.title, "No safe evidence phrase returned.");
  assert.equal(noEvidence.evidenceDetails.length, 0);

  const fallback = buildLowSignalFallback("ok");
  assert.equal(fallback.isLowSignal, true);
  assert.equal(fallback.title, "Not enough context to read safely.");
  assert.equal(fallback.evidenceDetails.length, 0);
});
