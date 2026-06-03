import {
  Activity,
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  FileText,
  Gauge,
  MessageSquare,
  ShieldCheck,
  SlidersHorizontal,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  API_CONFIG,
  fetchLegalPage,
  submitAnalyze,
  submitFeedback,
  submitMatch,
} from "./api.js";

const SAMPLE_TEXT =
  "self: Can you confirm Friday at 3pm?\nother: Yes, Friday at 3pm works. No pressure if we need to adjust.";

const LEGAL_SLUGS = [
  ["match-disclaimer", "Match Disclaimer"],
  ["privacy", "Privacy"],
  ["terms", "Terms"],
  ["data-deletion", "Deletion"],
  ["data-export", "Export"],
];

const FALLBACK_LEGAL = {
  title: "Closed Beta Legal Draft",
  status: "draft_requires_legal_review",
  sections: [
    "Vibe Signal is communication-support only.",
    "Outputs are pattern-based suggestions, not truth claims.",
    "Only submit messages you have permission to analyze.",
    "Do not include sensitive personal data, secrets, medical data, legal documents, financial data, or third-party private messages without permission.",
    "Closed beta is not production launch. Privacy and terms drafts require legal review before public launch.",
  ],
};

const CAN_TELL = [
  "Observable wording patterns such as direct asks, specificity, pressure, reassurance, and repair openings.",
  "Whether the visible exchange has enough evidence for a bounded pattern review.",
  "Lower-pressure next steps such as clarifying, pausing, or naming a boundary.",
];

const CANNOT_TELL = [
  "Private feelings, motives, attraction, or future relationship outcomes.",
  "Deception verdicts or private context not present in the text.",
  "Clinical, neurodevelopmental, personality, relationship-style, or identity labels.",
  "Whether you should reply or how to influence another person.",
];

const DEFAULT_NEXT_STEPS = [
  "Clarify one ask in plain language.",
  "Lower pressure by making no or later acceptable.",
  "Pause before replying if the exchange feels escalated.",
];

function normalizeText(value) {
  return String(value || "").trim();
}

function normalizeList(value) {
  return Array.isArray(value) ? value.map(normalizeText).filter(Boolean) : [];
}

function titleCase(value) {
  const text = normalizeText(value || "mixed").toLowerCase();
  return `${text.charAt(0).toUpperCase()}${text.slice(1)}`;
}

function collectEvidencePhrases(result) {
  const rows = [
    ...(Array.isArray(result?.evidence) ? result.evidence : []),
    ...(Array.isArray(result?.inconsistency_cues) ? result.inconsistency_cues : []),
    ...(Array.isArray(result?.unsupported_claim_shift) ? result.unsupported_claim_shift : []),
    ...(Array.isArray(result?.specificity_drop) ? result.specificity_drop : []),
    ...(Array.isArray(result?.answer_evasion_pattern) ? result.answer_evasion_pattern : []),
    ...(Array.isArray(result?.contradiction_against_prior_message)
      ? result.contradiction_against_prior_message
      : []),
  ];
  const seen = new Set();
  const phrases = [];
  for (const row of rows) {
    const phrase = normalizeText(row?.safe_phrase);
    if (!phrase || seen.has(phrase)) {
      continue;
    }
    seen.add(phrase);
    phrases.push(phrase);
  }
  return phrases.slice(0, 8);
}

function collectEvidenceDetails(result) {
  const rows = [
    ...(Array.isArray(result?.evidence) ? result.evidence : []),
    ...(Array.isArray(result?.inconsistency_cues) ? result.inconsistency_cues : []),
    ...(Array.isArray(result?.unsupported_claim_shift) ? result.unsupported_claim_shift : []),
    ...(Array.isArray(result?.specificity_drop) ? result.specificity_drop : []),
    ...(Array.isArray(result?.answer_evasion_pattern) ? result.answer_evasion_pattern : []),
    ...(Array.isArray(result?.contradiction_against_prior_message)
      ? result.contradiction_against_prior_message
      : []),
  ];
  const seen = new Set();
  return rows
    .filter((row) => {
      const evidenceId = normalizeText(row?.evidence_id);
      if (!evidenceId || seen.has(evidenceId)) {
        return false;
      }
      seen.add(evidenceId);
      return normalizeText(row?.safe_phrase || row?.evidence_text);
    })
    .slice(0, 6)
    .map((row) => ({
      id: normalizeText(row.evidence_id),
      family: normalizeText(row.cue_family || row.cue_id || "cue").replace(/_/g, " "),
      phrase: normalizeText(row.safe_phrase || row.evidence_text),
      explanation: normalizeText(row.explanation),
      repair: normalizeText(row.repair_suggestion),
    }));
}

