import assert from "node:assert/strict";
import test from "node:test";

import { buildSyntheticResult, buildTrustFirstResultView } from "../src/resultViewModel.js";
import {
  buildVariantSections,
  DEFAULT_VARIANT,
  getVariant,
  resolveVariant,
  VARIANT_STORAGE_KEY,
  VARIANTS,
} from "../src/variants.js";

function makeMemoryStorage(initial = {}) {
  const values = new Map(Object.entries(initial));
  return {
    getItem(key) {
      return values.has(key) ? values.get(key) : null;
    },
    setItem(key, value) {
      values.set(key, String(value));
    },
    snapshot() {
      return Object.fromEntries(values.entries());
    },
  };
}

test("variant resolver defaults to the production Codex baseline", () => {
  assert.equal(DEFAULT_VARIANT, "a");
  assert.equal(resolveVariant("", makeMemoryStorage()), "a");
  assert.equal(getVariant("missing").key, "a");
});

test("variant resolver uses URL query without cookies or identity tracking", () => {
  const storage = makeMemoryStorage();

  assert.equal(resolveVariant("?variant=b", storage), "b");
  assert.deepEqual(storage.snapshot(), { [VARIANT_STORAGE_KEY]: "b" });
  assert.equal(resolveVariant("?variant=a", storage), "a");
  assert.deepEqual(storage.snapshot(), { [VARIANT_STORAGE_KEY]: "a" });
});

test("invalid variant query falls back to A even when local storage has B", () => {
  const storage = makeMemoryStorage({ [VARIANT_STORAGE_KEY]: "b" });

  assert.equal(resolveVariant("?variant=bad", storage), "a");
  assert.equal(resolveVariant("", storage), "b");
});

test("variant A preserves the approved production hero copy", () => {
  assert.equal(
    VARIANTS.a.hero.title,
    "See what a message is doing - without guessing what someone feels."
  );
  assert.equal(VARIANTS.a.hero.primaryCta, "Run a demo");
  assert.equal(VARIANTS.a.hero.secondaryCta, "Analyze text");
});

test("variant B exposes the Replit-inspired Before You Reply direction", () => {
  assert.equal(
    VARIANTS.b.hero.title,
    "Before you reply, check what the message actually says."
  );
  assert.equal(VARIANTS.b.hero.primaryCta, "Check a demo");
  assert.equal(VARIANTS.b.hero.secondaryCta, "Paste your text");
  assert.equal(VARIANTS.b.hero.trustNote, "Useful for clarity. Not for mind-reading.");
  assert.equal(VARIANTS.b.demo.title, "When the answer is vague");
});

test("variant result sections remain evidence-first before interpretation", () => {
  const view = buildTrustFirstResultView(buildSyntheticResult("unclear_ask"));
  const sectionsA = buildVariantSections(view, "a");
  const sectionsB = buildVariantSections(view, "b");

  assert.deepEqual(sectionsA.map((section) => section.label), [
    "What stands out",
    "Evidence",
    "What it could mean",
    "Safer reply",
    "Limits",
  ]);
  assert.deepEqual(sectionsB.map((section) => section.label), [
    "The part to slow down on",
    "The exact words",
    "A grounded read",
    "A calmer reply",
    "Limits",
  ]);
  assert.equal(sectionsB[1].rows[0].phrase, "maybe later, not sure yet");
  assert.equal(sectionsB[2].text, "The timing is unresolved. You do not need to guess the reason.");
});

test("variant B synthetic demo uses the approved grounded example language", () => {
  const view = buildTrustFirstResultView(buildSyntheticResult("unclear_ask"));
  const sections = Object.fromEntries(
    buildVariantSections(view, "b").map((section) => [section.id, section])
  );

  assert.equal(sections.standsOut.text, "They did not clearly confirm or cancel.");
  assert.equal(
    sections.saferReply.text,
    "Got it - can you let me know by Thursday evening if Friday still works?"
  );
  assert.equal(sections.limits.text, "This cannot tell you what they mean or feel.");
});
