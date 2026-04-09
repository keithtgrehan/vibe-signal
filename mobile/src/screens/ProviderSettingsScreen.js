import * as DocumentPicker from "expo-document-picker";
import * as FileSystem from "expo-file-system";
import * as Clipboard from "expo-clipboard";
import React, { useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  Share,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import { PaywallCard } from "../components/PaywallCard.js";
import { QuotaBadge } from "../components/QuotaBadge.js";
import { useQuota } from "../hooks/useQuota.js";
import { buildProviderConsentPayload } from "../providers/providerConsent.js";
import { createProviderFlowController } from "../providers/providerFlowController.js";
import {
  buildProviderVerificationModel,
  deriveProviderFlowState,
  formatSavedCredentialLabel,
} from "../providers/providerViewModel.js";
import {
  buildAnalysisComposerState,
  buildLocalAnalysisResult,
  getMobileLayoutMetrics,
} from "./providerScreenModel.js";
import { createAnalysisHistoryStore } from "./analysisHistoryStore.js";

const controller = createProviderFlowController({
  platform: Platform.OS,
});
const historyStore = createAnalysisHistoryStore({
  platform: Platform.OS,
});

async function readTextFromPickedAsset(asset) {
  if (!asset) {
    return "";
  }
  if (asset.file && typeof asset.file.text === "function") {
    return asset.file.text();
  }
  if (typeof FileSystem.readAsStringAsync === "function" && asset.uri) {
    return FileSystem.readAsStringAsync(asset.uri);
  }
  if (asset.uri && typeof fetch === "function") {
    const response = await fetch(asset.uri);
    return response.text();
  }
  return "";
}

export default function ProviderSettingsScreen() {
  const [state, setState] = useState(controller.buildBaseState());
  const [localAnalysisResult, setLocalAnalysisResult] = useState(null);
  const [recentAnalyses, setRecentAnalyses] = useState([]);
  const [analysisText, setAnalysisText] = useState("");
  const [analysisStatusMessage, setAnalysisStatusMessage] = useState("");
  const [showExternalAi, setShowExternalAi] = useState(false);
  const [uploadInProgress, setUploadInProgress] = useState(false);
  const quota = useQuota();

  useEffect(() => {
    let cancelled = false;
    async function load() {
      const recent = await historyStore.getRecentAnalyses();
      const nextState = await controller.hydrateProviderState({
        providerName: "",
        consentAcknowledged: false,
        currentState: state,
      });
      if (!cancelled) {
        setRecentAnalyses(recent);
        setState(nextState);
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  const actions = controller.deriveActions(state);
  const verificationModel = buildProviderVerificationModel({
    selectedProvider: state.selectedProvider,
    draftCredential: state.draftCredential,
    credentialPresent: state.credentialPresent,
    validationStatus: state.validationResult?.status || "",
    validationMessage: state.validationResult?.user_message || "",
    saveMessage: state.saveMessage,
    busy: state.busy,
    pendingAction: state.pendingAction,
  });
  const flowState = deriveProviderFlowState({
    selectedProvider: state.selectedProvider,
    draftCredential: state.draftCredential,
    credentialPresent: state.credentialPresent,
    validationStatus: state.validationResult?.status || "",
    busy: state.busy,
    pendingAction: state.pendingAction,
  });
  const consentPayload = state.selectedProvider
    ? buildProviderConsentPayload(state.selectedProvider)
    : null;
  const providerUnavailable =
    ["provider_timeout", "rate_limited", "provider_unavailable", "unknown_error"].includes(
      state.lastRunResult?.status || state.validationResult?.status || ""
    );
  const canRunSummary = state.validationResult?.status === "ready" && actions.disableRun === false;
  const externalSummary = state.lastRunResult?.external_summary || null;
  const layout = getMobileLayoutMetrics();
  const composerState = buildAnalysisComposerState({
    analysisText,
    loading: quota.loading,
    uploadInProgress,
    analysisInProgress: quota.usage_in_progress,
    paywallRequired: quota.paywall_required,
  });

  const providerButtonLabel = useMemo(() => {
    if (canRunSummary && localAnalysisResult) {
      return state.busy && state.pendingAction === "summary"
        ? "Preparing summary..."
        : "Use this provider";
    }
    return state.busy && state.pendingAction === "verify" ? "Checking key..." : "Verify key";
  }, [canRunSummary, localAnalysisResult, state.busy, state.pendingAction]);

  async function withProviderBusy(action, task) {
    setState((current) => ({ ...current, busy: true, pendingAction: action }));
    try {
      await task();
    } finally {
      setState((current) => ({ ...current, busy: false, pendingAction: "" }));
    }
  }

  function clearProviderMessaging() {
    setState((current) => ({
      ...current,
      validationResult: null,
      lastRunResult: null,
      saveMessage: "",
    }));
  }

  async function handleUpload() {
    setUploadInProgress(true);
    setAnalysisStatusMessage("");
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ["text/plain", "text/*"],
        copyToCacheDirectory: true,
        multiple: false,
      });

      if (result.canceled || !result.assets?.length) {
        return;
      }

      const content = await readTextFromPickedAsset(result.assets[0]);
      const trimmedContent = String(content || "").trim();
      if (!trimmedContent) {
        setAnalysisStatusMessage("We couldn't read text from that file.");
        return;
      }

      setAnalysisText(trimmedContent);
      setAnalysisStatusMessage("Text loaded and ready to analyze.");
      setLocalAnalysisResult(null);
    } catch (_error) {
      setAnalysisStatusMessage("Upload couldn't be completed right now.");
    } finally {
      setUploadInProgress(false);
    }
  }

  async function handleLocalAnalysis() {
    setAnalysisStatusMessage("");
    const normalizedInput = String(analysisText || "").trim();
    if (!normalizedInput) {
      return;
    }
    setAnalysisStatusMessage("Running local analysis...");
    const analysisId = `local_${Date.now().toString(16)}`;
    const result = await quota.recordSuccessfulAnalysis({
      analysisId,
      runAnalysis: async () => buildLocalAnalysisResult(normalizedInput),
    });

    if (result.ok) {
      setLocalAnalysisResult(result.result);
      setAnalysisStatusMessage("See what changed in tone.");
      const recent = await historyStore.addAnalysis({
        id: analysisId,
        inputText: normalizedInput,
        inputPreview: normalizedInput.slice(0, 120),
        headline: result.result.headline,
        pattern: result.result.pattern,
        summary: result.result.summary,
        shareText: result.result.shareText,
        result: result.result,
      });
      setRecentAnalyses(recent);
      return;
    }

    setAnalysisStatusMessage("Analysis couldn't be completed right now.");
  }

  async function handleShareResult() {
    if (!localAnalysisResult?.shareText) {
      return;
    }
    try {
      await Share.share({
        title: localAnalysisResult.shareTitle || "VibeSignal",
        message: localAnalysisResult.shareText,
      });
    } catch (_error) {
      setAnalysisStatusMessage("Share couldn't be completed right now.");
    }
  }

  async function handleCopyResult() {
    if (!localAnalysisResult?.shareText) {
      return;
    }
    try {
      await Clipboard.setStringAsync(localAnalysisResult.shareText);
      setAnalysisStatusMessage("Summary copied.");
    } catch (_error) {
      setAnalysisStatusMessage("Copy couldn't be completed right now.");
    }
  }

  function handleTryAnotherMessage() {
    setAnalysisText("");
    setLocalAnalysisResult(null);
    setAnalysisStatusMessage("Paste another message when you're ready.");
  }

  function handlePasteDifferentConversation() {
    setAnalysisText("");
    setLocalAnalysisResult(null);
    setShowExternalAi(false);
    setAnalysisStatusMessage("Paste a different conversation to compare it with the last one.");
  }

  return (
    <SafeAreaView style={styles.safe}>
      <KeyboardAvoidingView
        style={styles.keyboardSafe}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <ScrollView contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
          <View style={[styles.stack, { maxWidth: layout.maxWidth, padding: layout.padding }]}>
          <View style={styles.hero}>
            <Text style={styles.title}>VibeSignal</Text>
            <Text style={styles.subtitle}>
              See what changed in tone and spot what feels off. Local analysis stays primary.
            </Text>
            <QuotaBadge
              usesLeft={quota.uses_left_label}
              periodLabel={quota.period_label}
              resetTiming={quota.reset_timing}
              premiumActive={quota.premium_active}
            />
          </View>

          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Primary action</Text>
            <Text style={styles.helper}>
              Local analysis is always the primary path. External providers never block this flow.
            </Text>
            <TextInput
              value={analysisText}
              onChangeText={(value) => {
                setAnalysisText(value);
                setAnalysisStatusMessage("");
              }}
              placeholder={composerState.placeholder}
              placeholderTextColor="#6b7280"
              multiline
              numberOfLines={8}
              scrollEnabled
              textAlignVertical="top"
              autoCorrect
              style={[styles.input, styles.textarea]}
            />
            <View style={styles.buttonRow}>
              <Pressable
                style={[styles.secondaryButton, !composerState.uploadEnabled && styles.actionDisabled]}
                disabled={!composerState.uploadEnabled}
                onPress={handleUpload}
              >
                <Text style={styles.secondaryLabel}>
                  {uploadInProgress ? "Loading file..." : "Upload text file"}
                </Text>
              </Pressable>
              <Pressable
                style={[styles.primaryButton, !composerState.analyzeEnabled && styles.actionDisabled]}
                disabled={!composerState.analyzeEnabled}
                onPress={handleLocalAnalysis}
              >
                <Text style={styles.primaryLabel}>
                  {quota.usage_in_progress ? "Analyzing..." : "See what changed"}
                </Text>
              </Pressable>
            </View>
            {!!analysisStatusMessage ? <Text style={styles.helper}>{analysisStatusMessage}</Text> : null}
            {!!quota.status_message && !quota.paywall_required ? (
              <Text style={styles.helper}>{quota.status_message}</Text>
            ) : null}
            {localAnalysisResult ? (
              <View style={styles.resultBox}>
                <Text style={styles.statusTitle}>{localAnalysisResult.headline}</Text>
                <Text style={styles.summarySection}>Pattern</Text>
                <Text style={styles.summaryParagraph}>{localAnalysisResult.pattern}</Text>
                <Text style={styles.summaryParagraph}>{localAnalysisResult.summary}</Text>
                {localAnalysisResult.highlights.map((item) => (
                  <Text key={item} style={styles.bulletLine}>
                    • {item}
                  </Text>
                ))}
                {localAnalysisResult.spans?.map((item) => (
                  <View key={`${item.label}:${item.excerpt}`} style={styles.spanBox}>
                    <Text style={styles.providerMeta}>{item.label}</Text>
                    <Text style={styles.helper}>{item.excerpt}</Text>
                  </View>
                ))}
                <Text style={styles.disclosureText}>{localAnalysisResult.disclosure}</Text>
                <Text style={styles.shareLine}>It can read differently the second time.</Text>
                <View style={styles.buttonRow}>
                  <Pressable style={styles.secondaryButton} onPress={handleShareResult}>
                    <Text style={styles.secondaryLabel}>Share result</Text>
                  </Pressable>
                  <Pressable style={styles.secondaryButton} onPress={handleCopyResult}>
                    <Text style={styles.secondaryLabel}>Copy summary</Text>
                  </Pressable>
                </View>
                <View style={styles.buttonRow}>
                  <Pressable style={styles.ghostButton} onPress={handleTryAnotherMessage}>
                    <Text style={styles.ghostLabel}>{localAnalysisResult.ctaPrimary}</Text>
                  </Pressable>
                  <Pressable style={styles.ghostButton} onPress={handlePasteDifferentConversation}>
                    <Text style={styles.ghostLabel}>{localAnalysisResult.ctaSecondary}</Text>
                  </Pressable>
                </View>
              </View>
            ) : null}

            {recentAnalyses.length ? (
              <View style={styles.recentBlock}>
                <Text style={styles.summarySection}>Recent analyses</Text>
                {recentAnalyses
                  .slice()
                  .reverse()
                  .map((item) => (
                    <Pressable
                      key={item.id}
                      style={styles.historyRow}
                      onPress={() => {
                        setAnalysisText(item.inputText || item.inputPreview);
                        setLocalAnalysisResult(item.result);
                        setAnalysisStatusMessage("Recent analysis reopened.");
                      }}
                    >
                      <Text style={styles.statusTitle}>{item.pattern}</Text>
                      <Text style={styles.helper}>{item.summary}</Text>
                    </Pressable>
                  ))}
              </View>
            ) : null}
          </View>

          <PaywallCard
            visible={quota.upgrade_prompt_visible}
            premiumActive={quota.premium_active}
            softPrompt={quota.upgrade_prompt_stage === "teaser"}
            priceDisplay={quota.price_display}
            purchaseAvailable={quota.purchase_available}
            storeMetadata={{
              privacyPolicyUrl: quota.privacy_policy_url,
              termsUrl: quota.terms_url,
              supportContactRef: quota.support_contact_ref,
              subscriptionDisclosure: quota.subscription_disclosure,
            }}
            purchaseInProgress={quota.purchase_in_progress}
            restoreAvailable={quota.restore_available}
            restoreInProgress={quota.restore_in_progress}
            statusMessage={quota.status_message}
            onContinuePremium={quota.purchasePremium}
            onRestorePurchases={quota.restorePurchases}
          />

          <View style={styles.card}>
            <Pressable
              style={styles.sectionToggle}
              onPress={() => setShowExternalAi((current) => !current)}
            >
              <View style={styles.sectionToggleCopy}>
                <Text style={styles.sectionTitle}>Optional external AI</Text>
                <Text style={styles.helper}>
                  Hidden by default. Local analysis remains the primary result.
                </Text>
              </View>
              <Text style={styles.toggleLabel}>{showExternalAi ? "Hide" : "Show"}</Text>
            </Pressable>

            {showExternalAi ? (
              <View style={styles.externalSection}>
                <View style={styles.providerRow}>
                  {state.providers.map((provider) => (
                    <Pressable
                      key={provider.provider_name}
                      style={[
                        styles.providerButton,
                        state.selectedProvider === provider.provider_name &&
                          styles.providerButtonSelected,
                      ]}
                      onPress={() =>
                        withProviderBusy("select-provider", async () => {
                          const nextState = await controller.hydrateProviderState({
                            providerName: provider.provider_name,
                            consentAcknowledged: state.consentAcknowledged,
                            currentState: {
                              ...state,
                              selectedProvider: provider.provider_name,
                              validationResult: null,
                              lastRunResult: null,
                              draftCredential: "",
                              saveMessage: "",
                            },
                          });
                          setState(nextState);
                        })
                      }
                    >
                      <Text style={styles.providerLabel}>{provider.display_name}</Text>
                    </Pressable>
                  ))}
                </View>

                <TextInput
                  value={state.draftCredential}
                  onChangeText={(value) =>
                    setState((current) => ({
                      ...current,
                      draftCredential: value,
                      validationResult: null,
                      lastRunResult: null,
                      saveMessage: "",
                    }))
                  }
                  placeholder="Paste your provider API key"
                  placeholderTextColor="#6b7280"
                  secureTextEntry
                  autoCapitalize="none"
                  autoCorrect={false}
                  style={styles.input}
                  editable={!state.busy}
                />

                <Text style={styles.savedState}>
                  {state.maskedCredential
                    ? formatSavedCredentialLabel(state.maskedCredential)
                    : "No key saved yet"}
                </Text>

                <View
                  style={[
                    styles.statusPanel,
                    verificationModel.tone === "success" && styles.statusPanelSuccess,
                    verificationModel.tone === "warning" && styles.statusPanelWarning,
                  ]}
                >
                  <Text style={styles.statusTitle}>{verificationModel.title}</Text>
                  <Text style={styles.helper}>{verificationModel.body}</Text>
                  {!!verificationModel.helper ? (
                    <Text style={styles.helper}>{verificationModel.helper}</Text>
                  ) : null}
                </View>

                <View style={styles.buttonRow}>
                  <Pressable
                    style={[styles.primaryButton, actions.disableValidate && styles.actionDisabled]}
                    disabled={actions.disableValidate}
                    onPress={() =>
                      withProviderBusy("verify", async () => {
                        const { state: nextState } = await controller.verifyCredential({
                          providerName: state.selectedProvider,
                          apiKey: state.draftCredential,
                          consentAcknowledged: state.consentAcknowledged,
                          currentState: state,
                        });
                        setState(nextState);
                      })
                    }
                  >
                    <Text style={styles.primaryLabel}>{providerButtonLabel}</Text>
                  </Pressable>

                  {actions.showRemove ? (
                    <Pressable
                      style={[styles.secondaryButton, actions.disableRemove && styles.actionDisabled]}
                      disabled={actions.disableRemove}
                      onPress={() =>
                        withProviderBusy("remove", async () => {
                          const { state: nextState } = await controller.removeCredential({
                            providerName: state.selectedProvider,
                            consentAcknowledged: state.consentAcknowledged,
                            currentState: state,
                          });
                          setState(nextState);
                        })
                      }
                    >
                      <Text style={styles.secondaryLabel}>Remove key</Text>
                    </Pressable>
                  ) : null}

                  {providerUnavailable ? (
                    <Pressable style={styles.ghostButton} onPress={clearProviderMessaging}>
                      <Text style={styles.ghostLabel}>Use local analysis only</Text>
                    </Pressable>
                  ) : null}
                </View>

                {flowState === "verified" && localAnalysisResult && !quota.paywall_required ? (
                  <Pressable
                    style={[styles.primaryButton, actions.disableRun && styles.actionDisabled]}
                    disabled={actions.disableRun}
                    onPress={() =>
                      withProviderBusy("summary", async () => {
                        const { state: nextState } = await controller.runExternalSummary({
                          providerName: state.selectedProvider,
                          consentAcknowledged: state.consentAcknowledged,
                          signalBundle: localAnalysisResult?.signalBundle || {},
                          currentState: state,
                        });
                        setState(nextState);
                      })
                    }
                  >
                    <Text style={styles.primaryLabel}>
                      {state.busy && state.pendingAction === "summary"
                        ? "Preparing summary..."
                        : "Use this provider"}
                    </Text>
                  </Pressable>
                ) : null}

                {state.lastRunResult && state.lastRunResult.status !== "success" && !externalSummary ? (
                  <View style={[styles.resultBox, styles.resultBoxWarning]}>
                    <Text style={styles.statusTitle}>
                      {providerUnavailable ? "Couldn't reach provider" : "External summary unavailable"}
                    </Text>
                    <Text style={styles.helper}>
                      {providerUnavailable
                        ? "Your local analysis still works. Try again in a moment."
                        : state.lastRunResult.user_message}
                    </Text>
                  </View>
                ) : null}

                {externalSummary ? (
                  <View style={styles.resultBox}>
                    <View style={styles.summaryHeader}>
                      <Text style={styles.sectionTitle}>External AI Summary</Text>
                      <Text style={styles.providerMeta}>{externalSummary.provider}</Text>
                    </View>
                    <Text style={styles.summaryIntro}>{externalSummary.intro}</Text>
                    <Text style={styles.summaryParagraph}>{externalSummary.summary}</Text>
                    <Text style={styles.summarySection}>What changed</Text>
                    {externalSummary.what_changed.map((item) => (
                      <Text key={item} style={styles.bulletLine}>
                        • {item}
                      </Text>
                    ))}
                    <Text style={styles.summarySection}>Compare it with</Text>
                    {externalSummary.compare_prompts.map((item) => (
                      <Text key={item} style={styles.comparePrompt}>
                        {item}
                      </Text>
                    ))}
                    <Text style={styles.disclosureText}>{externalSummary.disclosure}</Text>
                  </View>
                ) : null}
              </View>
            ) : null}
          </View>

          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Consent</Text>
            <Text style={styles.helper}>
              {consentPayload?.bullets?.[1] ||
                "Required only for optional external AI. Local analysis still works without this."}
            </Text>
            <Pressable
              style={styles.checkboxRow}
              onPress={() =>
                setState((current) => ({
                  ...current,
                  consentAcknowledged: !current.consentAcknowledged,
                  validationResult: null,
                  lastRunResult: null,
                }))
              }
            >
              <View style={[styles.checkbox, state.consentAcknowledged && styles.checkboxChecked]}>
                {state.consentAcknowledged ? <Text style={styles.checkboxMark}>✓</Text> : null}
              </View>
              <Text style={styles.checkboxLabel}>
                I understand that selected content may be sent to this provider.
              </Text>
            </Pressable>
          </View>

            {state.busy || uploadInProgress ? <ActivityIndicator size="small" color="#111827" /> : null}
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: "#f4efe5",
  },
  keyboardSafe: {
    flex: 1,
  },
  scrollContent: {
    paddingVertical: 16,
  },
  stack: {
    width: "100%",
    alignSelf: "center",
    gap: 16,
  },
  hero: {
    gap: 12,
  },
  title: {
    fontSize: 30,
    fontWeight: "700",
    color: "#111827",
  },
  subtitle: {
    color: "#374151",
    fontSize: 15,
    lineHeight: 22,
  },
  card: {
    width: "100%",
    backgroundColor: "#fffdf8",
    borderRadius: 16,
    padding: 16,
    gap: 12,
    borderWidth: 1,
    borderColor: "#e5ded1",
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#111827",
  },
  helper: {
    color: "#4b5563",
    fontSize: 14,
    lineHeight: 20,
  },
  input: {
    width: "100%",
    borderWidth: 1,
    borderColor: "#d1d5db",
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 12,
    backgroundColor: "#ffffff",
    color: "#111827",
  },
  textarea: {
    minHeight: 160,
  },
  buttonRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  primaryButton: {
    backgroundColor: "#1f2937",
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 14,
  },
  secondaryButton: {
    backgroundColor: "#ffffff",
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 14,
    borderWidth: 1,
    borderColor: "#d6ccba",
  },
  ghostButton: {
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 10,
  },
  actionDisabled: {
    opacity: 0.45,
  },
  primaryLabel: {
    color: "#ffffff",
    fontWeight: "600",
  },
  secondaryLabel: {
    color: "#1f2937",
    fontWeight: "600",
  },
  ghostLabel: {
    color: "#4b5563",
    fontWeight: "600",
  },
  resultBox: {
    padding: 12,
    borderRadius: 12,
    backgroundColor: "#eef5ef",
    gap: 8,
  },
  spanBox: {
    backgroundColor: "#ffffff",
    borderRadius: 10,
    padding: 10,
    gap: 4,
  },
  resultBoxWarning: {
    backgroundColor: "#f8ece7",
  },
  statusTitle: {
    color: "#111827",
    fontSize: 16,
    fontWeight: "700",
  },
  bulletLine: {
    color: "#374151",
    fontSize: 14,
    lineHeight: 20,
  },
  savedState: {
    color: "#1f2937",
    fontSize: 14,
    lineHeight: 20,
  },
  providerRow: {
    flexDirection: "row",
    gap: 10,
    flexWrap: "wrap",
  },
  providerButton: {
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 999,
    backgroundColor: "#ece7dc",
  },
  providerButtonSelected: {
    backgroundColor: "#b7d3c0",
  },
  providerLabel: {
    color: "#111827",
    fontWeight: "600",
  },
  statusPanel: {
    padding: 14,
    borderRadius: 14,
    backgroundColor: "#f6f1e8",
    gap: 6,
  },
  statusPanelSuccess: {
    backgroundColor: "#e6f2e8",
  },
  statusPanelWarning: {
    backgroundColor: "#f8ece7",
  },
  sectionToggle: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: 12,
  },
  sectionToggleCopy: {
    flex: 1,
    gap: 4,
  },
  toggleLabel: {
    color: "#1f2937",
    fontWeight: "600",
  },
  externalSection: {
    gap: 12,
  },
  checkboxRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 12,
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: "#c4b7a0",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#ffffff",
    marginTop: 1,
  },
  checkboxChecked: {
    backgroundColor: "#1f2937",
    borderColor: "#1f2937",
  },
  checkboxMark: {
    color: "#ffffff",
    fontSize: 14,
    fontWeight: "700",
  },
  checkboxLabel: {
    flex: 1,
    color: "#374151",
    fontSize: 14,
    lineHeight: 20,
  },
  summaryHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 12,
  },
  providerMeta: {
    color: "#6b7280",
    fontSize: 12,
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: 0.6,
  },
  summaryIntro: {
    color: "#4b5563",
    fontSize: 13,
    lineHeight: 18,
  },
  summaryParagraph: {
    color: "#111827",
    fontSize: 15,
    lineHeight: 22,
  },
  summarySection: {
    color: "#111827",
    fontSize: 14,
    fontWeight: "700",
    marginTop: 4,
  },
  recentBlock: {
    gap: 8,
    marginTop: 4,
  },
  historyRow: {
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#dfe6df",
    backgroundColor: "#ffffff",
    padding: 12,
    gap: 4,
  },
  comparePrompt: {
    color: "#374151",
    fontSize: 13,
    lineHeight: 18,
  },
  disclosureText: {
    color: "#6b7280",
    fontSize: 12,
    lineHeight: 17,
    marginTop: 4,
  },
  shareLine: {
    color: "#374151",
    fontSize: 13,
    lineHeight: 18,
    fontStyle: "italic",
  },
});
