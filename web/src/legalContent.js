export const LEGAL_STATUS = "draft_requires_legal_review";
export const LEGAL_STATUS_LINE = "Status: draft_requires_legal_review";
export const LEGAL_INTRO =
  "Vibe Signal is currently in closed beta / early public beta. These legal drafts are provided for transparency and require legal review before public launch.";

export const LEGAL_SLUGS = [
  ["privacy", "Privacy"],
  ["terms", "Terms"],
  ["data-request", "Data request/delete"],
  ["disclaimer", "Disclaimer"],
];

const BASE_DRAFT_BOUNDARIES = {
  status: LEGAL_STATUS,
  not_legal_advice: true,
  closed_beta_only: true,
  production_compliance_claimed: false,
  raw_message_persistence_added: false,
  account_storage_added: false,
  analytics_tracking_added: false,
  training_use_added: false,
  review_note: "Draft copy for closed-beta readiness; requires legal review before public launch.",
};

const PRIVACY_GROUPS = [
  {
    heading: "Operator and contact placeholders",
    items: [
      "Operator/controller: Keith Grehan.",
      "Privacy contact: keith.t.grehan@gmail.com.",
      "Business/contact method: Berlin, Germany; full address available on valid legal request.",
      "Production URL: https://www.vibe-signal.com.",
    ],
  },
  {
    heading: "Product purpose",
    items: [
      "Vibe Signal is a communication-support tool for reviewing observable wording patterns such as clarity, ambiguity, pressure, reassurance, directness, cognitive load, and repair opportunities.",
      "Outputs are suggestions and limits based on the text shown, not truth claims or relationship-outcome predictions.",
    ],
  },
  {
    heading: "Categories of data",
    items: [
      "Submitted text is processed transiently to provide analysis.",
      "Metadata required to operate the service may include request status, timing, error state, and reliability signals.",
      "Feedback stores result metadata only, never message text.",
      "Infrastructure logs may be created by Vercel and Render.",
      "Domain and DNS provider metadata may exist with GoDaddy where relevant to domain operation.",
    ],
  },
  {
    heading: "What is not intentionally stored",
    items: [
      "No raw chat history is intentionally stored.",
      "No raw submitted message persistence is added.",
      "No raw messages are used for training.",
      "No analytics, cookies, or tracking are added by this implementation.",
    ],
  },
  {
    heading: "Processing purposes",
    items: [
      "Provide wording-based analysis and safer reply suggestions.",
      "Support security, debugging, reliability, abuse prevention, and closed-beta feedback.",
      "Handle legal, privacy, data request, or deletion request correspondence where applicable.",
    ],
  },
  {
    heading: "Draft lawful-basis mapping",
    items: [
      "Draft lawful-basis mapping, subject to legal review:",
      "Submitted text for analysis: consent and/or steps requested by the user to use the service.",
      "Feedback metadata: consent and/or legitimate interests in improving safety, reliability, and closed-beta quality.",
      "Infrastructure logs: legitimate interests in security, debugging, abuse prevention, and service reliability.",
      "Data request correspondence: legal obligation and/or legitimate interests in handling privacy requests.",
      "This lawful-basis mapping is a draft and requires legal review before public launch.",
    ],
  },
  {
    heading: "Processors and subprocessors draft table",
    items: [
      "Vercel - frontend hosting, CDN, deployment, and runtime logs. Vercel Hobby/basic runtime logs are assumed to be retained for 1 hour unless the Vercel account changes.",
      "Render - backend/API hosting and logs. Render Hobby/basic backend logs are assumed to be retained for 7 days unless the Render workspace changes.",
      "GitHub - source code, CI, and project workflow. No raw user chats are committed.",
      "GoDaddy - domain registration and DNS metadata.",
      "Email provider - Gmail.",
      "AI provider - Disabled unless explicitly enabled. Optional external provider connectors are disabled by default unless production configuration changes.",
      "External log streaming - none configured.",
      "Analytics - none configured.",
    ],
  },
  {
    heading: "Retention draft",
    items: [
      "Raw submitted text: transient processing only and not intentionally retained.",
      "Feedback metadata: 90 days during beta.",
      "Vercel runtime logs: Hobby/basic, assume 1 hour unless account changes.",
      "Render logs: Hobby/basic, assume 7 days unless account changes.",
      "Legal/data request correspondence: 24 months unless legal review changes this.",
    ],
  },
  {
    heading: "Transfers, safeguards, and rights",
    items: [
      "Processors may process or store data outside the user country or EEA depending on provider infrastructure; this requires legal review.",
      "Safeguards summary: HTTPS, minimal data design, no raw chat persistence by design, restricted artifacts checks, and public copy safety checks.",
      "Data subject rights may include access/export, deletion, correction, objection/restriction, and withdrawal of consent where applicable.",
      "Users may lodge a complaint with their local EU/EEA data protection supervisory authority. For Berlin, the likely relevant authority is:",
      "Berliner Beauftragte für Datenschutz und Informationsfreiheit.",
      "Alt-Moabit 59–61, 10555 Berlin, Germany.",
      "Email: mailbox@datenschutz-berlin.de.",
      "This authority information should be verified before public launch.",
      "Vibe Signal is not intended for minors or teen romantic analysis.",
    ],
  },
  {
    heading: "Automated decision-making and model limits",
    items: [
      "Vibe Signal does not make automated legal, medical, financial, employment, education, housing, credit, or similarly significant decisions.",
      "Vibe Signal does not know intent, attraction, truthfulness, diagnosis, or outcomes.",
      "No model-quality, health-label, or emotion-recognition claims are made.",
    ],
  },
];

