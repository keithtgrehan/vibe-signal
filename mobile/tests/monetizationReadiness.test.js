import test from "node:test";
import assert from "node:assert/strict";

import { getMonetizationReadiness } from "../src/commerce/monetizationReadiness.js";
import { buildPaywallViewModel } from "../src/components/paywallViewModel.js";

test("monetization readiness reports missing RevenueCat key and legal links honestly", () => {
  const readiness = getMonetizationReadiness();

  assert.equal(readiness.purchaseReady, false);
  assert.equal(readiness.restoreReady, false);
  assert.equal(readiness.revenueCatKeyConfigured, false);
  assert.match(readiness.errors.join(","), /missing_revenuecat_api_key/);
  assert.match(readiness.warnings.join(","), /missing_privacy_policy_url/);
  assert.match(readiness.warnings.join(","), /missing_terms_url/);
});

test("paywall view model disables purchase when product metadata is not live", () => {
  const model = buildPaywallViewModel({
    premiumActive: false,
    priceDisplay: "€1.89/month",
    purchaseAvailable: false,
    restoreAvailable: true,
    storeMetadata: {
      subscriptionDisclosure: {
        planName: "VibeSignal Pro Monthly",
        billingFrequency: "Monthly subscription",
        priceDisplay: "€1.89/month",
        cancellationInfo: "Cancel anytime in your Apple account subscription settings.",
      },
      privacyPolicyUrl: "",
      termsUrl: "",
    },
    statusMessage: "Premium purchases aren't configured in this build yet.",
  });

  assert.equal(model.purchaseEnabled, false);
  assert.equal(model.restoreEnabled, true);
  assert.equal(model.legalLinks.length, 0);
  assert.match(model.legalLinksMessage, /secure HTTPS URLs/i);
  assert.match(model.disclosureLines[2], /auto-renewing subscription/i);
});

test("paywall view model can show a value-first teaser before the hard limit", () => {
  const model = buildPaywallViewModel({
    premiumActive: false,
    softPrompt: true,
    priceDisplay: "€1.89/month",
    purchaseAvailable: true,
    restoreAvailable: true,
    storeMetadata: {
      subscriptionDisclosure: {
        priceDisplay: "€1.89/month",
      },
      privacyPolicyUrl: "https://example.test/privacy",
      termsUrl: "https://example.test/terms",
    },
  });

  assert.equal(model.title, "Unlock deeper pattern detection");
  assert.match(model.body, /started spotting the shift/i);
});

test("paywall view model only accepts secure legal links", () => {
  const model = buildPaywallViewModel({
    premiumActive: false,
    priceDisplay: "€1.89/month",
    purchaseAvailable: true,
    restoreAvailable: false,
    storeMetadata: {
      subscriptionDisclosure: {
        priceDisplay: "€1.89/month",
      },
      privacyPolicyUrl: "http://example.test/privacy",
      termsUrl: "javascript:alert(1)",
    },
    statusMessage: "",
  });

  assert.equal(model.purchaseEnabled, true);
  assert.equal(model.restoreEnabled, false);
  assert.equal(model.legalLinks.length, 0);
  assert.equal(model.legalLinksConfigured, false);
  assert.match(model.legalLinksMessage, /secure HTTPS URLs/i);
});

test("paywall view model preserves secure legal links", () => {
  const model = buildPaywallViewModel({
    premiumActive: false,
    priceDisplay: "€1.89/month",
    purchaseAvailable: true,
    restoreAvailable: true,
    storeMetadata: {
      subscriptionDisclosure: {
        priceDisplay: "€1.89/month",
      },
      privacyPolicyUrl: "https://example.test/privacy",
      termsUrl: "https://example.test/terms",
    },
    statusMessage: "",
  });

  assert.equal(model.legalLinks.length, 2);
  assert.equal(model.legalLinksConfigured, true);
  assert.equal(model.legalLinksMessage, "");
});
