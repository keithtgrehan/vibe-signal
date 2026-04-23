import { sanitizeLocalAnalysisResult } from "./localAnalysisGuardrails.js";

const MAX_SCREEN_WIDTH = 480;
const SCREEN_PADDING = 20;
const HEDGE_TERMS = ["maybe", "perhaps", "might", "could", "possibly", "probably", "guess", "sort of"];
const VAGUE_TERMS = ["thing", "stuff", "somehow", "whatever", "later", "soon", "eventually"];
const DIRECT_TERMS = ["exactly", "specifically", "clearly", "directly", "because", "need", "answer"];
const POSITIVE_URGENCY = ["now", "immediately", "urgent", "asap", "tonight", "today"];
const WEAK_INPUT_WORD_THRESHOLD = 26;

function normalizeText(text) {
  return String(text || "").trim();
}

function countWords(text) {
  return normalizeText(text)
    .split(/\s+/)
    .filter(Boolean).length;
}

function excerpt(text, max = 100) {
  const normalized = normalizeText(text);
  if (!normalized) {
    return "";
  }
  if (normalized.length <= max) {
    return normalized;
  }
  return `${normalized.slice(0, Math.max(0, max - 1)).trim()}…`;
}

function splitMeaningfulLines(text) {
  const normalized = normalizeText(text);
  if (!normalized) {
    return [];
  }
  const lines = normalized
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);
  if (lines.length > 1) {
    return lines;
  }
  return normalized
    .split(/(?<=[.!?])\s+/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function partitionSegments(segments) {
  if (segments.length <= 1) {
    return {
      earlier: segments,
      later: segments,
    };
  }
  const pivot = Math.ceil(segments.length / 2);
  return {
    earlier: segments.slice(0, pivot),
    later: segments.slice(pivot),
  };
}

function countMatches(text, terms) {
  const lowered = normalizeText(text).toLowerCase();
  return terms.reduce((count, term) => {
    const pattern = new RegExp(`\\b${term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "g");
    return count + (lowered.match(pattern) || []).length;
  }, 0);
}

function tokenList(text) {
  return normalizeText(text)
    .toLowerCase()
    .split(/[^a-z0-9]+/i)
    .filter((token) => token.length >= 3);
}

function tokenSet(text) {
  return new Set(tokenList(text).filter((token) => token.length >= 4));
}

function lexicalOverlap(a, b) {
  const aTokens = tokenSet(a);
  const bTokens = tokenSet(b);
  if (!aTokens.size || !bTokens.size) {
    return 0;
  }
  let shared = 0;
  for (const token of aTokens) {
    if (bTokens.has(token)) {
      shared += 1;
    }
  }
  return shared / Math.max(aTokens.size, bTokens.size);
}

function uniqueTokenRatio(text) {
  const tokens = tokenList(text);
  if (!tokens.length) {
    return 0;
  }
  return new Set(tokens).size / tokens.length;
}

function averageAdjacentOverlap(segments) {
  if (segments.length <= 1) {
    return 1;
  }
  let total = 0;
  let pairs = 0;
  for (let index = 1; index < segments.length; index += 1) {
    total += lexicalOverlap(segments[index - 1], segments[index]);
    pairs += 1;
  }
  return pairs ? total / pairs : 1;
}

function summarizeMetrics(segments) {
  const joined = segments.join(" ");
  const questionCount = (joined.match(/\?/g) || []).length;
  const exclamationCount = (joined.match(/!/g) || []).length;
  const urgencyCount = countMatches(joined, POSITIVE_URGENCY);

  return {
    text: joined,
    segmentCount: segments.length,
    averageWords: segments.length
      ? Math.round(
          segments.reduce((sum, item) => sum + countWords(item), 0) / segments.length
        )
      : 0,
    hedgeCount: countMatches(joined, HEDGE_TERMS),
    vagueCount: countMatches(joined, VAGUE_TERMS),
    directCount: countMatches(joined, DIRECT_TERMS),
    questionCount,
    toneScore: exclamationCount + urgencyCount + questionCount,
  };
}

function buildShiftProfile(earlierMetrics, laterMetrics) {
  return {
    vagueUp: laterMetrics.vagueCount > earlierMetrics.vagueCount,
    vagueDown: laterMetrics.vagueCount < earlierMetrics.vagueCount,
    hedgeUp: laterMetrics.hedgeCount > earlierMetrics.hedgeCount,
    hedgeDown: laterMetrics.hedgeCount < earlierMetrics.hedgeCount,
    directUp: laterMetrics.directCount > earlierMetrics.directCount,
    directDown: laterMetrics.directCount < earlierMetrics.directCount,
    shorter: laterMetrics.averageWords + 1 < earlierMetrics.averageWords,
    longer: laterMetrics.averageWords > earlierMetrics.averageWords + 1,
    urgencyUp: laterMetrics.toneScore > earlierMetrics.toneScore,
    urgencyDown: laterMetrics.toneScore < earlierMetrics.toneScore,
    overlapLow: laterMetrics.overlap < 0.22,
  };
}

function buildHeroHeadline({ analysisText = "", hasResult = false } = {}) {
  const normalizedText = normalizeText(analysisText);
  if (hasResult) {
    return "Detect tone shifts instantly";
  }
  if (normalizedText) {
    return "This message feels different. Here’s why.";
  }
  return "See what changed in how they’re talking to you";
}

function countShiftSignals(profile) {
  return [
    profile.vagueUp,
    profile.vagueDown,
    profile.hedgeUp,
    profile.hedgeDown,
    profile.directUp,
    profile.directDown,
    profile.shorter,
    profile.longer,
    profile.urgencyUp,
    profile.urgencyDown,
    profile.overlapLow,
  ].filter(Boolean).length;
}

function detectWeakSignal({
  normalizedText,
  segments,
  earlierMetrics,
  laterMetrics,
  profile,
} = {}) {
  const totalWords = countWords(normalizedText);
  const uniqueRatio = uniqueTokenRatio(normalizedText);
  const adjacentOverlap = averageAdjacentOverlap(segments);
  const overlap = Number(laterMetrics.overlap || 0);
  const shiftSignals = countShiftSignals(profile);

  const veryShortInput = totalWords > 0 && totalWords < WEAK_INPUT_WORD_THRESHOLD;
  const lowVarianceText = uniqueRatio > 0 && uniqueRatio < 0.5;
  const noClearToneShift =
    shiftSignals <= 1 &&
    Math.abs(laterMetrics.toneScore - earlierMetrics.toneScore) <= 1 &&
    Math.abs(laterMetrics.directCount - earlierMetrics.directCount) <= 1 &&
    Math.abs(laterMetrics.vagueCount - earlierMetrics.vagueCount) <= 1 &&
    Math.abs(laterMetrics.hedgeCount - earlierMetrics.hedgeCount) <= 1;
  const highLexicalSimilarity = overlap >= 0.72 || adjacentOverlap >= 0.75;

  const weakSignal =
    (veryShortInput && (noClearToneShift || highLexicalSimilarity)) ||
    (lowVarianceText && highLexicalSimilarity) ||
    (noClearToneShift && highLexicalSimilarity) ||
    (segments.length <= 2 && noClearToneShift);

  return {
    weakSignal,
    veryShortInput,
    lowVarianceText,
    noClearToneShift,
    highLexicalSimilarity,
    totalWords,
    uniqueRatio,
  };
}

function describeSignalStrength(profile) {
  const score = [
    profile.vagueUp,
    profile.hedgeUp,
    profile.directDown,
    profile.shorter,
    profile.urgencyDown,
  ].filter(Boolean).length + (profile.overlapLow ? 2 : 0);

  if (score >= 4) {
    return "Clear shift";
  }
  if (score >= 2) {
    return "Noticeable shift";
  }
  return "Subtle shift";
}

function buildHeadlineInsight(profile) {
  if (profile.overlapLow && profile.directDown) {
    return "This may be avoiding a direct answer";
  }
  if (profile.hedgeUp && profile.vagueUp) {
    return "They’re pulling back slightly";
  }
  if (profile.hedgeUp) {
    return "Tone just became less certain";
  }
  if (profile.vagueUp) {
    return "The wording gets less specific";
  }
  if (profile.shorter && profile.directDown) {
    return "The reply gets shorter and less direct";
  }
  if (profile.directUp && !profile.hedgeUp) {
    return "The message becomes more direct";
  }
  if (profile.urgencyUp) {
    return "The tone becomes more urgent";
  }
  if (profile.urgencyDown) {
    return "The tone feels more measured";
  }
  return "There’s a subtle shift in tone";
}

function describePrimaryPattern(earlierMetrics, laterMetrics, profile) {
  if (profile.overlapLow && profile.directDown) {
    return "The later wording could suggest a looser reply to the earlier point, with less direct follow-through.";
  }
  if (profile.hedgeUp && profile.vagueUp) {
    return "The later wording may indicate more distance, using softer and less specific phrasing.";
  }
  if (profile.hedgeUp) {
    return "The later wording may indicate more uncertainty than the opening.";
  }
  if (profile.vagueUp) {
    return "The later wording becomes broader and less pinned to detail.";
  }
  if (profile.directUp) {
    return "The later wording becomes clearer and more direct than the opening.";
  }
  if (profile.shorter) {
    return "The later wording compresses the response, which can change how open it feels.";
  }
  if (profile.urgencyUp) {
    return "The later wording sounds more urgent than the opening.";
  }
  return "The message stays fairly steady, with only a subtle shift in pacing and specificity.";
}

function pushUnique(items, value) {
  const normalized = normalizeText(value);
  if (!normalized || items.includes(normalized)) {
    return;
  }
  items.push(normalized);
}

function buildWhatChanged(profile) {
  const changes = [];

  if (profile.vagueUp) {
    pushUnique(changes, "More vague wording");
  }
  if (profile.directDown || profile.overlapLow) {
    pushUnique(changes, "Less direct response");
  }
  if (profile.hedgeUp) {
    pushUnique(changes, "Lower certainty");
  }
  if (profile.urgencyDown || profile.shorter) {
    pushUnique(changes, "Lower urgency");
  }
  if (profile.shorter) {
    pushUnique(changes, "Shorter reply");
  }
  if (profile.directUp) {
    pushUnique(changes, "More direct wording");
  }
  if (profile.vagueDown) {
    pushUnique(changes, "More specific detail");
  }
  if (profile.urgencyUp) {
    pushUnique(changes, "Higher urgency");
  }

  if (!changes.length) {
    return ["Subtle tone shift", "Slight pacing change", "Mostly steady wording"];
  }

  if (changes.length < 3) {
    pushUnique(
      changes,
      profile.overlapLow ? "Looser match to the earlier point" : "Pacing shifts slightly"
    );
  }
  if (changes.length < 3) {
    pushUnique(changes, "Specificity feels different");
  }

  return changes.slice(0, 3);
}

function buildEarlierNotes(profile) {
  const notes = [];
  if (profile.vagueUp) {
    notes.push("More specific");
  }
  if (profile.hedgeUp) {
    notes.push("More certain");
  }
  if (profile.directDown) {
    notes.push("More direct");
  }
  if (profile.shorter) {
    notes.push("More expanded");
  }
  return notes.slice(0, 2);
}

function buildLaterNotes(profile) {
  const notes = [];
  if (profile.vagueUp) {
    notes.push("Less specific");
  }
  if (profile.hedgeUp) {
    notes.push("Less certain");
  }
  if (profile.directDown) {
    notes.push("Less direct");
  }
  if (profile.shorter) {
    notes.push("More compressed");
  }
  if (profile.overlapLow) {
    notes.push("Looser match");
  }
  if (profile.directUp) {
    notes.push("More direct");
  }
  return notes.slice(0, 2);
}

function formatSpanNote(notes, fallback) {
  return notes.length ? notes.join(" · ") : fallback;
}

function buildShareText(profile) {
  if (profile.overlapLow) {
    return "Not what it seems at first glance";
  }
  if (profile.hedgeUp || profile.vagueUp) {
    return "Something changed in the tone here";
  }
  return "This message reads differently the second time";
}

function buildWeakSignalHeadline(weakSignal) {
  if (weakSignal.veryShortInput) {
    return "No strong shift detected";
  }
  if (weakSignal.highLexicalSimilarity || weakSignal.lowVarianceText) {
    return "Tone appears consistent";
  }
  return "Nothing clearly changed here";
}

function buildWeakSignalPattern(weakSignal) {
  if (weakSignal.veryShortInput) {
    return "This sample is short, so there is not enough movement here to call a clear shift.";
  }
  if (weakSignal.highLexicalSimilarity) {
    return "The wording stays very close from start to finish, so the signal looks steady rather than changed.";
  }
  return "The language stays fairly consistent throughout, without a strong change in tone or intent.";
}

function buildWeakSignalHighlights(weakSignal) {
  const highlights = [
    "Language stays similar throughout",
    "No clear change in tone or intent",
  ];
  if (weakSignal.highLexicalSimilarity) {
    highlights.push("The wording overlaps heavily between earlier and later lines");
  } else if (weakSignal.lowVarianceText) {
    highlights.push("The phrasing stays repetitive or low-variance");
  } else {
    highlights.push("Nothing clearly changed here");
  }
  return highlights.slice(0, 3);
}

function buildWeakSignalSpans(earlier, later) {
  return [
    {
      label: "Earlier",
      note: "Sets the baseline",
      excerpt: excerpt(earlier.join(" "), 120),
    },
    {
      label: "Later",
      note: "Reads very similar",
      excerpt: excerpt(later.join(" "), 120),
    },
  ].filter((item) => item.excerpt);
}

function buildWeakSignalResult({
  weakSignal,
  earlier,
  later,
  earlierMetrics,
  laterMetrics,
} = {}) {
  const result = {
    headline: buildWeakSignalHeadline(weakSignal),
    signalLabel: "Low-signal input",
    analysisMode: "fallback",
    pattern: buildWeakSignalPattern(weakSignal),
    summary: "Nothing here points to a clear shift yet, so the safer read is that the tone appears steady.",
    highlights: buildWeakSignalHighlights(weakSignal),
    spans: buildWeakSignalSpans(earlier, later),
    disclosure:
      "Pattern-based only. When the sample is short or repetitive, the clearest answer may be that nothing strong changed.",
    shareTitle: "VibeSignal",
    shareText: weakSignal.highLexicalSimilarity
      ? "Tone appears consistent here"
      : "No strong shift detected",
    suggestion: "Try a longer exchange for a clearer signal.",
    signalBundle: {
      pattern: "No strong shift detected in this sample.",
      what_changed: buildWeakSignalHighlights(weakSignal),
      spans: [
        {
          label: "earlier",
          text: excerpt(earlier.join(" "), 140),
        },
        {
          label: "later",
          text: excerpt(later.join(" "), 140),
        },
      ].filter((item) => item.text),
      local_metrics: {
        earlier: {
          average_words: earlierMetrics.averageWords,
          hedge_count: earlierMetrics.hedgeCount,
          vague_count: earlierMetrics.vagueCount,
          direct_count: earlierMetrics.directCount,
        },
        later: {
          average_words: laterMetrics.averageWords,
          hedge_count: laterMetrics.hedgeCount,
          vague_count: laterMetrics.vagueCount,
          direct_count: laterMetrics.directCount,
          overlap_to_earlier: Number(laterMetrics.overlap.toFixed(3)),
        },
        weak_signal: {
          short_input: weakSignal.veryShortInput,
          low_variance: weakSignal.lowVarianceText,
          no_clear_shift: weakSignal.noClearToneShift,
          high_similarity: weakSignal.highLexicalSimilarity,
        },
      },
    },
    ctaPrimary: "Try another message",
    ctaSecondary: "Paste a different conversation",
  };

  return sanitizeLocalAnalysisResult(result);
}

export function getMobileLayoutMetrics() {
  return {
    maxWidth: MAX_SCREEN_WIDTH,
    padding: SCREEN_PADDING,
    singleColumn: true,
    noHorizontalOverflow: true,
  };
}

export function selectHeroHeadline({ analysisText = "", hasResult = false } = {}) {
  return buildHeroHeadline({ analysisText, hasResult });
}

export function buildAnalysisComposerState({
  analysisText = "",
  loading = false,
  uploadInProgress = false,
  analysisInProgress = false,
  paywallRequired = false,
} = {}) {
  const normalizedText = normalizeText(analysisText);
  const hasContent = Boolean(normalizedText);

  return {
    inputVisible: true,
    multiline: true,
    placeholder: "Paste a message or short conversation",
    ctaLabel: "See what changed",
    loadingLabel: "Running analysis...",
    uploadVisible: true,
    analyzeEnabled:
      hasContent && !loading && !uploadInProgress && !analysisInProgress && !paywallRequired,
    uploadEnabled: !loading && !uploadInProgress && !analysisInProgress,
  };
}

export function buildLocalAnalysisResult(text) {
  const normalizedText = normalizeText(text);
  const segments = splitMeaningfulLines(normalizedText);
  const { earlier, later } = partitionSegments(segments);
  const earlierMetrics = summarizeMetrics(earlier);
  const laterMetrics = {
    ...summarizeMetrics(later),
    overlap: lexicalOverlap(earlier.join(" "), later.join(" ")),
  };
  const profile = buildShiftProfile(earlierMetrics, laterMetrics);
  const weakSignal = detectWeakSignal({
    normalizedText,
    segments,
    earlierMetrics,
    laterMetrics,
    profile,
  });

  if (weakSignal.weakSignal) {
    return buildWeakSignalResult({
      weakSignal,
      earlier,
      later,
      earlierMetrics,
      laterMetrics,
    });
  }

  const headline = buildHeadlineInsight(profile);
  const pattern = describePrimaryPattern(earlierMetrics, laterMetrics, profile);
  const whatChanged = buildWhatChanged(profile);
  const shareText = buildShareText(profile);

  const result = {
    headline,
    signalLabel: describeSignalStrength(profile),
    analysisMode: "signal",
    pattern,
    summary:
      "We compare the opening and the later wording to surface tone, intent, and meaning shifts.",
    highlights: whatChanged,
    spans: [
      {
        label: "Earlier",
        note: formatSpanNote(buildEarlierNotes(profile), "Sets the baseline"),
        excerpt: excerpt(earlier.join(" "), 120),
      },
      {
        label: "Later",
        note: formatSpanNote(buildLaterNotes(profile), "Reads close to the opening"),
        excerpt: excerpt(later.join(" "), 120),
      },
    ].filter((item) => item.excerpt),
    disclosure:
      "Pattern-based only. This may indicate a subtle shift, not intent, truth, or motive.",
    shareTitle: "VibeSignal",
    shareText,
    suggestion: "",
    signalBundle: {
      pattern,
      what_changed: whatChanged.slice(0, 3),
      spans: [
        {
          label: "earlier",
          text: excerpt(earlier.join(" "), 140),
        },
        {
          label: "later",
          text: excerpt(later.join(" "), 140),
        },
      ].filter((item) => item.text),
      local_metrics: {
        earlier: {
          average_words: earlierMetrics.averageWords,
          hedge_count: earlierMetrics.hedgeCount,
          vague_count: earlierMetrics.vagueCount,
          direct_count: earlierMetrics.directCount,
        },
        later: {
          average_words: laterMetrics.averageWords,
          hedge_count: laterMetrics.hedgeCount,
          vague_count: laterMetrics.vagueCount,
          direct_count: laterMetrics.directCount,
          overlap_to_earlier: Number(laterMetrics.overlap.toFixed(3)),
        },
      },
    },
    ctaPrimary: "Try another message",
    ctaSecondary: "Paste a different conversation",
  };

  return sanitizeLocalAnalysisResult(result);
}
