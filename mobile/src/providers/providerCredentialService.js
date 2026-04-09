import { createProviderSecureStore } from "../secureStorage/providerSecureStore.js";
import { buildProviderStatusPayload } from "./providerStatus.js";
import { maskProviderCredential } from "./providerViewModel.js";

export function createProviderCredentialService(options = {}) {
  const secureStore = createProviderSecureStore(options);

  async function getProviderCredentialState({
    providerName,
    displayName,
    enabled = false,
    authMode = "disabled",
    modelName = "",
    providerMode = "local_only",
    externalProcessingUsed = false,
  } = {}) {
    const availability = await secureStore.secureStorageAvailable();
    const credentialResult =
      authMode === "byok"
        ? await secureStore.getProviderCredential(providerName)
        : {
            credentialPresent: false,
          };

    const payload = buildProviderStatusPayload({
      providerName,
      displayName,
      enabled,
      authMode,
      providerMode,
      modelName,
      secureStorageAvailable: availability.available,
      credentialPresent: Boolean(credentialResult.credentialPresent),
      externalProcessingUsed,
    });
    payload.masked_credential = credentialResult.credentialPresent
      ? maskProviderCredential(credentialResult.credential)
      : "";
    return payload;
  }

  async function getMaskedProviderCredential(providerName) {
    const credentialResult = await secureStore.getProviderCredential(providerName);
    return {
      provider: providerName,
      credentialPresent: Boolean(credentialResult.credentialPresent),
      maskedCredential: credentialResult.credentialPresent
        ? maskProviderCredential(credentialResult.credential)
        : "",
    };
  }

  async function disconnectProvider(providerName) {
    return secureStore.deleteProviderCredential(providerName);
  }

  return {
    ...secureStore,
    getProviderCredentialState,
    getMaskedProviderCredential,
    disconnectProvider,
  };
}
