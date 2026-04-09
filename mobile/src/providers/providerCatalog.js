export const PROVIDER_CATALOG = {
  openai: {
    providerName: "openai",
    displayName: "OpenAI",
    modelName: "gpt-4.1-mini",
    baseUrl: "https://api.openai.com/v1",
    validationPath: "/chat/completions",
    summaryPath: "/chat/completions",
  },
  anthropic: {
    providerName: "anthropic",
    displayName: "Anthropic",
    modelName: "claude-3-5-haiku-latest",
    baseUrl: "https://api.anthropic.com",
    validationPath: "/v1/messages",
    summaryPath: "/v1/messages",
  },
  groq: {
    providerName: "groq",
    displayName: "Groq",
    modelName: "llama-3.1-8b-instant",
    baseUrl: "https://api.groq.com/openai/v1",
    validationPath: "/chat/completions",
    summaryPath: "/chat/completions",
  },
};

export function getProviderCatalogEntry(providerName) {
  const normalized = String(providerName || "").trim().toLowerCase();
  return PROVIDER_CATALOG[normalized] || null;
}

export function listProviderOptions() {
  return Object.values(PROVIDER_CATALOG).map((entry) => ({
    provider_name: entry.providerName,
    display_name: entry.displayName,
    model_name: entry.modelName,
  }));
}
