import {
  Activity,
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  ChevronDown,
  Copy,
  RotateCcw,
  Scissors,
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
  REPLY_ACTIONS,
  buildComparisonResult,
  buildDraftReplyOptions,
  buildFeedbackMetadata,
  goalAwareNextStep,
  redactIdentifyingDetails,
} from "./guidedInteraction.js";
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

function AnalyzeMode({
  text,
  setText,
  consent,
  setConsent,
  loading,
  onSubmit,
  error,
  status,
  compareEnabled,
  setCompareEnabled,
  earlierText,
  setEarlierText,
  laterText,
  setLaterText,
  onRedact,
  onUndoRedaction,
  redactionStatus,
  canUndoRedaction,
}) {
  const hasText = compareEnabled
    ? normalizeText(earlierText) && normalizeText(laterText)
    : normalizeText(text);
  const canSubmit = hasText && consent && !loading;

  return (
    <section className="mode-panel" aria-labelledby="analyze-mode-title">
      <div className="mode-heading">
        <h2 id="analyze-mode-title">Analyze Text</h2>
        <p>Paste only text you have permission to review. Remove names and sensitive details.</p>
      </div>
      <label className="checkbox-row compare-toggle">
        <input
          checked={compareEnabled}
          onChange={(event) => setCompareEnabled(event.target.checked)}
          type="checkbox"
        />
        <span>Compare two snippets</span>
      </label>
      <div className="redaction-toolbar">
        <div>
          <strong>Remove identifying details</strong>
          <p>Helps remove obvious identifiers. This runs in your browser before analysis.</p>
        </div>
        <div className="redaction-actions">
          <Button tone="secondary" onClick={onRedact}>
            <Scissors size={16} />
            Remove identifying details
          </Button>
          <Button disabled={!canUndoRedaction} tone="secondary" onClick={onUndoRedaction}>
            <RotateCcw size={16} />
            Undo
          </Button>
        </div>
      </div>
      {redactionStatus ? <p className="status-text" role="status">{redactionStatus}</p> : null}
      {compareEnabled ? (
        <div className="comparison-fields">
          <div>
            <label className="field-label" htmlFor="conversation-earlier">Earlier message</label>
            <p className="field-helper" id="comparison-earlier-helper">
              Use observable wording from the earlier snippet only.
            </p>
            <textarea
              aria-describedby="comparison-earlier-helper consent-helper"
              id="conversation-earlier"
              onChange={(event) => setEarlierText(event.target.value)}
              placeholder="other: Friday at 7 works."
              value={earlierText}
            />
          </div>
          <div>
            <label className="field-label" htmlFor="conversation-later">Later message</label>
            <p className="field-helper" id="comparison-later-helper">
              Use observable wording from the later snippet only.
            </p>
            <textarea
              aria-describedby="comparison-later-helper consent-helper"
              id="conversation-later"
              onChange={(event) => setLaterText(event.target.value)}
              placeholder="other: maybe later"
              value={laterText}
            />
          </div>
        </div>
      ) : (
        <>
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
        </>
      )}
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

function EvidenceTable({ rows, styleId, feedbackConsent, submittedFeedback, onCueFeedback }) {
  const visibleRows = styleId === "quick" ? rows.slice(0, 2) : rows;

  return (
    <div
      className="evidence-table"
      role="table"
      aria-label="Evidence phrases, patterns, why they matter, and evidence quality"
    >
      <div className="evidence-table-head" role="row">
        <span role="columnheader">Evidence phrase</span>
        <span role="columnheader">Pattern</span>
        <span role="columnheader">Why it matters</span>
        <span role="columnheader">Evidence quality</span>
      </div>
      {visibleRows.map((row) => (
        <article className="evidence-table-row" key={row.id} role="row">
          <div role="cell" data-label="Evidence phrase">
            <span className="evidence-cell-label">Evidence phrase</span>
            <strong>“{row.phrase}”</strong>
          </div>
          <div role="cell" data-label="Pattern">
            <span className="evidence-cell-label">Pattern</span>
            <span className="pattern-pill">{row.family}</span>
          </div>
          <div role="cell" data-label="Why it matters">
            <span className="evidence-cell-label">Why it matters</span>
            <p>{styleId === "quick" ? "Visible wording supports this pattern label." : row.explanation || "This pattern is based on the quoted wording."}</p>
          </div>
          <div role="cell" data-label="Evidence quality">
            <span className="evidence-cell-label">Evidence quality</span>
            <span className={`quality-pill quality-${row.quality}`}>{row.qualityLabel}</span>
            <p>{row.qualityDescription}</p>
          </div>
          <div className="cue-feedback" role="group" aria-label={`Cue feedback for ${row.family}`}>
            {[
              { id: "cue_fits", label: "This cue fits", rating: 1 },
              { id: "cue_too_strong", label: "Too strong", rating: 0 },
              { id: "cue_wrong", label: "Wrong cue", rating: 0 },
            ].map((feedback) => {
              const { id, label, rating } = feedback;
              const key = `${id}:${row.id}`;
              return (
                <Button
                  className={submittedFeedback.includes(key) ? "feedback-option-selected" : ""}
                  disabled={!feedbackConsent || submittedFeedback.includes(key)}
                  key={id}
                  tone="secondary"
                  onClick={() => onCueFeedback({ id, rating }, row)}
                >
                  {label}
                </Button>
              );
            })}
          </div>
        </article>
      ))}
    </div>
  );
}

function ReplyHelper({ goalId, patternLabels }) {
  const [selectedType, setSelectedType] = useState("");
  const [copyStatus, setCopyStatus] = useState("");
  const drafts = useMemo(
    () => buildDraftReplyOptions({ goalId, patternLabels, selectedType }),
    [goalId, patternLabels, selectedType]
  );

  async function copyDraft(text) {
    setCopyStatus("");
    try {
      await navigator.clipboard.writeText(text);
      setCopyStatus("Draft option copied locally. Edit before using.");
    } catch (_error) {
      setCopyStatus("Copy is unavailable in this browser. You can select the draft text manually.");
    }
  }

  return (
    <section className="reply-helper" aria-labelledby="reply-helper-title">
      <div>
        <h3 id="reply-helper-title">Want a clearer reply?</h3>
        <p>Draft options are communication support, not proof of what someone means.</p>
      </div>
      <div className="reply-action-row" role="radiogroup" aria-label="Reply helper options">
        {REPLY_ACTIONS.map((action) => (
          <button
            aria-checked={selectedType === action.type}
            className={selectedType === action.type ? "selected" : ""}
            key={action.id}
            role="radio"
            type="button"
            onClick={() => setSelectedType((current) => (current === action.type ? "" : action.type))}
          >
            {action.label}
          </button>
        ))}
      </div>
      <div className="draft-list">
        {drafts.map((draft) => (
          <article className="draft-card" key={draft.type}>
            <div>
              <span>{draft.label}</span>
              <h4>{draft.title}</h4>
              <p>{draft.text}</p>
              <small>{draft.helper}</small>
            </div>
            <Button tone="secondary" onClick={() => copyDraft(draft.text)}>
              <Copy size={16} />
              Copy
            </Button>
          </article>
        ))}
      </div>
      {copyStatus ? <p className="status-text" role="status">{copyStatus}</p> : null}
    </section>
  );
}

function ResultPanel({ result, goalId, contextId, styleId, onRunDemo, onSwitchToAnalyze }) {
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
  const safeNextStep = goalAwareNextStep(view.safeNextStep, goalId, styleId);

  async function sendFeedback(option, row = null) {
    const feedbackKey = row ? `${option.id}:${row.id}` : `${option.id}:result`;
    if (submittedFeedback.includes(feedbackKey)) {
      setFeedbackStatus("Feedback metadata already accepted for this result.");
      setFeedbackError("");
      return;
    }
    setFeedbackStatus("");
    setFeedbackError("");
    const metadata = buildFeedbackMetadata({
      matchId: view.matchId,
      feedbackTag: option.id,
      cueId: row?.id || "",
      cueFamily: row?.cueId || "",
      evidenceQuality: row?.quality || view.evidenceQualitySummary || "",
      goalId,
      contextId,
      styleId,
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
          <h3>What context would help?</h3>
          <ul>
            {(view.contextSuggestions || view.tryItems).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className="result-section safe-next-card">
          <h3>Safer next step</h3>
          <p>{safeNextStep}</p>
        </div>
        <div className="low-signal-actions">
          <Button onClick={onSwitchToAnalyze}>Add more context</Button>
          <Button tone="secondary" onClick={onRunDemo}>Try a synthetic demo <ArrowRight size={16} /></Button>
        </div>
      </section>
    );
  }

  return (
    <section className="result-panel" aria-label="Vibe Signal result">
      <div className="result-header">
        <div className="signal-strength-block">
          <span className="micro-label">Signal strength</span>
          <span className="status-pill">{view.signalStrengthLabel}</span>
        </div>
        <p className="result-context">
          Your goal: {goal.label} · Context: {context.label} · Style: {style.label}
        </p>
      </div>
      <div className="result-section">
        <h3>{view.comparison ? "What changed" : "What stands out"}</h3>
        <p>{view.mainRead}</p>
      </div>
      <div className="result-section">
        <h3>Evidence</h3>
        <EvidenceTable
          feedbackConsent={feedbackConsent}
          onCueFeedback={sendFeedback}
          rows={view.evidenceDetails}
          styleId={styleId}
          submittedFeedback={submittedFeedback}
        />
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
      <ReplyHelper goalId={goalId} patternLabels={view.patternLabels} />
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
  const [compareEnabled, setCompareEnabled] = useState(false);
  const [earlierText, setEarlierText] = useState("other: Friday at 7 works.");
  const [laterText, setLaterText] = useState("other: maybe later");
  const [consent, setConsent] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [redactionSnapshot, setRedactionSnapshot] = useState(null);
  const [redactionStatus, setRedactionStatus] = useState("");

  const selectedStyle = optionById(ANALYSIS_STYLE_OPTIONS, styleId);
  const hasActiveText = compareEnabled
    ? normalizeText(earlierText) && normalizeText(laterText)
    : normalizeText(text);
  const status = !hasActiveText
    ? compareEnabled
      ? "Add both snippets, or run a synthetic demo first."
      : "Add a short exchange, or run a synthetic demo first."
    : !consent
      ? "Private analysis unlocks after the permission checkbox."
      : loading
        ? "Reviewing observable patterns..."
        : compareEnabled
          ? "Ready to compare observable wording changes locally."
          : "Ready to review permissioned text.";

  function runSyntheticDemo(demoId = PRIMARY_DEMO_IDS[0]) {
    setResult(buildSyntheticResult(demoId));
    setError("");
  }

  function switchToAnalyzeMode() {
    setMode("analyze");
    setError("");
  }

  function handleRedaction() {
    setRedactionSnapshot({ text, earlierText, laterText });
    if (compareEnabled) {
      const earlier = redactIdentifyingDetails(earlierText);
      const later = redactIdentifyingDetails(laterText);
      setEarlierText(earlier.text);
      setLaterText(later.text);
      const changedCount = Number(earlier.changed) + Number(later.changed);
      setRedactionStatus(
        changedCount
          ? "Removed obvious identifiers locally. Review the edited snippets before analysis."
          : "No obvious identifiers found. Review the text before analysis."
      );
      return;
    }

    const redacted = redactIdentifyingDetails(text);
    setText(redacted.text);
    setRedactionStatus(
      redacted.changed
        ? "Removed obvious identifiers locally. Review the edited text before analysis."
        : "No obvious identifiers found. Review the text before analysis."
    );
  }

  function undoRedaction() {
    if (!redactionSnapshot) {
      return;
    }
    setText(redactionSnapshot.text);
    setEarlierText(redactionSnapshot.earlierText);
    setLaterText(redactionSnapshot.laterText);
    setRedactionSnapshot(null);
    setRedactionStatus("Redaction undone locally.");
  }

  async function handleAnalyzeSubmit() {
    if (compareEnabled) {
      if (!normalizeText(earlierText) || !normalizeText(laterText)) {
        setError("Add both snippets before comparing observable wording.");
        return;
      }
      if (!consent) {
        setError("Confirm permission before private text analysis.");
        return;
      }
      setResult(buildComparisonResult({ earlierText, laterText }));
      setError("");
      return;
    }

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
              canUndoRedaction={redactionSnapshot !== null}
              compareEnabled={compareEnabled}
              consent={consent}
              earlierText={earlierText}
              error={error}
              laterText={laterText}
              loading={loading}
              onRedact={handleRedaction}
              onSubmit={handleAnalyzeSubmit}
              onUndoRedaction={undoRedaction}
              redactionStatus={redactionStatus}
              setCompareEnabled={(value) => {
                setCompareEnabled(value);
                setError("");
                setRedactionStatus("");
              }}
              setConsent={setConsent}
              setEarlierText={(value) => {
                setEarlierText(value);
                setError("");
              }}
              setLaterText={(value) => {
                setLaterText(value);
                setError("");
              }}
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
            onSwitchToAnalyze={switchToAnalyzeMode}
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
