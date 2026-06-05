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

const ROOT = resolve(import.meta.dirname, "..");
const BACKEND_LEGAL_TEXT = readFileSync(resolve(ROOT, "../backend/routes/legal.py"), "utf8");

test("landing hero exposes the Scanner-safe product promise and clear demo CTA", () => {
  assert.equal(HERO_COPY.title, "See what the wording shows.");
  assert.equal(
    HERO_COPY.subtitle,
    "Spot clarity, ambiguity, pressure, reassurance, and repair openings in text you are allowed to use."
  );
  assert.equal(HERO_COPY.primaryCta, "Run synthetic demo");
  assert.equal(HERO_COPY.secondaryCta, "Analyze with consent");
  assert.equal(
    HERO_COPY.trustNote,
    "Evidence from the words shown. Possible pattern, not a fact about intent."
  );

  const appText = readFileSync(resolve(ROOT, "src/App.jsx"), "utf8");
  assert.match(appText, /Demo/);
  assert.match(appText, /Analyze/);
  assert.match(appText, /Privacy/);
  assert.match(appText, /Run synthetic demo/);
});

test("home page follows the Scanner product information architecture", () => {
  const appText = readFileSync(resolve(ROOT, "src/App.jsx"), "utf8");

  for (const componentName of [
    "TopNav",
    "Hero",
    "DemoCard",
    "AnalyzePanel",
    "ConsentGate",
    "ScanningState",
    "ResultPanel",
    "SignalBreakdown",
    "EvidenceList",
    "SafeReplyCard",
    "LimitsCard",
    "FeedbackPanel",
    "TrustFooter",
    "Legal",
  ]) {
    assert.match(appText, new RegExp(`function ${componentName}`));
  }

  assert.match(appText, /scanner-workspace/);
  assert.match(appText, /scanner-result-shell/);

  for (const removed of [
    "GoalSelector",
    "ChipSelector",
    "Compare two snippets",
    "Analysis style",
    "What kind of exchange is this?",
    "Get the receipts",
    "Share my receipt",
    "Interest score",
    "window.VIBE",
    "decodedThisWeek",
    "ratingCount",
  ]) {
    assert.equal(appText.includes(removed), false, `App.jsx still includes ${removed}`);
  }
});

