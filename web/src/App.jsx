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

import { fetchLegalPage, submitAnalyze, submitFeedback, submitMatch } from "./api.js";
import {
  CAN_HELP_WITH,
  CANNOT_TELL,
  FAQ_ITEMS,
  HERO_COPY,
  HOW_IT_WORKS_STEPS,
  SYNTHETIC_DEMOS,
  TRUST_STRIP_ITEMS,
} from "./trustContent.js";
import {
  buildLowSignalFallback,
  buildSyntheticResult,
  buildTrustFirstResultView,
  FEEDBACK_OPTIONS,
  isContextLightInput,
} from "./resultViewModel.js";

const SAMPLE_TEXT = SYNTHETIC_DEMOS[0].exchange;

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

function Button({ children, tone = "primary", className = "", ...props }) {
  return (
    <button className={`button button-${tone} ${className}`.trim()} type="button" {...props}>
      {children}
    </button>
  );
}

function TopNav({ goToHowItWorks, runSyntheticDemo, setView }) {
  return (
    <header className="top-nav">
      <button className="brand-lockup" type="button" onClick={() => setView("home")}>
        <span className="brand-mark">
          <Activity size={18} />
        </span>
        <span>Vibe Signal</span>
      </button>
      <nav className="nav-links" aria-label="Primary">
        <button type="button" onClick={() => runSyntheticDemo(SYNTHETIC_DEMOS[0].id)}>
          Demo
        </button>
        <button type="button" onClick={goToHowItWorks}>
          How it works
        </button>
        <button type="button" onClick={() => setView("beta")}>
          Beta
        </button>
      </nav>
    </header>
  );
}