const TERMS_GROUPS = [
  {
    heading: "Beta status",
    items: [
      "Vibe Signal is offered as a closed beta / early public beta draft service.",
      "The service may change, pause, or be removed while legal, privacy, and product review continue.",
    ],
  },
  {
    heading: "Permission and permitted use",
    items: [
      "Only submit text you have permission to analyze.",
      "Permitted use includes communication clarity, reflection, and drafting safer replies.",
      "Use outputs as one input to your own judgment and context.",
    ],
  },
  {
    heading: "Prohibited use",
    items: [
      "Prohibited use includes stalking, harassment, coercion, manipulation, or trying to make someone respond.",
      "Do not use Vibe Signal to make hidden-intent, attraction, truthfulness, deception, cheating, or relationship-outcome certainty claims.",
      "Do not use Vibe Signal for workplace/education emotional assessment, minors/teen romantic analysis, or content you lack rights or permission to use.",
    ],
  },
  {
    heading: "No professional advice",
    items: [
      "Vibe Signal is not professional advice.",
      "Vibe Signal is not therapy, medical advice, legal advice, financial advice, or emergency support.",
      "For urgent risk or safety situations, contact appropriate emergency or local support services.",
    ],
  },
  {
    heading: "Accounts, payment, availability, and access",
    items: [
      "Account features are not currently implemented.",
      "Payment features are not currently implemented.",
      "Service availability and warranty language require legal review before launch.",
      "To the maximum extent permitted by applicable law, Vibe Signal is provided as a draft beta service without guarantees of uninterrupted availability, accuracy, or error-free operation. Nothing in these Terms excludes or limits liability where such exclusion or limitation is not permitted by applicable law. This clause requires legal review before public launch.",
      "These Terms are drafted with Germany as the expected governing-law jurisdiction, subject to legal review and any mandatory consumer protection rules that may apply in the user's country of residence.",
      "Access removal or termination process requires legal review before launch.",
    ],
  },
];

const DATA_REQUEST_GROUPS = [
  {
    heading: "Contact and request types",
    items: [
      "Send data requests to: keith.t.grehan@gmail.com.",
      "Request types may include access/export, deletion, correction, objection/restriction, and withdrawal of consent where applicable.",
      "Vibe Signal aims to respond to verified privacy requests without undue delay and, where GDPR applies, within one month of receipt. This timeline may depend on identity verification, request scope, and applicable legal requirements. This section requires legal review before public launch.",
    ],
  },
  {
    heading: "What to include",
    items: [
      "Include the email or contact method used with Vibe Signal.",
      "Include the request type and enough information to verify the request.",
      "Do not include unnecessary private message content in the request.",
      "Identity verification may be required before action is taken.",
    ],
  },
  {
    heading: "Raw message and metadata limits",
    items: [
      "Raw submitted text may not be available for export or deletion because the app is designed not to intentionally retain it.",
      "Feedback is metadata-only and does not include message text.",
      "Vercel Hobby/basic runtime logs are assumed to be retained for 1 hour unless the Vercel account changes.",
      "Render Hobby/basic backend logs are assumed to be retained for 7 days unless the Render workspace changes.",
      "Provider infrastructure logs may expire before a request is processed.",
    ],
  },
  {
    heading: "Closed-beta manual runbook",
    items: [
      "1. Receive request.",
      "2. Verify requester.",
      "3. Search app metadata stores if any.",
      "4. Check feedback metadata if applicable.",
      "5. Delete, export, or correct data where technically available.",
      "6. Respond with what was found or deleted, or explain when no retained raw text exists.",
    ],
  },
];

