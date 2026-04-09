const DISCLOSURE =
  "Pattern-based only. This summary does not determine intent, truth, or outcome.";

const INTRO =
  "This is a secondary summary based on the selected provider. Local pattern analysis remains the primary result.";

const BANNED_PATTERNS = [
  /\bcheat(?:ing|er)?\b/i,
  /\blying?\b/i,
  /\bliar\b/i,
  /\bfaithful\b/i,
  /\bunfaithful\b/i,
  /\bsuspicious(?:ly)?\b/i,
  /\bred flag(?:s)?\b/i,
  /\bexposed?\b/i,
  /\bcaught\b/i,
  /\bpass(?:ed|es)?\b/i,
  /\bfail(?:ed|s)?\b/i,
  /\bhired\b/i,
  /\brejected\b/i,
  /\bmanipulative?\b/i,
  /\btoxic\b/i,
  /\babusive\b/i,
  /\bthis means\b/i,
  /\bthis proves\b/i,
  /\bthis shows they are\b/i,
  /\bthis indicates they are\b/i,
  /\bthis suggests they are\b/i,
  /\btruth(?:ful)?\b/i,
  /\bintent\b/i,
  /\boutcome\b/i,
];

const MAX_SUMMARY_LENGTH = 220;
const MAX_BULLET_LENGTH = 110;
const MAX_PROMPT_LENGTH = 95;

function collapseWhitespace(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}

function clampText(text, limit) {
  return collapseWhitespace(text).slice(0, limit).trim();
}

function isSafeText(text) {
  const normalized = collapseWhitespace(text);
  if (!normalized) {
    return false;
  }
  return !BANNED_PATTERNS.some((pattern) => pattern.test(normalized));
}

function normalizeArray(values, limit, maxItems) {
  return (Array.isArray(values) ? values : [])
    .map((value) => clampText(value, limit))
    .filter((value) => isSafeText(value))
    .slice(0, maxItems);
}

function parseCandidate(value) {
  if (!value) {
    return null;
  }
  if (typeof value === "object") {
    return value;
  }
  const text = collapseWhitespace(value);
  if (!text) {
    return null;
  }
  try {
    return JSON.parse(text);
  } catch (_error) {
    return { summary: text };
  }
}

function extractPayloadCandidate(payload = {}) {
  const candidates = [
    payload,
    payload.output_text,
    payload.summary,
    payload.choices?.[0]?.message?.content,
    payload.content?.[0]?.text,
    payload.raw_text,
  ];

  for (const candidate of candidates) {
    const parsed = parseCandidate(candidate);
    if (parsed) {
      return parsed;
    }
  }
  return null;
}

function providerLabel(providerName) {
  const normalized = String(providerName || "").trim().toLowerCase();
  if (normalized === "anthropic") {
    return "Claude";
  }
  if (normalized === "openai") {
    return "OpenAI";
  }
  if (normalized === "groq") {
    return "Groq";
  }
  return "External Provider";
}

function collectHighlights(signalBundle = {}) {
  const highlights = [];
  const push = (value) => {
    const normalized = clampText(value, MAX_BULLET_LENGTH);
    if (normalized && isSafeText(normalized) && !highlights.includes(normalized)) {
      highlights.push(normalized);
    }
  };

  push(signalBundle?.shift_radar?.summary);
  for (const reason of signalBundle?.consistency?.top_reasons || []) {
    push(reason);
  }
  for (const change of signalBundle?.what_changed?.top_changes || []) {
    push(change);
  }
  push(signalBundle?.confidence_clarity?.confidence_marker_trend);

  return highlights.slice(0, 4);
}

export function buildFallbackExternalSummary({
  providerName,
  modelName,
  signalBundle = {},
  status = "success",
  usedFallback = true,
} = {}) {
  const highlights = collectHighlights(signalBundle);
  const fallbackSummary =
    highlights[0] ||
    "Compared with earlier messages, later replies read a little less detailed and more guarded.";

  return {
    provider: providerLabel(providerName),
    model: String(modelName || "").trim(),
    status,
    summary: clampText(fallbackSummary, MAX_SUMMARY_LENGTH),
    what_changed:
      highlights.slice(0, 3).length > 0
        ? highlights.slice(0, 3)
        : [
            "Later replies read shorter than earlier ones.",
            "Detail softens a little compared with the opening exchanges.",
          ],
    compare_prompts: [
      "Compare earlier replies with later replies for detail and pacing.",
      "Compare directness with specificity across the conversation.",
    ],
    disclosure: DISCLOSURE,
    intro: INTRO,
    used_fallback: usedFallback,
    safe_to_render: true,
  };
}

export function normalizeExternalSummary({
  providerName,
  modelName,
  payload,
  signalBundle = {},
} = {}) {
  const candidate = extractPayloadCandidate(payload);
  if (!candidate) {
    return buildFallbackExternalSummary({ providerName, modelName, signalBundle });
  }

  const summary = clampText(
    candidate.summary || candidate.output_text || candidate.text || "",
    MAX_SUMMARY_LENGTH
  );
  const whatChanged = normalizeArray(candidate.what_changed, MAX_BULLET_LENGTH, 3);
  const comparePrompts = normalizeArray(candidate.compare_prompts, MAX_PROMPT_LENGTH, 2);

  if (
    !isSafeText(summary) ||
    whatChanged.length === 0 ||
    comparePrompts.length === 0
  ) {
    return buildFallbackExternalSummary({ providerName, modelName, signalBundle });
  }

  return {
    provider: providerLabel(providerName),
    model: String(modelName || "").trim(),
    status: "success",
    summary,
    what_changed: whatChanged,
    compare_prompts: comparePrompts,
    disclosure: DISCLOSURE,
    intro: INTRO,
    used_fallback: false,
    safe_to_render: true,
  };
}

export function externalSummaryDisclosure() {
  return DISCLOSURE;
}

export function externalSummaryIntro() {
  return INTRO;
}
