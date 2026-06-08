export const HERO_COPY = {
  title: "Vibe Signal turns messy communication into evidence-backed signals.",
  subtitle:
    "It highlights observable wording patterns like clarity, ambiguity, pressure, reassurance, and repair opportunities without guessing intent, attraction, deception, diagnosis, manipulation, neurotype, attachment style, or relationship outcomes.",
  primaryCta: "Run synthetic demo",
  secondaryCta: "Analyze with consent",
  trustNote: "This is intentionally bounded. It reviews wording patterns, not people's motives.",
};

export const PROOF_CARDS = [
  {
    title: "Observable evidence",
    body: "Shows the exact phrases that triggered each signal.",
  },
  {
    title: "Bounded AI logic",
    body: "Deterministic-first cue engine with safe output rules and low-signal fallbacks.",
  },
  {
    title: "Privacy-conscious by design",
    body: "Consent-gated input, metadata-only feedback, no raw-chat persistence.",
  },
];

export const SYNTHETIC_DEMO_PATH_STEPS = [
  "Click Run synthetic demo",
  "Review the input text",
  "Check detected cues",
  "Inspect evidence phrases",
  "Read the safe next step",
  "Check what this does not claim",
];

export const TECHNICAL_DEMO_SHIPPED = [
  "Vite/React web app",
  "FastAPI backend on Render",
  "Expo mobile shell",
  "Deterministic cue engine",
  "Evidence objects and safe output checks",
  "/api/analyze",
  "/api/match",
  "/api/feedback",
  "/healthz",
  "/api/status",
  "Consent-gated custom input",
  "Public-copy, no-raw-content, and restricted-artifact safety scanners",
  "Synthetic eval harness",
  "Human-review packet scaffold",
];

export const TECHNICAL_DEMO_FLOW = [
  "Input text",
  "Consent / safety boundary",
  "Deterministic cue engine",
  "Evidence extraction",
  "Safe result cards",
  "Metadata-only feedback",
];

export const TECHNICAL_DEMO_NON_CLAIMS = [
  "no hidden-intent detection",
  "no attraction prediction",
  "no deception or cheating detection",
  "no diagnosis or therapy",
  "no neurotype or attachment labels",
  "no manipulation advice",
  "no relationship-outcome prediction",
  "no real-world accuracy claim from synthetic demos",
];

export const TRUST_STRIP_ITEMS = [
  "Evidence from the words shown",
  "Possible pattern, not a fact about intent",
  "Feedback stores result metadata only",
];

export const GOAL_OPTIONS = [
  {
    id: "unclear",
    label: "Understand what feels unclear",
    helper: "Focus the UI on ambiguity, vague timing, and missing decision points.",
    nextStep:
      "Ask for the specific point that feels unclear, without guessing the reason behind it.",
  },
  {
    id: "reduce_pressure",
    label: "Reduce pressure in my reply",
    helper: "Emphasize lower-pressure wording and room to pause.",
    nextStep: "Draft one lower-pressure reply and make later or no acceptable.",
  },
  {
    id: "direct_ask",
    label: "Find the direct ask",
    helper: "Pull the visible ask or decision point forward.",
    nextStep: "Name the direct ask in one sentence before replying.",
  },
  {
    id: "over_reading",
    label: "Check if I am over-reading",
    helper: "Keep limits prominent before any interpretation.",
    nextStep: "Compare the quote with the limits before deciding what it means.",
  },
  {
    id: "clearer_response",
    label: "Prepare a clearer response",
    helper: "Turn the read into one concrete, safer next step.",
    nextStep: "Write a short response that asks for one concrete next step.",
  },
];

export const CONTEXT_OPTIONS = [
  { id: "general", label: "General" },
  { id: "relationship", label: "Relationship" },
  { id: "work", label: "Work" },
  { id: "friends_family", label: "Friends/family" },
  { id: "difficult", label: "Difficult conversation" },
  { id: "unsure", label: "Unsure" },
];

export const ANALYSIS_STYLE_OPTIONS = [
  {
    id: "quick",
    label: "Quick read",
    description: "Fast summary with key evidence and one next step.",
  },
  {
    id: "evidence",
    label: "Evidence-first",
    description: "Quoted cues, pattern labels, limits, and repair options.",
  },
  {
    id: "careful",
    label: "Careful",
    description: "More cautious. Best for sensitive or unclear messages.",
  },
];

