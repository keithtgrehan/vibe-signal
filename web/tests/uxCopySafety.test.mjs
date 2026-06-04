import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";

const ROOT = resolve(import.meta.dirname, "..");
const USER_FACING_FILES = [
  "src/App.jsx",
  "src/api.js",
  "src/resultViewModel.js",
  "src/styles.css",
  "src/trustContent.js",
  "src/variants.js",
  "index.html",
];

const ALLOWED_BOUNDARY_PHRASES = [
  "Whether someone is cheating",
  "Whether someone is lying",
  "What someone secretly means",
  "Someone’s diagnosis, attachment style, neurotype, or personality",
];

const BLOCKED_PATTERNS = [
  /\bthey like you\b/i,
  /\bsecretly\b/i,
  /\bhidden intent\b/i,
  /\bcheating\b/i,
  /\bdiagnos/i,
  /\bnarcissist\b/i,
  /\battachment style\b/i,
  /\bADHD\b/i,
  /\bautism\b/i,
  /\bmanipulate\b/i,
  /\bmake them\b/i,
  /\bwin them back\b/i,
  /\bguaranteed\b/i,
  /\bthis proves\b/i,
  /\bemotional truth\b/i,
  /\bstreak\b/i,
  /\bdon't miss out\b/i,
  /\bkeep checking\b/i,
];

test("web user-facing copy avoids unsafe claim and dark-pattern phrases", () => {
  for (const file of USER_FACING_FILES) {
    let text = readFileSync(resolve(ROOT, file), "utf8");
    for (const phrase of ALLOWED_BOUNDARY_PHRASES) {
      text = text.replaceAll(phrase, "");
    }
    for (const pattern of BLOCKED_PATTERNS) {
      assert.equal(pattern.test(text), false, `${file} matched ${pattern}`);
    }
  }
});