test("featured synthetic demo is a single understandable first run", () => {
  const featured = SYNTHETIC_DEMOS.find((demo) => demo.id === "unclear_ask");

  assert.equal(featured?.title, "Unclear timing");
  assert.equal(featured?.exchange, "self: Are we still on for Friday?\nother: maybe later, not sure yet");
  assert.equal(featured?.requiresPrivateConsent, false);
  assert.equal(featured?.actionLabel, "Run synthetic demo");
  assert.deepEqual(TRUST_STRIP_ITEMS, [
    "Evidence from the words shown",
    "Possible pattern, not a fact about intent",
    "Feedback stores result metadata only",
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
  assert.equal(
    view.cannotInferText,
    "Vibe Signal does not know intent, attraction, truthfulness, diagnosis, or outcomes."
  );

  const appText = readFileSync(resolve(ROOT, "src/App.jsx"), "utf8");
  assert.match(appText, /Evidence from the words shown/);
  assert.match(appText, /Signal \/ cue breakdown/);
  assert.match(appText, /Evidence phrase list/);
  assert.match(appText, /What it could mean/);
  assert.match(appText, /Safer reply/);
  assert.match(appText, /Limits \/ cannot infer/);
  assert.match(appText, /buildTrustFirstResultView/);
});

test("analyze flow keeps consent required before pasted text analysis", () => {
  const appText = readFileSync(resolve(ROOT, "src/App.jsx"), "utf8");

  assert.match(appText, /I have permission to analyze this text and understand the limits\./);
  assert.match(appText, /Check the consent box before analyzing private text\./);
  assert.match(appText, /disabled=\{!canSubmit\}/);
  assert.match(appText, /Only paste text you have permission to use/);
  assert.match(appText, /runSyntheticDemo/);
  assert.match(appText, /buildSyntheticResult/);
  assert.match(appText, /onRetry/);
  assert.match(appText, /API_RETRYING_BACKEND_MESSAGE/);
  assert.match(appText, /The backend may be waking up\. Trying once more\.\.\./);
  assert.match(appText, /buildLowSignalFallback/);
  assert.match(appText, /ScanningState/);
});

test("feedback stays result-metadata only and avoids raw text fields", () => {
  const appText = readFileSync(resolve(ROOT, "src/App.jsx"), "utf8");

  assert.match(appText, /Feedback stores result metadata only, never message text\./);
  assert.match(appText, /I agree to send metadata-only result feedback\./);
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

  for (const token of [
    "--bg: #0A0F1C",
    "--bg2: #0E1525",
    "--text: #EAF0FF",
    "--muted: rgba(234,240,255,0.56)",
    "--cyan: #54E6FF",
    "--lime: #8DF7C9",
    "--magenta: #FF6BBA",
    "--panel: rgba(255,255,255,0.04)",
    "--line: rgba(255,255,255,0.09)",
  ]) {
    assert.match(stylesText, new RegExp(token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }

  assert.match(stylesText, /@media \(max-width: 920px\)/);
  assert.match(stylesText, /\.scanner-workspace \{\n    grid-template-columns: 1fr;/);
  assert.match(stylesText, /\.left-stack \{\n    display: contents;/);
  assert.match(stylesText, /\.demo-card \{\n    order: 1;/);
  assert.match(stylesText, /\.analyze-panel \{\n    order: 2;/);
  assert.match(stylesText, /\.scanner-result-shell \{\n    order: 3;/);
  assert.match(stylesText, /\.how-section \{\n    order: 4;/);
  assert.match(stylesText, /\.scanner-result-shell \{\n    position: static;/);
  assert.match(stylesText, /@media \(max-width: 640px\)/);
  assert.match(stylesText, /\.button \{\n    width: 100%;/);
  assert.equal(/overflow-x:\s*hidden/.test(stylesText), true);
});

test("supporting trust content stays short and safe", () => {
  assert.deepEqual(HOW_IT_WORKS_STEPS.map((step) => step.title), [
    "Start with the demo",
    "See the evidence",
    "Choose a safer next step",
  ]);
  assert.deepEqual(REVIEWER_DEMO_FLOW, [
    "Open with a synthetic Scanner card",
    "Show quoted evidence before interpretation",
    "Keep limits and the safe next step visible",
    "Use consented metadata-only feedback",
  ]);
  assert.deepEqual(CAN_HELP_WITH, [
    "Spot clarity, ambiguity, pressure, reassurance, and repair openings",
    "Show evidence from the words shown",
    "Separate possible patterns from facts about intent",
    "Suggest one clearer, lower-pressure follow-up",
    "Keep limits visible before you act",
  ]);
  assert.deepEqual(CANNOT_TELL, [
    "Intent",
    "Attraction",
    "Truthfulness",
    "Health labels",
    "Outcomes",
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

test("legal and privacy surfaces remain visible from public UI", () => {
  const appText = readFileSync(resolve(ROOT, "src/App.jsx"), "utf8");
  const stylesText = readFileSync(resolve(ROOT, "src/styles.css"), "utf8");

  for (const label of ["Privacy", "Terms", "Data request/delete", "Disclaimer"]) {
    assert.match(appText, new RegExp(label.replace("/", "\\/")));
  }
  assert.match(appText, /fetchLegalPage/);
  assert.match(appText, /page\.groups/);
  assert.match(appText, /legal-section-list/);
  assert.match(appText, /legal-group/);
  assert.match(stylesText, /\.legal-section-list/);
  assert.match(stylesText, /\.legal-group/);
  assert.match(stylesText, /\.segmented-control/);
});

test("public legal drafts include required draft status and closed-beta intro", () => {
  assert.match(BACKEND_LEGAL_TEXT, /Status: draft_requires_legal_review/);
  assert.match(BACKEND_LEGAL_TEXT, /Vibe Signal is currently in closed beta \/ early public beta\./);
  assert.match(BACKEND_LEGAL_TEXT, /These legal drafts are provided for transparency and require legal review before public launch\./);

  for (const route of [
    '"privacy"',
    '"terms"',
    '"data-deletion"',
    '"data-export"',
    '"match-disclaimer"',
  ]) {
    assert.match(BACKEND_LEGAL_TEXT, new RegExp(`${route}:`));
  }
});

test("privacy legal draft exposes infrastructure assumptions and missing inputs", () => {
  for (const required of [
    "[LEGAL_OPERATOR_NAME_REQUIRED]",
    "[PRIVACY_CONTACT_EMAIL_REQUIRED]",
    "[BUSINESS_ADDRESS_OR_CONTACT_METHOD_REQUIRED]",
    "https://www.vibe-signal.com",
    "Vercel Hobby/basic runtime logs are assumed to be retained for 1 hour unless the Vercel account changes.",
    "Render Hobby/basic backend logs are assumed to be retained for 7 days unless the Render workspace changes.",
    "No raw messages are used for training.",
    "No analytics, cookies, or tracking are added by this implementation.",
    "[LAWFUL_BASIS_REQUIRES_LEGAL_REVIEW]",
    "[SUPERVISORY_AUTHORITY_REQUIRES_LEGAL_REVIEW]",
  ]) {
    assert.match(BACKEND_LEGAL_TEXT, new RegExp(required.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
});

test("terms, data request, and disclaimer drafts include required safety boundaries", () => {
  for (const required of [
    "Only submit text you have permission to analyze.",
    "Prohibited use includes stalking, harassment, coercion, manipulation, or trying to make someone respond.",
    "[ACCOUNT_FEATURES_NOT_CURRENTLY_IMPLEMENTED]",
    "[PAYMENT_FEATURES_NOT_CURRENTLY_IMPLEMENTED]",
    "access/export",
    "deletion",
    "correction",
    "objection/restriction",
    "withdrawal of consent where applicable",
    "[RESPONSE_TIMELINE_REQUIRES_LEGAL_REVIEW]",
    "Raw submitted text may not be available for export or deletion because the app is designed not to intentionally retain it.",
    "Vibe Signal does not know intent, attraction, truthfulness, diagnosis, or outcomes.",
  ]) {
    assert.match(BACKEND_LEGAL_TEXT, new RegExp(required.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
});