export const CAN_HELP_WITH = [
  "Spot clarity, ambiguity, pressure, reassurance, and repair openings",
  "Show evidence from the words shown",
  "Separate possible patterns from facts about intent",
  "Suggest one clearer, lower-pressure follow-up",
  "Keep limits visible before you act",
];

export const CANNOT_TELL = [
  "Intent",
  "Attraction",
  "Truthfulness",
  "Health labels",
  "Outcomes",
];

export const HOW_IT_WORKS_STEPS = [
  {
    title: "Start with the demo",
    body: "Run the synthetic Scanner example before using any private text.",
  },
  {
    title: "See the evidence",
    body: "Quoted wording appears before any possible pattern or repair step.",
  },
  {
    title: "Choose a safer next step",
    body: "Use the reply as an editable draft, then decide what fits your context.",
  },
];

export const RESULT_EXPLAINABILITY_STEPS = [
  "What stands out",
  "Evidence",
  "What it could mean",
  "Safer reply",
  "Limits",
];

export const REVIEWER_DEMO_FLOW = [
  "Open with a synthetic Scanner card",
  "Show quoted evidence before interpretation",
  "Keep limits and the safe next step visible",
  "Use consented metadata-only feedback",
];

export const FAQ_ITEMS = [
  {
    question: "Is this trying to read intent?",
    answer: "No. Vibe Signal stays with visible wording patterns and shows clear limits.",
  },
  {
    question: "Can I test it without private messages?",
    answer: "Yes. The synthetic demo cards are designed for a first run without private text.",
  },
  {
    question: "What should I paste?",
    answer:
      "Use short exchanges with names and sensitive details removed, and only when you have permission.",
  },
];

