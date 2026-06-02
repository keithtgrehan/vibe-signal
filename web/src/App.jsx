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
  API_BASE_URL,
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

function buildMatchView(result) {
  const score = Number(result?.score ?? 0);
  const normalizedScore = Number.isFinite(score) ? Math.max(0, Math.min(1, score)) : 0;
  return {
    matchId: normalizeText(result?.match_id),
    score: normalizedScore,
    scoreLabel: `${Math.round(normalizedScore * 100)}%`,
    bandLabel: `${titleCase(result?.compatibility_band)} fit`,
    confidenceLabel: result?.confidence?.level
      ? `${titleCase(result.confidence.level)} evidence confidence`
      : "Evidence confidence unavailable",
    positiveFactors: normalizeList(
      result?.positive_factors?.length ? result.positive_factors : result?.top_alignment_factors
    ),
    riskFactors: normalizeList(
      result?.risk_factors?.length ? result.risk_factors : result?.top_friction_factors
    ),
    evidencePhrases: collectEvidencePhrases(result),
    explanation:
      normalizeText(result?.safe_explanation) ||
      normalizeText(result?.safe_summary) ||
      "Compatibility is based on explicit observable communication cues.",
    disclosure:
      "The match score reflects observable communication-pattern compatibility only, not feelings, motives, identity, health, or relationship outcomes.",
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
  const start = (nextMode) => {
    setMode(nextMode);
    setView("analyze");
  };

  return (
    <main className="page home-page">
      <section className="hero-grid" aria-labelledby="hero-title">
        <div className="hero-copy">
          <p className="eyebrow">Communication support</p>
          <h1 id="hero-title">Something Feels Different</h1>
          <p className="hero-subtitle">
            Review observable communication patterns with current deterministic contracts and
            cautious wording.
          </p>
          <div className="hero-actions">
            <Button onClick={() => start("match")}>
              Check fit <ArrowRight size={17} />
            </Button>
            <Button tone="secondary" onClick={() => start("evidence")}>
              Surface cues <SlidersHorizontal size={17} />
            </Button>
          </div>
          <p className="quiet-copy">
            Only use synthetic or permissioned text. Raw messages are not persisted by default.
          </p>
        </div>
        <div className="hero-visual" aria-label="Vibe Signal preview">
          <img src="/opengraph.jpg" alt="" />
          <div className="preview-panel">
            <div>
              <span className="metric-label">Current backend</span>
              <strong>{API_BASE_URL.replace(/^https?:\/\//, "")}</strong>
            </div>
            <span className="status-pill">safe routes</span>
          </div>
        </div>
      </section>

      <section className="mode-grid" aria-label="Vibe Signal tools">
        <button className="mode-tile" type="button" onClick={() => start("match")}>
          <MessageSquare size={22} />
          <span>Communication Fit</span>
          <small>Score, fit band, factors, evidence phrases.</small>
        </button>
        <button className="mode-tile" type="button" onClick={() => start("evidence")}>
          <Gauge size={22} />
          <span>Cue Evidence</span>
          <small>Deterministic cue taxonomy rows from `/api/analyze`.</small>
        </button>
        <button className="mode-tile" type="button" onClick={() => setView("legal")}>
          <ShieldCheck size={22} />
          <span>Safety Copy</span>
          <small>Draft legal routes fetched from the backend.</small>
        </button>
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
          <h2>Look Again</h2>
          <p>
            The backend uses deterministic contracts. Results stay bounded to observable wording
            cues.
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
              not truth claims. Do not submit sensitive personal data or third-party private
              messages without permission.
            </p>
          </div>
        </div>

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
            {loading ? "Checking..." : mode === "match" ? "Check fit" : "Surface cues"}
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

  async function sendFeedback(rating) {
    setFeedbackStatus("");
    setFeedbackError("");
    try {
      await submitFeedback({
        matchId: view.matchId,
        rating,
        consent: feedbackConsent,
      });
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
          <p className="eyebrow">Communication fit</p>
          <h2>{view.bandLabel}</h2>
          <p>{view.explanation}</p>
        </div>
        <div className="score-ring" style={{ "--score": `${view.score * 100}%` }}>
          <span>{view.scoreLabel}</span>
        </div>
      </section>

      <div className="result-grid">
        <ListBlock
          title="Positive factors"
          items={view.positiveFactors}
          empty="No strong alignment factor is visible from the current text."
        />
        <ListBlock
          title="Risk factors"
          items={view.riskFactors}
          empty="No major deterministic friction cue is visible from the current text."
        />
      </div>

      <section className="result-block wide-block">
        <h3>Evidence safe phrases</h3>
        <div className="phrase-grid">
          {(view.evidencePhrases.length
            ? view.evidencePhrases
            : ["No evidence phrases returned yet."]
          ).map((phrase) => (
            <span key={phrase}>{phrase}</span>
          ))}
        </div>
      </section>

      <section className="disclaimer-strip">
        <CheckCircle2 size={18} />
        <span>{view.confidenceLabel}. {view.disclosure}</span>
      </section>

      <section className="feedback-panel">
        <div>
          <h3>Feedback</h3>
          <p>Optional metadata-only feedback for this match result.</p>
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
          <Button tone="secondary" disabled={!view.matchId} onClick={() => sendFeedback(1)}>
            Useful
          </Button>
          <Button tone="secondary" disabled={!view.matchId} onClick={() => sendFeedback(0)}>
            Not useful
          </Button>
        </div>
        {feedbackStatus ? <p className="success-text">{feedbackStatus}</p> : null}
        {feedbackError ? <p className="error-text">{feedbackError}</p> : null}
      </section>

      <Button onClick={() => setView("analyze")}>
        Analyze another <ArrowRight size={17} />
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
            `/api/analyze` returned evidence objects from the current cue taxonomy. Display text
            uses safe phrases and explanations from the backend.
          </p>
        </div>
        <div className="status-pill large">raw not stored</div>
      </section>

      <section className="evidence-list">
        {(evidence.length ? evidence : [{ cue_id: "no_cue", safe_phrase: "No deterministic cue returned for this text.", explanation: "Try a longer synthetic exchange for more surface area." }]).map((row, index) => (
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
          Evidence rows include interpretation limits and text hashes from the backend contract.
          They do not infer true emotion, deception, personality, or health.
        </span>
      </section>

      <Button onClick={() => setView("analyze")}>
        Analyze another <ArrowRight size={17} />
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
          <p className="eyebrow">Backend legal routes</p>
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
    </div>
  );
}
