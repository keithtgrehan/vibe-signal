import { createProviderCredentialService } from "./providerCredentialService.js";
import { getProviderCatalogEntry, listProviderOptions } from "./providerCatalog.js";
import { buildProviderActionState, maskProviderCredential } from "./providerViewModel.js";
import { requestProviderSummary, validateStoredProviderCredential } from "./providerValidation.js";

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
    let workingState = currentState;

    if (trimmedCredential) {
      const saveStep = await saveCredential({
        providerName,
        apiKey: trimmedCredential,
        consentAcknowledged,
        currentState: {
          ...currentState,
          draftCredential: trimmedCredential,
        },
      });
      workingState = saveStep.state;
      if (!saveStep.result.ok) {
        return {
          result: {
            status: saveStep.result.reason || "credential_save_blocked",
            user_message: "Couldn't save key — try again",
          },
          state: workingState,
        };
      }
    }

    const validateStep = await validateProvider({
      providerName,
      consentAcknowledged,
      fetchImpl,
      timeoutMs,
      currentState: workingState,
    });

    if (validateStep.result.status !== "ready" && trimmedCredential) {
      validateStep.state.draftCredential = trimmedCredential;
    }

    return validateStep;
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
