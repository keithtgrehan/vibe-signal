export function buildProviderConsentPayload(providerName) {
  const normalized = String(providerName || "").trim().toLowerCase();
  const names = {
    openai: "OpenAI",
    anthropic: "Anthropic",
    groq: "Groq",
  };
  const displayName = names[normalized] || "External Provider";
  return {
    provider_name: normalized,
    display_name: displayName,
    title: `${displayName} External AI Consent`,
    bullets: [
      "Local deterministic analysis stays on-device by default.",
      "External provider use is optional and must be enabled explicitly.",
      "Selected content may be sent to the provider when external summaries are requested.",
      "Use only content you have the right to submit.",
      "Provider credentials are stored securely on-device when secure storage is supported.",
      "The provider can be disconnected and its stored credential deleted later.",
    ],
  };
}