const DISCLAIMER_GROUPS = [
  {
    heading: "Communication support only",
    items: [
      "Vibe Signal is communication-support only.",
      "Vibe Signal provides wording-based suggestions only.",
      "Outputs should be read as observable text evidence and possible patterns.",
      "Vibe Signal does not know intent, attraction, truthfulness, diagnosis, or outcomes.",
    ],
  },
  {
    heading: "Not professional or crisis support",
    items: [
      "Vibe Signal is not therapy.",
      "Vibe Signal is not medical advice, legal advice, or financial advice.",
      "Vibe Signal is not emergency/crisis support.",
      "If there is urgent risk or a safety situation, contact appropriate emergency or local support services.",
    ],
  },
  {
    heading: "Use human judgment",
    items: [
      "Vibe Signal is not a substitute for human judgment, context, consent, or respectful communication.",
      "Low-signal outputs may be incomplete.",
      "Use safe, respectful, non-coercive communication and ask one clear follow-up when appropriate.",
    ],
  },
];

function groupsToSections(groups) {
  return [
    LEGAL_STATUS_LINE,
    LEGAL_INTRO,
    ...groups.flatMap((group) => [group.heading, ...(group.items || [])]),
  ];
}

function buildLegalPage({ slug, title, documentRef, groups }) {
  return {
    ...BASE_DRAFT_BOUNDARIES,
    slug,
    title,
    document_ref: documentRef,
    intro: LEGAL_INTRO,
    groups,
    sections: groupsToSections(groups),
  };
}

export const LOCAL_LEGAL_PAGES = {
  privacy: buildLegalPage({
    slug: "privacy",
    title: "Privacy",
    documentRef: "docs/legal/research/gdpr_privacy_notice_research.md",
    groups: PRIVACY_GROUPS,
  }),
  terms: buildLegalPage({
    slug: "terms",
    title: "Terms",
    documentRef: "docs/legal/research/terms_research.md",
    groups: TERMS_GROUPS,
  }),
  "data-request": buildLegalPage({
    slug: "data-request",
    title: "Data request/delete",
    documentRef: "docs/legal/research/data_request_delete_research.md",
    groups: DATA_REQUEST_GROUPS,
  }),
  disclaimer: buildLegalPage({
    slug: "disclaimer",
    title: "Disclaimer",
    documentRef: "docs/legal/research/disclaimer_ai_safety_research.md",
    groups: DISCLAIMER_GROUPS,
  }),
};

const LEGAL_PLACEHOLDER_RE = /\[[^\]]*(?:REQUIRES|REQUIRED)[^\]]*\]/;

function legalPageText(page) {
  return [
    page?.title,
    page?.intro,
    ...(Array.isArray(page?.sections) ? page.sections : []),
    ...(Array.isArray(page?.groups)
      ? page.groups.flatMap((group) => [group?.heading, ...(Array.isArray(group?.items) ? group.items : [])])
      : []),
  ]
    .map((item) => String(item || ""))
    .join(" ");
}

export function isValidLegalPage(page) {
  if (!page || typeof page !== "object") {
    return false;
  }
  if (page.status !== LEGAL_STATUS || !page.title || !page.intro) {
    return false;
  }
  if (!Array.isArray(page.groups) || !page.groups.length) {
    return false;
  }
  if (!Array.isArray(page.sections) || !page.sections.includes(LEGAL_STATUS_LINE)) {
    return false;
  }
  if (!page.groups.every((group) => group?.heading && Array.isArray(group?.items) && group.items.length)) {
    return false;
  }
  return !LEGAL_PLACEHOLDER_RE.test(legalPageText(page));
}

export function getLocalLegalPage(slug = "privacy") {
  return LOCAL_LEGAL_PAGES[slug] || LOCAL_LEGAL_PAGES.privacy;
}