function buildMatchView(result) {
  const score = Number(result?.score ?? 0);
  const normalizedScore = Number.isFinite(score) ? Math.max(0, Math.min(1, score)) : 0;
  const resultState = normalizeText(result?.result_state);
  const isLowSignal =
    resultState === "low_signal" ||
    result?.low_signal_fallback === true ||
    result?.signal_strength === "insufficient";
  return {
    matchId: normalizeText(result?.match_id),
    score: normalizedScore,
    scoreLabel: `${Math.round(normalizedScore * 100)}% cue-weight score`,
    resultState,
    isLowSignal,
    signalStrength: normalizeText(result?.signal_strength || (isLowSignal ? "insufficient" : "medium")),
    bandLabel: isLowSignal
      ? "Insufficient signal"
      : `${titleCase(result?.compatibility_band)} communication pattern band`,
    confidenceLabel: result?.confidence?.level
      ? `${titleCase(result.confidence.level)} evidence confidence`
      : "Evidence confidence unavailable",
    confidenceReasons: normalizeList(result?.confidence?.reasons).slice(0, 3),
    positiveFactors: normalizeList(
      result?.positive_factors?.length ? result.positive_factors : result?.top_alignment_factors
    ),
    riskFactors: normalizeList(
      result?.risk_factors?.length ? result.risk_factors : result?.top_friction_factors
    ),
    evidencePhrases: collectEvidencePhrases(result),
    evidenceDetails: collectEvidenceDetails(result),
    explanation:
      normalizeText(result?.safe_explanation) ||
      normalizeText(result?.safe_summary) ||
      "This result is based on explicit observable communication cues.",
    cannotInfer: normalizeList(result?.cannot_infer).length
      ? normalizeList(result?.cannot_infer)
      : CANNOT_TELL,
    canTell: CAN_TELL,
    safeNextSteps: normalizeList(result?.safe_next_steps).length
      ? normalizeList(result?.safe_next_steps)
      : DEFAULT_NEXT_STEPS,
    disclosure:
      "This is a bounded communication-pattern review, not a verdict about another person.",
  };
}

function Button({ children, tone = "primary", ...props }) {
  return (
    <button className={`button button-${tone}`} type="button" {...props}>
      {children}
    </button>
  );
}

function TopNav({ setView }) {
  return (
    <header className="top-nav">
      <button className="brand-lockup" type="button" onClick={() => setView("home")}>
        <span className="brand-mark">
          <Activity size={18} />
        </span>
        <span>Vibe Signal</span>
      </button>
      <nav className="nav-links" aria-label="Primary">
        <button type="button" onClick={() => setView("analyze")}>
          Analyze
        </button>
        <button type="button" onClick={() => setView("legal")}>
          Legal
        </button>
      </nav>
    </header>
  );
}