function Home({ goToHowItWorks, runSyntheticDemo, setView }) {
  const preview = buildTrustFirstResultView(buildSyntheticResult(SYNTHETIC_DEMOS[0].id));

  return (
    <main className="page home-page">
      <section className="hero-grid" aria-labelledby="hero-title">
        <div className="hero-copy">
          <p className="eyebrow">Communication support</p>
          <h1 id="hero-title">{HERO_COPY.title}</h1>
          <p className="hero-subtitle">{HERO_COPY.subtitle}</p>
          <div className="hero-actions">
            <Button onClick={() => runSyntheticDemo(SYNTHETIC_DEMOS[0].id)}>
              {HERO_COPY.primaryCta} <ArrowRight size={17} />
            </Button>
            <Button tone="secondary" onClick={goToHowItWorks}>
              {HERO_COPY.secondaryCta} <SlidersHorizontal size={17} />
            </Button>
          </div>
          <p className="quiet-copy">{HERO_COPY.trustNote}</p>
        </div>
        <div className="hero-visual demo-visual" aria-label="Synthetic Vibe Signal result preview">
          <div className="demo-phone">
            <p className="metric-label">Synthetic example</p>
            <div className="message-bubble self">Are we still on for Friday?</div>
            <div className="message-bubble other">maybe later, not sure yet</div>
            <div className="demo-result">
              <strong>{preview.signalStrengthLabel}</strong>
              {preview.patternLabels.map((label) => (
                <span key={label}>{label}</span>
              ))}
            </div>
          </div>
          <div className="preview-panel">
            <div>
              <span className="metric-label">Evidence first</span>
              <strong>{preview.evidencePhrases.map((phrase) => `“${phrase}”`).join("  ")}</strong>
            </div>
            <span className="status-pill">bounded read</span>
          </div>
        </div>
      </section>

      <section className="trust-strip" aria-label="Trust boundaries">
        {TRUST_STRIP_ITEMS.map((item) => (
          <span key={item}>{item}</span>
        ))}
      </section>

      <section className="section-stack" aria-labelledby="demo-title">
        <div className="section-heading split-heading">
          <div>
            <p className="eyebrow">Synthetic demo cards</p>
            <h2 id="demo-title">Try the product before using private text.</h2>
          </div>
          <p>
            Each example is authored for demo use, so the first success state is safe and
            repeatable.
          </p>
        </div>
        <SyntheticDemoCards runSyntheticDemo={runSyntheticDemo} />
      </section>

      <section className="result-preview-section" aria-labelledby="preview-title">
        <div className="section-heading">
          <p className="eyebrow">Example result preview</p>
          <h2 id="preview-title">Evidence stays above interpretation.</h2>
          <p>
            Vibe Signal shows the visible phrase, the pattern label, what cannot be inferred, and
            one low-pressure next step.
          </p>
        </div>
        <ResultPreview view={preview} />
      </section>

      <section className="section-stack" id="how-it-works" aria-labelledby="how-title">
        <div className="section-heading">
          <p className="eyebrow">How it works</p>
          <h2 id="how-title">A simple read, then details when you want them.</h2>
        </div>
        <div className="info-grid">
          {HOW_IT_WORKS_STEPS.map((step) => (
            <div key={step.title}>
              <h3>{step.title}</h3>
              <p>{step.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="limits-grid landing-limits" aria-label="Can and cannot">
        <ListBlock title="What this can help with" items={CAN_HELP_WITH} empty="" />
        <ListBlock title="What this cannot tell you" items={CANNOT_TELL} empty="" />
      </section>

      <section className="safety-band" aria-labelledby="safety-title">
        <ShieldCheck size={22} />
        <div>
          <p className="eyebrow">Safety and privacy note</p>
          <h2 id="safety-title">Use permissioned, minimized text.</h2>
          <p>
            Start with synthetic examples. If you paste private text, remove names, phone numbers,
            addresses, and sensitive details first.
          </p>
        </div>
      </section>

      <section className="closed-beta-cta" aria-labelledby="beta-title">
        <div>
          <p className="eyebrow">Closed beta feedback</p>
          <h2 id="beta-title">Recruiter-ready demo flow, feedback still bounded.</h2>
          <p>
            Demo with synthetic examples, then use the beta form only when you are ready to share
            permissioned feedback about the product experience.
          </p>
        </div>
        <Button tone="secondary" onClick={() => setView("beta")}>
          Request beta access <ArrowRight size={17} />
        </Button>
      </section>

      <section className="faq-grid" aria-label="FAQ">
        {FAQ_ITEMS.map((item) => (
          <article className="faq-item" key={item.question}>
            <h3>{item.question}</h3>
            <p>{item.answer}</p>
          </article>
        ))}
      </section>
    </main>
  );
}

function SyntheticDemoCards({ runSyntheticDemo }) {
  return (
    <div className="synthetic-demo-grid">
      {SYNTHETIC_DEMOS.map((demo) => (
        <article className="synthetic-demo-card" key={demo.id}>
          <div>
            <h3>{demo.title}</h3>
            <p className="synthetic-exchange">{demo.exchange}</p>
            <p>{demo.highlight}</p>
          </div>
          <Button tone="secondary" onClick={() => runSyntheticDemo(demo.id)}>
            {demo.actionLabel} <ArrowRight size={16} />
          </Button>
        </article>
      ))}
    </div>
  );
}

function ResultPreview({ view }) {
  return (
    <article className="result-preview-card">
      <div className="result-preview-main">
        <span className="signal-pill">{view.signalStrengthLabel}</span>
        <h3>{view.mainRead}</h3>
      </div>
      <div className="evidence-detail-grid compact-grid">
        {view.evidenceDetails.map((row) => (
          <div className="evidence-detail" key={row.id}>
            <span>{row.family}</span>
            <strong>“{row.phrase}”</strong>
          </div>
        ))}
      </div>
      <div className="cannot-infer-block">{view.cannotInferText}</div>
      <div className="safe-next-card">
        <strong>Safe next step</strong>
        <p>{view.safeNextStep}</p>
      </div>
    </article>
  );
}

function Analyze({ mode, runSyntheticDemo, setMode, setView, setResult }) {
  const [text, setText] = useState(SAMPLE_TEXT);
  const [consent, setConsent] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const hasText = normalizeText(text).length > 0;
  const canSubmit = hasText && consent && !loading;

  async function handleSubmit() {
    if (!hasText) {
      setError("Add a short exchange, or run a synthetic example first.");
      return;
    }
    if (!consent) {
      setError("Confirm permission before private text analysis.");
      return;
    }
    if (isContextLightInput(text)) {
      setResult({
        kind: "match",
        payload: {
          ...buildLowSignalFallback(text),
          match_id: "local_low_signal",
          low_signal_fallback: true,
        },
      });
      setView("results");
      return;
    }

    setError("");
    setLoading(true);
    try {
      const payload = mode === "match" ? await submitMatch(text) : await submitAnalyze(text);
      setResult({
        kind: mode,
        payload,
      });
      setView("results");
    } catch (requestError) {
      setError(
        requestError?.message ||
          "The request could not be completed. Try a synthetic example or use a shorter permissioned exchange."
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
            Run a synthetic card without consent, or paste permissioned text after the lightweight
            consent check.
          </p>
        </div>

        <div className="inline-demo-row" aria-label="Synthetic examples">
          {SYNTHETIC_DEMOS.map((demo) => (
            <button key={demo.id} type="button" onClick={() => runSyntheticDemo(demo.id)}>
              <span>{demo.title}</span>
              <small>{demo.actionLabel}</small>
            </button>
          ))}
        </div>

        <div className="segmented-control" role="tablist" aria-label="Analysis mode">
          <button
            className={mode === "match" ? "active" : ""}
            type="button"
            onClick={() => setMode("match")}
          >
            <MessageSquare size={16} /> Pattern
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
          Permissioned conversation text
        </label>
        <div className="input-tools">
          <Button tone="secondary" onClick={() => setText(SAMPLE_TEXT)}>
            Load synthetic text
          </Button>
          <Button tone="secondary" onClick={() => setText("")}>
            Clear input
          </Button>
        </div>
        <textarea
          id="conversation"
          value={text}
          onChange={(event) => {
            setText(event.target.value);
            setError("");
          }}
          placeholder="self: Can you confirm Friday?&#10;other: maybe later"
        />

        <div className="disclosure-box consent-card">
          <ShieldCheck size={18} />
          <div>
            <strong>Before you paste</strong>
            <ul>
              <li>Only submit messages you have permission to analyze.</li>
              <li>Remove names, phone numbers, addresses, and sensitive details.</li>
              <li>Use synthetic examples if you just want to test the app.</li>
            </ul>
          </div>
        </div>

        <label className="checkbox-row">
          <input
            checked={consent}
            onChange={(event) => setConsent(event.target.checked)}
            type="checkbox"
          />
          <span>I understand and have permission to analyze this text.</span>
        </label>

        {error ? (
          <div className="error-banner" role="alert">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        ) : null}

        <div className="form-footer">
          <span>Private text requires permission. Synthetic demos do not.</span>
          <Button disabled={!canSubmit} onClick={handleSubmit}>
            {loading ? "Checking..." : mode === "match" ? "Review patterns" : "Surface evidence"}
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

function PatternChips({ labels }) {
  return (
    <div className="pattern-chip-row">
      {labels.map((label) => (
        <span key={label}>{label}</span>
      ))}
    </div>
  );
}

function MatchResults({ result, runSyntheticDemo, setView }) {
  const view = useMemo(() => buildTrustFirstResultView(result), [result]);
  const [feedbackConsent, setFeedbackConsent] = useState(false);
  const [feedbackStatus, setFeedbackStatus] = useState("");
  const [feedbackError, setFeedbackError] = useState("");
  const [submittedFeedback, setSubmittedFeedback] = useState([]);

  async function sendFeedback(option) {
    if (submittedFeedback.includes(option.id)) {
      setFeedbackStatus("Feedback metadata already accepted for this result.");
      setFeedbackError("");
      return;
    }
    setFeedbackStatus("");
    setFeedbackError("");
    try {
      await submitFeedback({
        matchId: view.matchId,
        feedbackTag: option.id,
        rating: option.rating,
        consent: feedbackConsent,
      });
      setSubmittedFeedback((current) =>
        current.includes(option.id) ? current : [...current, option.id]
      );
      setFeedbackStatus("Feedback metadata accepted. No raw message text was sent.");
    } catch (error) {
      setFeedbackError(
        feedbackConsent
          ? error?.message || "Feedback could not be stored."
          : "Feedback storage requires explicit consent."
      );
    }
  }

  if (view.isLowSignal) {
    return (
      <>
        <section className="result-hero low-signal-result">
          <div>
            <p className="eyebrow">Low-signal fallback</p>
            <h2>{view.title}</h2>
            <p>{view.body}</p>
          </div>
        </section>
        <section className="result-block wide-block">
          <h3>Try</h3>
          <ul>
            {view.tryItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
        <div className="result-action-row">
          <Button tone="secondary" onClick={() => setView("analyze")}>
            Add more context
          </Button>
          <Button onClick={() => runSyntheticDemo(SYNTHETIC_DEMOS[0].id)}>
            Try a synthetic example <ArrowRight size={17} />
          </Button>
        </div>
      </>
    );
  }

  return (
    <>
      <section className="result-hero evidence-first-hero">
        <div>
          <p className="eyebrow">Main read</p>
          <h2>{view.mainRead}</h2>
          <span className="signal-pill">{view.signalStrengthLabel}</span>
        </div>
      </section>

      <section className="result-block wide-block">
        <div className="section-heading">
          <p className="eyebrow">Evidence phrases</p>
          <h3>Quoted wording behind the read</h3>
        </div>
        <div className="evidence-detail-grid">
          {view.evidenceDetails.map((row) => (
            <article className="evidence-detail" key={row.id}>
              <span>{row.family}</span>
              <strong>“{row.phrase}”</strong>
              {row.repair ? <p>{row.repair}</p> : null}
            </article>
          ))}
        </div>
      </section>

      <section className="result-block wide-block">
        <div className="section-heading">
          <p className="eyebrow">Pattern explanation</p>
          <h3>{view.patternExplanation}</h3>
        </div>
        <PatternChips labels={view.patternLabels} />
      </section>

      <section className="cannot-infer-block wide-block">
        <h3>What this cannot tell you</h3>
        <p>{view.cannotInferText}</p>
      </section>

      <section className="safe-next-card wide-block">
        <h3>Safe next step</h3>
        <p>{view.safeNextStep}</p>
      </section>

      <section className="limits-grid" aria-label="Result boundaries">
        <ListBlock title="Can help with" items={view.canTell} empty="" />
        <ListBlock title="Cannot tell you" items={view.cannotTell} empty="" />
      </section>

      <section className="disclaimer-strip">
        <CheckCircle2 size={18} />
        <span>{view.disclosure}</span>
      </section>

      <section className="feedback-panel">
        <div>
          <h3>Was this result useful?</h3>
          <p>Optional metadata-only feedback. No free-text comment or message text is sent.</p>
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
          {FEEDBACK_OPTIONS.map((option) => (
            <Button
              key={option.id}
              tone="secondary"
              disabled={!feedbackConsent || !view.matchId || submittedFeedback.includes(option.id)}
              onClick={() => sendFeedback(option)}
            >
              {option.label}
            </Button>
          ))}
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
          <h2>{evidence.length ? `${evidence.length} observable cues` : "No cue rows returned"}</h2>
          <p>
            Evidence objects display safe phrases and cautious explanations from the current cue
            taxonomy.
          </p>
        </div>
        <div className="status-pill large">bounded display</div>
      </section>

      <section className="evidence-list">
        {(evidence.length
          ? evidence
          : [
              {
                cue_id: "no_cue",
                safe_phrase: "No observable cue returned for this text.",
                explanation:
                  "No action is required; add permissioned context only if a broader pattern review would help.",
              },
            ]
        ).map((row, index) => (
          <article className="evidence-row" key={`${row.evidence_id || row.cue_id}:${index}`}>
            <div>
              <span>{normalizeText(row.cue_family || row.cue_id || "cue").replace(/_/g, " ")}</span>
              <strong>{normalizeText(row.safe_phrase || "Safe phrase unavailable.")}</strong>
            </div>
            <p>{normalizeText(row.explanation || "Cue explanation unavailable.")}</p>
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

function Results({ result, runSyntheticDemo, setView }) {
  if (!result) {
    return (
      <main className="page narrow-page">
        <section className="surface">
          <h2>No result yet</h2>
          <Button onClick={() => runSyntheticDemo(SYNTHETIC_DEMOS[0].id)}>Start with a demo</Button>
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
        <MatchResults result={result.payload} runSyntheticDemo={runSyntheticDemo} setView={setView} />
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
          setError(requestError?.message || "The legal draft could not be fetched.");
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
            <span>Using fallback copy because the legal draft did not load.</span>
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
        <label className="field-label" htmlFor="beta-email">
          Email
        </label>
        <input
          id="beta-email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@example.com"
        />
        <label className="field-label" htmlFor="beta-platform">
          Platform
        </label>
        <select
          id="beta-platform"
          value={platform}
          onChange={(event) => setPlatform(event.target.value)}
        >
          <option>iOS</option>
          <option>Web</option>
          <option>Both</option>
        </select>
        <label className="field-label" htmlFor="beta-intent">
          Tester intent
        </label>
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

  function runSyntheticDemo(demoId) {
    setResult({
      kind: "match",
      payload: buildSyntheticResult(demoId),
    });
    setMode("match");
    setView("results");
  }

  function goToHowItWorks() {
    setView("home");
    window.setTimeout(() => {
      document.getElementById("how-it-works")?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 0);
  }

  return (
    <div className="app-shell">
      <TopNav
        goToHowItWorks={goToHowItWorks}
        runSyntheticDemo={runSyntheticDemo}
        setView={setView}
      />
      {view === "home" ? (
        <Home
          goToHowItWorks={goToHowItWorks}
          runSyntheticDemo={runSyntheticDemo}
          setView={setView}
        />
      ) : null}
      {view === "analyze" ? (
        <Analyze
          mode={mode}
          runSyntheticDemo={runSyntheticDemo}
          setMode={setMode}
          setView={setView}
          setResult={setResult}
        />
      ) : null}
      {view === "results" ? (
        <Results result={result} runSyntheticDemo={runSyntheticDemo} setView={setView} />
      ) : null}
      {view === "legal" ? <Legal setView={setView} /> : null}
      {view === "beta" ? <Beta setView={setView} /> : null}
    </div>
  );
}
