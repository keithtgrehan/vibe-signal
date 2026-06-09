import React, { useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  Image,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import {
  buildLowSignalFallback,
  buildMatchResultViewModel,
  FEEDBACK_OPTIONS,
  isContextLightInput,
} from "./matchScreenModel.js";
import { parseBackendBaseUrl } from "../services/backendUrl.js";
import { createMatchClient } from "../services/matchClient.js";
import { createVibeBackendClient } from "../services/vibeBackendClient.js";

const COLORS = {
  background: "#0A0F1C",
  surface: "#111827",
  surfaceSoft: "#162033",
  surfaceMuted: "#1A2438",
  foreground: "#E8EAF0",
  muted: "#8EA0BE",
  quiet: "#4A6080",
  border: "#22314D",
  primary: "#FFB84D",
  primaryForeground: "#0A0F1C",
  positive: "#7DD3A8",
  risk: "#FF7A7A",
  white: "#FFFFFF",
};

const SAMPLE_TEXT =
  "self: Are we still on for Friday?\nother: maybe later, not sure yet";

const HERO_COPY = {
  title: "Understand message patterns without guessing motives.",
  subtitle:
    "Vibe Signal highlights observable cues like clarity, ambiguity, pressure, reassurance, and repair opportunities — with evidence, limits, and safe next steps.",
  primaryCta: "Try a synthetic example",
  secondaryCta: "See how it works",
  trustNote: "Use synthetic text first, or only messages you have permission to analyze.",
};

const TRUST_STRIP_ITEMS = [
  "Evidence-first outputs",
  "No hidden-intent claims",
  "Synthetic demo available",
  "Privacy-conscious beta design",
  "Built for clarity, not manipulation",
];

const CAN_HELP_WITH = [
  "Spot vague or overloaded messages",
  "Identify unclear asks",
  "Surface pressure or urgency cues",
  "Show reassurance and repair opportunities",
  "Suggest clearer, lower-pressure replies",
];

const CANNOT_TELL = [
  "Whether someone likes you",
  "Whether someone is cheating",
  "Whether someone is lying",
  "What someone secretly means",
  "Someone’s diagnosis, attachment style, neurotype, or personality",
  "Whether a relationship will work",
];

const SYNTHETIC_DEMOS = [
  {
    id: "unclear_ask",
    title: "Unclear ask",
    exchange: SAMPLE_TEXT,
    highlight: "Highlights vague timing after a direct question.",
    previewPattern: "Vague timing",
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
    highlight: "Highlights urgency and consequence pressure in the wording.",
    previewPattern: "Urgency pressure",
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
    highlight: "Highlights reassurance, repair wording, and a clear next step.",
    previewPattern: "Repair wording",
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
    highlight: "Avoids over-reading a short context-light exchange.",
    previewPattern: "Not enough context",
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
    highlight: "Highlights a clear ask that leaves room for a no or later.",
    previewPattern: "Clear low-pressure ask",
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
    highlight: "Highlights cognitive load and suggests narrowing the next ask.",
    previewPattern: "Overloaded reply",
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

const CLOSED_BETA_QA_FIXTURE_MODE =
  process.env.EXPO_PUBLIC_QA_FIXTURE_MODE === "closed_beta_synthetic";

const DEMO_QA_FIXTURE_IDS = {
  unclear_ask: "qa_ambiguity_vague_timing_001",
  pressure_urgency: "qa_pressure_urgency_001",
  repair_opportunity: "qa_reassurance_directness_001",
  low_signal_fallback: "qa_low_evidence_context_light_001",
  boundary_respecting_request: "qa_reassurance_directness_001",
  overloaded_message: "qa_cognitive_overload_001",
};

const LEGAL_PAGES = [
  ["match-disclaimer", "Match", "legal.tab.match-disclaimer"],
  ["privacy", "Privacy", "legal.tab.privacy"],
  ["terms", "Terms", "legal.tab.terms"],
  ["data-deletion", "Deletion", "legal.tab.data-deletion"],
  ["data-export", "Export", "legal.tab.data-export"],
];

const FALLBACK_LEGAL = {
  title: "Match Usage Consent Disclaimer",
  status: "draft_requires_legal_review",
  document_ref: "docs/match_usage_consent_disclaimer.md",
  sections: [
    "Vibe Signal matching is communication-support only.",
    "Outputs are pattern-based suggestions, not truth claims.",
    "Only submit messages you have permission to analyze.",
    "Do not include sensitive personal data, secrets, medical data, legal documents, financial data, or third-party private messages without permission.",
    "Closed beta is not production launch. Privacy and terms drafts require legal review before public launch.",
  ],
};

function normalizeText(value) {
  return String(value || "").trim();
}

function buildSyntheticResult(demoId) {
  const demo = SYNTHETIC_DEMOS.find((item) => item.id === demoId) || SYNTHETIC_DEMOS[0];
  return {
    ...demo.result,
    synthetic: true,
    demoTitle: demo.title,
    qaFixtureId: DEMO_QA_FIXTURE_IDS[demo.id] || demo.id,
    qaFixtureMode: CLOSED_BETA_QA_FIXTURE_MODE ? "closed_beta_synthetic" : "",
    requiresPrivateConsent: false,
  };
}

function useBackendClients() {
  const apiUrl = process.env.EXPO_PUBLIC_API_URL || "";
  return useMemo(
    () => ({
      apiUrl,
      matchClient: createMatchClient({ apiUrl }),
      backendClient: createVibeBackendClient({ apiUrl }),
    }),
    [apiUrl]
  );
}

function PressableText({ children, style, textStyle, disabled = false, ...props }) {
  return (
    <Pressable
      accessibilityRole={props.accessibilityRole || "button"}
      disabled={disabled}
      hitSlop={props.hitSlop || 6}
      style={({ pressed }) => [
        ...(Array.isArray(style) ? style : [style]),
        pressed && !disabled && styles.pressed,
        disabled && styles.disabled,
      ]}
      {...props}
    >
      <Text style={textStyle}>{children}</Text>
    </Pressable>
  );
}

function Shell({ children, testID }) {
  const isWeb = Platform.OS === "web";
  return (
    <SafeAreaView testID={testID} style={styles.safe}>
      <KeyboardAvoidingView
        style={styles.keyboardSafe}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <ScrollView
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
          contentContainerStyle={[styles.content, isWeb && styles.contentWeb]}
        >
          {children}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

function SyntheticQaBadge({ fixtureId = "" }) {
  const label = CLOSED_BETA_QA_FIXTURE_MODE ? "Synthetic QA" : "Synthetic demo result";
  if (!CLOSED_BETA_QA_FIXTURE_MODE && !fixtureId) {
    return null;
  }
  return (
    <Text
      testID="result.synthetic_badge"
      accessibilityLabel="Synthetic QA fixture badge"
      style={styles.syntheticResultPill}
    >
      {label}{fixtureId ? `: ${fixtureId}` : ""}
    </Text>
  );
}

function Header({ onHome, onLegal }) {
  return (
    <View style={styles.header}>
      <Pressable style={({ pressed }) => [styles.brand, pressed && styles.pressed]} onPress={onHome}>
        <Image source={require("../../assets/images/icon.png")} style={styles.logoImage} />
        <View>
          <Text style={styles.brandTitle}>Vibe Signal</Text>
          <Text style={styles.brandSubtitle}>Communication support</Text>
        </View>
      </Pressable>
      <PressableText style={styles.headerButton} textStyle={styles.headerButtonText} onPress={onLegal}>
        Legal
      </PressableText>
    </View>
  );
}

function HomeScreen({ runSyntheticDemo, setScreen, setMode }) {
  return (
    <Shell testID="screen.home">
      <Header onHome={() => setScreen("home")} onLegal={() => setScreen("legal")} />
      <View style={styles.hero}>
        <SyntheticQaBadge fixtureId={CLOSED_BETA_QA_FIXTURE_MODE ? "closed_beta_synthetic" : ""} />
        <Text style={styles.eyebrow}>Communication support</Text>
        <Text style={styles.heroTitle}>{HERO_COPY.title}</Text>
        <Text style={styles.heroSubtitle}>{HERO_COPY.subtitle}</Text>
        <View style={styles.heroActions}>
          <PressableText
            testID="home.synthetic.primary"
            accessibilityLabel="Run primary synthetic example"
            style={styles.primaryButton}
            textStyle={styles.primaryButtonText}
            onPress={() => runSyntheticDemo(SYNTHETIC_DEMOS[0].id)}
          >
            {HERO_COPY.primaryCta}
          </PressableText>
          <PressableText
            testID="home.analyze.cta"
            accessibilityLabel="Open analysis screen"
            style={styles.secondaryButton}
            textStyle={styles.secondaryButtonText}
            onPress={() => setScreen("analyze")}
          >
            {HERO_COPY.secondaryCta}
          </PressableText>
        </View>
        <Text style={styles.quietText}>{HERO_COPY.trustNote}</Text>
      </View>

      <View style={styles.trustStrip}>
        {TRUST_STRIP_ITEMS.map((item) => (
          <Text key={item} style={styles.trustItem}>{item}</Text>
        ))}
      </View>

      <View style={styles.card}>
        <Text style={styles.eyebrow}>Synthetic demo cards</Text>
        <Text style={styles.screenTitle}>Try the product before using private text.</Text>
        {SYNTHETIC_DEMOS.map((demo) => (
          <Pressable
            key={demo.id}
            style={({ pressed }) => [styles.demoCard, pressed && styles.pressed]}
            onPress={() => runSyntheticDemo(demo.id)}
          >
            <Text style={styles.modeLabel}>{demo.title}</Text>
            <Text style={styles.demoPatternPill}>{demo.previewPattern}</Text>
            <Text style={styles.syntheticExchange}>{demo.exchange}</Text>
            <Text style={styles.modeBody}>{demo.highlight}</Text>
            <Text style={styles.modeAction}>Run demo</Text>
          </Pressable>
        ))}
      </View>

      <View style={styles.card}>
        <Text style={styles.eyebrow}>How it works</Text>
        <Text style={styles.sectionTitle}>Evidence first, interpretation second.</Text>
        <Text style={styles.helperText}>
          Start with a synthetic example, read the quoted phrase, check the limits, then choose a
          lower-pressure next step.
        </Text>
      </View>

      <View style={styles.resultGrid}>
        <FactorList title="Can help with" items={CAN_HELP_WITH} empty="" />
        <FactorList title="Cannot tell you" items={CANNOT_TELL} empty="" />
      </View>
    </Shell>
  );
}

function ModeCard({ label, marker, body, onPress }) {
  return (
    <Pressable style={({ pressed }) => [styles.modeCard, pressed && styles.pressed]} onPress={onPress}>
      <View style={styles.modeMarker}>
        <Text style={styles.modeMarkerText}>{marker}</Text>
      </View>
      <Text style={styles.modeLabel}>{label}</Text>
      <Text style={styles.modeBody}>{body}</Text>
      <Text style={styles.modeAction}>Review cues</Text>
    </Pressable>
  );
}

function AnalyzeScreen({ mode, runSyntheticDemo, setMode, setResult, setScreen }) {
  const { apiUrl, matchClient, backendClient } = useBackendClients();
  const [text, setText] = useState(SAMPLE_TEXT);
  const [consent, setConsent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const apiUrlState = parseBackendBaseUrl(apiUrl);
  const apiConfigured = apiUrlState.ok;
  const hasText = Boolean(normalizeText(text));
  const canSubmit = hasText && consent && apiConfigured && !loading;
  const submitStatus = !hasText
    ? "Add a short exchange, or run a synthetic example first."
    : !consent
      ? "Private analysis unlocks after the permission checkbox."
      : !apiConfigured
        ? "Private analysis is not connected in this build. Synthetic demos still work."
        : loading
          ? mode === "match"
            ? "Checking communication patterns..."
            : "Surfacing cue evidence..."
          : "Ready to review permissioned text.";

  async function handleSubmit() {
    if (!hasText) {
      setStatus("Add a short exchange, or run a synthetic example first.");
      return;
    }
    if (!consent) {
      setStatus("Confirm permission before private text analysis.");
      return;
    }
    if (!apiConfigured) {
      setStatus(
        apiUrlState.status === "missing_api_url"
          ? "Private analysis is not connected in this build. Synthetic demos still work."
          : "Private analysis needs a clean beta service connection."
      );
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
      setStatus("");
      setScreen("results");
      return;
    }

    setLoading(true);
    setStatus(mode === "match" ? "Checking communication patterns..." : "Surfacing cue evidence...");
    setError("");
    try {
      const response =
        mode === "match"
          ? await matchClient.submitMatchDraft({
              conversationText: text,
              conversationId: `mobile_match_${Date.now().toString(16)}`,
            })
          : await backendClient.submitAnalyzeDraft({
              conversationText: text,
              conversationId: `mobile_analysis_${Date.now().toString(16)}`,
            });

      if (!response.ok) {
        setError(response.userMessage || "The request could not be completed.");
        setStatus("");
        return;
      }

      setResult({
        kind: mode,
        payload: response.result,
      });
      setStatus("");
      setScreen("results");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Shell testID="screen.analyze">
      <Header onHome={() => setScreen("home")} onLegal={() => setScreen("legal")} />
      <PressableText
        style={styles.backButton}
        textStyle={styles.backButtonText}
        onPress={() => setScreen("home")}
      >
        Back
      </PressableText>

      <View style={styles.card}>
        <SyntheticQaBadge fixtureId={CLOSED_BETA_QA_FIXTURE_MODE ? "closed_beta_synthetic" : ""} />
        <Text style={styles.eyebrow}>Pattern review</Text>
        <Text style={styles.screenTitle}>Review observable wording cues</Text>
        <Text style={styles.helperText}>
          Run a synthetic card without consent, or paste permissioned text after the lightweight
          consent check.
        </Text>

        <View style={styles.inlineDemoRow}>
          {SYNTHETIC_DEMOS.map((demo) => (
            <Pressable
              key={demo.id}
              style={({ pressed }) => [styles.inlineDemoButton, pressed && styles.pressed]}
              onPress={() => runSyntheticDemo(demo.id)}
            >
              <Text style={styles.inlineDemoTitle}>{demo.title}</Text>
              <Text style={styles.inlineDemoPattern}>{demo.previewPattern}</Text>
              <Text style={styles.inlineDemoAction}>Run demo</Text>
            </Pressable>
          ))}
        </View>

        <View style={styles.segmented}>
          <PressableText
            testID="mode.match"
            accessibilityLabel="Use pattern mode"
            style={[styles.segmentButton, mode === "match" && styles.segmentButtonActive]}
            textStyle={[styles.segmentText, mode === "match" && styles.segmentTextActive]}
            onPress={() => setMode("match")}
          >
            Pattern
          </PressableText>
          <PressableText
            testID="mode.evidence"
            accessibilityLabel="Use evidence mode"
            style={[styles.segmentButton, mode === "evidence" && styles.segmentButtonActive]}
            textStyle={[styles.segmentText, mode === "evidence" && styles.segmentTextActive]}
            onPress={() => setMode("evidence")}
          >
            Evidence
          </PressableText>
        </View>

        <Text style={styles.fieldLabel}>Permissioned conversation text</Text>
        <TextInput
          testID="input.conversation"
          value={text}
          onChangeText={(value) => {
            setText(value);
            setError("");
            setStatus("");
          }}
          placeholder={SAMPLE_TEXT}
          placeholderTextColor={COLORS.quiet}
          multiline
          textAlignVertical="top"
          autoCorrect={false}
          autoCapitalize="none"
          accessibilityLabel="Permissioned conversation text"
          style={styles.textArea}
        />

        <View style={styles.disclosureBox}>
          <Text style={styles.disclosureTitle}>Before you paste</Text>
          <Text style={styles.disclosureText}>Only submit messages you have permission to analyze.</Text>
          <Text style={styles.disclosureText}>
            Remove names, phone numbers, addresses, and sensitive details.
          </Text>
          <Text style={styles.disclosureText}>
            Use synthetic examples if you just want to test the app.
          </Text>
        </View>

        <View style={styles.resultGrid}>
          <FactorList title="Can help with" items={CAN_HELP_WITH} empty="" />
          <FactorList title="Cannot tell you" items={CANNOT_TELL} empty="" />
        </View>

        <Pressable
          testID="consent.permission.checkbox"
          accessibilityRole="checkbox"
          accessibilityState={{ checked: consent }}
          hitSlop={6}
          style={({ pressed }) => [styles.checkboxRow, pressed && styles.pressed]}
          onPress={() => setConsent((current) => !current)}
        >
          <View style={[styles.checkbox, consent && styles.checkboxChecked]}>
            <Text style={styles.checkboxMark}>{consent ? "OK" : ""}</Text>
          </View>
          <Text style={styles.checkboxLabel}>
            I understand and have permission to analyze this text.
          </Text>
        </Pressable>

        <Text accessibilityLiveRegion="polite" style={styles.statusText}>{submitStatus}</Text>
        {status && status !== submitStatus ? (
          <Text accessibilityLiveRegion="polite" style={styles.statusText}>{status}</Text>
        ) : null}
        {error ? (
          <Text accessibilityLiveRegion="assertive" style={styles.errorText}>{error}</Text>
        ) : null}

        <PressableText
          testID="submit.review"
          accessibilityLabel="Submit pattern review"
          disabled={!canSubmit}
          style={styles.primaryButton}
          textStyle={styles.primaryButtonText}
          onPress={handleSubmit}
        >
          {loading ? "Checking..." : mode === "match" ? "Review patterns" : "Surface evidence"}
        </PressableText>

        {loading ? <ActivityIndicator color={COLORS.primary} /> : null}
      </View>
    </Shell>
  );
}

function ResultsScreen({ result, runSyntheticDemo, setScreen, setMode }) {
  if (!result) {
    return (
      <Shell testID="screen.results">
        <Header onHome={() => setScreen("home")} onLegal={() => setScreen("legal")} />
        <View style={styles.card}>
          <Text style={styles.screenTitle}>No result yet</Text>
          <PressableText
            style={styles.primaryButton}
            textStyle={styles.primaryButtonText}
            onPress={() => setScreen("analyze")}
          >
            Start analysis
          </PressableText>
        </View>
      </Shell>
    );
  }

  return (
    <Shell testID="screen.results">
      <Header onHome={() => setScreen("home")} onLegal={() => setScreen("legal")} />
      <PressableText
        style={styles.backButton}
        textStyle={styles.backButtonText}
        onPress={() => setScreen("analyze")}
      >
        Back to input
      </PressableText>

      {result.kind === "match" ? (
        <MatchResult
          result={result.payload}
          runSyntheticDemo={runSyntheticDemo}
          setScreen={setScreen}
          setMode={setMode}
        />
      ) : (
        <EvidenceResult result={result.payload} setScreen={setScreen} setMode={setMode} />
      )}
    </Shell>
  );
}

function MatchResult({ result, runSyntheticDemo, setScreen, setMode }) {
  const { backendClient } = useBackendClients();
  const viewModel = buildMatchResultViewModel(result || {});
  const [feedbackConsent, setFeedbackConsent] = useState(false);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [feedbackStatus, setFeedbackStatus] = useState("");
  const [feedbackError, setFeedbackError] = useState("");
  const [submittedFeedbackTags, setSubmittedFeedbackTags] = useState([]);
  const [pendingFeedbackTag, setPendingFeedbackTag] = useState("");

  async function sendFeedback(option) {
    if (feedbackLoading) {
      return;
    }
    if (submittedFeedbackTags.includes(option.id)) {
      setFeedbackStatus("Feedback metadata already accepted for this result.");
      setFeedbackError("");
      return;
    }
    setFeedbackLoading(true);
    setPendingFeedbackTag(option.id);
    setFeedbackStatus("");
    setFeedbackError("");
    try {
      const response = await backendClient.submitFeedbackMetadata({
        matchId: result?.match_id || "",
        rating: option.rating,
        feedbackTag: option.id,
        consent: feedbackConsent,
      });
      if (response.ok) {
        setSubmittedFeedbackTags((current) =>
          current.includes(option.id) ? current : [...current, option.id]
        );
        setFeedbackStatus("Feedback metadata accepted. No raw message text was sent.");
        return;
      }
      setFeedbackError(response.userMessage || "Feedback could not be sent.");
    } finally {
      setFeedbackLoading(false);
      setPendingFeedbackTag("");
    }
  }

  if (viewModel.isLowSignal) {
    return (
      <>
        <View style={[styles.resultHero, styles.lowSignalCard]}>
          <Text style={styles.eyebrow}>
            {viewModel.resultState === "no_safe_evidence" ? "Evidence fallback" : "Low-signal fallback"}
          </Text>
          <Text style={styles.screenTitle}>{viewModel.title}</Text>
          <Text style={styles.helperText}>{viewModel.body}</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Try</Text>
          {viewModel.tryItems.map((item) => (
            <Text key={item} style={styles.factorText}>• {item}</Text>
          ))}
        </View>

        <View style={styles.buttonRow}>
          <PressableText
            style={[styles.secondaryButton, styles.flexButton]}
            textStyle={styles.secondaryButtonText}
            onPress={() => setScreen("analyze")}
          >
            Add more context
          </PressableText>
          <PressableText
            style={[styles.primaryButton, styles.flexButton]}
            textStyle={styles.primaryButtonText}
            onPress={() => runSyntheticDemo(SYNTHETIC_DEMOS[0].id)}
          >
            Try a synthetic example
          </PressableText>
        </View>
      </>
    );
  }

  return (
    <>
      <View style={styles.resultHero}>
        {result?.synthetic ? <SyntheticQaBadge fixtureId={result.qaFixtureId || result.demoTitle} /> : null}
        <Text style={styles.eyebrow}>Main read</Text>
        <Text style={styles.screenTitle}>{viewModel.mainRead}</Text>
        <Text style={styles.signalPill}>{viewModel.signalStrengthLabel}</Text>
      </View>

      <View style={styles.resultSignalGrid}>
        <View style={styles.signalStatCard}>
          <Text style={styles.evidenceFamily}>Fit read</Text>
          <Text style={styles.signalStatText}>{viewModel.bandLabel}</Text>
        </View>
        <View style={styles.signalStatCard}>
          <Text style={styles.evidenceFamily}>Evidence confidence</Text>
          <Text style={styles.signalStatText}>{viewModel.confidenceLabel}</Text>
        </View>
      </View>

      <View style={styles.resultGrid}>
        <FactorList
          title="Alignment cues"
          items={viewModel.positiveFactors}
          empty={viewModel.emptyPositiveLabel}
        />
        <FactorList
          title="Friction cues"
          items={viewModel.riskFactors}
          empty={viewModel.emptyRiskLabel}
        />
      </View>

      <View testID="result.evidence.section" style={styles.card}>
        <Text style={styles.eyebrow}>Evidence phrases</Text>
        <Text style={styles.sectionTitle}>Quoted wording behind the read</Text>
        {viewModel.evidenceDetails.map((row) => (
          <View key={row.id} style={styles.evidenceDetail}>
            <Text style={styles.evidenceFamily}>{row.family}</Text>
            <Text style={styles.evidencePhrase}>“{row.phrase}”</Text>
            {!!row.repair ? <Text style={styles.helperText}>{row.repair}</Text> : null}
          </View>
        ))}
      </View>

      <View style={styles.card}>
        <Text style={styles.eyebrow}>Pattern explanation</Text>
        <Text style={styles.sectionTitle}>{viewModel.patternExplanation}</Text>
        <View style={styles.chipRow}>
          {viewModel.patternLabels.map((label, index) => (
            <Text key={`${label}:${index}`} style={styles.patternChip}>{label}</Text>
          ))}
        </View>
      </View>

      <View style={styles.cannotInferCard}>
        <Text style={styles.sectionTitle}>What this cannot tell you</Text>
        <Text style={styles.helperText}>{viewModel.cannotInferText}</Text>
      </View>

      <View testID="result.safe_next_step" style={styles.safeNextCard}>
        <Text style={styles.sectionTitle}>Safe next step</Text>
        <Text style={styles.helperText}>{viewModel.safeNextStep}</Text>
      </View>

      <View style={styles.resultGrid}>
        <FactorList title="Can help with" items={viewModel.canTell} empty="" />
        <FactorList title="Cannot tell you" items={viewModel.cannotInfer} empty="" />
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Was this result useful?</Text>
        <Text style={styles.helperText}>
          Optional metadata-only feedback. No free-text comment or message text is sent.
        </Text>
        <Pressable
          testID="feedback.consent"
          accessibilityRole="checkbox"
          accessibilityState={{ checked: feedbackConsent }}
          hitSlop={6}
          style={({ pressed }) => [styles.checkboxRow, pressed && styles.pressed]}
          onPress={() => setFeedbackConsent((current) => !current)}
        >
          <View style={[styles.checkbox, feedbackConsent && styles.checkboxChecked]}>
            <Text style={styles.checkboxMark}>{feedbackConsent ? "OK" : ""}</Text>
          </View>
          <Text style={styles.checkboxLabel}>Consent to store bounded feedback metadata.</Text>
        </Pressable>
        <View style={styles.buttonRow}>
          {FEEDBACK_OPTIONS.map((option) => (
            <PressableText
              key={option.id}
              disabled={
                !feedbackConsent || feedbackLoading || submittedFeedbackTags.includes(option.id)
              }
              style={[
                styles.secondaryButton,
                styles.feedbackButton,
                submittedFeedbackTags.includes(option.id) && styles.feedbackButtonSelected,
              ]}
              textStyle={styles.secondaryButtonText}
              onPress={() => sendFeedback(option)}
            >
              {pendingFeedbackTag === option.id ? "Sending..." : option.label}
            </PressableText>
          ))}
        </View>
        {feedbackStatus ? (
          <Text accessibilityLiveRegion="polite" style={styles.statusText}>{feedbackStatus}</Text>
        ) : null}
        {feedbackError ? (
          <Text accessibilityLiveRegion="assertive" style={styles.errorText}>{feedbackError}</Text>
        ) : null}
      </View>

      <PressableText
        style={styles.primaryButton}
        textStyle={styles.primaryButtonText}
        onPress={() => {
          setMode("match");
          setScreen("analyze");
        }}
      >
        Review another synthetic or permissioned example
      </PressableText>
    </>
  );
}

function FactorList({ title, items, empty }) {
  const rows = items.length ? items : [empty];
  return (
    <View style={styles.card}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {rows.map((item) => (
        <View style={styles.factorRow} key={item}>
          <View style={styles.factorDot} />
          <Text style={styles.factorText}>{item}</Text>
        </View>
      ))}
    </View>
  );
}

function EvidenceResult({ result, setScreen, setMode }) {
  const evidence = Array.isArray(result?.evidence) ? result.evidence : [];
  const rows = evidence.length
    ? evidence
    : [
        {
          cue_id: "no_cue",
          cue_family: "cue",
          safe_phrase: "No observable cue returned for this text.",
          explanation: "No action is required; add permissioned context only if a broader pattern review would help.",
        },
      ];

  return (
    <>
      <View style={styles.resultHero}>
        <Text style={styles.eyebrow}>Cue evidence</Text>
        <Text style={styles.screenTitle}>
          {evidence.length ? `${evidence.length} observable cues` : "No cue rows returned"}
        </Text>
        <Text style={styles.disclosureText}>
          Evidence rows come from the current cue taxonomy and include safe phrases, explanations,
          interpretation limits, and bounded display fields.
        </Text>
      </View>

      <View testID="result.evidence.section">
      {rows.map((row, index) => (
        <View style={styles.evidenceCard} key={`${row.evidence_id || row.cue_id}:${index}`}>
          <Text style={styles.evidenceFamily}>
            {normalizeText(row.cue_family || row.cue_id || "cue").replace(/_/g, " ")}
          </Text>
          <Text style={styles.evidencePhrase}>
            {normalizeText(row.safe_phrase || "Safe phrase unavailable.")}
          </Text>
          <Text style={styles.helperText}>
            {normalizeText(row.explanation || "Cue explanation unavailable.")}
          </Text>
        </View>
      ))}
      </View>

      <View style={styles.card}>
        <Text style={styles.disclosureText}>
          These results are observable wording cues only. They do not decide motives, identity,
          health, or outcomes.
        </Text>
      </View>

      <PressableText
        style={styles.primaryButton}
        textStyle={styles.primaryButtonText}
        onPress={() => {
          setMode("evidence");
          setScreen("analyze");
        }}
      >
        Review another synthetic or permissioned example
      </PressableText>
    </>
  );
}

function LegalScreen({ setScreen }) {
  const { backendClient, apiUrl } = useBackendClients();
  const [slug, setSlug] = useState("match-disclaimer");
  const [page, setPage] = useState(FALLBACK_LEGAL);
  const [status, setStatus] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!normalizeText(apiUrl)) {
        setPage(FALLBACK_LEGAL);
        setStatus("Using fallback copy because the legal draft is not connected in this build.");
        return;
      }

      setStatus("Loading legal draft...");
      const response = await backendClient.fetchLegalDraft(slug);
      if (cancelled) {
        return;
      }
      if (response.ok) {
        setPage(response.result);
        setStatus("");
        return;
      }
      setPage(FALLBACK_LEGAL);
      setStatus("Using fallback copy because the legal draft did not load.");
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [apiUrl, backendClient, slug]);

  return (
    <Shell testID="screen.legal">
      <Header onHome={() => setScreen("home")} onLegal={() => setScreen("legal")} />
      <PressableText
        style={styles.backButton}
        textStyle={styles.backButtonText}
        onPress={() => setScreen("home")}
      >
        Back
      </PressableText>

      <View style={styles.card}>
        <Text style={styles.eyebrow}>Legal and privacy</Text>
        <Text style={styles.screenTitle}>{page.title}</Text>
        <Text style={styles.helperText}>Status: {page.status || "draft_requires_legal_review"}</Text>

        <View style={styles.segmented}>
          {LEGAL_PAGES.map(([nextSlug, label, testId]) => (
            <PressableText
              key={nextSlug}
              testID={testId}
              style={[styles.legalButton, slug === nextSlug && styles.segmentButtonActive]}
              textStyle={[styles.segmentText, slug === nextSlug && styles.segmentTextActive]}
              onPress={() => setSlug(nextSlug)}
            >
              {label}
            </PressableText>
          ))}
        </View>

        {status ? (
          <Text accessibilityLiveRegion="polite" style={styles.statusText}>{status}</Text>
        ) : null}
        {(page.sections || []).map((section) => (
          <Text key={section} style={styles.legalSection}>
            {section}
          </Text>
        ))}
        <Text style={styles.quietText}>
          Document reference: {page.document_ref || "docs/match_usage_consent_disclaimer.md"}
        </Text>
      </View>
    </Shell>
  );
}

export default function VibeSignalApp() {
  const [screen, setScreen] = useState("home");
  const [mode, setMode] = useState("match");
  const [result, setResult] = useState(null);

  function runSyntheticDemo(demoId) {
    setResult({
      kind: "match",
      payload: buildSyntheticResult(demoId),
    });
    setMode("match");
    setScreen("results");
  }

  if (screen === "analyze") {
    return (
      <AnalyzeScreen
        mode={mode}
        runSyntheticDemo={runSyntheticDemo}
        setMode={setMode}
        setResult={setResult}
        setScreen={setScreen}
      />
    );
  }

  if (screen === "results") {
    return (
      <ResultsScreen
        result={result}
        runSyntheticDemo={runSyntheticDemo}
        setMode={setMode}
        setScreen={setScreen}
      />
    );
  }

  if (screen === "legal") {
    return <LegalScreen setScreen={setScreen} />;
  }

  return (
    <HomeScreen
      runSyntheticDemo={runSyntheticDemo}
      setMode={setMode}
      setScreen={setScreen}
    />
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  keyboardSafe: {
    flex: 1,
  },
  content: {
    paddingHorizontal: 18,
    paddingTop: 18,
    paddingBottom: 34,
    gap: 14,
  },
  contentWeb: {
    width: "100%",
    maxWidth: 780,
    alignSelf: "center",
    paddingTop: 34,
    paddingBottom: 56,
  },
  header: {
    minHeight: 48,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
  },
  brand: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    flexShrink: 1,
  },
  logoImage: {
    width: 38,
    height: 38,
    borderRadius: 8,
    backgroundColor: COLORS.primary,
  },
  brandTitle: {
    color: COLORS.foreground,
    fontSize: 17,
    lineHeight: 22,
    fontWeight: "800",
    letterSpacing: 0,
  },
  brandSubtitle: {
    color: COLORS.quiet,
    fontSize: 12,
    lineHeight: 16,
    letterSpacing: 0,
  },
  headerButton: {
    minHeight: 44,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surface,
    paddingHorizontal: 14,
    alignItems: "center",
    justifyContent: "center",
  },
  headerButtonText: {
    color: COLORS.muted,
    fontSize: 13,
    fontWeight: "700",
  },
  hero: {
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surface,
    borderRadius: 8,
    padding: 20,
    gap: 13,
  },
  eyebrow: {
    color: COLORS.primary,
    fontSize: 11,
    lineHeight: 16,
    fontWeight: "800",
    letterSpacing: 0,
    textTransform: "uppercase",
  },
  heroTitle: {
    color: COLORS.foreground,
    fontSize: 38,
    lineHeight: 43,
    fontWeight: "900",
    letterSpacing: 0,
  },
  heroSubtitle: {
    color: COLORS.muted,
    fontSize: 16,
    lineHeight: 24,
  },
  heroActions: {
    gap: 10,
  },
  primaryButton: {
    minHeight: 50,
    borderRadius: 8,
    backgroundColor: COLORS.primary,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 16,
  },
  primaryButtonText: {
    color: COLORS.primaryForeground,
    fontSize: 15,
    fontWeight: "900",
    textAlign: "center",
  },
  secondaryButton: {
    minHeight: 48,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surfaceSoft,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 16,
  },
  secondaryButtonText: {
    color: COLORS.foreground,
    fontSize: 14,
    fontWeight: "800",
    textAlign: "center",
  },
  quietText: {
    color: COLORS.quiet,
    fontSize: 12,
    lineHeight: 18,
  },
  trustStrip: {
    gap: 8,
  },
  trustItem: {
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surface,
    borderRadius: 8,
    color: COLORS.muted,
    fontSize: 12,
    lineHeight: 18,
    fontWeight: "700",
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  modeGrid: {
    gap: 10,
  },
  demoCard: {
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surfaceSoft,
    borderRadius: 8,
    padding: 13,
    gap: 8,
  },
  syntheticExchange: {
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: "#060A12",
    borderRadius: 8,
    color: COLORS.foreground,
    fontSize: 12,
    lineHeight: 18,
    paddingHorizontal: 10,
    paddingVertical: 9,
  },
  demoPatternPill: {
    alignSelf: "flex-start",
    color: COLORS.primary,
    borderWidth: 1,
    borderColor: "rgba(255, 184, 77, 0.28)",
    backgroundColor: "rgba(255, 184, 77, 0.1)",
    borderRadius: 8,
    overflow: "hidden",
    paddingHorizontal: 9,
    paddingVertical: 5,
    fontSize: 11,
    lineHeight: 15,
    fontWeight: "900",
  },
  modeCard: {
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surface,
    borderRadius: 8,
    padding: 16,
    gap: 9,
  },
  modeMarker: {
    width: 34,
    height: 34,
    borderRadius: 8,
    backgroundColor: COLORS.surfaceMuted,
    alignItems: "center",
    justifyContent: "center",
  },
  modeMarkerText: {
    color: COLORS.primary,
    fontSize: 14,
    fontWeight: "900",
  },
  modeLabel: {
    color: COLORS.foreground,
    fontSize: 16,
    fontWeight: "800",
    letterSpacing: 0,
  },
  modeBody: {
    color: COLORS.muted,
    fontSize: 13,
    lineHeight: 20,
  },
  modeAction: {
    color: COLORS.primary,
    fontSize: 13,
    fontWeight: "800",
  },
  backButton: {
    alignSelf: "flex-start",
    minHeight: 44,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surface,
    justifyContent: "center",
    paddingHorizontal: 12,
  },
  backButtonText: {
    color: COLORS.muted,
    fontSize: 13,
    fontWeight: "800",
  },
  card: {
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surface,
    borderRadius: 8,
    padding: 16,
    gap: 13,
  },
  screenTitle: {
    color: COLORS.foreground,
    fontSize: 28,
    lineHeight: 34,
    fontWeight: "900",
    letterSpacing: 0,
  },
  helperText: {
    color: COLORS.muted,
    fontSize: 13,
    lineHeight: 20,
  },
  inlineDemoRow: {
    gap: 8,
  },
  inlineDemoButton: {
    minHeight: 58,
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surfaceSoft,
    borderRadius: 8,
    justifyContent: "center",
    paddingHorizontal: 12,
    paddingVertical: 10,
    gap: 2,
  },
  inlineDemoTitle: {
    color: COLORS.foreground,
    fontSize: 13,
    lineHeight: 18,
    fontWeight: "800",
  },
  inlineDemoPattern: {
    color: COLORS.muted,
    fontSize: 11,
    lineHeight: 15,
    fontWeight: "700",
  },
  inlineDemoAction: {
    color: COLORS.primary,
    fontSize: 12,
    lineHeight: 16,
    fontWeight: "800",
  },
  segmented: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  segmentButton: {
    minHeight: 44,
    flex: 1,
    minWidth: 120,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surfaceSoft,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 12,
  },
  legalButton: {
    minHeight: 44,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surfaceSoft,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 12,
  },
  segmentButtonActive: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  segmentText: {
    color: COLORS.muted,
    fontSize: 13,
    fontWeight: "800",
  },
  segmentTextActive: {
    color: COLORS.primaryForeground,
  },
  fieldLabel: {
    color: COLORS.foreground,
    fontSize: 13,
    lineHeight: 18,
    fontWeight: "800",
  },
  textArea: {
    minHeight: 230,
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: "#060A12",
    borderRadius: 8,
    color: COLORS.foreground,
    paddingHorizontal: 14,
    paddingVertical: 14,
    fontSize: 14,
    lineHeight: 22,
  },
  disclosureBox: {
    borderWidth: 1,
    borderColor: "rgba(125, 211, 168, 0.24)",
    backgroundColor: "rgba(125, 211, 168, 0.08)",
    borderRadius: 8,
    padding: 13,
    gap: 5,
  },
  disclosureTitle: {
    color: COLORS.foreground,
    fontSize: 14,
    fontWeight: "800",
  },
  disclosureText: {
    color: COLORS.muted,
    fontSize: 12,
    lineHeight: 19,
  },
  checkboxRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 10,
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surfaceSoft,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 1,
  },
  checkboxChecked: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  checkboxMark: {
    color: COLORS.primaryForeground,
    fontSize: 9,
    fontWeight: "900",
    lineHeight: 12,
  },
  checkboxLabel: {
    color: COLORS.muted,
    flex: 1,
    fontSize: 13,
    lineHeight: 20,
  },
  statusText: {
    color: COLORS.positive,
    fontSize: 13,
    lineHeight: 19,
    fontWeight: "700",
  },
  errorText: {
    color: COLORS.risk,
    fontSize: 13,
    lineHeight: 19,
    fontWeight: "700",
  },
  resultHero: {
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surface,
    borderRadius: 8,
    padding: 16,
    gap: 14,
  },
  syntheticResultPill: {
    alignSelf: "flex-start",
    color: COLORS.positive,
    borderWidth: 1,
    borderColor: "rgba(125, 211, 168, 0.24)",
    backgroundColor: "rgba(125, 211, 168, 0.08)",
    borderRadius: 8,
    overflow: "hidden",
    paddingHorizontal: 10,
    paddingVertical: 7,
    fontSize: 12,
    lineHeight: 16,
    fontWeight: "900",
  },
  scorePanel: {
    borderWidth: 1,
    borderColor: "rgba(255, 184, 77, 0.28)",
    backgroundColor: "rgba(255, 184, 77, 0.08)",
    borderRadius: 8,
    padding: 15,
    gap: 6,
  },
  scoreLabel: {
    color: COLORS.primary,
    fontSize: 11,
    fontWeight: "900",
    textTransform: "uppercase",
    letterSpacing: 0,
  },
  scoreValue: {
    color: COLORS.foreground,
    fontSize: 28,
    lineHeight: 34,
    fontWeight: "900",
    letterSpacing: 0,
  },
  bandPill: {
    alignSelf: "flex-start",
    color: COLORS.primaryForeground,
    backgroundColor: COLORS.primary,
    borderRadius: 8,
    overflow: "hidden",
    paddingHorizontal: 10,
    paddingVertical: 6,
    fontSize: 12,
    fontWeight: "900",
  },
  resultExplanation: {
    color: COLORS.foreground,
    fontSize: 15,
    lineHeight: 23,
    fontWeight: "700",
  },
  signalPill: {
    alignSelf: "flex-start",
    color: COLORS.primary,
    borderWidth: 1,
    borderColor: "rgba(255, 184, 77, 0.28)",
    backgroundColor: "rgba(255, 184, 77, 0.1)",
    borderRadius: 8,
    overflow: "hidden",
    paddingHorizontal: 10,
    paddingVertical: 7,
    fontSize: 12,
    lineHeight: 17,
    fontWeight: "900",
  },
  resultGrid: {
    gap: 10,
  },
  resultSignalGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  signalStatCard: {
    flexGrow: 1,
    flexBasis: "46%",
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surface,
    borderRadius: 8,
    padding: 13,
    gap: 6,
  },
  signalStatText: {
    color: COLORS.foreground,
    fontSize: 13,
    lineHeight: 19,
    fontWeight: "800",
  },
  sectionTitle: {
    color: COLORS.foreground,
    fontSize: 16,
    lineHeight: 22,
    fontWeight: "850",
    letterSpacing: 0,
  },
  factorRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 10,
  },
  factorDot: {
    width: 7,
    height: 7,
    borderRadius: 4,
    backgroundColor: COLORS.primary,
    marginTop: 7,
  },
  factorText: {
    color: COLORS.muted,
    flex: 1,
    fontSize: 13,
    lineHeight: 20,
  },
  evidencePhrase: {
    color: COLORS.foreground,
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surfaceSoft,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 13,
    lineHeight: 20,
  },
  evidenceDetail: {
    gap: 8,
  },
  chipRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  patternChip: {
    color: COLORS.primary,
    borderWidth: 1,
    borderColor: "rgba(255, 184, 77, 0.28)",
    backgroundColor: "rgba(255, 184, 77, 0.1)",
    borderRadius: 8,
    overflow: "hidden",
    paddingHorizontal: 10,
    paddingVertical: 7,
    fontSize: 12,
    lineHeight: 16,
    fontWeight: "900",
  },
  cannotInferCard: {
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: "rgba(142, 160, 190, 0.08)",
    borderRadius: 8,
    padding: 15,
    gap: 8,
  },
  safeNextCard: {
    borderWidth: 1,
    borderColor: "rgba(125, 211, 168, 0.24)",
    backgroundColor: "rgba(125, 211, 168, 0.08)",
    borderRadius: 8,
    padding: 15,
    gap: 8,
  },
  lowSignalCard: {
    borderWidth: 1,
    borderColor: "rgba(255, 184, 77, 0.34)",
    backgroundColor: "rgba(255, 184, 77, 0.08)",
    borderRadius: 8,
    padding: 15,
    gap: 9,
  },
  buttonRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  flexButton: {
    flex: 1,
  },
  feedbackButton: {
    flexGrow: 1,
    flexBasis: "46%",
  },
  feedbackButtonSelected: {
    borderColor: "rgba(125, 211, 168, 0.34)",
    backgroundColor: "rgba(125, 211, 168, 0.1)",
  },
  evidenceCard: {
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surface,
    borderRadius: 8,
    padding: 15,
    gap: 9,
  },
  evidenceFamily: {
    color: COLORS.primary,
    fontSize: 11,
    lineHeight: 16,
    fontWeight: "900",
    textTransform: "uppercase",
  },
  legalSection: {
    color: COLORS.muted,
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.surfaceSoft,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 11,
    fontSize: 13,
    lineHeight: 20,
  },
  pressed: {
    opacity: 0.72,
  },
  disabled: {
    opacity: 0.42,
  },
});