function Home({ setView, setMode }) {
  const backendLabel = API_CONFIG.ok ? API_CONFIG.host : "backend misconfigured";

  const start = (nextMode) => {
    setMode(nextMode);
    setView("analyze");
  };

  return (
    <main className="page home-page">
      <section className="hero-grid" aria-labelledby="hero-title">
        <div className="hero-copy">
          <p className="eyebrow">Communication support</p>
          <h1 id="hero-title">Understand message patterns without guessing motives.</h1>
          <p className="hero-subtitle">
            Paste a synthetic or permissioned exchange to review observable fit and friction cues.
            Vibe Signal does not infer truth, motive, attraction, identity, health, or outcomes.
          </p>
          <div className="hero-actions">
            <Button onClick={() => start("match")}>
              Try a synthetic example <ArrowRight size={17} />
            </Button>
            <Button tone="secondary" onClick={() => setView("beta")}>
              Request beta access <SlidersHorizontal size={17} />
            </Button>
          </div>
          <p className="quiet-copy">
            Synthetic demo first. Use only permissioned text and avoid sensitive personal details.
          </p>
        </div>
        <div className="hero-visual demo-visual" aria-label="Synthetic Vibe Signal demo">
          <div className="demo-phone">
            <p className="metric-label">Synthetic demo</p>
            <div className="message-bubble self">Can you confirm Friday at 3pm?</div>
            <div className="message-bubble other">Yes, Friday at 3pm works. No pressure if we need to adjust.</div>
            <div className="demo-result">
              <strong>Medium signal strength</strong>
              <span>Specific timing</span>
              <span>Low-pressure wording</span>
              <span>Direct ask</span>
            </div>
          </div>
          <div className="preview-panel">
            <div>
              <span className="metric-label">Current backend</span>
              <strong>{backendLabel}</strong>
            </div>
            <span className="status-pill">{API_CONFIG.ok ? "ready" : "check env"}</span>
          </div>
        </div>
      </section>

      <section className="trust-strip" aria-label="Trust boundaries">
        <span>Synthetic demo available</span>
        <span>Permissioned text only</span>
        <span>No hidden-state claims</span>
        <span>Raw messages not persisted by default</span>
        <span>Legal review pending</span>
      </section>

      <section className="mode-grid" aria-label="Vibe Signal tools">
        <button className="mode-tile" type="button" onClick={() => start("match")}>
          <MessageSquare size={22} />
          <span>Synthetic demo</span>
          <small>Start with authored sample text before using permissioned text.</small>
        </button>
        <button className="mode-tile" type="button" onClick={() => start("evidence")}>
          <Gauge size={22} />
          <span>Observable cues</span>
          <small>Review directness, ambiguity, pressure, repair, and cognitive load.</small>
        </button>
        <button className="mode-tile" type="button" onClick={() => setView("legal")}>
          <ShieldCheck size={22} />
          <span>Legal and privacy</span>
          <small>Draft closed-beta boundaries, deletion, and export references.</small>
        </button>
      </section>

      <section className="info-grid" aria-label="How Vibe Signal works">
        <div>
          <h3>How it works</h3>
          <p>Review synthetic or permissioned text, inspect evidence-backed cues, then choose a calm next step or stop.</p>
        </div>
        <div>
          <h3>Can help with</h3>
          <p>Clarifying asks, lowering pressure, noticing overloaded messages, and finding repair openings.</p>
        </div>
        <div>
          <h3>Cannot tell you</h3>
          <p>It does not read minds, identify deception, assign clinical labels, or optimize persuasion.</p>
        </div>
      </section>
    </main>
  );
}

