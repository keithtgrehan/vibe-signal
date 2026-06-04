import {
  Activity,
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  ChevronDown,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  API_BACKEND_CONNECTION_ERROR_MESSAGE,
  API_RETRYING_BACKEND_MESSAGE,
  ApiRequestError,
  fetchLegalPage,
  submitAnalyze,
  submitFeedback,
} from "./api.js";
import {
  HOW_IT_WORKS_STEPS,
  SYNTHETIC_DEMOS,
} from "./trustContent.js";
import {
  buildVariantSections,
  DEFAULT_VARIANT,
  getVariant,
  resolveVariant,
} from "./variants.js";
import { buildFeedbackMetadata } from "./guidedInteraction.js";
import {
  buildLowSignalFallback,
  buildSyntheticResult,
  buildTrustFirstResultView,
  FEEDBACK_OPTIONS,
  isContextLightInput,
} from "./resultViewModel.js";

const FEATURED_DEMO_ID = "unclear_ask";
const FALLBACK_LEGAL = {
  title: "Closed Beta Legal Draft",
  status: "draft_requires_legal_review",
  sections: [
    "Vibe Signal is communication support only.",
    "Outputs are wording-based suggestions, not truth claims.",
    "Only submit text you have permission to analyze.",
    "Privacy and terms drafts require legal review before public launch.",
  ],
};
const LEGAL_SLUGS = [
  ["privacy", "Privacy"],
  ["terms", "Terms"],
  ["data-deletion", "Data request/delete"],
  ["match-disclaimer", "Disclaimer"],
];

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

function scrollToId(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function getBrowserVariantKey() {
  if (typeof window === "undefined") {
    return DEFAULT_VARIANT;
  }
  return resolveVariant(window.location.search, window.localStorage);
}

function useResolvedVariant() {
  const [variantKey, setVariantKey] = useState(getBrowserVariantKey);
  const variant = useMemo(() => getVariant(variantKey), [variantKey]);

  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.dataset.variant = variant.key;
    }
  }, [variant.key]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return undefined;
    }

    function syncVariantFromUrl() {
      setVariantKey(resolveVariant(window.location.search, window.localStorage));
    }

    window.addEventListener("popstate", syncVariantFromUrl);
    return () => window.removeEventListener("popstate", syncVariantFromUrl);
  }, []);

  return variant;
}

function TopNav({ onRunDemo, onPrivacy, variant }) {
  return (
    <header className="top-nav">
      <button className="brand-lockup" type="button" onClick={() => scrollToId("top")}>
        <span className="brand-mark">
          <Activity size={18} />
        </span>
        <span>Vibe Signal</span>
      </button>
      <nav className="nav-links" aria-label="Primary">
        <button type="button" onClick={() => scrollToId("demo")}>Demo</button>
        <button type="button" onClick={() => scrollToId("how-it-works")}>How it works</button>
        <button type="button" onClick={onPrivacy}>Privacy</button>
        <Button className="nav-cta" onClick={onRunDemo}>{variant.hero.navCta}</Button>
      </nav>
    </header>
  );
}

function Hero({ onRunDemo, variant }) {
  return (
    <section className="hero" id="top" aria-labelledby="hero-title">
      <div className="hero-copy">
        <h1 id="hero-title">{variant.hero.title}</h1>
        <p>{variant.hero.subtitle}</p>
        <div className="hero-actions" aria-label="Primary actions">
          <Button onClick={onRunDemo}>
            {variant.hero.primaryCta}
            <ArrowRight size={17} />
          </Button>
          <Button tone="secondary" onClick={() => scrollToId("analyze")}>
            {variant.hero.secondaryCta}
          </Button>
        </div>
        <p className="trust-line">{variant.hero.trustNote}</p>
      </div>
    </section>
  );
}

