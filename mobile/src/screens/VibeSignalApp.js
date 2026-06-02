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

import { buildMatchResultViewModel } from "./matchScreenModel.js";
import { formatBackendUrlStatus, parseBackendBaseUrl } from "../services/backendUrl.js";
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
  "self: Can you confirm Friday at 3pm?\nother: Yes, Friday at 3pm works. No pressure if we need to adjust.";

const LEGAL_PAGES = [
  ["match-disclaimer", "Match"],
  ["privacy", "Privacy"],
  ["terms", "Terms"],
  ["data-deletion", "Deletion"],
  ["data-export", "Export"],
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
      disabled={disabled}
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

function Shell({ children }) {
  const isWeb = Platform.OS === "web";
  return (
    <SafeAreaView style={styles.safe}>
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

function HomeScreen({ setScreen, setMode }) {
  function start(nextMode) {
    setMode(nextMode);
    setScreen("analyze");
  }

  return (
    <Shell>
      <Header onHome={() => setScreen("home")} onLegal={() => setScreen("legal")} />
      <View style={styles.hero}>
        <Text style={styles.eyebrow}>Pattern-based review</Text>
        <Text style={styles.heroTitle}>Something Feels Different</Text>
        <Text style={styles.heroSubtitle}>
          Check observable communication cues against the current backend contracts.
        </Text>
        <View style={styles.heroActions}>
          <PressableText
            style={styles.primaryButton}
            textStyle={styles.primaryButtonText}
            onPress={() => start("match")}
          >
            Check communication fit
          </PressableText>
          <PressableText
            style={styles.secondaryButton}
            textStyle={styles.secondaryButtonText}
            onPress={() => start("evidence")}
          >
            Surface cue evidence
          </PressableText>
        </View>
        <Text style={styles.quietText}>
          Use synthetic or permissioned text only. Raw messages are not persisted by default.
        </Text>
      </View>

      <View style={styles.modeGrid}>
        <ModeCard
          label="Communication Fit"
          marker="M"
          body="Score, fit band, positive factors, risk factors, evidence phrases, and cautious explanation."
          onPress={() => start("match")}
        />
        <ModeCard
          label="Cue Evidence"
          marker="E"
          body="Current cue taxonomy evidence rows from the deterministic `/api/analyze` route."
          onPress={() => start("evidence")}
        />
        <ModeCard
          label="Legal Boundaries"
          marker="L"
          body="Draft closed-beta legal copy fetched from the current backend legal routes."
          onPress={() => setScreen("legal")}
        />
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
      <Text style={styles.modeAction}>Look closer</Text>
    </Pressable>
  );
}

function AnalyzeScreen({ mode, setMode, setResult, setScreen }) {
  const { apiUrl, matchClient, backendClient } = useBackendClients();
  const [text, setText] = useState(SAMPLE_TEXT);
  const [consent, setConsent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const apiUrlState = parseBackendBaseUrl(apiUrl);
  const apiConfigured = apiUrlState.ok;
  const canSubmit = Boolean(normalizeText(text)) && consent && apiConfigured && !loading;

  async function handleSubmit() {
    if (!canSubmit) {
      setStatus(
        apiConfigured
          ? "Confirm permission before sending."
          : apiUrlState.status === "missing_api_url"
            ? "Set EXPO_PUBLIC_API_URL first."
            : "EXPO_PUBLIC_API_URL must be a clean http(s) backend base URL."
      );
      return;
    }

    setLoading(true);
    setStatus(mode === "match" ? "Checking communication fit..." : "Surfacing cue evidence...");
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
        setError(response.userMessage || "The backend could not complete this request.");
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
    <Shell>
      <Header onHome={() => setScreen("home")} onLegal={() => setScreen("legal")} />
      <PressableText
        style={styles.backButton}
        textStyle={styles.backButtonText}
        onPress={() => setScreen("home")}
      >
        Back
      </PressableText>

      <View style={styles.card}>
        <Text style={styles.eyebrow}>Backend route</Text>
        <Text style={styles.screenTitle}>Look Again</Text>
        <Text style={styles.helperText}>{formatBackendUrlStatus(apiUrl)}</Text>

        <View style={styles.segmented}>
          <PressableText
            style={[styles.segmentButton, mode === "match" && styles.segmentButtonActive]}
            textStyle={[styles.segmentText, mode === "match" && styles.segmentTextActive]}
            onPress={() => setMode("match")}
          >
            Match
          </PressableText>
          <PressableText
            style={[styles.segmentButton, mode === "evidence" && styles.segmentButtonActive]}
            textStyle={[styles.segmentText, mode === "evidence" && styles.segmentTextActive]}
            onPress={() => setMode("evidence")}
          >
            Evidence
          </PressableText>
        </View>

        <Text style={styles.fieldLabel}>Conversation text</Text>
        <TextInput
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
          style={styles.textArea}
        />

        <View style={styles.disclosureBox}>
          <Text style={styles.disclosureTitle}>Before you analyze</Text>
          <Text style={styles.disclosureText}>
            Vibe Signal is communication-support only. Outputs are pattern-based suggestions, not
            truth claims. Do not submit sensitive personal data, secrets, medical data, legal
            documents, financial data, or third-party private messages without permission.
          </Text>
        </View>

        <Pressable
          style={({ pressed }) => [styles.checkboxRow, pressed && styles.pressed]}
          onPress={() => setConsent((current) => !current)}
        >
          <View style={[styles.checkbox, consent && styles.checkboxChecked]}>
            <Text style={styles.checkboxMark}>{consent ? "OK" : ""}</Text>
          </View>
          <Text style={styles.checkboxLabel}>
            I have permission to process this text and understand the draft legal boundaries.
          </Text>
        </Pressable>

        {status ? <Text style={styles.statusText}>{status}</Text> : null}
        {error ? <Text style={styles.errorText}>{error}</Text> : null}

        <PressableText
          disabled={!canSubmit}
          style={styles.primaryButton}
          textStyle={styles.primaryButtonText}
          onPress={handleSubmit}
        >
          {loading ? "Checking..." : mode === "match" ? "Check fit" : "Surface cues"}
        </PressableText>

        {loading ? <ActivityIndicator color={COLORS.primary} /> : null}
      </View>
    </Shell>
  );
}

function ResultsScreen({ result, setScreen, setMode }) {
  if (!result) {
    return (
      <Shell>
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
    <Shell>
      <Header onHome={() => setScreen("home")} onLegal={() => setScreen("legal")} />
      <PressableText
        style={styles.backButton}
        textStyle={styles.backButtonText}
        onPress={() => setScreen("analyze")}
      >
        Back to input
      </PressableText>

      {result.kind === "match" ? (
        <MatchResult result={result.payload} setScreen={setScreen} setMode={setMode} />
      ) : (
        <EvidenceResult result={result.payload} setScreen={setScreen} setMode={setMode} />
      )}
    </Shell>
  );
}

function MatchResult({ result, setScreen, setMode }) {
  const { backendClient } = useBackendClients();
  const viewModel = buildMatchResultViewModel(result || {});
  const [feedbackConsent, setFeedbackConsent] = useState(false);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [feedbackStatus, setFeedbackStatus] = useState("");
  const [feedbackError, setFeedbackError] = useState("");
  const [submittedFeedbackRatings, setSubmittedFeedbackRatings] = useState([]);

  async function sendFeedback(rating) {
    if (feedbackLoading) {
      return;
    }
    if (submittedFeedbackRatings.includes(rating)) {
      setFeedbackStatus("Feedback metadata already accepted for this result.");
      setFeedbackError("");
      return;
    }
    setFeedbackLoading(true);
    setFeedbackStatus("");
    setFeedbackError("");
    try {
      const response = await backendClient.submitFeedbackMetadata({
        matchId: result?.match_id || "",
        rating,
        consent: feedbackConsent,
      });
      if (response.ok) {
        setSubmittedFeedbackRatings((current) =>
          current.includes(rating) ? current : [...current, rating]
        );
        setFeedbackStatus("Feedback metadata accepted. No raw comment was sent.");
        return;
      }
      setFeedbackError(response.userMessage || "Feedback could not be sent.");
    } finally {
      setFeedbackLoading(false);
    }
  }

  return (
    <>
      <View style={styles.resultHero}>
        <View style={styles.scorePanel}>
          <Text style={styles.scoreLabel}>Compatibility score</Text>
          <Text style={styles.scoreValue}>{viewModel.compatibilityScoreLabel}</Text>
          <Text style={styles.bandPill}>{viewModel.bandLabel}</Text>
        </View>
        <Text style={styles.resultExplanation}>{viewModel.explanation}</Text>
        <Text style={styles.disclosureText}>{viewModel.disclosure}</Text>
      </View>

      <View style={styles.resultGrid}>
        <FactorList
          title="Positive factors"
          items={viewModel.positiveFactors}
          empty={viewModel.emptyPositiveLabel}
        />
        <FactorList
          title="Risk factors"
          items={viewModel.riskFactors}
          empty={viewModel.emptyRiskLabel}
        />
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Evidence safe phrases</Text>
        {(viewModel.evidencePhrases.length
          ? viewModel.evidencePhrases
          : [viewModel.emptyEvidenceLabel]
        ).map((phrase) => (
          <Text key={phrase} style={styles.evidencePhrase}>
            {phrase}
          </Text>
        ))}
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Feedback</Text>
        <Text style={styles.helperText}>Optional metadata-only feedback for this result.</Text>
        <Pressable
          style={({ pressed }) => [styles.checkboxRow, pressed && styles.pressed]}
          onPress={() => setFeedbackConsent((current) => !current)}
        >
          <View style={[styles.checkbox, feedbackConsent && styles.checkboxChecked]}>
            <Text style={styles.checkboxMark}>{feedbackConsent ? "OK" : ""}</Text>
          </View>
          <Text style={styles.checkboxLabel}>Consent to store bounded feedback metadata.</Text>
        </Pressable>
        <View style={styles.buttonRow}>
          <PressableText
            disabled={feedbackLoading || submittedFeedbackRatings.includes(1)}
            style={[styles.secondaryButton, styles.flexButton]}
            textStyle={styles.secondaryButtonText}
            onPress={() => sendFeedback(1)}
          >
            {feedbackLoading ? "Sending..." : "Useful"}
          </PressableText>
          <PressableText
            disabled={feedbackLoading || submittedFeedbackRatings.includes(0)}
            style={[styles.secondaryButton, styles.flexButton]}
            textStyle={styles.secondaryButtonText}
            onPress={() => sendFeedback(0)}
          >
            {feedbackLoading ? "Sending..." : "Not useful"}
          </PressableText>
        </View>
        {feedbackStatus ? <Text style={styles.statusText}>{feedbackStatus}</Text> : null}
        {feedbackError ? <Text style={styles.errorText}>{feedbackError}</Text> : null}
      </View>

      <PressableText
        style={styles.primaryButton}
        textStyle={styles.primaryButtonText}
        onPress={() => {
          setMode("match");
          setScreen("analyze");
        }}
      >
        Analyze another
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
          safe_phrase: "No deterministic cue returned for this text.",
          explanation: "Try a longer synthetic exchange for more surface area.",
        },
      ];

  return (
    <>
      <View style={styles.resultHero}>
        <Text style={styles.eyebrow}>Cue evidence</Text>
        <Text style={styles.screenTitle}>
          {evidence.length ? `${evidence.length} deterministic cues` : "No cue rows returned"}
        </Text>
        <Text style={styles.disclosureText}>
          Evidence rows come from the current cue taxonomy and include safe phrases, explanations,
          interpretation limits, and text hashes.
        </Text>
      </View>

      {rows.map((row, index) => (
        <View style={styles.evidenceCard} key={`${row.evidence_id || row.cue_id}:${index}`}>
          <Text style={styles.evidenceFamily}>
            {normalizeText(row.cue_family || row.cue_id || "cue").replace(/_/g, " ")}
          </Text>
          <Text style={styles.evidencePhrase}>
            {normalizeText(row.safe_phrase || "Safe phrase unavailable.")}
          </Text>
          <Text style={styles.helperText}>
            {normalizeText(row.explanation || "Deterministic cue explanation unavailable.")}
          </Text>
        </View>
      ))}

      <View style={styles.card}>
        <Text style={styles.disclosureText}>
          These results do not infer true emotion, deception, personality, identity, health, or
          relationship outcomes.
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
        Analyze another
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
        setStatus("Set EXPO_PUBLIC_API_URL to fetch the backend legal routes.");
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
      setStatus("Using fallback copy because the legal route did not load.");
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [apiUrl, backendClient, slug]);

  return (
    <Shell>
      <Header onHome={() => setScreen("home")} onLegal={() => setScreen("legal")} />
      <PressableText
        style={styles.backButton}
        textStyle={styles.backButtonText}
        onPress={() => setScreen("home")}
      >
        Back
      </PressableText>

      <View style={styles.card}>
        <Text style={styles.eyebrow}>Legal route</Text>
        <Text style={styles.screenTitle}>{page.title}</Text>
        <Text style={styles.helperText}>Status: {page.status || "draft_requires_legal_review"}</Text>

        <View style={styles.segmented}>
          {LEGAL_PAGES.map(([nextSlug, label]) => (
            <PressableText
              key={nextSlug}
              style={[styles.legalButton, slug === nextSlug && styles.segmentButtonActive]}
              textStyle={[styles.segmentText, slug === nextSlug && styles.segmentTextActive]}
              onPress={() => setSlug(nextSlug)}
            >
              {label}
            </PressableText>
          ))}
        </View>

        {status ? <Text style={styles.statusText}>{status}</Text> : null}
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

  if (screen === "analyze") {
    return (
      <AnalyzeScreen
        mode={mode}
        setMode={setMode}
        setResult={setResult}
        setScreen={setScreen}
      />
    );
  }

  if (screen === "results") {
    return <ResultsScreen result={result} setMode={setMode} setScreen={setScreen} />;
  }

  if (screen === "legal") {
    return <LegalScreen setScreen={setScreen} />;
  }

  return <HomeScreen setMode={setMode} setScreen={setScreen} />;
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
    minHeight: 38,
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
  modeGrid: {
    gap: 10,
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
    minHeight: 34,
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
  segmented: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  segmentButton: {
    minHeight: 40,
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
    minHeight: 38,
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
    fontSize: 40,
    lineHeight: 46,
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
  resultGrid: {
    gap: 10,
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
  buttonRow: {
    flexDirection: "row",
    gap: 10,
  },
  flexButton: {
    flex: 1,
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
