const REPLACEMENTS = [
  [/\bcheating\b/gi, "a notable inconsistency"],
  [/\blying\b/gi, "stating something inaccurately"],
  [/\bliar\b/gi, "speaker"],
  [/\bfaithful\b/gi, "consistent"],
  [/\bunfaithful\b/gi, "inconsistent"],
  [/\bsuspicious\b/gi, "notable"],
  [/\bred flag\b/gi, "change marker"],
  [/\bexposed\b/gi, "made more visible"],
  [/\bcaught\b/gi, "noticed"],
  [/\bpass\b/gi, "fit"],
  [/\bfail\b/gi, "fall short"],
  [/\bmanipulative\b/gi, "hard to read"],
  [/\btoxic\b/gi, "strained"],
  [/\babusive\b/gi, "harmful"],
  [/\bthis means\b/gi, "this may indicate"],
  [/\bthis proves\b/gi, "this can suggest"],
  [/\bthis shows they are\b/gi, "this can read as"],
];

function sanitizeText(text) {
  let normalized = String(text || "").trim();
  for (const [pattern, replacement] of REPLACEMENTS) {
    normalized = normalized.replace(pattern, replacement);
  }
  normalized = normalized.replace(/\s{2,}/g, " ").trim();
  return normalized;
}

export function sanitizeLocalAnalysisResult(result = {}) {
  return {
    ...result,
    headline: sanitizeText(result.headline),
    signalLabel: sanitizeText(result.signalLabel),
    analysisMode: String(result.analysisMode || "").trim(),
    pattern: sanitizeText(result.pattern),
    summary: sanitizeText(result.summary),
    disclosure: sanitizeText(result.disclosure),
    shareTitle: sanitizeText(result.shareTitle),
    shareText: sanitizeText(result.shareText),
    suggestion: sanitizeText(result.suggestion),
    highlights: Array.isArray(result.highlights)
      ? result.highlights.map(sanitizeText).filter(Boolean).slice(0, 3)
      : [],
    spans: Array.isArray(result.spans)
      ? result.spans
          .map((item) => ({
            label: sanitizeText(item?.label),
            note: sanitizeText(item?.note),
            excerpt: sanitizeText(item?.excerpt),
          }))
          .filter((item) => item.label || item.note || item.excerpt)
          .slice(0, 2)
      : [],
  };
}
