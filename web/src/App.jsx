import {
  Activity,
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  ChevronDown,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import {
  ANALYZE_INPUT_LIMIT_MESSAGE,
  API_RETRYING_BACKEND_MESSAGE,
  fetchLegalPage,
  MAX_ANALYZE_INPUT_CHARS,
  submitAnalyze,
  submitFeedback,
} from "./api.js";
import {
  HERO_COPY,
  HOW_IT_WORKS_STEPS,
  PROOF_CARDS,
  SYNTHETIC_DEMO_PATH_STEPS,
  SYNTHETIC_DEMOS,
  TECHNICAL_DEMO_FLOW,
  TECHNICAL_DEMO_NON_CLAIMS,
  TECHNICAL_DEMO_SHIPPED,
  TRUST_STRIP_ITEMS,
} from "./trustContent.js";
import { buildFeedbackMetadata } from "./guidedInteraction.js";
import {
  getLocalLegalPage,
  isValidLegalPage,
  LEGAL_SLUGS,
} from "./legalContent.js";
import {
  buildLowSignalFallback,
  buildSyntheticResult,
  buildTrustFirstResultView,
  FEEDBACK_OPTIONS,
  isContextLightInput,
} from "./resultViewModel.js";

const FEATURED_DEMO_ID = "unclear_ask";
const BACKEND_RETRY_COPY =
  API_RETRYING_BACKEND_MESSAGE || "The backend may be waking up. Trying once more...";

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

function TopNav({ onRunDemo, onOpenLegal }) {
  return (
    <header className="top-nav">
      <button className="brand-lockup" type="button" onClick={() => scrollToId("top")}>
        <span className="brand-mark" aria-hidden="true">
          <Activity size={18} />
        </span>
        <span>Vibe Signal</span>
      </button>
      <nav className="nav-links" aria-label="Primary">
        <button type="button" onClick={() => scrollToId("demo")}>Demo</button>
        <button type="button" onClick={() => scrollToId("technical-demo")}>2 minute demo</button>
        <button type="button" onClick={() => scrollToId("analyze")}>Analyze</button>
        <button type="button" onClick={() => onOpenLegal("privacy")}>Privacy</button>
        <Button className="nav-cta" onClick={onRunDemo}>
          Run synthetic demo
        </Button>
      </nav>
    </header>
  );
}

function Hero({ onRunDemo }) {
  return (
    <section className="hero" id="top" aria-labelledby="hero-title">
      <div className="hero-copy">
        <p className="section-kicker">Scanner beta</p>
        <h1 id="hero-title">{HERO_COPY.title}</h1>
        <p>{HERO_COPY.subtitle}</p>
        <div className="hero-actions" aria-label="Primary actions">
          <Button onClick={onRunDemo}>
            {HERO_COPY.primaryCta}
            <ArrowRight size={17} />
          </Button>
          <Button tone="secondary" onClick={() => scrollToId("analyze")}>
            {HERO_COPY.secondaryCta}
          </Button>
        </div>
        <p className="trust-line">{HERO_COPY.trustNote}</p>
      </div>
      <ScannerPreview />
    </section>
  );
}

function ScannerPreview() {
  const demo = SYNTHETIC_DEMOS.find((item) => item.id === FEATURED_DEMO_ID) || SYNTHETIC_DEMOS[0];
  const lines = demo.exchange.split("\n").slice(0, 3);

  return (
    <aside className="scanner-preview" aria-label="Scanner preview">
      <div className="scanner-preview-header">
        <span className="scanner-dot" aria-hidden="true" />
        <span>Evidence scan</span>
      </div>
      <div className="scan-window">
        <div className="scan-line" aria-hidden="true" />
        {lines.map((line) => (
          <p className={line.startsWith("self:") ? "message-row self" : "message-row"} key={line}>
            {line}
          </p>
        ))}
      </div>
      <ul className="trust-strip" aria-label="Product boundaries">
        {TRUST_STRIP_ITEMS.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </aside>
  );
}

function ProofCards() {
  return (
    <section className="proof-grid" aria-label="Product proof points">
      {PROOF_CARDS.map((card) => (
        <article key={card.title}>
          <h2>{card.title}</h2>
          <p>{card.body}</p>
        </article>
      ))}
    </section>
  );
}

function DemoCard({ onRunDemo }) {
  const featured = SYNTHETIC_DEMOS.find((item) => item.id === FEATURED_DEMO_ID) || SYNTHETIC_DEMOS[0];
  const extraDemos = SYNTHETIC_DEMOS.filter((item) => item.id !== featured.id).slice(0, 4);

  return (
    <section className="panel demo-card" id="demo" aria-labelledby="demo-title">
      <div className="panel-heading">
        <p className="section-kicker">Synthetic demo</p>
        <h2 id="demo-title">{featured.title}</h2>
        <p>{featured.highlight}</p>
      </div>
      <div className="message-sample" aria-label="Synthetic example text">
        {featured.exchange.split("\n").map((line) => (
          <p className={line.startsWith("self:") ? "message-row self" : "message-row"} key={line}>
            {line}
          </p>
        ))}
      </div>
      <Button onClick={() => onRunDemo(featured.id)}>
        {featured.actionLabel}
        <ArrowRight size={17} />
      </Button>
      <p className="quiet-copy">
        This first run uses a synthetic exchange, so it does not require private-message consent.
      </p>
      <div className="demo-path" aria-label="Synthetic demo path">
        <h3>Try the synthetic demo first.</h3>
        <ol>
          {SYNTHETIC_DEMO_PATH_STEPS.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </div>
      <details className="example-disclosure">
        <summary>
          More synthetic examples
          <ChevronDown size={16} />
        </summary>
        <div className="demo-options">
          {extraDemos.map((item) => (
            <button key={item.id} type="button" onClick={() => onRunDemo(item.id)}>
              <span>{item.title}</span>
              <small>{item.previewPattern}</small>
            </button>
          ))}
        </div>
      </details>
    </section>
  );
}

function TechnicalDemoSection({ onRunDemo }) {
  return (
    <section className="panel technical-demo" id="technical-demo" aria-labelledby="technical-demo-title">
      <div className="panel-heading">
        <p className="section-kicker">Reviewer walkthrough</p>
        <h2 id="technical-demo-title">Vibe Signal - 2 Minute Technical Demo</h2>
        <p>
          A compact reviewer path through the product problem, shipped surface, architecture, caveats,
          and non-claims.
        </p>
      </div>
      <div className="technical-demo-grid">
        <section aria-labelledby="problem-title">
          <h3 id="problem-title">Product problem</h3>
          <p>
            People paste messy communication into generic LLMs and get unsafe, overconfident
            interpretations. Vibe Signal gives bounded, evidence-backed communication cues instead.
          </p>
        </section>
        <section aria-labelledby="shipped-title">
          <h3 id="shipped-title">What shipped</h3>
          <ul>
            {TECHNICAL_DEMO_SHIPPED.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
        <section aria-labelledby="architecture-title">
          <h3 id="architecture-title">Architecture</h3>
          <ol className="flow-list">
            {TECHNICAL_DEMO_FLOW.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </section>
        <section aria-labelledby="demo-caveat-title">
          <h3 id="demo-caveat-title">Demo caveat</h3>
          <p>
            Synthetic demo examples are for product demonstration, regression checks, and coverage
            only. They are not real-world accuracy claims.
          </p>
        </section>
        <section aria-labelledby="non-claims-title">
          <h3 id="non-claims-title">What it does not claim</h3>
          <ul>
            {TECHNICAL_DEMO_NON_CLAIMS.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
      </div>
      <div className="reviewer-actions" aria-label="Reviewer links">
        <Button onClick={onRunDemo}>
          Run synthetic demo
          <ArrowRight size={17} />
        </Button>
        <a className="button button-secondary" href="https://github.com/keithtgrehan/vibe-signal">
          View GitHub repo
        </a>
        <a
          className="button button-secondary"
          href="https://github.com/keithtgrehan/vibe-signal/blob/main/docs/recruiter_readiness/project_summary.md"
        >
          Read project summary
        </a>
        <a
          className="button button-secondary"
          href="https://github.com/keithtgrehan/vibe-signal/blob/main/docs/recruiter_readiness/repo_tour.md"
        >
          Read repo tour
        </a>
      </div>
    </section>
  );
}

function ConsentGate({ consent, setConsent }) {
  return (
    <label className="checkbox-row consent-gate" id="consent-copy">
      <input
        checked={consent}
        onChange={(event) => setConsent(event.target.checked)}
        type="checkbox"
      />
      <span>I have permission to analyze this text and understand the limits.</span>
    </label>
  );
}

function AnalyzePanel({
  text,
  setText,
  consent,
  setConsent,
  loading,
  error,
  status,
  onSubmit,
  onCancel,
}) {
  const inputLength = normalizeText(text).length;
  const inputTooLong = inputLength > MAX_ANALYZE_INPUT_CHARS;
  const canSubmit = normalizeText(text) && consent && !loading && !inputTooLong;
  const canRetry = Boolean(normalizeText(text)) && consent && !loading && !inputTooLong;

  return (
    <section className="panel analyze-panel" id="analyze" aria-labelledby="analyze-title">
      <div className="panel-heading">
        <p className="section-kicker">Private input</p>
        <h2 id="analyze-title">Analyze text with consent</h2>
        <p>Only paste text you have permission to use. Remove names and sensitive details first.</p>
      </div>
      <label className="field-label" htmlFor="conversation">Message text</label>
      <textarea
        aria-describedby="analyze-helper analyze-limit-helper consent-copy"
        aria-invalid={inputTooLong ? "true" : "false"}
        id="conversation"
        onChange={(event) => setText(event.target.value)}
        placeholder="self: Are we still on for Friday?&#10;other: maybe later, not sure yet"
        value={text}
      />
      <ConsentGate consent={consent} setConsent={setConsent} />
      <p className="helper-copy" id="analyze-helper">
        Vibe Signal reviews wording cues only. It does not decide what happened or what someone meant.
      </p>
      <p
        className={`helper-copy ${inputTooLong ? "limit-warning" : ""}`.trim()}
        id="analyze-limit-helper"
      >
        {inputTooLong
          ? ANALYZE_INPUT_LIMIT_MESSAGE
          : `Short excerpts work best. ${inputLength}/${MAX_ANALYZE_INPUT_CHARS} characters.`}
      </p>
      {error ? (
        <div className="error-banner" role="alert">
          <AlertCircle size={18} />
          <span>{error}</span>
          {canRetry ? (
            <Button className="inline-error-action" tone="secondary" onClick={onSubmit}>
              Try again
            </Button>
          ) : null}
        </div>
      ) : null}
      <div className="form-footer">
        <span aria-live="polite">{status}</span>
        <div className="form-actions">
          {loading ? (
            <Button tone="secondary" onClick={onCancel}>
              Cancel
            </Button>
          ) : null}
          <Button disabled={!canSubmit} onClick={onSubmit}>
            {loading ? "Scanning..." : "Analyze"}
          </Button>
        </div>
      </div>
    </section>
  );
}

function ScanningState({ status = "Reading the wording..." }) {
  const steps = [
    "Mapping clarity and ambiguity",
    "Checking pressure and reassurance cues",
    "Finding repair openings",
  ];

  return (
    <section className="scanner-result-shell scanning-state" aria-label="Scanning state">
      <div className="radar" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
      <div className="panel-heading">
        <p className="section-kicker">Scanning</p>
        <h2>Scanning the wording</h2>
        <p aria-live="polite">{status}</p>
      </div>
      <ul className="scan-steps">
        {steps.map((step) => (
          <li key={step}>{step}</li>
        ))}
      </ul>
    </section>
  );
}

function EmptyResult({ onRunDemo }) {
  return (
    <section className="scanner-result-shell empty-result" aria-label="Result preview">
      <p className="section-kicker">Evidence-first result</p>
      <h2>Run the synthetic demo first.</h2>
      <p>
        The result will show evidence phrases, possible patterns, a safer reply, and clear limits.
      </p>
      <Button onClick={onRunDemo}>
        Run synthetic demo
        <ArrowRight size={17} />
      </Button>
    </section>
  );
}

function ResultPanel({ loading, result, scanStatus, onRunDemo }) {
  const view = useMemo(() => (result ? buildTrustFirstResultView(result) : null), [result]);

  if (loading) {
    return <ScanningState status={scanStatus} />;
  }

  if (!view) {
    return <EmptyResult onRunDemo={onRunDemo} />;
  }

  const interpretation = view.isLowSignal
    ? "There is not enough wording to read safely yet."
    : view.interpretation || view.patternExplanation || view.mainRead;

  return (
    <section className="scanner-result-shell" aria-label="Vibe Signal result">
      <div className="result-hero-card">
        <p className="section-kicker">{view.synthetic ? "Synthetic result" : "Evidence-first result"}</p>
        <h2>{view.isLowSignal ? view.title : view.mainRead}</h2>
        <p>{view.disclosure || "Evidence from the words shown appears before any possible pattern."}</p>
      </div>
      <SignalBreakdown view={view} />
      <EvidenceList rows={view.evidenceDetails} />
      <section className="result-section" aria-labelledby="meaning-title">
        <h3 id="meaning-title">What it could mean</h3>
        <p>{interpretation}</p>
      </section>
      <SafeReplyCard nextStep={view.safeNextStep} />
      <ComfortLoopCard />
      <LimitsCard view={view} />
      <FeedbackPanel view={view} />
    </section>
  );
}

function SignalBreakdown({ view }) {
  const rows = view.evidenceDetails.length
    ? view.evidenceDetails
    : view.contextSuggestions.map((item, index) => ({
        id: `context_${index}`,
        family: item,
        qualityLabel: "Insufficient",
        qualityDescription: "More context is needed.",
      }));

  return (
    <section className="result-section" aria-labelledby="signal-title">
      <div className="section-title-row">
        <h3 id="signal-title">Signal / cue breakdown</h3>
        <span>{view.evidenceQualitySummary || "mixed"}</span>
      </div>
      <div className="cue-list">
        {rows.slice(0, 4).map((row) => (
          <article key={row.id}>
            <div>
              <strong>{row.family}</strong>
              <small>{row.qualityLabel}: {row.qualityDescription}</small>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function EvidenceList({ rows }) {
  return (
    <section className="result-section" aria-labelledby="evidence-title">
      <h3 id="evidence-title">Evidence phrase list</h3>
      {rows.length ? (
        <ul className="evidence-list">
          {rows.slice(0, 5).map((row) => (
            <li key={row.id}>
              <span>{row.phrase}</span>
              {row.explanation ? <p>{row.explanation}</p> : null}
            </li>
          ))}
        </ul>
      ) : (
        <p>Add a little more context so there is wording to quote.</p>
      )}
    </section>
  );
}

function SafeReplyCard({ nextStep }) {
  return (
    <section className="safe-reply-card" aria-labelledby="reply-title">
      <p className="section-kicker">Repair opening</p>
      <h3 id="reply-title">Safer reply</h3>
      <p>{nextStep || "Ask one clear follow-up and leave room for a later answer."}</p>
      <small>Use this as a draft. Edit before sending.</small>
    </section>
  );
}

function ComfortLoopCard() {
  const actions = [
    {
      id: "clearer-reply",
      label: "Try a clearer reply",
      detail: "Keep one ask, one timeframe, and room for the other person to answer later.",
    },
    {
      id: "compare-rewrite",
      label: "Compare this rewrite",
      detail: "Check whether the draft lowers pressure while preserving what you need to say.",
    },
    {
      id: "more-context",
      label: "Need more context?",
      detail: "Add the previous message or the later reply before treating a pattern as useful.",
    },
    {
      id: "copy-what-helps",
      label: "Copy what helps",
      detail: "Use only the words that fit your situation. Edit before sending.",
    },
  ];
  const [selectedAction, setSelectedAction] = useState(actions[0]);

  return (
    <section className="comfort-loop-card" aria-labelledby="comfort-loop-title">
      <p className="section-kicker">Next small step</p>
      <h3 id="comfort-loop-title">Stay oriented before you act.</h3>
      <p>No result is a verdict. Pick the next useful step, then check the limits below.</p>
      <div className="comfort-actions" aria-label="Helpful next-step options">
        {actions.map((action) => (
          <button
            className={selectedAction.id === action.id ? "active" : ""}
            key={action.id}
            type="button"
            onClick={() => setSelectedAction(action)}
          >
            {action.label}
          </button>
        ))}
      </div>
      <p className="comfort-detail" role="status">{selectedAction.detail}</p>
    </section>
  );
}

function LimitsCard({ view }) {
  return (
    <section className="limits-card" aria-labelledby="limits-title">
      <p className="section-kicker">Limits / cannot infer</p>
      <h3 id="limits-title">Limits / cannot infer</h3>
      <p>{view.cannotInferText}</p>
      <div className="limit-pills" aria-label="Cannot infer">
        {view.cannotTell.map((item) => (
          <span key={item}>{item}</span>
        ))}
      </div>
    </section>
  );
}

function FeedbackPanel({ view }) {
  const [feedbackConsent, setFeedbackConsent] = useState(false);
  const [feedbackStatus, setFeedbackStatus] = useState("");
  const [feedbackError, setFeedbackError] = useState("");
  const [submittedFeedback, setSubmittedFeedback] = useState([]);

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
      goalId: "scanner_ui",
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
    <section className="feedback-panel" aria-labelledby="feedback-title">
      <div>
        <h3 id="feedback-title">Metadata-only feedback</h3>
        <p>Feedback stores result metadata only, never message text.</p>
      </div>
      <label className="checkbox-row compact">
        <input
          checked={feedbackConsent}
          onChange={(event) => setFeedbackConsent(event.target.checked)}
          type="checkbox"
        />
        <span>I agree to send metadata-only result feedback.</span>
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
  );
}

function HowItWorks() {
  return (
    <section className="panel how-section" aria-labelledby="how-title">
      <div className="panel-heading">
        <p className="section-kicker">How it works</p>
        <h2 id="how-title">Evidence first, then a safer next step.</h2>
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

function BetaGuidance({ onOpenLegal }) {
  const guidanceItems = [
    "Use the synthetic demo first.",
    "Only paste short text you have permission to analyze.",
    "Do not paste sensitive details, secrets, or private third-party content without permission.",
    "Vibe Signal does not know intent, attraction, truthfulness, diagnosis, or outcomes.",
    "Report unsafe or confusing output through metadata-only feedback.",
  ];

  return (
    <section className="panel beta-guidance" aria-labelledby="beta-guidance-title">
      <div className="panel-heading">
        <p className="section-kicker">Closed beta</p>
        <h2 id="beta-guidance-title">Beta tester notes</h2>
        <p>Use Vibe Signal for communication clarity, not professional advice or certainty.</p>
      </div>
      <ul>
        {guidanceItems.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
      <button type="button" onClick={() => onOpenLegal("data-request")}>
        Data request/delete
      </button>
    </section>
  );
}

function TrustFooter({ onOpenLegal }) {
  return (
    <footer className="trust-footer">
      <p>Vibe Signal does not know intent, attraction, truthfulness, diagnosis, or outcomes.</p>
      <div>
        {LEGAL_SLUGS.map(([slug, label]) => (
          <button key={slug} type="button" onClick={() => onOpenLegal(slug)}>
            {label}
          </button>
        ))}
      </div>
    </footer>
  );
}

function Home({ navDemoRequest, onOpenLegal }) {
  const [text, setText] = useState("");
  const [consent, setConsent] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [scanStatus, setScanStatus] = useState("Ready to scan wording cues.");
  const analyzeAbortRef = useRef(null);
  const analyzeRunRef = useRef(0);

  const hasText = normalizeText(text);
  const inputTooLong = hasText.length > MAX_ANALYZE_INPUT_CHARS;
  const status = !hasText
    ? "Run the synthetic demo first, or add text with consent."
    : inputTooLong
      ? ANALYZE_INPUT_LIMIT_MESSAGE
    : !consent
      ? "Check the consent box before analyzing private text."
      : loading
        ? scanStatus
        : "Ready to analyze.";

  function runSyntheticDemo(demoId = FEATURED_DEMO_ID) {
    analyzeRunRef.current += 1;
    analyzeAbortRef.current?.abort();
    analyzeAbortRef.current = null;
    setResult(buildSyntheticResult(demoId));
    setLoading(false);
    setError("");
    setScanStatus("Synthetic result ready.");
    window.setTimeout(() => scrollToId("demo"), 0);
  }

  useEffect(() => {
    if (navDemoRequest > 0) {
      runSyntheticDemo();
    }
  }, [navDemoRequest]);

  useEffect(() => () => analyzeAbortRef.current?.abort(), []);

  function handleCancelAnalyze() {
    if (!loading) {
      return;
    }
    analyzeRunRef.current += 1;
    analyzeAbortRef.current?.abort();
    analyzeAbortRef.current = null;
    setLoading(false);
    setError("Analysis cancelled.");
    setScanStatus("Analysis cancelled.");
  }

  async function handleAnalyzeSubmit() {
    if (!normalizeText(text)) {
      setError("Add a short exchange, or run the synthetic demo first.");
      return;
    }
    if (inputTooLong) {
      setError(ANALYZE_INPUT_LIMIT_MESSAGE);
      setScanStatus("Shorten the excerpt before analyzing.");
      return;
    }
    if (!consent) {
      setError("Check the consent box before analyzing private text.");
      return;
    }
    if (isContextLightInput(text)) {
      setResult({
        ...buildLowSignalFallback(text),
        match_id: "local_low_signal",
        low_signal_fallback: true,
      });
      setError("");
      setScanStatus("Local low-signal fallback ready.");
      window.setTimeout(() => scrollToId("demo"), 0);
      return;
    }

    const runId = analyzeRunRef.current + 1;
    const controller = new AbortController();
    analyzeRunRef.current = runId;
    analyzeAbortRef.current = controller;
    setLoading(true);
    setResult(null);
    setError("");
    setScanStatus("Reading the wording...");
    try {
      const payload = await submitAnalyze(text, {
        signal: controller.signal,
        onRetry: (retryState) => {
          if (retryState?.classification === "backend_waking") {
            setScanStatus(BACKEND_RETRY_COPY);
          }
        },
      });
      if (analyzeRunRef.current !== runId) {
        return;
      }
      setResult(payload);
      setError("");
      setScanStatus("Result ready.");
      window.setTimeout(() => scrollToId("demo"), 0);
    } catch (requestError) {
      if (analyzeRunRef.current !== runId) {
        return;
      }
      setError(
        requestError?.message ||
          "The backend could not complete the analysis. Try the synthetic demo or try again in a moment."
      );
      setScanStatus("Analysis paused.");
    } finally {
      if (analyzeRunRef.current === runId) {
        setLoading(false);
        analyzeAbortRef.current = null;
      }
    }
  }

  return (
    <main className="page">
      <Hero onRunDemo={() => runSyntheticDemo()} />
      <ProofCards />
      <section className="scanner-workspace" aria-label="Demo, analysis, and result">
        <div className="left-stack">
          <DemoCard onRunDemo={runSyntheticDemo} />
          <AnalyzePanel
            consent={consent}
            error={error}
            loading={loading}
            onCancel={handleCancelAnalyze}
            onSubmit={handleAnalyzeSubmit}
            setConsent={setConsent}
            setText={(value) => {
              setText(value);
              setError("");
            }}
            status={status}
            text={text}
          />
          <HowItWorks />
        </div>
        <ResultPanel
          loading={loading}
          onRunDemo={() => runSyntheticDemo()}
          result={result}
          scanStatus={scanStatus}
        />
      </section>
      <TechnicalDemoSection onRunDemo={() => runSyntheticDemo()} />
      <BetaGuidance onOpenLegal={onOpenLegal} />
      <TrustFooter onOpenLegal={onOpenLegal} />
    </main>
  );
}

function Legal({ initialSlug, setView }) {
  const [slug, setSlug] = useState(initialSlug || "privacy");
  const [page, setPage] = useState(() => getLocalLegalPage(initialSlug || "privacy"));
  const legalGroups = Array.isArray(page.groups) ? page.groups : [];
  const legalSections = Array.isArray(page.sections) ? page.sections : [];

  useEffect(() => {
    const nextSlug = initialSlug || "privacy";
    setSlug(nextSlug);
    setPage(getLocalLegalPage(nextSlug));
  }, [initialSlug]);

  useEffect(() => {
    let cancelled = false;
    const localPage = getLocalLegalPage(slug);
    setPage(localPage);

    async function load() {
      try {
        const payload = await fetchLegalPage(slug);
        if (!cancelled && isValidLegalPage(payload)) {
          setPage(payload);
        }
      } catch (_requestError) {
        if (import.meta.env?.DEV) {
          console.warn("Legal draft API unavailable; using bundled legal copy.");
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
      <section className="panel legal-surface">
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
        {page.intro ? <p className="legal-intro">{page.intro}</p> : null}
        {legalGroups.length > 0 ? (
          <div className="legal-section-list">
            {legalGroups.map((group) => (
              <section className="legal-group" key={group.heading || JSON.stringify(group)}>
                <h2>{group.heading}</h2>
                <ul>
                  {(Array.isArray(group.items) ? group.items : []).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </section>
            ))}
          </div>
        ) : (
          <div className="legal-list">
            {legalSections.map((section) => <p key={section}>{section}</p>)}
          </div>
        )}
      </section>
    </main>
  );
}

export default function App() {
  const [view, setView] = useState("home");
  const [legalSlug, setLegalSlug] = useState("privacy");
  const [navDemoRequest, setNavDemoRequest] = useState(0);

  function openLegal(slug = "privacy") {
    setLegalSlug(slug);
    setView("legal");
  }

  function runDemoFromNav() {
    setView("home");
    setNavDemoRequest((current) => current + 1);
  }

  return (
    <div className="app-shell">
      <TopNav
        onOpenLegal={openLegal}
        onRunDemo={runDemoFromNav}
      />
      {view === "home" ? <Home navDemoRequest={navDemoRequest} onOpenLegal={openLegal} /> : null}
      {view === "legal" ? <Legal initialSlug={legalSlug} setView={setView} /> : null}
    </div>
  );
}
