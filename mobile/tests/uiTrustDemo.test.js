import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const ROOT = resolve(import.meta.dirname, "..");

test("mobile landing uses required trust-first hero and synthetic-first actions", () => {
  const appText = readFileSync(resolve(ROOT, "src/screens/VibeSignalApp.js"), "utf8");

  assert.match(appText, /Understand message patterns without guessing motives\./);
  assert.match(
    appText,
    /Vibe Signal highlights observable cues like clarity, ambiguity, pressure, reassurance, and repair opportunities/
  );
  assert.match(appText, /Try a synthetic example/);
  assert.match(appText, /See how it works/);
  assert.match(
    appText,
    /Use synthetic text first, or only messages you have permission to analyze\./
  );
  assert.match(appText, /Unclear ask/);
  assert.match(appText, /Pressure \/ urgency/);
  assert.match(appText, /Repair opportunity/);
  assert.match(appText, /Low-signal fallback/);
  assert.match(appText, /Boundary-respecting request/);
  assert.match(appText, /Overloaded message/);
  assert.match(appText, /Synthetic demo result/);
  assert.match(appText, /accessibilityRole="checkbox"/);
  assert.match(appText, /accessibilityLiveRegion="polite"/);
  assert.match(appText, /accessibilityLiveRegion="assertive"/);
});

test("mobile consumer UI avoids developer-facing backend and API detail copy", () => {
  for (const file of ["src/screens/VibeSignalApp.js", "src/screens/ProviderSettingsScreen.js"]) {
    const text = readFileSync(resolve(ROOT, file), "utf8");
    for (const forbidden of ["API detail", "Waiting for the local backend", "/api/"]) {
      assert.equal(text.includes(forbidden), false, `${file} exposed ${forbidden}`);
    }
  }
});

test("provider screen custom consent checkboxes expose accessibility roles and state", () => {
  const providerText = readFileSync(resolve(ROOT, "src/screens/ProviderSettingsScreen.js"), "utf8");
  assert.match(providerText, /accessibilityRole="checkbox"/);
  assert.match(providerText, /accessibilityState=\{\{ checked: analysisConsent \}\}/);
  assert.match(providerText, /accessibilityState=\{\{ checked: matchConsent \}\}/);
  assert.match(providerText, /accessibilityState=\{\{ checked: state\.consentAcknowledged \}\}/);
});
