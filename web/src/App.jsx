import {
  Activity,
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  ChevronDown,
  ShieldCheck,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  API_RETRYING_BACKEND_MESSAGE,
  fetchLegalPage,
  submitAnalyze,
  submitFeedback,
} from "./api.js";
import {
  ANALYSIS_STYLE_OPTIONS,
  CAN_HELP_WITH,
  CANNOT_TELL,
  CONTEXT_OPTIONS,
  GOAL_OPTIONS,
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
const PRIMARY_DEMO_IDS = ["unclear_ask", "pressure_urgency", "repair_opportunity"];
const EXTRA_DEMO_IDS = ["low_signal_fallback", "boundary_respecting_request", "overloaded_message"];

const LEGAL_SLUGS = [
  ["privacy", "Privacy"],
  ["terms", "Terms"],
  ["data-deletion", "Data request/delete"],
  ["match-disclaimer", "Disclaimer"],
];

const FALLBACK_LEGAL = {
  title: "Closed Beta Legal Draft",
  status: "draft_requires_legal_review",
  sections: [
    "Vibe Signal is communication-support only.",
    "Outputs are pattern-based suggestions, not truth claims.",
    "Only submit messages you have permission to analyze.",
    "Privacy and terms drafts require legal review before public launch.",
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

function optionById(options, id) {
  return options.find((option) => option.id === id) || options[0];
}

function presentationNextStep(view, goalId, styleId) {
  const goal = optionById(GOAL_OPTIONS, goalId);
  const engineStep = view.safeNextStep;
  const goalStep = `Goal focus: ${goal.nextStep}`;
  const cautionStep =
    styleId === "careful" || goalId === "over_reading"
      ? "Keep the limits visible before acting."
      : "";

  if (!engineStep) {
    return [goal.nextStep, cautionStep].filter(Boolean).join(" ");
  }

  if (styleId === "quick") {
    return [goalStep, cautionStep].filter(Boolean).join(" ");
  }

  return [engineStep, goalStep, cautionStep].filter(Boolean).join(" ");
}

function TopNav({ onHome, onHowItWorks, onBeta, onPrivacy }) {
  return (
    <header className="top-nav">
      <button className="brand-lockup" type="button" onClick={onHome}>
        <span className="brand-mark">
          <Activity size={18} />
        </span>
        <span>Vibe Signal</span>
      </button>
      <nav className="nav-links" aria-label="Primary">
        <button type="button" onClick={onHome}>Demo</button>
        <button type="button" onClick={onHowItWorks}>How it works</button>
        <button type="button" onClick={onBeta}>Beta</button>
        <button type="button" onClick={onPrivacy}>Privacy</button>
      </nav>
    </header>
  );
}

function SegmentedControl({ label, value, options, onChange }) {
  return (
    <div className="control-group">
      <span className="control-label">{label}</span>
      <div className="segmented-control" role="radiogroup" aria-label={label}>
        {options.map((option) => (
          <button
            aria-checked={value === option.id}
            className={value === option.id ? "active" : ""}
            key={option.id}
            role="radio"
            type="button"
            onClick={() => onChange(option.id)}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}

function ChipSelector({ label, helper, value, options, onChange }) {
  return (
    <div className="control-group">
      <span className="control-label">{label}</span>
      {helper ? <p className="control-helper">{helper}</p> : null}
      <div className="chip-row" role="radiogroup" aria-label={label}>
        {options.map((option) => (
          <button
            aria-checked={value === option.id}
            className={value === option.id ? "selected" : ""}
            key={option.id}
            role="radio"
            type="button"
            onClick={() => onChange(option.id)}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}

function GoalSelector({ value, onChange }) {
  return (
    <section className="goal-panel" aria-labelledby="goal-title">
      <div>
        <h2 id="goal-title">What do you want help with?</h2>
        <p>Goal only shapes wording and suggested next steps. It does not change backend inference.</p>
      </div>
      <div className="goal-grid" role="radiogroup" aria-label="Goal">
        {GOAL_OPTIONS.map((option) => (
          <button
            aria-checked={value === option.id}
            className={value === option.id ? "selected" : ""}
            key={option.id}
            role="radio"
            type="button"
            onClick={() => onChange(option.id)}
          >
            <strong>{option.label}</strong>
            <span>{option.helper}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

function DemoCard({ demo, onRun }) {
  return (
    <article className="demo-card">
      <div>
        <div className="demo-card-header">
          <h3>{demo.title}</h3>
          <span>{demo.previewPattern}</span>
        </div>
        <p className="synthetic-exchange">{demo.exchange}</p>
        <p>{demo.highlight}</p>
      </div>
      <Button tone="secondary" onClick={() => onRun(demo.id)}>
        Run demo <ArrowRight size={16} />
      </Button>
    </article>
  );
}

function DemoMode({ onRunDemo }) {
  const [showMore, setShowMore] = useState(false);
  const primaryDemos = PRIMARY_DEMO_IDS.map((id) => SYNTHETIC_DEMOS.find((demo) => demo.id === id)).filter(Boolean);
  const extraDemos = EXTRA_DEMO_IDS.map((id) => SYNTHETIC_DEMOS.find((demo) => demo.id === id)).filter(Boolean);

  return (
    <section className="mode-panel" aria-labelledby="demo-mode-title">
      <div className="mode-heading">
        <h2 id="demo-mode-title">Demo Mode</h2>
        <p>Try safe synthetic examples first. No private messages needed.</p>
      </div>
      <div className="demo-list">
        {primaryDemos.map((demo) => (
          <DemoCard demo={demo} key={demo.id} onRun={onRunDemo} />
        ))}
      </div>
      <button className="more-examples" type="button" onClick={() => setShowMore((current) => !current)}>
        <ChevronDown size={16} className={showMore ? "rotate" : ""} />
        More examples
      </button>
      {showMore ? (
        <div className="demo-list extra-demo-list">
          {extraDemos.map((demo) => (
            <DemoCard demo={demo} key={demo.id} onRun={onRunDemo} />
          ))}
        </div>
      ) : null}
    </section>
  );
}

function AnalyzeMode({ text, setText, consent, setConsent, loading, onSubmit, error, status }) {
  const canSubmit = normalizeText(text) && consent && !loading;

  return (
    <section className="mode-panel" aria-labelledby="analyze-mode-title">
      <div className="mode-heading">
        <h2 id="analyze-mode-title">Analyze Text</h2>
        <p>Paste only text you have permission to review. Remove names and sensitive details.</p>
      </div>
      <label className="field-label" htmlFor="conversation">Permissioned conversation text</label>
      <p className="field-helper" id="conversation-helper">
        Use one line per message. Prefixing with self: or other: helps keep evidence clear.
      </p>
      <textarea
        aria-describedby="conversation-helper consent-helper"
        id="conversation"
        onChange={(event) => setText(event.target.value)}
        placeholder="self: Can you confirm Friday?&#10;other: maybe later"
        value={text}
      />
      <div className="consent-card" id="consent-helper">
        <ShieldCheck size={18} />
        <p>Only submit messages you have permission to analyze. Remove names, phone numbers, addresses, and sensitive details.</p>
      </div>
      <label className="checkbox-row">
        <input
          checked={consent}
          onChange={(event) => setConsent(event.target.checked)}
          type="checkbox"
        />
        <span>I have permission to review this text.</span>
      </label>
      {error ? (
        <div className="error-banner" role="alert">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      ) : null}
      <div className="form-footer">
        <span aria-live="polite">{status}</span>
        <Button disabled={!canSubmit} onClick={onSubmit}>
          {loading ? "Reviewing..." : "Review observable patterns"}
        </Button>
      </div>
    </section>
  );
}

function EmptyResult({ onRunDemo }) {
  return (
    <section className="result-panel empty-result" aria-label="Result preview">
      <div className="result-header">
        <span className="status-pill">Preview</span>
        <h2>Run a demo to see the result shape.</h2>
      </div>
      <div className="result-section">
        <h3>What stands out</h3>
        <p>Observable wording patterns appear here after a demo or permissioned analysis.</p>
      </div>
      <div className="result-section">
        <h3>Evidence</h3>
        <p>Quoted phrases are shown before interpretation.</p>
      </div>
      <div className="result-section muted-section">
        <h3>Limits</h3>
        <p>Vibe Signal does not read minds or judge people.</p>
      </div>
      <div className="result-section safe-next-card">
        <h3>Safer next step</h3>
        <p>One lower-pressure option appears here.</p>
      </div>
      <Button onClick={onRunDemo}>Run a safe demo <ArrowRight size={16} /></Button>
    </section>
  );
}

function ResultPanel({ result, goalId, contextId, styleId, onRunDemo }) {
  const view = useMemo(() => (result ? buildTrustFirstResultView(result) : null), [result]);
  const [feedbackConsent, setFeedbackConsent] = useState(false);
  const [feedbackStatus, setFeedbackStatus] = useState("");
  const [feedbackError, setFeedbackError] = useState("");
  const [submittedFeedback, setSubmittedFeedback] = useState([]);

  if (!view) {
    return <EmptyResult onRunDemo={onRunDemo} />;
  }

  const goal = optionById(GOAL_OPTIONS, goalId);
  const context = optionById(CONTEXT_OPTIONS, contextId);
  const style = optionById(ANALYSIS_STYLE_OPTIONS, styleId);
  const safeNextStep = presentationNextStep(view, goalId, styleId);

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
          ? "Feedback could not be stored. Please try again in a moment."
          : "Feedback storage requires explicit consent."
      );
    }
  }

  if (view.isLowSignal) {
    return (
      <section className="result-panel low-signal-result" aria-label="Low-signal result">
        <div className="result-header">
          <span className="status-pill warning">Low signal</span>
          <h2>Not enough context to read safely.</h2>
          <p>This message is too short or context-light. Add context or try a synthetic demo.</p>
        </div>
        <div className="result-section">
          <h3>Try</h3>
          <ul>
            {view.tryItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className="result-section safe-next-card">
          <h3>Safer next step</h3>
          <p>{safeNextStep}</p>
        </div>
        <Button onClick={onRunDemo}>Try a synthetic demo <ArrowRight size={16} /></Button>
      </section>
    );
  }

  const evidenceRows = styleId === "quick" ? view.evidenceDetails.slice(0, 2) : view.evidenceDetails;

  return (
    <section className="result-panel" aria-label="Vibe Signal result">
      <div className="result-header">
        <div className="signal-strength-block">
          <span className="micro-label">Signal strength</span>
          <span className="status-pill">{view.signalStrengthLabel}</span>
        </div>
        <p className="result-context">
          Goal: {goal.label} · Context: {context.label} · Style: {style.label}
        </p>
      </div>
      <div className="result-section">
        <h3>What stands out</h3>
        <p>{view.mainRead}</p>
      </div>
      <div className="result-section">
        <h3>Evidence</h3>
        <div className="evidence-list">
          {evidenceRows.map((row) => (
            <article className="evidence-detail" key={row.id}>
              <span>{row.family}</span>
              <strong>“{row.phrase}”</strong>
              {styleId !== "quick" && row.explanation ? <p>{row.explanation}</p> : null}
            </article>
          ))}
        </div>
      </div>
      <div className="result-section">
        <h3>Pattern</h3>
        <div className="pattern-chip-row">
          {view.patternLabels.map((label) => (
            <span key={label}>{label}</span>
          ))}
        </div>
        {styleId === "evidence" || styleId === "careful" ? <p>{view.patternExplanation}</p> : null}
      </div>
      <div className="result-section muted-section">
        <h3>What this cannot tell you</h3>
        <p>{view.cannotInferText}</p>
      </div>
      <div className="result-section safe-next-card">
        <h3>Safer next step</h3>
        <p>{safeNextStep}</p>
      </div>
      <section className="feedback-panel">
        <div>
          <h3>Metadata-only feedback</h3>
          <p>No free-text comment or message text is sent.</p>
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
              className={submittedFeedback.includes(option.id) ? "feedback-option-selected" : ""}
              disabled={!feedbackConsent || !view.matchId || submittedFeedback.includes(option.id)}
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

function HowItWorks() {
  return (
    <section className="support-section" id="how-it-works" aria-labelledby="how-title">
      <div className="section-heading">
        <h2 id="how-title">How it works</h2>
        <p>A short, evidence-first flow that keeps agency with the user.</p>
      </div>
      <div className="info-grid">
        {HOW_IT_WORKS_STEPS.map((step) => (
          <article key={step.title}>
            <h3>{step.title}</h3>
            <p>{step.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function BoundarySection() {
  return (
    <section className="boundary-section" aria-label="Can and cannot">
      <article>
        <h2>Can help with</h2>
        <ul>
          {CAN_HELP_WITH.slice(0, 4).map((item) => <li key={item}>{item}</li>)}
        </ul>
      </article>
      <article>
        <h2>Cannot tell you</h2>
        <ul>
          {CANNOT_TELL.slice(0, 5).map((item) => <li key={item}>{item}</li>)}
        </ul>
      </article>
    </section>
  );
}

function Footer({ onPrivacy }) {
  return (
    <footer className="footer">
      <span>Vibe Signal is closed-beta communication support. Human review gates remain human.</span>
      <div>
        <button type="button" onClick={onPrivacy}>Privacy</button>
        <button type="button" onClick={onPrivacy}>Terms</button>
        <button type="button" onClick={onPrivacy}>Support</button>
        <button type="button" onClick={onPrivacy}>Data request/delete</button>
      </div>
    </footer>
  );
}

function Home({ setView }) {
  const [goalId, setGoalId] = useState(GOAL_OPTIONS[0].id);
  const [mode, setMode] = useState("demo");
  const [contextId, setContextId] = useState("general");
  const [styleId, setStyleId] = useState("evidence");
  const [text, setText] = useState(SAMPLE_TEXT);
  const [consent, setConsent] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const selectedStyle = optionById(ANALYSIS_STYLE_OPTIONS, styleId);
  const status = !normalizeText(text)
    ? "Add a short exchange, or run a synthetic demo first."
    : !consent
      ? "Private analysis unlocks after the permission checkbox."
      : loading
        ? "Reviewing observable patterns..."
        : "Ready to review permissioned text.";

  function runSyntheticDemo(demoId = PRIMARY_DEMO_IDS[0]) {
    setResult(buildSyntheticResult(demoId));
    setError("");
  }

  async function handleAnalyzeSubmit() {
    if (!normalizeText(text)) {
      setError("Add a short exchange, or run a synthetic demo first.");
      return;
    }
    if (!consent) {
      setError("Confirm permission before private text analysis.");
      return;
    }
    if (isContextLightInput(text)) {
      setResult({
        ...buildLowSignalFallback(text),
        match_id: "local_low_signal",
        low_signal_fallback: true,
      });
      setError("");
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
    } catch (_requestError) {
      setError("The backend may be waking up. Please try again in a moment.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <section className="hero" aria-labelledby="hero-title">
        <div>
          <h1 id="hero-title">{HERO_COPY.title}</h1>
          <p>{HERO_COPY.subtitle}</p>
        </div>
        <p className="trust-line">{HERO_COPY.trustNote}</p>
      </section>

      <GoalSelector value={goalId} onChange={setGoalId} />

      <section className="product-workspace" aria-label="Demo and analysis workspace">
        <div className="workspace-left">
          <SegmentedControl
            label="Mode"
            value={mode}
            options={[
              { id: "demo", label: "Demo Mode" },
              { id: "analyze", label: "Analyze Text" },
            ]}
            onChange={setMode}
          />
          <ChipSelector
            helper="Context only adjusts caution and wording. It does not infer intent."
            label="What kind of exchange is this?"
            onChange={setContextId}
            options={CONTEXT_OPTIONS}
            value={contextId}
          />
          <div className="control-group">
            <span className="control-label">Analysis style</span>
            <div className="style-grid" role="radiogroup" aria-label="Analysis style">
              {ANALYSIS_STYLE_OPTIONS.map((option) => (
                <button
                  aria-checked={styleId === option.id}
                  className={styleId === option.id ? "selected" : ""}
                  key={option.id}
                  role="radio"
                  type="button"
                  onClick={() => setStyleId(option.id)}
                >
                  <strong>{option.label}</strong>
                  <span>{option.description}</span>
                </button>
              ))}
            </div>
            <p className="control-helper">{selectedStyle.description}</p>
          </div>

          {mode === "demo" ? (
            <DemoMode onRunDemo={runSyntheticDemo} />
          ) : (
            <AnalyzeMode
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
            />
          )}
        </div>
        <div className="workspace-right">
          <ResultPanel
            contextId={contextId}
            goalId={goalId}
            onRunDemo={() => runSyntheticDemo(PRIMARY_DEMO_IDS[0])}
            result={result}
            styleId={styleId}
          />
        </div>
      </section>

      <section className="trust-strip" aria-label="Trust boundaries">
        {TRUST_STRIP_ITEMS.map((item) => <span key={item}>{item}</span>)}
      </section>

      <HowItWorks />
      <BoundarySection />
      <Footer onPrivacy={() => setView("legal")} />
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

function Beta({ setView }) {
  return (
    <main className="page narrow-page">
      <button className="back-link" type="button" onClick={() => setView("home")}>Back</button>
      <section className="surface beta-surface">
        <CheckCircle2 size={22} />
        <h1>Closed beta</h1>
        <p>
          Tester invites remain blocked until legal/privacy review, real-device QA, and human gates
          are complete.
        </p>
        <Button disabled>Beta request fields not submitted in this build</Button>
      </section>
    </main>
  );
}

export default function App() {
  const [view, setView] = useState("home");

  function goToHowItWorks() {
    setView("home");
    window.setTimeout(() => {
      document.getElementById("how-it-works")?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 0);
  }

  return (
    <div className="app-shell">
      <TopNav
        onBeta={() => setView("beta")}
        onHome={() => setView("home")}
        onHowItWorks={goToHowItWorks}
        onPrivacy={() => setView("legal")}
      />
      {view === "home" ? <Home setView={setView} /> : null}
      {view === "legal" ? <Legal setView={setView} /> : null}
      {view === "beta" ? <Beta setView={setView} /> : null}
    </div>
  );
}
