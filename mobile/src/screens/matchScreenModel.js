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

function titleCase(value) {
  const text = normalizeText(value || "cue")
    .replace(/_/g, " ")
    .replace(/\s+/g, " ")
    .toLowerCase();
  return `${text.charAt(0).toUpperCase()}${text.slice(1)}`;
}

const CAN_TELL = [
  "Spot vague or overloaded messages",
  "Identify unclear asks",
  "Surface pressure or urgency cues",
  "Show reassurance and repair opportunities",
  "Suggest clearer, lower-pressure replies",
];

const CANNOT_TELL = [
  "Whether someone likes you",
  "Whether someone is cheating",
  "Whether someone is lying",
  "What someone secretly means",
  "Someone’s diagnosis, attachment style, neurotype, or personality",
  "Whether a relationship will work",
];

const DEFAULT_NEXT_STEPS = [
  "Clarify one ask in plain language.",
  "Lower pressure by making no or later acceptable.",
  "Pause before replying if the exchange feels escalated.",
];

const DEFAULT_CANNOT_INFER =
  "This does not prove intent, attraction, honesty, or emotional state.";
const LOW_SIGNAL_TRIGGERS = new Set(["hey", "hi", "ok", "okay", "k", "fine", "lol", "lol sure"]);

export const FEEDBACK_OPTIONS = [
  { id: "useful", label: "Useful", rating: 1, comment: "" },
  { id: "too_strong", label: "Too strong", rating: 0, comment: "" },
  { id: "missed_context", label: "Missed context", rating: 0, comment: "" },
  { id: "unsafe_wording", label: "Unsafe wording", rating: 0, comment: "" },
  { id: "confusing", label: "Confusing", rating: 0, comment: "" },
];

function collectEvidenceRows(result) {
  return [
    ...(Array.isArray(result?.evidence) ? result.evidence : []),
    ...(Array.isArray(result?.inconsistency_cues) ? result.inconsistency_cues : []),
    ...(Array.isArray(result?.unsupported_claim_shift) ? result.unsupported_claim_shift : []),
    ...(Array.isArray(result?.specificity_drop) ? result.specificity_drop : []),
    ...(Array.isArray(result?.answer_evasion_pattern) ? result.answer_evasion_pattern : []),
    ...(Array.isArray(result?.contradiction_against_prior_message)
      ? result.contradiction_against_prior_message
      : []),
  ];
}

