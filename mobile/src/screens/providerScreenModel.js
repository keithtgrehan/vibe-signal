import { sanitizeLocalAnalysisResult } from "./localAnalysisGuardrails.js";

const MAX_SCREEN_WIDTH = 480;
const SCREEN_PADDING = 16;
const HEDGE_TERMS = ["maybe", "perhaps", "might", "could", "possibly", "probably", "sort of", "kind of"];
const VAGUE_TERMS = ["thing", "stuff", "somehow", "whatever", "later", "soon", "eventually"];
const DIRECT_TERMS = ["exactly", "specifically", "clearly", "directly", "because"];
const POSITIVE_URGENCY = ["now", "immediately", "urgent", "asap"];

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

function tokenSet(text) {
  return new Set(
    normalizeText(text)
      .toLowerCase()
      .split(/[^a-z0-9]+/i)
      .filter((token) => token.length >= 4)
  );
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

function describePrimaryPattern(earlierMetrics, laterMetrics) {
  if (laterMetrics.vagueCount > earlierMetrics.vagueCount) {
    return "The later portion may indicate more vagueness than the opening lines.";
  }
  if (laterMetrics.hedgeCount > earlierMetrics.hedgeCount) {
    return "The later portion can suggest more hedging and less direct wording.";
  }
  if (laterMetrics.averageWords < earlierMetrics.averageWords * 0.75) {
    return "The later portion reads shorter and more compressed than the opening lines.";
  }
  if (laterMetrics.toneScore > earlierMetrics.toneScore + 1) {
    return "The later portion reads more urgent or more emotionally charged than the opening lines.";
  }
  if (laterMetrics.overlap < 0.22) {
    return "The reply can suggest a weaker match with the earlier topic than the opening lines set up.";
  }
  if (laterMetrics.directCount > earlierMetrics.directCount) {
    return "The later portion reads more direct and more concrete than the opening lines.";
  }
  return "The later portion reads slightly different from the opening lines in pacing and specificity.";
}

function buildWhatChanged(earlierMetrics, laterMetrics) {
  const changes = [];
  if (laterMetrics.vagueCount !== earlierMetrics.vagueCount) {
    changes.push(
      laterMetrics.vagueCount > earlierMetrics.vagueCount
        ? "Specific detail becomes lighter in the later portion."
        : "Specific detail becomes clearer in the later portion."
    );
  }
  if (laterMetrics.hedgeCount !== earlierMetrics.hedgeCount) {
    changes.push(
      laterMetrics.hedgeCount > earlierMetrics.hedgeCount
        ? "Hedging becomes more noticeable later on."
        : "Hedging eases in the later portion."
    );
  }
  if (laterMetrics.averageWords !== earlierMetrics.averageWords) {
    changes.push(
      laterMetrics.averageWords < earlierMetrics.averageWords
        ? "Message length drops in the later portion."
        : "Message length grows in the later portion."
    );
  }
  if (laterMetrics.overlap < 0.22) {
    changes.push("The later portion tracks the earlier topic less closely.");
  }
  if (!changes.length) {
    changes.push("The wording stays relatively steady across the sample.");
  }
  if (changes.length < 3) {
    changes.push(
      laterMetrics.questionCount !== earlierMetrics.questionCount
        ? "The balance of questions and statements shifts across the sample."
        : "The pacing changes slightly even when the wording stays close."
    );
  }
  if (changes.length < 3) {
    changes.push("Specificity and directness can read differently across the sample.");
  }
  return changes.slice(0, 3);
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
    toneScore: exclamationCount + urgencyCount + (questionCount ? 1 : 0),
    overlap: 1,
  };
}

export function getMobileLayoutMetrics() {
  return {
    maxWidth: MAX_SCREEN_WIDTH,
    padding: SCREEN_PADDING,
    singleColumn: true,
    noHorizontalOverflow: true,
  };
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
    placeholder: "Paste text to analyze",
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
  const pattern = describePrimaryPattern(earlierMetrics, laterMetrics);
  const whatChanged = buildWhatChanged(earlierMetrics, laterMetrics);

  const result = {
    headline: "Local pattern analysis ready",
    pattern,
    summary:
      "See what changed in tone and specificity between the earlier and later portion of the text.",
    highlights: whatChanged.length
      ? whatChanged
      : ["The sample reads steadily with only a light change in pacing."],
    spans: [
      {
        label: "Earlier",
        excerpt: excerpt(earlier.join(" "), 90),
      },
      {
        label: "Later",
        excerpt: excerpt(later.join(" "), 90),
      },
    ].filter((item) => item.excerpt),
    disclosure: "Pattern-based only. This does not determine intent, truth, or outcome.",
    shareTitle: "VibeSignal",
    shareText: [
      "See what changed in tone.",
      "It can read differently the second time.",
      pattern,
    ].join(" "),
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