export const SYNTHETIC_DEMOS = [
  {
    id: "unclear_ask",
    title: "Unclear timing",
    exchange: "self: Are we still on for Friday?\nother: maybe later, not sure yet",
    highlight: "Vibe Signal will highlight the loose answer after a direct timing question.",
    previewPattern: "Vague timing",
    actionLabel: "Run synthetic demo",
    requiresPrivateConsent: false,
    result: {
      match_id: "synthetic_unclear_ask",
      synthetic: true,
      requiresPrivateConsent: false,
      signal_strength: "medium",
      compatibility_band: "mixed",
      safe_explanation: "The reply answers loosely, but does not confirm Friday.",
      safe_interpretation:
        "There may not be a clear decision yet. The safest read is that timing is still open.",
      evidence: [
        {
          evidence_id: "unclear_1",
          safe_phrase: "maybe later, not sure yet",
          cue_family: "vague_timing",
          explanation: "The wording leaves the Friday plan unconfirmed.",
          repair_suggestion:
            "No worries - can you confirm by Thursday evening so I know whether to keep Friday free?",
        },
      ],
      safe_next_steps: [
        "No worries - can you confirm by Thursday evening so I know whether to keep Friday free?",
      ],
    },
  },
  {
    id: "pressure_urgency",
    title: "Pressure / urgency",
    exchange:
      "self: I need a little time to think.\nother: I need an answer tonight or this will not work.",
    highlight: "Vibe Signal will highlight urgency and consequence pressure in the wording.",
    previewPattern: "Urgency pressure",
    actionLabel: "Run synthetic demo",
    requiresPrivateConsent: false,
    result: {
      match_id: "synthetic_pressure_urgency",
      synthetic: true,
      requiresPrivateConsent: false,
      signal_strength: "medium",
      compatibility_band: "mixed",
      safe_explanation: "This reply adds urgency and a consequence after a request for time.",
      evidence: [
        {
          evidence_id: "pressure_1",
          safe_phrase: "answer tonight",
          cue_family: "urgency_pressure",
          explanation: "The wording compresses the decision window.",
          repair_suggestion: "Name when you can respond without adding pressure back.",
        },
        {
          evidence_id: "pressure_2",
          safe_phrase: "this will not work",
          cue_family: "boundary_pressure",
          explanation: "The reply links the timing to a consequence.",
        },
      ],
      safe_next_steps: ["Name when you can respond without adding pressure back."],
    },
  },
  {
    id: "repair_opportunity",
    title: "Repair opportunity",
    exchange:
      "self: That landed harder than I meant.\nother: I appreciate you saying that. Can we reset and choose a time tomorrow?",
    highlight: "Vibe Signal will highlight reassurance, repair wording, and a clear next step.",
    previewPattern: "Repair wording",
    actionLabel: "Run synthetic demo",
    requiresPrivateConsent: false,
    result: {
      match_id: "synthetic_repair_opportunity",
      synthetic: true,
      requiresPrivateConsent: false,
      signal_strength: "high",
      compatibility_band: "supportive",
      safe_explanation: "This exchange includes repair wording and a clear low-pressure next step.",
      evidence: [
        {
          evidence_id: "repair_1",
          safe_phrase: "I appreciate you saying that",
          cue_family: "reassurance",
          explanation: "The reply acknowledges the repair attempt.",
          repair_suggestion: "Keep the next reply specific and low pressure.",
        },
        {
          evidence_id: "repair_2",
          safe_phrase: "reset and choose a time tomorrow",
          cue_family: "repair_opportunity",
          explanation: "The wording offers a concrete next step after repair.",
        },
      ],
      safe_next_steps: ["Keep the next reply specific and low pressure."],
    },
  },
  {
    id: "low_signal_fallback",
    title: "Low-signal fallback",
    exchange: "self: hey\nother: ok",
    highlight: "Vibe Signal will avoid over-reading a short context-light exchange.",
    previewPattern: "Not enough context",
    actionLabel: "Run synthetic demo",
    requiresPrivateConsent: false,
    result: {
      match_id: "synthetic_low_signal_fallback",
      synthetic: true,
      requiresPrivateConsent: false,
      result_state: "low_signal",
      low_signal_fallback: true,
      signal_strength: "insufficient",
      safe_explanation: "This exchange is too short to read safely.",
      safe_next_steps: ["Add the previous message or try a synthetic example."],
    },
  },
  {
    id: "boundary_respecting_request",
    title: "Boundary-respecting request",
    exchange:
      "self: I cannot decide tonight.\nother: That is okay. Could you send a yes or no by Friday if you have capacity?",
    highlight: "Vibe Signal will highlight a clear ask that leaves room for a no or later.",
    previewPattern: "Clear low-pressure ask",
    actionLabel: "Run synthetic demo",
    requiresPrivateConsent: false,
    result: {
      match_id: "synthetic_boundary_respecting_request",
      synthetic: true,
      requiresPrivateConsent: false,
      signal_strength: "high",
      compatibility_band: "supportive",
      safe_explanation: "This reply makes a specific request while preserving room to decline or delay.",
      evidence: [
        {
          evidence_id: "boundary_1",
          safe_phrase: "That is okay",
          cue_family: "reassurance",
          explanation: "The reply accepts the stated boundary before making another ask.",
          repair_suggestion: "Respond with the decision point you can actually meet.",
        },
        {
          evidence_id: "boundary_2",
          safe_phrase: "if you have capacity",
          cue_family: "low_pressure_request",
          explanation: "The wording keeps the request conditional on capacity.",
        },
      ],
      safe_next_steps: ["Respond with the decision point you can actually meet."],
    },
  },
  {
    id: "overloaded_message",
    title: "Overloaded message",
    exchange:
      "self: Can we choose one plan?\nother: I can talk after work, but also need to finish errands, call Sam, and figure out dinner.",
    highlight: "Vibe Signal will highlight cognitive load and suggest narrowing the next ask.",
    previewPattern: "Overloaded reply",
    actionLabel: "Run synthetic demo",
    requiresPrivateConsent: false,
    result: {
      match_id: "synthetic_overloaded_message",
      synthetic: true,
      requiresPrivateConsent: false,
      signal_strength: "medium",
      compatibility_band: "mixed",
      safe_explanation: "This reply stacks several tasks after a request to choose one plan.",
      evidence: [
        {
          evidence_id: "overloaded_1",
          safe_phrase: "also need to finish errands, call Sam, and figure out dinner",
          cue_family: "cognitive_load",
          explanation: "The reply adds several competing tasks instead of narrowing to one plan.",
          repair_suggestion: "Ask for one decision point and make later acceptable.",
        },
        {
          evidence_id: "overloaded_2",
          safe_phrase: "I can talk after work",
          cue_family: "partial_clarity",
          explanation: "There is one usable timing cue, but the rest of the message adds load.",
        },
      ],
      safe_next_steps: ["Ask for one decision point and make later acceptable."],
    },
  },
];