function FeaturedDemo({ onRunDemo, variant }) {
  const demo = SYNTHETIC_DEMOS.find((item) => item.id === FEATURED_DEMO_ID) || SYNTHETIC_DEMOS[0];
  const extraDemos = SYNTHETIC_DEMOS.filter((item) => item.id !== demo.id);

  return (
    <section className="demo-card" aria-labelledby="demo-title">
      <div className="section-kicker">{variant.demo.kicker}</div>
      <h2 id="demo-title">{variant.demo.title || demo.title}</h2>
      <div className="message-sample" aria-label="Synthetic example text">
        {demo.exchange.split("\n").map((line) => (
          <p key={line}>{line}</p>
        ))}
      </div>
      <p>{demo.highlight}</p>
      <Button onClick={() => onRunDemo(demo.id)}>
        {variant.demo.cta}
        <ArrowRight size={17} />
      </Button>
      <p className="quiet-copy">{variant.demo.storedCopy}</p>
      <details className="example-disclosure">
        <summary>
          Show more examples
          <ChevronDown size={16} />
        </summary>
        <ul>
          {extraDemos.map((item) => (
            <li key={item.id}>{item.title}</li>
          ))}
        </ul>
      </details>
    </section>
  );
}

function EmptyResult({ onRunDemo, variant }) {
  return (
    <section className="result-card empty-result" aria-label="Result preview">
      <p className="section-kicker">{variant.emptyResult.kicker}</p>
      <h2>{variant.emptyResult.title}</h2>
      <div className="result-section">
        <h3>{variant.resultLabels.standsOut}</h3>
        <p>{variant.emptyResult.standsOutPreview}</p>
      </div>
      <div className="result-section">
        <h3>{variant.resultLabels.evidence}</h3>
        <p>{variant.emptyResult.evidencePreview}</p>
      </div>
      <div className="result-section">
        <h3>{variant.resultLabels.saferReply}</h3>
        <p>{variant.emptyResult.saferReplyPreview}</p>
      </div>
      <Button onClick={onRunDemo}>
        {variant.emptyResult.cta}
        <ArrowRight size={17} />
      </Button>
    </section>
  );
}

function EvidenceList({ rows }) {
  if (!rows.length) {
    return <p>Add a little more context so there is wording to quote.</p>;
  }

  return (
    <ul className="evidence-list">
      {rows.slice(0, 3).map((row) => (
        <li key={row.id}>
          <span>{row.phrase}</span>
        </li>
      ))}
    </ul>
  );
}

function ResultCard({ result, onRunDemo, variant }) {
  const view = useMemo(() => (result ? buildTrustFirstResultView(result) : null), [result]);
  const [feedbackConsent, setFeedbackConsent] = useState(false);
  const [feedbackStatus, setFeedbackStatus] = useState("");
  const [feedbackError, setFeedbackError] = useState("");
  const [submittedFeedback, setSubmittedFeedback] = useState([]);

  if (!view) {
    return <EmptyResult onRunDemo={onRunDemo} variant={variant} />;
  }

  const sections = buildVariantSections(view, variant.key);
  const sectionById = Object.fromEntries(sections.map((section) => [section.id, section]));

  async function sendFeedback(option) {
    const feedbackKey = `${option.id}:result`;
    if (submittedFeedback.includes(feedbackKey)) {
      setFeedbackStatus("Feedback already recorded for this result.");
      setFeedbackError("");
      return;
    }

    setFeedbackStatus("");
    setFeedbackError("");
    const primaryCue = view.evidenceDetails[0] || {};
    const metadata = buildFeedbackMetadata({
      matchId: view.matchId,
      feedbackTag: option.id,
      cueId: primaryCue.id || "",
      cueFamily: primaryCue.cueId || "",
      evidenceQuality: primaryCue.quality || view.evidenceQualitySummary || "",
      goalId: "minimal_ui",
      contextId: "general",
      styleId: "evidence_first",
      lowSignal: view.isLowSignal,
      synthetic: view.synthetic,
    });

    try {
      await submitFeedback({
        ...metadata,
        feedbackTag: option.id,
        rating: option.rating,
        consent: feedbackConsent,
      });
      setSubmittedFeedback((current) =>
        current.includes(feedbackKey) ? current : [...current, feedbackKey]
      );
      setFeedbackStatus("Feedback saved with result metadata only.");
    } catch (_error) {
      setFeedbackError(
        feedbackConsent
          ? "Feedback could not be saved. Try again in a moment."
          : "Check the box before sending feedback."
      );
    }
  }

  return (
    <section className="result-card" aria-label="Vibe Signal result">
      <p className="section-kicker">{view.synthetic ? "Synthetic result" : "Result"}</p>
      <div className="result-section result-primary">
        <h2>{sectionById.standsOut.label}</h2>
        <p>{sectionById.standsOut.text}</p>
      </div>
      <div className="result-section">
        <h3>{sectionById.evidence.label}</h3>
        <EvidenceList rows={sectionById.evidence.rows} />
      </div>
      <div className="result-section">
        <h3>{sectionById.couldMean.label}</h3>
        <p>{sectionById.couldMean.text}</p>
      </div>
      <div className="result-section safer-reply">
        <h3>{sectionById.saferReply.label}</h3>
        <p>{sectionById.saferReply.text}</p>
        <small>{sectionById.saferReply.helper}</small>
      </div>
      <div className="result-section limits">
        <h3>{sectionById.limits.label}</h3>
        <p>{sectionById.limits.text}</p>
      </div>
      <section className="feedback-panel" aria-labelledby="feedback-title">
        <div>
          <h3 id="feedback-title">Was this useful?</h3>
          <p>Feedback stores only result metadata, never the message text.</p>
        </div>
        <label className="checkbox-row compact">
          <input
            checked={feedbackConsent}
            onChange={(event) => setFeedbackConsent(event.target.checked)}
            type="checkbox"
          />
          <span>I agree to send result feedback.</span>
        </label>
        <div className="feedback-actions">
          {FEEDBACK_OPTIONS.slice(0, 3).map((option) => (
            <Button
              className={submittedFeedback.includes(`${option.id}:result`) ? "feedback-option-selected" : ""}
              disabled={!feedbackConsent || !view.matchId || submittedFeedback.includes(`${option.id}:result`)}
              key={option.id}
              tone="secondary"
              onClick={() => sendFeedback(option)}
            >
              {option.label}
            </Button>
          ))}
        </div>
        {feedbackStatus ? <p className="success-text" role="status">{feedbackStatus}</p> : null}
        {feedbackError ? <p className="error-text" role="alert">{feedbackError}</p> : null}
      </section>
    </section>
  );
}