function Analyze({ mode, setMode, setView, setResult }) {
  const [text, setText] = useState(SAMPLE_TEXT);
  const [consent, setConsent] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const canSubmit = normalizeText(text).length > 0 && consent && !loading;

  async function handleSubmit() {
    if (!canSubmit) {
      return;
    }
    setError("");
    setLoading(true);
    try {
      const payload = mode === "match" ? await submitMatch(text) : await submitAnalyze(text);
      setResult({
        kind: mode,
        sourceTextPreview: normalizeText(text).slice(0, 120),
        payload,
      });
      setView("results");
    } catch (requestError) {
      setError(
        requestError?.message ||
          "The backend could not complete this request with the current payload."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page narrow-page">
      <button className="back-link" type="button" onClick={() => setView("home")}>
        <ArrowLeft size={16} /> Back
      </button>

      <section className="surface analyze-surface">
        <div className="section-heading">
          <p className="eyebrow">Pattern review</p>
          <h2>Review observable wording cues</h2>
          <p>
            Start with the synthetic example or use text you have permission to review. Results
            stay bounded to visible wording patterns.
          </p>
        </div>

        <div className="segmented-control" role="tablist" aria-label="Analysis mode">
          <button
            className={mode === "match" ? "active" : ""}
            type="button"
            onClick={() => setMode("match")}
          >
            <MessageSquare size={16} /> Match
          </button>
          <button
            className={mode === "evidence" ? "active" : ""}
            type="button"
            onClick={() => setMode("evidence")}
          >
            <FileText size={16} /> Evidence
          </button>
        </div>

        <label className="field-label" htmlFor="conversation">
          Conversation text
        </label>
        <div className="input-tools">
          <Button tone="secondary" onClick={() => setText(SAMPLE_TEXT)}>
            Use synthetic example
          </Button>
          <Button tone="secondary" onClick={() => setText("")}>
            Clear input
          </Button>
        </div>
        <textarea
          id="conversation"
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="self: Can you confirm Friday at 3pm?&#10;other: Yes, Friday at 3pm works. No pressure if we need to adjust."
        />

        <div className="disclosure-box">
          <ShieldCheck size={18} />
          <div>
            <strong>Before you analyze</strong>
            <p>
              Vibe Signal is communication-support only. Outputs are pattern-based suggestions,
              not decisions about another person. Only submit messages you have permission to
              analyze. Do not include names, phone numbers, addresses, minors, medical/legal/
              financial/workplace-sensitive content, or highly sensitive third-party content.
            </p>
          </div>
        </div>

        <section className="limits-grid" aria-label="Analysis boundaries">
          <ListBlock title="Can tell you" items={CAN_TELL} empty="" />
          <ListBlock title="Cannot tell you" items={CANNOT_TELL} empty="" />
        </section>

        <label className="checkbox-row">
          <input
            checked={consent}
            onChange={(event) => setConsent(event.target.checked)}
            type="checkbox"
          />
          <span>I have permission to process this text and understand the draft legal boundaries.</span>
        </label>

        {error ? (
          <div className="error-banner" role="alert">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        ) : null}

        <div className="form-footer">
          <span>{loading ? "Waiting for backend..." : "Backend only. No local model changes."}</span>
          <Button disabled={!canSubmit} onClick={handleSubmit}>
            {loading ? "Checking..." : mode === "match" ? "Review pattern band" : "Surface cues"}
          </Button>
        </div>
      </section>
    </main>
  );
}

function ListBlock({ title, items, empty }) {
  const rows = items.length ? items : [empty];
  return (
    <section className="result-block">
      <h3>{title}</h3>
      <ul>
        {rows.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

function MatchResults({ result, setView }) {
  const view = useMemo(() => buildMatchView(result), [result]);
  const [feedbackConsent, setFeedbackConsent] = useState(false);
  const [feedbackStatus, setFeedbackStatus] = useState("");
  const [feedbackError, setFeedbackError] = useState("");
  const [submittedFeedbackRatings, setSubmittedFeedbackRatings] = useState([]);

  async function sendFeedback(rating) {
    if (submittedFeedbackRatings.includes(rating)) {
      setFeedbackStatus("Feedback metadata already accepted for this result.");
      setFeedbackError("");
      return;
    }
    setFeedbackStatus("");
    setFeedbackError("");
    try {
      await submitFeedback({
        matchId: view.matchId,
        rating,
        consent: feedbackConsent,
      });
      setSubmittedFeedbackRatings((current) =>
        current.includes(rating) ? current : [...current, rating]
      );
      setFeedbackStatus("Feedback metadata accepted. No raw comment was sent.");
    } catch (error) {
      setFeedbackError(
        feedbackConsent
          ? error?.message || "Feedback could not be stored."
          : "Feedback storage requires explicit consent."
      );
    }
  }

  return (
    <>
      <section className="result-hero">
        <div>
          <p className="eyebrow">Evidence-backed communication review</p>
          <h2>{view.bandLabel}</h2>
          <p>{view.explanation}</p>
          <p className="result-meta">
            Signal strength: {titleCase(view.signalStrength.replace(/_/g, " "))}. {view.confidenceLabel}.
          </p>
        </div>
        <div className="score-detail">
          <span>API detail</span>
          <strong>{view.isLowSignal ? "Not shown" : view.scoreLabel}</strong>
        </div>
      </section>

      <section className="disclaimer-strip">
        <CheckCircle2 size={18} />
        <span>{view.disclosure}</span>
      </section>

      <section className="limits-grid" aria-label="Result boundaries">
        <ListBlock title="What this can tell you" items={view.canTell} empty="" />
        <ListBlock title="What this cannot tell you" items={view.cannotInfer} empty="" />
      </section>

      {view.isLowSignal ? (
        <section className="low-signal-panel">
          <h3>Low signal</h3>
          <p>
            Not enough visible evidence was returned for a normal pattern review. No action is
            required; add more permissioned context only if you want a broader review.
          </p>
          {view.confidenceReasons.length ? (
            <ul>
              {view.confidenceReasons.map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
          ) : null}
        </section>
      ) : null}

      <section className="result-block wide-block">
        <h3>Observed cue phrases</h3>
        <div className="evidence-detail-grid">
          {(view.evidenceDetails.length
            ? view.evidenceDetails
            : [
                {
                  id: "empty",
                  family: "low signal",
                  phrase: "No evidence phrases returned yet.",
                  explanation: "",
                  repair: "",
                },
              ]
          ).map((row) => (
            <article className="evidence-detail" key={row.id}>
              <span>{row.family}</span>
              <strong>{row.phrase}</strong>
              {row.repair ? <p>{row.repair}</p> : null}
            </article>
          ))}
        </div>
      </section>

      <div className="result-grid">
        <ListBlock
          title="Helpful cues"
          items={view.positiveFactors}
          empty="No strong alignment factor is visible from the current text."
        />
        <ListBlock
          title="Friction cues"
          items={view.riskFactors}
          empty="No major deterministic friction cue is visible from the current text."
        />
      </div>

      <section className="result-block wide-block">
        <h3>Possible next steps</h3>
        <ul>
          {view.safeNextSteps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ul>
      </section>

      <section className="feedback-panel">
        <div>
          <h3>Feedback</h3>
          <p>Optional one-time metadata feedback for this match result.</p>
        </div>
        <label className="checkbox-row compact">
          <input
            checked={feedbackConsent}
            onChange={(event) => setFeedbackConsent(event.target.checked)}
            type="checkbox"
          />
          <span>Consent to store bounded feedback metadata.</span>
        </label>
        <div className="feedback-actions">
          <Button
            tone="secondary"
            disabled={!view.matchId || submittedFeedbackRatings.includes(1)}
            onClick={() => sendFeedback(1)}
          >
            Useful for review
          </Button>
          <Button
            tone="secondary"
            disabled={!view.matchId || submittedFeedbackRatings.includes(0)}
            onClick={() => sendFeedback(0)}
          >
            Not useful for review
          </Button>
        </div>
        {feedbackStatus ? <p className="success-text">{feedbackStatus}</p> : null}
        {feedbackError ? <p className="error-text">{feedbackError}</p> : null}
      </section>

      <Button onClick={() => setView("analyze")}>
        Review another synthetic or permissioned example <ArrowRight size={17} />
      </Button>
    </>
  );
}

function AnalyzeResults({ result, setView }) {
  const evidence = Array.isArray(result?.evidence) ? result.evidence : [];
  return (
    <>
      <section className="result-hero">
        <div>
          <p className="eyebrow">Cue evidence</p>
          <h2>{evidence.length ? `${evidence.length} deterministic cues` : "No cue rows returned"}</h2>
          <p>
            Evidence objects came from the deterministic cue taxonomy. Display text uses safe
            phrases and cautious explanations from the backend.
          </p>
        </div>
        <div className="status-pill large">raw not stored</div>
      </section>

      <section className="evidence-list">
        {(evidence.length ? evidence : [{ cue_id: "no_cue", safe_phrase: "No deterministic cue returned for this text.", explanation: "No action is required; add permissioned context only if a broader pattern review would help." }]).map((row, index) => (
          <article className="evidence-row" key={`${row.evidence_id || row.cue_id}:${index}`}>
            <div>
              <span>{normalizeText(row.cue_family || row.cue_id || "cue").replace(/_/g, " ")}</span>
              <strong>{normalizeText(row.safe_phrase || "Safe phrase unavailable.")}</strong>
            </div>
            <p>{normalizeText(row.explanation || "Deterministic cue explanation unavailable.")}</p>
          </article>
        ))}
      </section>

      <section className="disclaimer-strip">
        <CheckCircle2 size={18} />
        <span>
          Evidence rows are observable wording cues only. They do not decide motives, identity,
          health, or outcomes.
        </span>
      </section>

      <Button onClick={() => setView("analyze")}>
        Review another synthetic or permissioned example <ArrowRight size={17} />
      </Button>
    </>
  );
}

function Results({ result, setView }) {
  if (!result) {
    return (
      <main className="page narrow-page">
        <section className="surface">
          <h2>No result yet</h2>
          <Button onClick={() => setView("analyze")}>Start analysis</Button>
        </section>
      </main>
    );
  }

  return (
    <main className="page results-page">
      <button className="back-link" type="button" onClick={() => setView("analyze")}>
        <ArrowLeft size={16} /> Back to input
      </button>
      {result.kind === "match" ? (
        <MatchResults result={result.payload} setView={setView} />
      ) : (
        <AnalyzeResults result={result.payload} setView={setView} />
      )}
    </main>
  );
}

function Legal({ setView }) {
  const [slug, setSlug] = useState("match-disclaimer");
  const [page, setPage] = useState(FALLBACK_LEGAL);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const payload = await fetchLegalPage(slug);
        if (!cancelled) {
          setPage(payload);
        }
      } catch (requestError) {
        if (!cancelled) {
          setPage(FALLBACK_LEGAL);
          setError(requestError?.message || "Legal route could not be fetched.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [slug]);

  return (
    <main className="page narrow-page">
      <button className="back-link" type="button" onClick={() => setView("home")}>
        <ArrowLeft size={16} /> Back
      </button>
      <section className="surface legal-surface">
        <div className="section-heading">
          <p className="eyebrow">Legal and privacy</p>
          <h2>{page.title}</h2>
          <p>Status: {page.status || "draft_requires_legal_review"}</p>
        </div>
        <div className="legal-tabs">
          {LEGAL_SLUGS.map(([nextSlug, label]) => (
            <button
              className={slug === nextSlug ? "active" : ""}
              key={nextSlug}
              type="button"
              onClick={() => setSlug(nextSlug)}
            >
              {label}
            </button>
          ))}
        </div>
        {error ? (
          <div className="error-banner" role="alert">
            <AlertCircle size={18} />
            <span>Using fallback copy because the legal route did not load.</span>
          </div>
        ) : null}
        {loading ? <p className="quiet-copy">Loading legal draft...</p> : null}
        <div className="legal-list">
          {(page.sections || []).map((section) => (
            <p key={section}>{section}</p>
          ))}
        </div>
        <p className="quiet-copy">
          Document reference: {page.document_ref || "docs/match_usage_consent_disclaimer.md"}
        </p>
      </section>
    </main>
  );
}

function Beta({ setView }) {
  const [email, setEmail] = useState("");
  const [platform, setPlatform] = useState("iOS");
  const [intent, setIntent] = useState("");
  const [boundaryConsent, setBoundaryConsent] = useState(false);
  const [permissionConsent, setPermissionConsent] = useState(false);

  const ready = normalizeText(email) && normalizeText(intent) && boundaryConsent && permissionConsent;

  return (
    <main className="page narrow-page">
      <button className="back-link" type="button" onClick={() => setView("home")}>
        <ArrowLeft size={16} /> Back
      </button>
      <section className="surface analyze-surface">
        <div className="section-heading">
          <p className="eyebrow">Closed beta</p>
          <h2>Request beta access</h2>
          <p>
            This local form stages the intended beta fields without sending data. Tester invites
            remain blocked until real-device QA and legal review pass.
          </p>
        </div>
        <label className="field-label" htmlFor="beta-email">Email</label>
        <input
          id="beta-email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@example.com"
        />
        <label className="field-label" htmlFor="beta-platform">Platform</label>
        <select
          id="beta-platform"
          value={platform}
          onChange={(event) => setPlatform(event.target.value)}
        >
          <option>iOS</option>
          <option>Web</option>
          <option>Both</option>
        </select>
        <label className="field-label" htmlFor="beta-intent">Tester intent</label>
        <textarea
          className="short-textarea"
          id="beta-intent"
          value={intent}
          onChange={(event) => setIntent(event.target.value)}
          placeholder="Briefly describe the communication-support scenario you want to test with synthetic or permissioned text."
        />
        <label className="checkbox-row">
          <input
            checked={boundaryConsent}
            onChange={(event) => setBoundaryConsent(event.target.checked)}
            type="checkbox"
          />
          <span>I understand this beta is communication support only and not production-ready.</span>
        </label>
        <label className="checkbox-row">
          <input
            checked={permissionConsent}
            onChange={(event) => setPermissionConsent(event.target.checked)}
            type="checkbox"
          />
          <span>I will use synthetic text or messages I have permission to review.</span>
        </label>
        <Button disabled={!ready}>Beta request fields ready</Button>
        <p className="quiet-copy">No beta request is submitted from this static form in this build.</p>
      </section>
    </main>
  );
}

export default function App() {
  const [view, setView] = useState("home");
  const [mode, setMode] = useState("match");
  const [result, setResult] = useState(null);

  return (
    <div className="app-shell">
      <TopNav setView={setView} />
      {view === "home" ? <Home setView={setView} setMode={setMode} /> : null}
      {view === "analyze" ? (
        <Analyze mode={mode} setMode={setMode} setView={setView} setResult={setResult} />
      ) : null}
      {view === "results" ? <Results result={result} setView={setView} /> : null}
      {view === "legal" ? <Legal setView={setView} /> : null}
      {view === "beta" ? <Beta setView={setView} /> : null}
    </div>
  );
}
