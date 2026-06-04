export const REPLY_ACTIONS = [
  {
    id: "ask_directly",
    label: "Ask directly",
    type: "ask_directly",
    title: "Ask directly",
    text: "Can you clarify what you mean by that?",
  },
  {
    id: "lower_pressure",
    label: "Lower pressure",
    type: "lower_pressure",
    title: "Lower pressure",
    text: "No rush — could you let me know when you have a clearer answer?",
  },
  {
    id: "set_boundary",
    label: "Set a boundary",
    type: "set_boundary",
    title: "Set a boundary",
    text: "I need a bit more time before I respond. I will come back to this later.",
  },
  {
    id: "repair_tone",
    label: "Repair tone",
    type: "repair_tone",
    title: "Repair tone",
    text: "I think I came across more strongly than I meant. Let me try that again.",
  },
  {
    id: "ask_for_timing",
    label: "Ask for timing",
    type: "ask_for_timing",
    title: "Ask for timing",
    text: "Could you give me a specific time or day that works?",
  },
];

const REDACTION_NOTE =
  "Helps remove obvious identifiers. This runs in your browser before analysis.";

const GOAL_NEXT_STEPS = {
  unclear:
    "Ask for the specific point that feels unclear, without guessing the reason behind it.",
  reduce_pressure:
    "Try a lower-pressure reply that leaves room to pause, answer later, or say no.",
  direct_ask:
    "Name the direct ask in one sentence, then decide what answer or timing you need.",
  over_reading:
    "Based on the evidence shown, avoid treating this as proof. Ask a clarifying question instead.",
  clearer_response:
    "Use the evidence shown to write one concrete next step, without guessing motives.",
};

function normalizeText(value) {
  return String(value || "").trim();
}

function words(value) {
  return normalizeText(value).toLowerCase().split(/\s+/).filter(Boolean);
}

function safeToken(value, fallback = "") {
  return normalizeText(value || fallback)
    .toLowerCase()
    .replace(/[^a-z0-9_.:-]/g, "_")
    .slice(0, 48);
}

function lowContextSnippet(value) {
  const text = normalizeText(value).toLowerCase().replace(/\s+/g, " ");
  return !text || (words(text).length <= 2 && text.length <= 16);
}

function hasConcreteTiming(value) {
  return /\b(?:today|tonight|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{1,2}(?::\d{2})?\s?(?:am|pm)?|\d{1,2}\/\d{1,2})\b/i.test(value);
}

function hasVagueTiming(value) {
  return /\b(?:maybe|later|sometime|not sure|we will see|eventually)\b/i.test(value);
}

function hasPressure(value) {
  return /\b(?:have to|need an answer|right now|tonight or|or this will|must)\b/i.test(value);
}

function hasRepair(value) {
  return /\b(?:sorry|appreciate|reset|try again|rephrase|came across)\b/i.test(value);
}

function hasWarmth(value) {
  return /\b(?:thanks|thank you|appreciate|works|sounds good|no rush)\b/i.test(value);
}

function firstMeaningfulPhrase(value) {
  const text = normalizeText(value)
    .replace(/^(?:self|other|me|them|unknown)\s*[:\-]\s*/i, "")
    .replace(/\s+/g, " ");
  return text.slice(0, 96);
}

function actionByType(type) {
  return REPLY_ACTIONS.find((action) => action.type === type) || REPLY_ACTIONS[0];
}

export function goalAwareNextStep(baseStep, goalId, styleId = "evidence") {
  const goalStep = GOAL_NEXT_STEPS[goalId] || GOAL_NEXT_STEPS.unclear;
  const cautionStep =
    styleId === "careful" || goalId === "over_reading"
      ? "Keep the limits visible before acting."
      : "";

  if (goalId === "over_reading") {
    return goalStep;
  }

  if (!normalizeText(baseStep)) {
    return [goalStep, cautionStep].filter(Boolean).join(" ");
  }

  if (goalId === "reduce_pressure" || goalId === "clearer_response") {
    return [goalStep, cautionStep].filter(Boolean).join(" ");
  }

  return [baseStep, `Your goal: ${goalStep}`, cautionStep].filter(Boolean).join(" ");
}

export function buildDraftReplyOptions({ goalId = "unclear", patternLabels = [], selectedType = "" } = {}) {
  const patternText = patternLabels.join(" ").toLowerCase();
  let orderedTypes;

  if (selectedType) {
    orderedTypes = [selectedType];
  } else if (goalId === "reduce_pressure") {
    orderedTypes = ["lower_pressure", "set_boundary", "ask_for_timing"];
  } else if (goalId === "over_reading") {
    orderedTypes = ["ask_directly", "lower_pressure"];
  } else if (goalId === "direct_ask") {
    orderedTypes = ["ask_directly", "ask_for_timing"];
  } else if (goalId === "clearer_response") {
    orderedTypes = ["ask_directly", "repair_tone", "set_boundary"];
  } else {
    orderedTypes = ["ask_directly", "ask_for_timing", "lower_pressure"];
  }

  if (!selectedType && /pressure|urgency|boundary/.test(patternText)) {
    orderedTypes = ["lower_pressure", "set_boundary", "ask_for_timing", ...orderedTypes];
  }
  if (!selectedType && /repair/.test(patternText)) {
    orderedTypes = ["repair_tone", "ask_directly", ...orderedTypes];
  }

  const seen = new Set();
  return orderedTypes
    .map((type) => actionByType(type))
    .filter((action) => {
      if (seen.has(action.type)) {
        return false;
      }
      seen.add(action.type);
      return true;
    })
    .slice(0, selectedType ? 1 : 3)
    .map((action) => ({
      ...action,
      label: "Draft option",
      helper: "Choose and edit before using.",
    }));
}