function AnalyzeText({ text, setText, consent, setConsent, loading, error, status, onSubmit, variant }) {
  const canSubmit = normalizeText(text) && consent && !loading;

  return (
    <section className="analyze-section" id="analyze" aria-labelledby="analyze-title">
      <div className="section-heading">
        <p className="section-kicker">{variant.analyze.kicker}</p>
        <h2 id="analyze-title">{variant.analyze.title}</h2>
        <p>{variant.analyze.intro}</p>
      </div>
      <label className="field-label" htmlFor="conversation">Message text</label>
      <textarea
        aria-describedby="analyze-helper consent-copy"
        id="conversation"
        onChange={(event) => setText(event.target.value)}
        placeholder="self: Are we still on for Friday?&#10;other: maybe later, not sure yet"
        value={text}
      />
      <label className="checkbox-row" id="consent-copy">
        <input
          checked={consent}
          onChange={(event) => setConsent(event.target.checked)}
          type="checkbox"
        />
        <span>I have permission to analyze this text.</span>
      </label>
      <p className="helper-copy" id="analyze-helper">
        Avoid sensitive, legal, medical, workplace, or third-party private content unless you have the right to use it.
      </p>
      {error ? (
        <div className="error-banner" role="alert">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      ) : null}
      <div className="form-footer">
        <span aria-live="polite">{status}</span>
        <Button disabled={!canSubmit} onClick={onSubmit}>
          {loading ? "Analyzing..." : variant.analyze.cta}
        </Button>
      </div>
    </section>
  );
}

