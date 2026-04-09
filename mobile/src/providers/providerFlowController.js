import { createProviderCredentialService } from "./providerCredentialService.js";
import { getProviderCatalogEntry, listProviderOptions } from "./providerCatalog.js";
import { buildProviderActionState, maskProviderCredential } from "./providerViewModel.js";
import {
  requestProviderSummary,
  validateProviderCredentialDraft,
  validateStoredProviderCredential,
} from "./providerValidation.js";

export function createProviderFlowController(options = {}) {
  const credentialService = createProviderCredentialService(options);

  function buildBaseState(overrides = {}) {
    return {
      selectedProvider: "",
      draftCredential: "",
      maskedCredential: "",
      credentialPresent: false,
      secureStorageAvailable: null,
      storageResolved: false,
      consentAcknowledged: false,
      validationResult: null,
      lastRunResult: null,
      busy: false,
      pendingAction: "",
      saveMessage: "",
      providers: listProviderOptions(),
      ...overrides,
    };
  }

  async function hydrateProviderState({
    providerName,
    consentAcknowledged = false,
    currentState = {},
  } = {}) {
    const availability = await credentialService.secureStorageAvailable();
    const entry = getProviderCatalogEntry(providerName);
    if (!entry) {
      return buildBaseState({
        ...currentState,
        selectedProvider: "",
        secureStorageAvailable: Boolean(availability.available),
        storageResolved: true,
        consentAcknowledged,
      });
    }
    const credentialResult = await credentialService.getProviderCredential(entry.providerName);
    return buildBaseState({
      ...currentState,
      selectedProvider: entry.providerName,
      secureStorageAvailable: Boolean(availability.available),
      storageResolved: true,
      credentialPresent: Boolean(credentialResult.credentialPresent),
      maskedCredential: credentialResult.credentialPresent
        ? maskProviderCredential(credentialResult.credential)
        : "",
      consentAcknowledged,
    });
  }

  async function saveCredential({ providerName, apiKey, consentAcknowledged = false, currentState = {} } = {}) {
    const result = await credentialService.saveProviderCredential(providerName, apiKey);
    const nextState = await hydrateProviderState({
      providerName,
      consentAcknowledged,
      currentState: {
        ...currentState,
        draftCredential: result.ok ? "" : currentState.draftCredential || "",
        validationResult: null,
        lastRunResult: null,
        saveMessage: result.ok ? "" : "Couldn't save key — try again",
      },
    });
    return {
      result,
      state: nextState,
    };
  }

  async function removeCredential({ providerName, consentAcknowledged = false, currentState = {} } = {}) {
    const result = await credentialService.disconnectProvider(providerName);
    const nextState = await hydrateProviderState({
      providerName,
      consentAcknowledged,
      currentState: {
        ...currentState,
        validationResult: null,
        lastRunResult: null,
        saveMessage: "",
      },
    });
    return {
      result,
      state: nextState,
    };
  }

  async function validateProvider({
    providerName,
    consentAcknowledged = false,
    fetchImpl,
    timeoutMs,
    currentState = {},
  } = {}) {
    const result = await validateStoredProviderCredential({
      providerName,
      consentConfirmed: consentAcknowledged,
      secureStorage: credentialService,
      fetchImpl,
      timeoutMs,
    });
    const nextState = await hydrateProviderState({
      providerName,
      consentAcknowledged,
      currentState: {
        ...currentState,
        validationResult: result,
      },
    });
    nextState.validationResult = result;
    return {
      result,
      state: nextState,
    };
  }

  async function verifyCredential({
    providerName,
    apiKey = "",
    consentAcknowledged = false,
    fetchImpl,
    timeoutMs,
    currentState = {},
  } = {}) {
    const trimmedCredential = String(apiKey || currentState.draftCredential || "").trim();
    const validationResult = await validateProviderCredentialDraft({
      providerName,
      apiKey: trimmedCredential,
      consentConfirmed: consentAcknowledged,
      secureStorage: credentialService,
      fetchImpl,
      timeoutMs,
    });

    if (validationResult.status !== "ready") {
      const nextState = await hydrateProviderState({
        providerName,
        consentAcknowledged,
        currentState: {
          ...currentState,
          draftCredential: trimmedCredential,
          validationResult,
          lastRunResult: null,
          saveMessage:
            validationResult.status === "secure_storage_unavailable"
              ? "Couldn't save key — try again"
              : "",
        },
      });
      nextState.validationResult = validationResult;
      nextState.draftCredential = trimmedCredential;
      return {
        result: validationResult,
        state: nextState,
      };
    }

    const saveStep = await saveCredential({
      providerName,
      apiKey: trimmedCredential,
      consentAcknowledged,
      currentState: {
        ...currentState,
        draftCredential: trimmedCredential,
      },
    });

    if (!saveStep.result.ok) {
      const blockedResult = {
        ...validationResult,
        status: saveStep.result.reason || "credential_save_blocked",
        ready: false,
        user_message: "Couldn't save key — try again",
      };
      saveStep.state.validationResult = blockedResult;
      saveStep.state.draftCredential = trimmedCredential;
      return {
        result: blockedResult,
        state: saveStep.state,
      };
    }

    const successResult = {
      ...validationResult,
      user_message: "Key verified and saved",
      credential_present: true,
    };
    saveStep.state.validationResult = successResult;
    saveStep.state.saveMessage = "";
    return {
      result: successResult,
      state: saveStep.state,
    };
  }

  async function runExternalSummary({
    providerName,
    consentAcknowledged = false,
    signalBundle = {},
    selectedExcerpts = [],
    fetchImpl,
    timeoutMs,
    currentState = {},
  } = {}) {
    const validationResult = currentState.validationResult
      ? currentState.validationResult
      : (
          await validateProvider({
            providerName,
            consentAcknowledged,
            fetchImpl,
            timeoutMs,
            currentState,
          })
        ).result;

    if (validationResult.status !== "ready") {
      const gatedState = await hydrateProviderState({
        providerName,
        consentAcknowledged,
        currentState: {
          ...currentState,
          validationResult,
          lastRunResult: {
            status: validationResult.status,
            user_message: validationResult.user_message,
            ready: false,
          },
        },
      });
      gatedState.validationResult = validationResult;
      gatedState.lastRunResult = {
        status: validationResult.status,
        user_message: validationResult.user_message,
        ready: false,
      };
      return {
        result: gatedState.lastRunResult,
        state: gatedState,
      };
    }

    const runResult = await requestProviderSummary({
      providerName,
      consentConfirmed: consentAcknowledged,
      secureStorage: credentialService,
      signalBundle,
      selectedExcerpts,
      fetchImpl,
      timeoutMs,
    });
    const nextState = await hydrateProviderState({
      providerName,
      consentAcknowledged,
      currentState: {
        ...currentState,
        validationResult,
        lastRunResult: runResult,
      },
    });
    nextState.validationResult = validationResult;
    nextState.lastRunResult = runResult;
    return {
      result: runResult,
      state: nextState,
    };
  }

  function deriveActions(state = {}) {
    return buildProviderActionState({
      busy: state.busy,
      selectedProvider: state.selectedProvider,
      draftCredential: state.draftCredential,
      credentialPresent: state.credentialPresent,
      consentAcknowledged: state.consentAcknowledged,
      validationStatus: state.validationResult?.status || "",
    });
  }

  return {
    credentialService,
    buildBaseState,
    hydrateProviderState,
    saveCredential,
    removeCredential,
    validateProvider,
    verifyCredential,
    runExternalSummary,
    deriveActions,
  };
}
