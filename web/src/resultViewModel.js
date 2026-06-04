import { CAN_HELP_WITH, CANNOT_TELL, SYNTHETIC_DEMOS } from "./trustContent.js";

const DEFAULT_CANNOT_INFER =
  "This does not tell you what they feel or intend.";
const DEFAULT_NEXT_STEP = "Ask one clear, lower-pressure follow-up.";
const LOW_SIGNAL_TRIGGERS = new Set(["hey", "hi", "ok", "okay", "k", "fine", "lol", "lol sure"]);

export const EVIDENCE_QUALITY_LABELS = {
  strong: "Strong",
  mixed: "Mixed",
  low: "Low",
  insufficient: "Insufficient",
};

export const EVIDENCE_QUALITY_DESCRIPTIONS = {
  strong: "clear wording supports the pattern.",
  mixed: "More than one reading is possible.",
  low: "Context is limited.",
  insufficient: "Not enough evidence to analyze safely.",
};

const MISSING_CONTEXT_SUGGESTIONS = [
  "Add the previous message",
  "Add the question this replied to",
  "Add what decision you need to make",
  "Add timing if timing matters",
  "Try a synthetic demo",
];

export const FEEDBACK_OPTIONS = [
  { id: "useful", label: "Useful", rating: 1, comment: "" },
  { id: "too_strong", label: "Too strong", rating: 0, comment: "" },
  { id: "missed_context", label: "Missed context", rating: 0, comment: "" },
  { id: "unsafe_wording", label: "Unsafe wording", rating: 0, comment: "" },
  { id: "confusing", label: "Confusing", rating: 0, comment: "" },
];

function normalizeText(value) {
  return String(value || "").trim();
}

function normalizeList(value) {
  return Array.isArray(value) ? value.map(normalizeText).filter(Boolean) : [];
}

function titleCase(value) {
  const text = normalizeText(value || "pattern")
    .replace(/_/g, " ")
    .replace(/\s+/g, " ")
    .toLowerCase();
  return `${text.charAt(0).toUpperCase()}${text.slice(1)}`;
}

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

function evidenceQuality(row, signalStrength, rowCount) {
  const signal = normalizeText(signalStrength).toLowerCase();
  if (signal === "insufficient") {
    return "insufficient";
  }
  if (signal === "low") {
    return "low";
  }
  if (!normalizeText(row?.explanation)) {
    return "mixed";
  }
  if (signal === "high" || rowCount > 1) {
    return "strong";
  }
  return "mixed";
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
    title: "Not enough context to read safely.",
    body: "This message is too short or context-light. Add context or try a synthetic demo.",
    tryItems: MISSING_CONTEXT_SUGGESTIONS,
    contextSuggestions: MISSING_CONTEXT_SUGGESTIONS,
    mainRead: "Not enough context to read safely.",
    signalStrengthLabel: signalStrengthLabel("insufficient"),
    evidencePhrases: [],
    evidenceDetails: [],
    evidenceQualitySummary: "insufficient",
    patternLabels: ["Context-light message"],
    patternExplanation:
      "There is not enough observable wording to separate a pattern from ordinary short-message noise.",
    cannotInferText: DEFAULT_CANNOT_INFER,
    safeNextStep: "Add the previous message or try a synthetic demo.",
    canTell: CAN_HELP_WITH,
    cannotTell: CANNOT_TELL,
  };
}

export function buildNoEvidenceFallback() {
  return {
    inputPreviewLength: 0,
    isLowSignal: true,
    resultState: "no_safe_evidence",
    signalStrength: "insufficient",
    title: "No safe evidence phrase returned.",
    body:
      "This result did not include a safe quoted phrase, so Vibe Signal will not render a full read.",
    tryItems: MISSING_CONTEXT_SUGGESTIONS,
    contextSuggestions: MISSING_CONTEXT_SUGGESTIONS,
    mainRead: "No safe evidence phrase returned.",
    signalStrengthLabel: signalStrengthLabel("insufficient"),
    evidencePhrases: [],
    evidenceDetails: [],
    evidenceQualitySummary: "insufficient",
    patternLabels: ["Evidence unavailable"],
    patternExplanation:
      "A result needs at least one safe quoted phrase before Vibe Signal shows interpretation.",
    cannotInferText: DEFAULT_CANNOT_INFER,
    safeNextStep: "Add context or try a synthetic example before relying on this read.",
    canTell: CAN_HELP_WITH,
    cannotTell: CANNOT_TELL,
  };
}