function HowItWorks() {
  return (
    <section className="how-section" id="how-it-works" aria-labelledby="how-title">
      <div className="section-heading">
        <p className="section-kicker">How it works</p>
        <h2 id="how-title">Three steps, no guesswork.</h2>
      </div>
      <div className="steps-grid">
        {HOW_IT_WORKS_STEPS.map((step, index) => (
          <article key={step.title}>
            <span>{index + 1}</span>
            <h3>{step.title}</h3>
            <p>{step.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function TrustFooter({ onPrivacy }) {
  return (
    <footer className="footer">
      <p>Vibe Signal shows wording patterns. It does not know intent, feelings, truthfulness, health labels, or outcomes.</p>
      <div>
        <button type="button" onClick={onPrivacy}>Privacy</button>
        <button type="button" onClick={onPrivacy}>Terms</button>
        <button type="button" onClick={onPrivacy}>Data request/delete</button>
      </div>
    </footer>
  );
}

function Home({ navDemoRequest, setView, variant }) {
  const [text, setText] = useState("");
  const [consent, setConsent] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const hasText = normalizeText(text);
  const status = !hasText
    ? "Add text, or run the synthetic demo first."
    : !consent
      ? "Check permission before analyzing."
      : loading
        ? "Looking at the wording..."
        : "Ready to analyze.";

  function runSyntheticDemo(demoId = FEATURED_DEMO_ID) {
    setResult(buildSyntheticResult(demoId));
    setError("");
    window.setTimeout(() => scrollToId("demo"), 0);
  }

  useEffect(() => {
    if (navDemoRequest > 0) {
      runSyntheticDemo();
    }
  }, [navDemoRequest]);

  async function handleAnalyzeSubmit() {
    if (!normalizeText(text)) {
      setError("Add a short exchange, or run the demo first.");
      return;
    }
    if (!consent) {
      setError("Check the permission box before analyzing.");
      return;
    }
    if (isContextLightInput(text)) {
      setResult({
        ...buildLowSignalFallback(text),
        match_id: "local_low_signal",
        low_signal_fallback: true,
      });
      setError("");
      window.setTimeout(() => scrollToId("demo"), 0);
      return;
    }

    setLoading(true);
    setError("");
    try {
      const payload = await submitAnalyze(text, {
        onRetry: (retryState) => {
          if (retryState?.classification === "backend_waking") {
            setError(API_RETRYING_BACKEND_MESSAGE);
          }
        },
      });
      setResult(payload);
      setError("");
      window.setTimeout(() => scrollToId("demo"), 0);
    } catch (requestError) {
      setError(
        requestError instanceof ApiRequestError
          ? requestError.message
          : API_BACKEND_CONNECTION_ERROR_MESSAGE
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <Hero onRunDemo={() => runSyntheticDemo()} variant={variant} />
      <section className="demo-result-grid" id="demo" aria-label="Demo and result">
        <FeaturedDemo onRunDemo={runSyntheticDemo} variant={variant} />
        <ResultCard result={result} onRunDemo={() => runSyntheticDemo()} variant={variant} />
      </section>
      <AnalyzeText
        consent={consent}
        error={error}
        loading={loading}
        onSubmit={handleAnalyzeSubmit}
        setConsent={setConsent}
        setText={(value) => {
          setText(value);
          setError("");
        }}
        status={status}
        text={text}
        variant={variant}
      />
      <HowItWorks />
      <TrustFooter onPrivacy={() => setView("legal")} />
    </main>
  );
}

function Legal({ setView }) {
  const [slug, setSlug] = useState("privacy");
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
      } catch (_requestError) {
        if (!cancelled) {
          setPage(FALLBACK_LEGAL);
          setError("Using fallback copy because the legal draft did not load.");
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
      <button className="back-link" type="button" onClick={() => setView("home")}>Back</button>
      <section className="surface legal-surface">
        <CheckCircle2 size={22} />
        <h1>{page.title}</h1>
        <p>Status: {page.status || "draft_requires_legal_review"}</p>
        <div className="segmented-control" aria-label="Legal page">
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
        {error ? <div className="error-banner" role="alert">{error}</div> : null}
        {loading ? <p className="quiet-copy">Loading legal draft...</p> : null}
        <div className="legal-list">
          {(page.sections || []).map((section) => <p key={section}>{section}</p>)}
        </div>
      </section>
    </main>
  );
}

export default function App() {
  const [view, setView] = useState("home");
  const [navDemoRequest, setNavDemoRequest] = useState(0);
  const variant = useResolvedVariant();

  function runDemoFromNav() {
    setView("home");
    setNavDemoRequest((current) => current + 1);
  }

  return (
    <div className="app-shell" data-variant={variant.key}>
      <TopNav
        onPrivacy={() => setView("legal")}
        onRunDemo={runDemoFromNav}
        variant={variant}
      />
      {view === "home" ? <Home navDemoRequest={navDemoRequest} setView={setView} variant={variant} /> : null}
      {view === "legal" ? <Legal setView={setView} /> : null}
    </div>
  );
}
