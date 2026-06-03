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

const CAN_TELL = [
  "Observable wording patterns such as direct asks, specificity, pressure, reassurance, and repair openings.",
  "Whether the visible exchange has enough evidence for a bounded pattern review.",
  "Lower-pressure next steps such as clarifying, pausing, or naming a boundary.",
];

const CANNOT_TELL = [
  "Private feelings, motives, attraction, or future relationship outcomes.",
  "Deception verdicts or private context not present in the text.",
  "Clinical, neurodevelopmental, personality, relationship-style, or identity labels.",
  "Whether you should reply or how to influence another person.",
];

const DEFAULT_NEXT_STEPS = [
  "Clarify one ask in plain language.",
  "Lower pressure by making no or later acceptable.",
  "Pause before replying if the exchange feels escalated.",
];

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

function collectEvidenceDetails(result) {
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
  return rows
    .filter((row) => {
      const evidenceId = normalizeText(row?.evidence_id);
      if (!evidenceId || seen.has(evidenceId)) {
        return false;
      }
      seen.add(evidenceId);
      return normalizeText(row?.safe_phrase || row?.evidence_text);
    })
    .slice(0, 6)
    .map((row) => ({
      id: normalizeText(row.evidence_id),
      family: normalizeText(row.cue_family || row.cue_id || "cue").replace(/_/g, " "),
      phrase: normalizeText(row.safe_phrase || row.evidence_text),
      explanation: normalizeText(row.explanation),
      repair: normalizeText(row.repair_suggestion),
    }));
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
    consentLabel:
      "Only submit messages you have permission to analyze. Matching is communication-support only.",
    privacyNote:
      "Do not include sensitive personal data, secrets, medical data, legal documents, financial data, or third-party private messages without permission. Closed beta privacy and terms drafts require legal review before public launch.",
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
  const resultState = normalizeText(result?.result_state);
  const isLowSignal =
    resultState === "low_signal" ||
    result?.low_signal_fallback === true ||
    result?.signal_strength === "insufficient";
  const positiveFactors = normalizeList(
    result?.positive_factors?.length ? result.positive_factors : result?.top_alignment_factors
  );
  const riskFactors = normalizeList(
    result?.risk_factors?.length ? result.risk_factors : result?.top_friction_factors
  );

  return {
    hasResult: Boolean(result && Object.keys(result).length),
    compatibilityScoreLabel: `${Math.round(normalizedScore * 100)}% cue-weight score`,
    rawScore: normalizedScore,
    resultState,
    isLowSignal,
    signalStrength: normalizeText(result?.signal_strength || (isLowSignal ? "insufficient" : "medium")),
    bandLabel: isLowSignal ? "Insufficient signal" : titleCaseBand(result?.compatibility_band),
    confidenceLabel: result?.confidence?.level
      ? `${normalizeText(result.confidence.level)} evidence confidence`
      : "Evidence confidence unavailable",
    confidenceReasons: normalizeList(result?.confidence?.reasons).slice(0, 3),
    positiveFactors,
    riskFactors,
    evidencePhrases: collectEvidencePhrases(result),
    evidenceDetails: collectEvidenceDetails(result),
    explanation:
      normalizeText(result?.safe_explanation) ||
      normalizeText(result?.safe_summary) ||
      "This result is based on explicit observable communication cues.",
    emptyPositiveLabel: "No strong alignment factor is visible from the current text.",
    emptyRiskLabel: "No major deterministic friction cue is visible from the current text.",
    emptyEvidenceLabel: "No evidence phrases returned yet.",
    canTell: CAN_TELL,
    cannotInfer: normalizeList(result?.cannot_infer).length
      ? normalizeList(result?.cannot_infer)
      : CANNOT_TELL,
    safeNextSteps: normalizeList(result?.safe_next_steps).length
      ? normalizeList(result?.safe_next_steps)
      : DEFAULT_NEXT_STEPS,
    disclosure:
      "This is a bounded communication-pattern review, not a verdict about another person.",
  };
}
