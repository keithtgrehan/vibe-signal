import test from "node:test";
import assert from "node:assert/strict";

import {
  buildFallbackExternalSummary,
  normalizeExternalSummary,
} from "../src/providers/externalSummary.js";

test("external summary normalization keeps a strict safe schema", () => {
  const summary = normalizeExternalSummary({
    providerName: "openai",
    modelName: "gpt-test",
    payload: {
      summary: "Later replies read shorter and a little less specific than earlier ones.",
      what_changed: [
        "Directness softens after the midpoint.",
        "Later replies include less concrete detail.",
      ],
      compare_prompts: [
        "Compare earlier replies with later replies for detail.",
        "Compare pacing with directness across the exchange.",
      ],
    },
  });

  assert.equal(summary.provider, "OpenAI");
  assert.equal(summary.safe_to_render, true);
  assert.equal(summary.what_changed.length, 2);
  assert.equal(summary.compare_prompts.length, 2);
});

test("unsafe external summaries are replaced with a safe fallback", () => {
  const summary = normalizeExternalSummary({
    providerName: "groq",
    payload: {
      summary: "This means they are lying.",
      what_changed: ["A red flag appears later."],
      compare_prompts: ["Ask whether this proves dishonesty."],
    },
    signalBundle: {
      shift_radar: { summary: "Later replies look shorter than earlier ones." },
      consistency: { top_reasons: ["Direct answer style weakens after the midpoint."] },
    },
  });

  assert.equal(summary.provider, "Groq");
  assert.equal(summary.used_fallback, true);
  assert.equal(summary.summary.includes("lying"), false);
  assert.equal(summary.what_changed.some((item) => /red flag/i.test(item)), false);
});

test("fallback summaries stay short and reviewable", () => {
  const summary = buildFallbackExternalSummary({
    providerName: "anthropic",
    signalBundle: {
      shift_radar: { summary: "Later replies look shorter and less detailed than earlier ones." },
      consistency: { top_reasons: ["Direct answer style weakens after the midpoint."] },
    },
  });

  assert.equal(summary.provider, "Claude");
  assert.equal(summary.summary.length <= 220, true);
  assert.equal(summary.what_changed.length <= 3, true);
  assert.equal(summary.compare_prompts.length <= 2, true);
});