export function buildSyntheticResult(demoId) {
  const demo = SYNTHETIC_DEMOS.find((item) => item.id === demoId) || SYNTHETIC_DEMOS[0];
  return {
    ...demo.result,
    synthetic: true,
    demoTitle: demo.title,
    requiresPrivateConsent: false,
  };
}

export function buildTrustFirstResultView(result = {}) {
  const resultState = normalizeText(result?.result_state);
  const isLowSignal =
    resultState === "low_signal" ||
    result?.low_signal_fallback === true ||
    result?.signal_strength === "insufficient";
  if (isLowSignal) {
    return {
      ...buildLowSignalFallback(""),
      matchId: normalizeText(result?.match_id),
      confidenceReasons: normalizeList(result?.confidence?.reasons).slice(0, 3),
    };
  }

  const rows = collectEvidenceRows(result);
  const evidenceDetails = rows
    .map((row, index) => {
      const cueId = normalizeText(row?.cue_family || row?.cue_id || "observable_cue");
      const quality = evidenceQuality(row, result?.signal_strength || "medium", rows.length);
      return {
        id: normalizeText(row?.evidence_id) || `evidence_${index}`,
        cueId,
        family: titleCase(cueId),
        phrase: normalizeText(row?.safe_phrase || row?.evidence_text),
        explanation: normalizeText(row?.explanation),
        repair: normalizeText(row?.repair_suggestion),
        quality,
        qualityLabel: EVIDENCE_QUALITY_LABELS[quality],
        qualityDescription: EVIDENCE_QUALITY_DESCRIPTIONS[quality],
      };
    })
    .filter((row) => row.phrase)
    .slice(0, 6);

  if (!evidenceDetails.length) {
    return {
      ...buildNoEvidenceFallback(),
      matchId: normalizeText(result?.match_id),
      confidenceReasons: normalizeList(result?.confidence?.reasons).slice(0, 3),
    };
  }

  const seenPatterns = new Set();
  const patternLabels = evidenceDetails
    .map((row) => row.family)
    .filter((family) => {
      if (seenPatterns.has(family)) {
        return false;
      }
      seenPatterns.add(family);
      return true;
    });
  const safeNextSteps = normalizeList(result?.safe_next_steps);
  const firstRepair = evidenceDetails.map((row) => row.repair).find(Boolean);

  return {
    matchId: normalizeText(result?.match_id),
    synthetic: result?.synthetic === true,
    comparison: result?.comparison === true,
    requiresPrivateConsent: result?.requiresPrivateConsent === true,
    isLowSignal: false,
    resultState,
    mainRead:
      normalizeText(result?.main_read) ||
      normalizeText(result?.safe_explanation) ||
      normalizeText(result?.safe_summary) ||
      "This result is based on observable wording cues in the exchange.",
    signalStrength: normalizeText(result?.signal_strength || "medium"),
    signalStrengthLabel: signalStrengthLabel(result?.signal_strength || "medium"),
    evidencePhrases: evidenceDetails.map((row) => row.phrase),
    evidenceDetails,
    evidenceQualitySummary:
      evidenceDetails.every((row) => row.quality === "strong")
        ? "strong"
        : evidenceDetails.some((row) => row.quality === "low")
          ? "low"
          : "mixed",
    patternLabels: patternLabels.length ? patternLabels : ["Observable wording"],
    patternExplanation:
      evidenceDetails.map((row) => row.explanation).find(Boolean) ||
      "This pattern is based on the quoted wording above.",
    interpretation:
      normalizeText(result?.safe_interpretation) ||
      evidenceDetails.map((row) => row.explanation).find(Boolean) ||
      "The safest read is limited to the wording shown here.",
    cannotInferText: DEFAULT_CANNOT_INFER,
    safeNextStep: safeNextSteps[0] || firstRepair || DEFAULT_NEXT_STEP,
    canTell: CAN_HELP_WITH,
    cannotTell: CANNOT_TELL,
    feedbackOptions: FEEDBACK_OPTIONS,
    disclosure:
      "Evidence is shown before interpretation so you can decide whether the read fits the wider context.",
  };
}
