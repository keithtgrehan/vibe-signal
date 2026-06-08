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
  "index.html",
];

const ALLOWED_BOUNDARY_PHRASES = [
  "Whether someone is cheating",
  "Whether someone is lying",
  "What someone secretly means",
  "Someone’s diagnosis, attachment style, neurotype, or personality",
  "Vibe Signal does not know intent, attraction, truthfulness, diagnosis, or outcomes.",
  "without guessing intent, attraction, deception, diagnosis, manipulation, neurotype, attachment style, or relationship outcomes",
  "no deception or cheating detection",
  "no diagnosis or therapy",
  "no manipulation advice",
];

const BLOCKED_PATTERNS = [
  /\bwhat did they actually mean\b/i,
  /\bwhat they(?:'|’)re really doing\b/i,
  /\bwhat it(?:'|’)s actually doing\b/i,
  /\binterest score\b/i,
  /\bavoidance\b/i,
  /\bsoft no\b/i,
  /\bpre-loads blame\b/i,
  /\bred flags\b/i,
  /\bmixed signals\b/i,
  /\bget the receipts\b/i,
  /\bshare my receipt\b/i,
  /\b1m people\b/i,
  /\bdecoded this week\b/i,
  /\bfomo\b/i,
  /\bfake ratings?\b/i,
  /\bdeleted the second you (?:leave|close this)\b/i,
  /★\s*\d/i,
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
