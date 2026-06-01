function normalizeText(value) {
  return String(value || "").trim();
}

function normalizeList(value) {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.map((item) => normalizeText(item)).filter(Boolean);
}

function titleCaseBand(value) {
  const text = normalizeText(value || "mixed").toLowerCase();
  if (!text) {
    return "Mixed fit";
  }
  return `${text.charAt(0).toUpperCase()}${text.slice(1)} fit`;
}

function collectEvidencePhrases(result) {
  const rows = [
    ...(Array.isArray(result?.evidence) ? result.evidence : []),
    ...(Array.isArray(result?.inconsistency_cues) ? result.inconsistency_cues : []),
    ...(Array.isArray(result?.unsupported_claim_shift) ? result.unsupported_claim_shift : []),
    ...(Array.isArray(result?.specificity_drop) ? result.specificity_drop : []),
    ...(Array.isArray(result?.answer_evasion_pattern) ? result.answer_evasion_pattern : []),
    ...(Array.isArray(result?.contradiction_against_prior_message)
      ? result.contradiction_against_prior_message
      : []),
  ];
  const seen = new Set();
  const phrases = [];
  for (const row of rows) {
    const phrase = normalizeText(row?.safe_phrase);
    if (!phrase || seen.has(phrase)) {
      continue;
    }
    seen.add(phrase);
    phrases.push(phrase);
  }
  return phrases.slice(0, 6);
}

export function buildMatchComposerState({
  conversationText = "",
  loading = false,
  apiUrl = process.env.EXPO_PUBLIC_API_URL || "",
} = {}) {
  const hasText = Boolean(normalizeText(conversationText));
  const backendConfigured = Boolean(normalizeText(apiUrl));
  return {
    empty: !hasText,
    backendConfigured,
    placeholder:
      "self: Can you confirm Friday at 3pm?\nother: Yes, Friday at 3pm works. No pressure if we need to adjust.",
    helper:
      "Use one line per message. Prefix lines with self: or other: for stronger evidence.",
    statusLabel: loading ? "Checking communication fit..." : "Check communication fit",
    submitEnabled: hasText && backendConfigured && !loading,
    emptyLabel: backendConfigured
      ? "Paste a short exchange to check communication fit."
      : "Set EXPO_PUBLIC_API_URL to use backend matching locally.",
  };
}

export function buildMatchResultViewModel(result = {}) {
  const score = Number(result?.score ?? 0);
  const normalizedScore = Number.isFinite(score) ? Math.max(0, Math.min(1, score)) : 0;
  const positiveFactors = normalizeList(
    result?.positive_factors?.length ? result.positive_factors : result?.top_alignment_factors
  );
  const riskFactors = normalizeList(
    result?.risk_factors?.length ? result.risk_factors : result?.top_friction_factors
  );

  return {
    hasResult: Boolean(result && Object.keys(result).length),
    compatibilityScoreLabel: `${Math.round(normalizedScore * 100)}%`,
    rawScore: normalizedScore,
    bandLabel: titleCaseBand(result?.compatibility_band),
    positiveFactors,
    riskFactors,
    evidencePhrases: collectEvidencePhrases(result),
    explanation:
      normalizeText(result?.safe_explanation) ||
      normalizeText(result?.safe_summary) ||
      "Compatibility is based on explicit observable communication cues.",
    emptyPositiveLabel: "No strong alignment factor is visible from the current text.",
    emptyRiskLabel: "No major deterministic friction cue is visible from the current text.",
    emptyEvidenceLabel: "No evidence phrases returned yet.",
    disclosure:
      "The match score reflects observable communication-pattern compatibility, not feelings, motives, identity, health, or relationship outcomes.",
  };
}
