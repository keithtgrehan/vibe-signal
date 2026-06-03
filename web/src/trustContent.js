export const HERO_COPY = {
  title: "Understand message patterns without guessing motives.",
  subtitle:
    "Vibe Signal highlights observable cues like clarity, ambiguity, pressure, reassurance, and repair opportunities — with evidence, limits, and safe next steps.",
  primaryCta: "Try a synthetic example",
  secondaryCta: "See how it works",
  trustNote: "Use synthetic text first, or only messages you have permission to analyze.",
};

export const TRUST_STRIP_ITEMS = [
  "Evidence-first outputs",
  "No hidden-intent claims",
  "Synthetic demo available",
  "Privacy-conscious beta design",
  "Built for clarity, not manipulation",
];

export const CAN_HELP_WITH = [
  "Spot vague or overloaded messages",
  "Identify unclear asks",
  "Surface pressure or urgency cues",
  "Show reassurance and repair opportunities",
  "Suggest clearer, lower-pressure replies",
];

export const CANNOT_TELL = [
  "Whether someone likes you",
  "Whether someone is cheating",
  "Whether someone is lying",
  "What someone secretly means",
  "Someone’s diagnosis, attachment style, neurotype, or personality",
  "Whether a relationship will work",
];

export const HOW_IT_WORKS_STEPS = [
  {
    title: "Start safely",
    body: "Run a synthetic exchange first, or paste only text you have permission to review.",
  },
  {
    title: "Read the evidence",
    body: "The result shows quoted phrases before any pattern explanation or suggested next step.",
  },
  {
    title: "Keep agency",
    body: "Use the limits and next step as options, then decide whether to ask, pause, or stop.",
  },
];

export const RESULT_EXPLAINABILITY_STEPS = [
  "Evidence",
  "Pattern",
  "Limits",
  "Next step",
];

export const REVIEWER_DEMO_FLOW = [
  "Open with a synthetic card",
  "Show evidence before interpretation",
  "Point to limits and the safe next step",
  "Use metadata-only feedback",
];

export const FAQ_ITEMS = [
  {
    question: "Is this trying to read intent?",
    answer:
      "No. Vibe Signal stays with visible wording patterns and shows what it cannot infer.",
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
    title: "Unclear ask",
    exchange: "self: Are we still on for Friday?\nother: maybe later, not sure yet",
    highlight: "Vibe Signal will highlight vague timing after a direct question.",
    previewPattern: "Vague timing",
    actionLabel: "Run demo",
    requiresPrivateConsent: false,
    result: {
      match_id: "synthetic_unclear_ask",
      synthetic: true,
      requiresPrivateConsent: false,
      signal_strength: "medium",
      compatibility_band: "mixed",
      safe_explanation: "This message gives a vague timing answer after a direct question.",
      evidence: [
        {
          evidence_id: "unclear_1",
          safe_phrase: "maybe later",
          cue_family: "vague_timing",
          explanation: "The reply gives an open-ended timing answer after a direct question.",
          repair_suggestion: "Ask for a specific time or decision point.",
        },
        {
          evidence_id: "unclear_2",
          safe_phrase: "not sure yet",
          cue_family: "vague_timing",
          explanation: "The reply does not give a clear decision point.",
        },
      ],
      safe_next_steps: ["Ask for a specific time or decision point."],
    },
  },
  {
    id: "pressure_urgency",
    title: "Pressure / urgency",
    exchange:
      "self: I need a little time to think.\nother: I need an answer tonight or this will not work.",
    highlight: "Vibe Signal will highlight urgency and consequence pressure in the wording.",
    previewPattern: "Urgency pressure",
    actionLabel: "Run demo",
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
    actionLabel: "Run demo",
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
    actionLabel: "Run demo",
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
    actionLabel: "Run demo",
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
    actionLabel: "Run demo",
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
