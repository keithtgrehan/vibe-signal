import { HERO_COPY } from "./trustContent.js";

export const DEFAULT_VARIANT = "a";
export const VARIANT_STORAGE_KEY = "vibe_signal_visual_variant";

const VARIANT_A_RESULT_LABELS = {
  standsOut: "What stands out",
  evidence: "Evidence",
  couldMean: "What it could mean",
  saferReply: "Safer reply",
  limits: "Limits",
};

const VARIANT_B_RESULT_LABELS = {
  standsOut: "The part to slow down on",
  evidence: "The exact words",
  couldMean: "A grounded read",
  saferReply: "A calmer reply",
  limits: "Limits",
};

export const VARIANTS = {
  a: {
    key: "a",
    name: "Production Codex baseline",
    hero: {
      ...HERO_COPY,
      navCta: "Run demo",
    },
    demo: {
      kicker: "Synthetic example",
      title: "Unclear timing",
      cta: "Run this demo",
      storedCopy: "No private chats stored for this demo.",
    },
    emptyResult: {
      kicker: "Result preview",
      title: "Run a demo to see what stands out.",
      standsOutPreview: "A short read appears here after the demo runs.",
      evidencePreview: "The exact words that triggered it appear before any interpretation.",
      saferReplyPreview: "A clearer next step appears here.",
      cta: "Run a demo",
    },
    resultLabels: VARIANT_A_RESULT_LABELS,
    analyze: {
      kicker: "Try your text",
      title: "Analyze text",
      intro: "Paste a short exchange and keep the result grounded in the words shown.",
      cta: "Analyze",
    },
    saferReplyHelper: "You stay in control of the reply. Edit before sending.",
  },
  b: {
    key: "b",
    name: "Before You Reply experiment",
    hero: {
      title: "Before you reply, check what the message actually says.",
      subtitle:
        "When a text feels off, Vibe Signal helps you slow down, spot the unclear part, and choose a calmer next step.",
      primaryCta: "Check a demo",
      secondaryCta: "Paste your text",
      trustNote: "Useful for clarity. Not for mind-reading.",
      navCta: "Check demo",
    },
    demo: {
      kicker: "Synthetic example",
      title: "When the answer is vague",
      cta: "Check this demo",
      storedCopy: "No private chats stored for this demo.",
    },
    emptyResult: {
      kicker: "Result preview",
      title: "Check a demo to see what stands out.",
      standsOutPreview: "The unclear part appears here after the demo runs.",
      evidencePreview: "The exact words appear before any read.",
      saferReplyPreview: "A calmer next step appears here.",
      cta: "Check a demo",
    },
    resultLabels: VARIANT_B_RESULT_LABELS,
    analyze: {
      kicker: "Try your text",
      title: "Paste your text",
      intro: "Use text you have permission to analyze, then keep the read grounded in the words.",
      cta: "Analyze",
    },
    saferReplyHelper: "Use this as a calmer draft, then edit it in your own voice.",
  },
};

function normalizeVariant(value) {
  const normalized = String(value || "").trim().toLowerCase();
  return Object.prototype.hasOwnProperty.call(VARIANTS, normalized) ? normalized : "";
}

function safeGetStorage(storage) {
  if (!storage) return "";
  try {
    return normalizeVariant(storage.getItem(VARIANT_STORAGE_KEY));
  } catch (_error) {
    return "";
  }
}

function safeSetStorage(storage, variantKey) {
  if (!storage) return;
  try {
    storage.setItem(VARIANT_STORAGE_KEY, variantKey);
  } catch (_error) {
    // Variant persistence is optional and only affects this browser's UI view.
  }
}

function getQueryVariant(search) {
  const rawSearch = String(search || "");
  if (!rawSearch) return { hasQuery: false, variant: "" };
  const params = new URLSearchParams(rawSearch.startsWith("?") ? rawSearch : `?${rawSearch}`);
  if (!params.has("variant")) return { hasQuery: false, variant: "" };
  return { hasQuery: true, variant: normalizeVariant(params.get("variant")) };
}

export function resolveVariant(search = "", storage = null) {
  const query = getQueryVariant(search);
  if (query.hasQuery) {
    if (query.variant) {
      safeSetStorage(storage, query.variant);
      return query.variant;
    }
    return DEFAULT_VARIANT;
  }

  return safeGetStorage(storage) || DEFAULT_VARIANT;
}

export function getVariant(variantKey = DEFAULT_VARIANT) {
  return VARIANTS[normalizeVariant(variantKey) || DEFAULT_VARIANT];
}

export function buildVariantSections(view, variantKey = DEFAULT_VARIANT) {
  const variant = getVariant(variantKey);
  const labels = variant.resultLabels;
  const isVariantBUnclearDemo =
    variant.key === "b" && view?.matchId === "synthetic_unclear_ask" && !view?.isLowSignal;
  const safeNextStep = view?.safeNextStep || "Ask one clear follow-up and leave room for a later answer.";
  const interpretation = view?.interpretation || view?.patternExplanation || view?.body || "";

  return [
    {
      id: "standsOut",
      label: labels.standsOut,
      text: isVariantBUnclearDemo
        ? "They did not clearly confirm or cancel."
        : view?.isLowSignal
          ? view?.body
          : view?.mainRead,
    },
    {
      id: "evidence",
      label: labels.evidence,
      rows: view?.evidenceDetails || [],
    },
    {
      id: "couldMean",
      label: labels.couldMean,
      text: isVariantBUnclearDemo
        ? "The timing is unresolved. You do not need to guess the reason."
        : view?.isLowSignal
          ? "There is not enough wording to read safely yet."
          : interpretation,
    },
    {
      id: "saferReply",
      label: labels.saferReply,
      text: isVariantBUnclearDemo
        ? "Got it - can you let me know by Thursday evening if Friday still works?"
        : safeNextStep,
      helper: variant.saferReplyHelper,
    },
    {
      id: "limits",
      label: labels.limits,
      text: isVariantBUnclearDemo
        ? "This cannot tell you what they mean or feel."
        : view?.cannotInferText,
    },
  ];
}