function collectEvidencePhrases(result) {
  const seen = new Set();
  const phrases = [];
  for (const row of collectEvidenceRows(result)) {
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
  const seen = new Set();
  return collectEvidenceRows(result)
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

function signalStrengthLabel(value) {
  const normalized = normalizeText(value || "medium").toLowerCase().replace(/_/g, " ");
  if (normalized === "high") {
    return "High — multiple visible cues point to the same pattern.";
  }
  if (normalized === "low") {
    return "Low — one cue is visible, but context could easily change the read.";
  }
  if (normalized === "insufficient") {
    return "Insufficient — there is not enough visible context for a safe read.";
  }
  return "Medium — there is evidence, but context could change the read.";
}

export function isContextLightInput(text) {
  const normalized = normalizeText(text).toLowerCase().replace(/\s+/g, " ");
  if (!normalized) {
    return false;
  }
  if (LOW_SIGNAL_TRIGGERS.has(normalized)) {
    return true;
  }
  const words = normalized.split(/\s+/).filter(Boolean);
  return words.length <= 2 && normalized.length <= 14;
}

export function buildLowSignalFallback(text = "") {
  return {
    inputPreviewLength: normalizeText(text).length,
    isLowSignal: true,
    resultState: "low_signal",
    signalStrength: "insufficient",
    signalStrengthLabel: signalStrengthLabel("insufficient"),
    title: "Not enough context to read safely.",
    body:
      "This message is too short or context-light. Vibe Signal can help with wording patterns, but this would be over-reading it.",
    tryItems: ["Add the previous message", "Ask for a clearer version", "Try a synthetic example"],
    mainRead: "Not enough context to read safely.",
    evidencePhrases: [],
    evidenceDetails: [],
    patternLabels: ["Context-light message"],
    patternExplanation:
      "There is not enough observable wording to separate a pattern from ordinary short-message noise.",
    cannotInferText: DEFAULT_CANNOT_INFER,
    safeNextStep: "Add the previous message or try a synthetic example.",
    safeNextSteps: ["Add the previous message or try a synthetic example."],
    canTell: CAN_TELL,
    cannotInfer: CANNOT_TELL,
    feedbackOptions: FEEDBACK_OPTIONS,
  };
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
      "self: Can you confirm Friday?\nother: maybe later, not sure yet",
    helper:
      "Use one line per message. Prefix lines with self: or other: for stronger evidence.",
    consentTitle: "Before you paste",
    consentBullets: [
      "Only submit messages you have permission to analyze.",
      "Remove names, phone numbers, addresses, and sensitive details.",
      "Use synthetic examples if you just want to test the app.",
    ],
    consentCheckboxLabel: "I understand and have permission to analyze this text.",
    consentLabel:
      "Only submit messages you have permission to analyze. Matching is communication-support only.",
    privacyNote:
      "Do not include sensitive personal data, secrets, medical data, legal documents, financial data, or third-party private messages without permission. Closed beta privacy and terms drafts require legal review before public launch.",
    statusLabel: loading ? "Checking communication fit..." : "Review communication patterns",
    submitEnabled: hasText && backendConfigured && !loading,
    emptyLabel: backendConfigured
      ? "Paste a short exchange to review communication patterns."
      : "Private analysis is not connected in this build. Synthetic demos still work.",
  };
}

export function buildMatchResultViewModel(result = {}) {
  const resultState = normalizeText(result?.result_state);
  const isLowSignal =
    resultState === "low_signal" ||
    result?.low_signal_fallback === true ||
    result?.signal_strength === "insufficient";

  if (isLowSignal) {
    return {
      ...buildLowSignalFallback(""),
      hasResult: Boolean(result && Object.keys(result).length),
      bandLabel: "Insufficient signal",
      confidenceLabel: result?.confidence?.level
        ? `${normalizeText(result.confidence.level)} evidence confidence`
        : "Evidence confidence unavailable",
      confidenceReasons: normalizeList(result?.confidence?.reasons).slice(0, 3),
      disclosure:
        "This is a bounded communication-pattern review, not a verdict about another person.",
    };
  }

  const positiveFactors = normalizeList(
    result?.positive_factors?.length ? result.positive_factors : result?.top_alignment_factors
  );
  const riskFactors = normalizeList(
    result?.risk_factors?.length ? result.risk_factors : result?.top_friction_factors
  );
  const evidenceDetails = collectEvidenceDetails(result);
  const safeNextSteps = normalizeList(result?.safe_next_steps).length
    ? normalizeList(result?.safe_next_steps)
    : DEFAULT_NEXT_STEPS;

  return {
    hasResult: Boolean(result && Object.keys(result).length),
    resultState,
    isLowSignal: false,
    signalStrength: normalizeText(result?.signal_strength || "medium"),
    signalStrengthLabel: signalStrengthLabel(result?.signal_strength || "medium"),
    bandLabel: titleCaseBand(result?.compatibility_band),
    confidenceLabel: result?.confidence?.level
      ? `${normalizeText(result.confidence.level)} evidence confidence`
      : "Evidence confidence unavailable",
    confidenceReasons: normalizeList(result?.confidence?.reasons).slice(0, 3),
    positiveFactors,
    riskFactors,
    evidencePhrases: collectEvidencePhrases(result),
    evidenceDetails,
    patternLabels: evidenceDetails.length
      ? evidenceDetails.map((row) => titleCase(row.family || "cue"))
      : ["Observable wording"],
    patternExplanation:
      evidenceDetails.map((row) => normalizeText(row.explanation)).find(Boolean) ||
      "This pattern is based on the quoted wording above.",
    mainRead:
      normalizeText(result?.main_read) ||
      normalizeText(result?.safe_explanation) ||
      normalizeText(result?.safe_summary) ||
      "This result is based on explicit observable communication cues.",
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
    cannotInferText: DEFAULT_CANNOT_INFER,
    safeNextSteps,
    safeNextStep: safeNextSteps[0],
    feedbackOptions: FEEDBACK_OPTIONS,
    disclosure:
      "This is a bounded communication-pattern review, not a verdict about another person.",
  };
}