export function redactIdentifyingDetails(inputText) {
  let text = String(inputText || "");
  const replacements = [];

  function replace(pattern, token, id) {
    text = text.replace(pattern, (match) => {
      replacements.push({ type: id, length: match.length });
      return typeof token === "function" ? token(match) : token;
    });
  }

  replace(/\bhttps?:\/\/[^\s]+/gi, "[link]", "link");
  replace(/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi, "[email]", "email");
  replace(/(?:\+?\d[\d\s().-]{7,}\d)/g, "[phone]", "phone");
  text = text.replace(/(^|[\s(])@[A-Za-z0-9_]{2,30}\b/g, (match, prefix) => {
    replacements.push({ type: "handle", length: match.length });
    return `${prefix}[handle]`;
  });
  replace(
    /\b\d{1,5}\s+(?:[A-Za-z0-9'.-]+\s+){0,4}(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Drive|Dr|Lane|Ln|Court|Ct|Way)\.?\b/gi,
    "[address]",
    "address"
  );

  return {
    text,
    changed: text !== String(inputText || ""),
    replacements,
    note: REDACTION_NOTE,
  };
}

export function buildComparisonResult({ earlierText = "", laterText = "" } = {}) {
  const earlier = normalizeText(earlierText);
  const later = normalizeText(laterText);

  if (lowContextSnippet(earlier) || lowContextSnippet(later)) {
    return {
      match_id: "local_comparison_low_signal",
      comparison: true,
      low_signal_fallback: true,
      result_state: "low_signal",
      signal_strength: "insufficient",
      safe_explanation:
        "Not enough context to compare safely. Add a fuller earlier and later snippet.",
      safe_next_steps: ["Add the previous message and the later reply, or try a synthetic demo."],
      evidence: [],
    };
  }

  const earlierConcrete = hasConcreteTiming(earlier);
  const laterConcrete = hasConcreteTiming(later);
  const laterVague = hasVagueTiming(later);
  const evidence = [];
  let summary = "What changed: the visible wording changed between the two snippets.";
  let pattern = "observable_change";
  let nextStep = "Name the visible change, then ask one clarifying question if it matters.";

  if (earlierConcrete && laterVague) {
    pattern = "specificity_drop";
    summary = "What changed: the later wording is less specific than the earlier wording.";
    nextStep = "Ask for the specific time, day, or decision point you need.";
    evidence.push({
      evidence_id: "comparison_earlier_specific",
      safe_phrase: firstMeaningfulPhrase(earlier),
      cue_family: "earlier_specificity",
      explanation: "The earlier wording includes a more concrete time or decision point.",
    });
    evidence.push({
      evidence_id: "comparison_later_vague",
      safe_phrase: firstMeaningfulPhrase(later),
      cue_family: "specificity_drop",
      explanation: "The later wording is more open-ended or less specific.",
    });
  } else if (!earlierConcrete && laterConcrete) {
    pattern = "timing_became_clearer";
    summary = "What changed: the later wording gives clearer timing than the earlier wording.";
    nextStep = "Confirm the timing if that is the decision you need to make.";
  } else if (hasPressure(later) && !hasPressure(earlier)) {
    pattern = "pressure_increased";
    summary = "What changed: the later wording adds urgency or consequence pressure.";
    nextStep = "Pause before replying and name when you can respond.";
  } else if (hasRepair(later) && !hasRepair(earlier)) {
    pattern = "repair_appeared";
    summary = "What changed: the later wording includes a repair or reset cue.";
    nextStep = "Keep the reply specific and leave room for a calmer reset.";
  } else if (hasWarmth(later) && !hasWarmth(earlier)) {
    pattern = "tone_became_warmer";
    summary = "What changed: the later wording sounds warmer or more reassuring.";
    nextStep = "Respond to the concrete ask without treating warmth as a hidden meaning.";
  }

  if (!evidence.length) {
    evidence.push({
      evidence_id: "comparison_earlier",
      safe_phrase: firstMeaningfulPhrase(earlier),
      cue_family: "earlier_wording",
      explanation: "This is the earlier wording being compared.",
    });
    evidence.push({
      evidence_id: "comparison_later",
      safe_phrase: firstMeaningfulPhrase(later),
      cue_family: pattern,
      explanation: "This is the later wording being compared.",
    });
  }

  return {
    match_id: `local_comparison_${Date.now().toString(16)}`,
    comparison: true,
    result_state: "comparison",
    signal_strength: pattern === "observable_change" ? "low" : "medium",
    safe_explanation: summary,
    evidence,
    safe_next_steps: [nextStep],
  };
}

export function buildFeedbackMetadata({
  matchId,
  feedbackTag,
  cueId = "",
  cueFamily = "",
  evidenceQuality = "",
  goalId = "",
  contextId = "",
  styleId = "",
  lowSignal = false,
  synthetic = false,
} = {}) {
  const safeMatchId = safeToken(matchId, "unknown");
  const safeTag = safeToken(feedbackTag, "feedback");
  const safeCueId = safeToken(cueId);
  const suffix = [safeMatchId, safeTag, safeCueId || "result", Date.now().toString(16)]
    .filter(Boolean)
    .join("_")
    .slice(0, 72);

  return {
    matchId: normalizeText(matchId),
    feedbackTag: safeTag,
    cueId: safeCueId,
    cueFamily: safeToken(cueFamily),
    evidenceQuality: safeToken(evidenceQuality),
    goalId: safeToken(goalId),
    contextId: safeToken(contextId),
    styleId: safeToken(styleId),
    lowSignal: lowSignal === true,
    synthetic: synthetic === true,
    clientEventId: `evt_feedback_${suffix}`,
    clientTimestamp: Date.now(),
  };
}
