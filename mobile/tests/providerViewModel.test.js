import test from "node:test";
import assert from "node:assert/strict";

import {
  buildProviderActionState,
  buildProviderReadinessCopy,
  buildProviderVerificationModel,
  deriveProviderFlowState,
  formatSavedCredentialLabel,
  maskProviderCredential,
} from "../src/providers/providerViewModel.js";

test("credential masking hides the middle of a saved key", () => {
  const masked = maskProviderCredential("sk_live_1234567890");
  assert.equal(masked.includes("1234567890"), false);
  assert.equal(masked, "••••7890");
});

test("saved key labels stay clean across provider formats", () => {
  assert.equal(
    formatSavedCredentialLabel("sk-proj-1234ABCD"),
    "Saved key ending in ••••ABCD"
  );
  assert.equal(
    formatSavedCredentialLabel("sk-ant-api03-xyzWXYZ"),
    "Saved key ending in ••••WXYZ"
  );
  assert.equal(
    formatSavedCredentialLabel("gsk_live_9876"),
    "Saved key ending in ••••9876"
  );
});

test("disabled action state reflects loading and validation truthfully", () => {
  const disabledBusy = buildProviderActionState({
    busy: true,
    selectedProvider: "openai",
    draftCredential: "sk-test",
    credentialPresent: true,
    consentAcknowledged: true,
    validationStatus: "ready",
  });
  assert.equal(disabledBusy.disableSave, true);
  assert.equal(disabledBusy.disableRun, true);
  assert.equal(disabledBusy.disableValidate, true);

  const ready = buildProviderActionState({
    busy: false,
    selectedProvider: "openai",
    draftCredential: "",
    credentialPresent: true,
    consentAcknowledged: true,
    validationStatus: "ready",
  });
  assert.equal(ready.disableRun, false);
  assert.equal(ready.disableValidate, true);

  const keyEntered = buildProviderActionState({
    busy: false,
    selectedProvider: "openai",
    draftCredential: "sk-valid-123456",
    credentialPresent: false,
  });
  assert.equal(keyEntered.disableValidate, false);
});

test("readiness copy stays user-facing and avoids raw storage-debug wording", () => {
  assert.equal(
    buildProviderReadinessCopy({
      storageResolved: true,
      credentialPresent: false,
    }),
    "No key saved yet"
  );

  assert.equal(
    buildProviderReadinessCopy({
      storageResolved: true,
      credentialPresent: true,
    }),
    "Ready to use"
  );

  assert.equal(
    buildProviderReadinessCopy({
      saveMessage: "Couldn't save key — try again",
    }),
    "Couldn't save key — try again"
  );
});

test("verification model distinguishes empty, verifying, success, and failure states", () => {
  assert.equal(
    buildProviderVerificationModel({
      selectedProvider: "openai",
      credentialPresent: false,
    }).title,
    "No key saved yet"
  );

  assert.equal(
    buildProviderVerificationModel({
      selectedProvider: "openai",
      busy: true,
      pendingAction: "verify",
    }).title,
    "Checking key..."
  );

  assert.equal(
    buildProviderVerificationModel({
      selectedProvider: "openai",
      draftCredential: "sk-valid-123456",
      credentialPresent: true,
      validationStatus: "ready",
      validationMessage: "Key verified and saved",
    }).helper,
    "Key verified and saved"
  );

  assert.equal(
    buildProviderVerificationModel({
      selectedProvider: "openai",
      draftCredential: "sk-valid-123456",
      credentialPresent: true,
      validationStatus: "ready",
    }).title,
    "Key verified"
  );

  assert.equal(
    buildProviderVerificationModel({
      selectedProvider: "openai",
      validationStatus: "invalid_credentials",
    }).title,
    "Couldn't verify key"
  );

  assert.equal(
    buildProviderVerificationModel({
      selectedProvider: "openai",
      validationStatus: "provider_unavailable",
    }).title,
    "Couldn't reach provider"
  );
});

test("provider flow state follows the expected BYOK state machine", () => {
  assert.equal(deriveProviderFlowState({}), "no_provider");
  assert.equal(
    deriveProviderFlowState({
      selectedProvider: "openai",
    }),
    "provider_selected"
  );
  assert.equal(
    deriveProviderFlowState({
      selectedProvider: "openai",
      draftCredential: "sk-draft-123456",
    }),
    "key_entered"
  );
  assert.equal(
    deriveProviderFlowState({
      selectedProvider: "openai",
      busy: true,
      pendingAction: "verify",
    }),
    "verifying"
  );
  assert.equal(
    deriveProviderFlowState({
      selectedProvider: "openai",
      credentialPresent: true,
      validationStatus: "ready",
    }),
    "verified"
  );
  assert.equal(
    deriveProviderFlowState({
      selectedProvider: "openai",
      validationStatus: "invalid_credentials",
    }),
    "failed"
  );
});
