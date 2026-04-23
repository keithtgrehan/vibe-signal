import * as Clipboard from "expo-clipboard";
import * as DocumentPicker from "expo-document-picker";
import * as FileSystem from "expo-file-system";
import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  Share,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import { PaywallCard } from "../components/PaywallCard.js";
import { SignalShareCard } from "../components/SignalShareCard.js";
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
  selectHeroHeadline,
} from "./providerScreenModel.js";
import { sanitizeLocalAnalysisResult } from "./localAnalysisGuardrails.js";
import { createAnalysisHistoryStore } from "./analysisHistoryStore.js";

const controller = createProviderFlowController({
  platform: Platform.OS,
});
const historyStore = createAnalysisHistoryStore({
  platform: Platform.OS,
});

function buildPressableStyle(baseStyle, pressedStyle, disabled, pressed, extraStyles = []) {
  return [baseStyle, ...extraStyles, pressed && !disabled && pressedStyle, disabled && styles.actionDisabled];
}

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
  const [shareCardPrepared, setShareCardPrepared] = useState(false);
  const [resultRevealStage, setResultRevealStage] = useState(0);
  const [revealMode, setRevealMode] = useState("idle");
  const revealTimersRef = useRef([]);
  const quota = useQuota();

  function clearRevealTimers() {
    revealTimersRef.current.forEach((timer) => clearTimeout(timer));
    revealTimersRef.current = [];
  }

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
      clearRevealTimers();
    };
  }, []);

  useEffect(() => {
    clearRevealTimers();
    if (!localAnalysisResult) {
      setResultRevealStage(0);
      return;
    }
    if (revealMode !== "staged") {
      setResultRevealStage(3);
      return;
    }
    setResultRevealStage(0);
    revealTimersRef.current = [
      setTimeout(() => setResultRevealStage(1), 180),
      setTimeout(() => setResultRevealStage(2), 360),
      setTimeout(() => setResultRevealStage(3), 560),
    ];

    return () => {
      clearRevealTimers();
    };
  }, [localAnalysisResult, revealMode]);

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
  const heroHeadline = useMemo(
    () =>
      selectHeroHeadline({
        analysisText,
        hasResult: Boolean(localAnalysisResult),
      }),
    [analysisText, localAnalysisResult]
  );
  const providerButtonLabel = useMemo(() => {
    if (canRunSummary && localAnalysisResult) {
      return state.busy && state.pendingAction === "summary"
        ? "Preparing summary..."
        : "Use this provider";
    }
    return state.busy && state.pendingAction === "verify" ? "Checking key..." : "Verify key";
  }, [canRunSummary, localAnalysisResult, state.busy, state.pendingAction]);
  const usageCaption = useMemo(() => {
    if (quota.premium_active) {
      return "Premium active. Unlimited local checks on this device.";
    }
    return [quota.uses_left_label, quota.reset_timing].filter(Boolean).join(" • ");
  }, [quota.premium_active, quota.reset_timing, quota.uses_left_label]);

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

  function clearCurrentResult() {
    setLocalAnalysisResult(null);
    setRevealMode("idle");
    setShareCardPrepared(false);
  }

  function presentResult(result, { staged = false } = {}) {
    const safeResult = sanitizeLocalAnalysisResult(result || {});
    setShareCardPrepared(false);
    setRevealMode(staged ? "staged" : "instant");
    setLocalAnalysisResult(safeResult);
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
      setAnalysisStatusMessage("Message loaded. Ready when you are.");
      clearCurrentResult();
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
    setAnalysisStatusMessage(composerState.loadingLabel);
    clearCurrentResult();
    const analysisId = `local_${Date.now().toString(16)}`;
    const result = await quota.recordSuccessfulAnalysis({
      analysisId,
      runAnalysis: async () => buildLocalAnalysisResult(normalizedInput),
    });

    if (result.ok) {
      presentResult(result.result, { staged: true });
      setAnalysisStatusMessage(
        result.result.analysisMode === "fallback" ? "Nothing clearly changed here." : "Here’s what changed."
      );
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

    setAnalysisStatusMessage("This couldn't be read clearly right now.");
  }

  async function handleShareResult() {
    if (!localAnalysisResult?.shareText) {
      return;
    }
    try {
      await Share.share({
        title: localAnalysisResult.shareTitle || "VibeSignal",
        message: [localAnalysisResult.headline, ...localAnalysisResult.highlights].join("\n"),
      });
      setAnalysisStatusMessage("Share sheet ready.");
    } catch (_error) {
      try {
        await Clipboard.setStringAsync(localAnalysisResult.shareText);
        setAnalysisStatusMessage("Share text copied for you.");
      } catch (_clipboardError) {
        setAnalysisStatusMessage("Share couldn't be completed right now.");
      }
    }
  }

  async function handleCopyResult() {
    if (!localAnalysisResult?.shareText) {
      return;
    }
    try {
      await Clipboard.setStringAsync(
        [localAnalysisResult.headline, localAnalysisResult.shareText, localAnalysisResult.suggestion]
          .filter(Boolean)
          .join("\n")
      );
      setAnalysisStatusMessage("Insight text copied.");
    } catch (_error) {
      setAnalysisStatusMessage("Copy couldn't be completed right now.");
    }
  }

  function handlePrepareScreenshot() {
    setShareCardPrepared((current) => {
      const next = !current;
      setAnalysisStatusMessage(next ? "Share card ready for screenshot." : "Back to the full result.");
      return next;
    });
  }

  function handleTryAnotherMessage() {
    setAnalysisText("");
    clearCurrentResult();
    setAnalysisStatusMessage("Paste another message to spot the next shift.");
  }

  function handlePasteDifferentConversation() {
    setAnalysisText("");
    clearCurrentResult();
    setShowExternalAi(false);
    setAnalysisStatusMessage("Paste a different conversation to compare a new signal.");
  }

  return (
    <SafeAreaView style={styles.safe}>
      <KeyboardAvoidingView
        style={styles.keyboardSafe}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
          keyboardDismissMode="on-drag"
          showsVerticalScrollIndicator={false}
        >
          <View
            style={[
              styles.stack,
              {
                maxWidth: layout.maxWidth,
                paddingHorizontal: layout.padding,
              },
            ]}
          >
            <View style={styles.hero}>
              <Text style={styles.heroEyebrow}>VibeSignal</Text>
              <Text style={styles.heroTitle}>{heroHeadline}</Text>
              <Text style={styles.heroSubtitle}>
                Paste a message. We highlight what changed - tone, intent, and meaning.
              </Text>
            </View>

            <View style={styles.inputCard}>
              <Text style={styles.inputLabel}>Paste a message</Text>
              <Text style={styles.inputHelper}>
                Drop in one message or a short exchange. We compare the opening against what comes
                later.
              </Text>
              <TextInput
                value={analysisText}
                onChangeText={(value) => {
                  setAnalysisText(value);
                  setAnalysisStatusMessage("");
                }}
                placeholder={composerState.placeholder}
                placeholderTextColor="#7b7280"
                multiline
                numberOfLines={8}
                scrollEnabled
                textAlignVertical="top"
                autoCorrect={false}
                style={[styles.input, styles.textarea]}
              />

              <Pressable
                style={({ pressed }) =>
                  buildPressableStyle(
                    styles.uploadButton,
                    styles.buttonPressed,
                    !composerState.uploadEnabled,
                    pressed
                  )
                }
                disabled={!composerState.uploadEnabled}
                onPress={handleUpload}
              >
                <Text style={styles.uploadButtonLabel}>
                  {uploadInProgress ? "Loading file..." : "Upload text file"}
                </Text>
              </Pressable>

              <Pressable
                style={({ pressed }) =>
                  buildPressableStyle(
                    styles.ctaButton,
                    styles.buttonPressed,
                    !composerState.analyzeEnabled,
                    pressed
                  )
                }
                disabled={!composerState.analyzeEnabled}
                onPress={handleLocalAnalysis}
              >
                <Text style={styles.ctaLabel}>
                  {quota.usage_in_progress ? composerState.loadingLabel : composerState.ctaLabel}
                </Text>
              </Pressable>

              {!!analysisStatusMessage ? (
                <Text style={styles.statusMessage}>{analysisStatusMessage}</Text>
              ) : null}
              {!!quota.status_message && !quota.paywall_required ? (
                <Text style={styles.usageMeta}>{quota.status_message}</Text>
              ) : null}
              {!!usageCaption ? <Text style={styles.usageMeta}>{usageCaption}</Text> : null}
            </View>

            {localAnalysisResult ? (
              <View style={[styles.resultCard, shareCardPrepared && styles.resultCardPrepared]}>
                {resultRevealStage === 0 ? (
                  <View style={styles.revealLoading}>
                    <ActivityIndicator size="small" color="#d8e1ef" />
                    <Text style={styles.revealLoadingText}>Reading the clearest signal...</Text>
                  </View>
                ) : null}

                {resultRevealStage >= 1 ? (
                  <View style={styles.resultHeader}>
                    <View style={styles.resultHeaderCopy}>
                      <Text style={styles.resultEyebrow}>Headline insight</Text>
                      <Text style={styles.resultHeadline}>{localAnalysisResult.headline}</Text>
                    </View>
                    <View style={styles.signalPill}>
                      <Text style={styles.signalPillLabel}>{localAnalysisResult.signalLabel}</Text>
                    </View>
                  </View>
                ) : null}

                {resultRevealStage >= 1 ? (
                  <>
                    <Text style={styles.resultPattern}>{localAnalysisResult.pattern}</Text>
                    <Text style={styles.resultSummary}>{localAnalysisResult.summary}</Text>
                    {!!localAnalysisResult.suggestion ? (
                      <Text style={styles.suggestionText}>{localAnalysisResult.suggestion}</Text>
                    ) : null}
                  </>
                ) : null}

                {resultRevealStage >= 2 ? (
                  <View style={styles.sectionBlock}>
                    <Text style={styles.sectionEyebrow}>What changed</Text>
                    {localAnalysisResult.highlights.map((item) => (
                      <View key={item} style={styles.bulletRow}>
                        <View style={styles.bulletDot} />
                        <Text style={styles.bulletText}>{item}</Text>
                      </View>
                    ))}
                  </View>
                ) : null}

                {resultRevealStage >= 3 ? (
                  <>
                    <View style={styles.sectionBlock}>
                      <Text style={styles.sectionEyebrow}>Where it changed</Text>
                      {localAnalysisResult.spans?.map((item) => (
                        <View key={`${item.label}:${item.excerpt}`} style={styles.spanCard}>
                          <View style={styles.spanHeader}>
                            <Text style={styles.spanLabel}>{item.label}</Text>
                            {!!item.note ? <Text style={styles.spanNote}>{item.note}</Text> : null}
                          </View>
                          <Text style={styles.spanExcerpt}>{item.excerpt}</Text>
                        </View>
                      ))}
                    </View>

                    <View style={styles.sectionBlock}>
                      <Text style={styles.sectionEyebrow}>Share this signal</Text>
                      <SignalShareCard
                        headline={localAnalysisResult.headline}
                        highlights={localAnalysisResult.highlights}
                        suggestion={localAnalysisResult.suggestion}
                        prepared={shareCardPrepared}
                      />
                    </View>

                    <Text style={styles.disclosureText}>{localAnalysisResult.disclosure}</Text>

                    <View style={styles.buttonRow}>
                      <Pressable
                        style={({ pressed }) =>
                          buildPressableStyle(
                            styles.secondaryButton,
                            styles.buttonPressedLight,
                            false,
                            pressed,
                            [styles.flexButton]
                          )
                        }
                        onPress={handleShareResult}
                      >
                        <Text style={styles.secondaryLabel}>Share this signal</Text>
                      </Pressable>
                      <Pressable
                        style={({ pressed }) =>
                          buildPressableStyle(
                            styles.secondaryButton,
                            styles.buttonPressedLight,
                            false,
                            pressed,
                            [styles.flexButton]
                          )
                        }
                        onPress={handlePrepareScreenshot}
                      >
                        <Text style={styles.secondaryLabel}>
                          {shareCardPrepared ? "Exit screenshot mode" : "Prepare for screenshot"}
                        </Text>
                      </Pressable>
                    </View>

                    <View style={styles.buttonRow}>
                      <Pressable
                        style={({ pressed }) =>
                          buildPressableStyle(
                            styles.ghostButton,
                            styles.buttonPressedDark,
                            false,
                            pressed,
                            [styles.flexButton]
                          )
                        }
                        onPress={handleCopyResult}
                      >
                        <Text style={styles.ghostLabel}>Copy insight text</Text>
                      </Pressable>
                      <Pressable
                        style={({ pressed }) =>
                          buildPressableStyle(
                            styles.ghostButton,
                            styles.buttonPressedDark,
                            false,
                            pressed,
                            [styles.flexButton]
                          )
                        }
                        onPress={handleTryAnotherMessage}
                      >
                        <Text style={styles.ghostLabel}>{localAnalysisResult.ctaPrimary}</Text>
                      </Pressable>
                      <Pressable
                        style={({ pressed }) =>
                          buildPressableStyle(
                            styles.ghostButton,
                            styles.buttonPressedDark,
                            false,
                            pressed,
                            [styles.flexButton]
                          )
                        }
                        onPress={handlePasteDifferentConversation}
                      >
                        <Text style={styles.ghostLabel}>{localAnalysisResult.ctaSecondary}</Text>
                      </Pressable>
                    </View>
                  </>
                ) : null}
              </View>
            ) : null}

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

            {recentAnalyses.length ? (
              <View style={styles.card}>
                <Text style={styles.sectionTitle}>Recent signals</Text>
                <Text style={styles.helper}>
                  Reopen a recent read and keep comparing without starting from scratch.
                </Text>
                <View style={styles.recentList}>
                  {recentAnalyses
                    .slice()
                    .reverse()
                    .map((item) => (
                      <Pressable
                        key={item.id}
                        style={({ pressed }) =>
                          buildPressableStyle(styles.historyRow, styles.buttonPressedLight, false, pressed)
                        }
                        onPress={() => {
                          setAnalysisText(item.inputText || item.inputPreview);
                          presentResult(item.result, { staged: false });
                          setAnalysisStatusMessage("This reads differently.");
                        }}
                      >
                        <Text style={styles.historyHeadline}>{item.headline}</Text>
                        <Text style={styles.historyPattern}>{item.pattern}</Text>
                      </Pressable>
                    ))}
                </View>
              </View>
            ) : null}

            <View style={styles.card}>
              <Pressable
                style={({ pressed }) =>
                  buildPressableStyle(styles.sectionToggle, styles.buttonPressedLight, false, pressed)
                }
                onPress={() => setShowExternalAi((current) => !current)}
              >
                <View style={styles.sectionToggleCopy}>
                  <Text style={styles.sectionTitle}>Optional BYOK</Text>
                  <Text style={styles.helper}>
                    Use your own provider for an extra summary after the local signal check.
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
                        style={({ pressed }) =>
                          buildPressableStyle(
                            styles.providerButton,
                            styles.buttonPressedLight,
                            false,
                            pressed,
                            [
                              state.selectedProvider === provider.provider_name &&
                                styles.providerButtonSelected,
                            ]
                          )
                        }
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
                    placeholderTextColor="#7b7280"
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
                      style={({ pressed }) =>
                        buildPressableStyle(
                          styles.primaryButton,
                          styles.buttonPressed,
                          actions.disableValidate,
                          pressed,
                          [styles.flexButton]
                        )
                      }
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
                        style={({ pressed }) =>
                          buildPressableStyle(
                            styles.secondaryButton,
                            styles.buttonPressedLight,
                            actions.disableRemove,
                            pressed,
                            [styles.flexButton]
                          )
                        }
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
                      <Pressable
                        style={({ pressed }) =>
                          buildPressableStyle(
                            styles.ghostButton,
                            styles.buttonPressedDark,
                            false,
                            pressed,
                            [styles.flexButton]
                          )
                        }
                        onPress={clearProviderMessaging}
                      >
                        <Text style={styles.ghostLabel}>Use local analysis only</Text>
                      </Pressable>
                    ) : null}
                  </View>

                  {flowState === "verified" && localAnalysisResult && !quota.paywall_required ? (
                    <Pressable
                      style={({ pressed }) =>
                        buildPressableStyle(
                          styles.primaryButton,
                          styles.buttonPressed,
                          actions.disableRun,
                          pressed
                        )
                      }
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
                style={({ pressed }) =>
                  buildPressableStyle(styles.checkboxRow, styles.buttonPressedLight, false, pressed)
                }
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

            {state.busy || uploadInProgress ? <ActivityIndicator size="small" color="#121826" /> : null}
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: "#f5efe6",
  },
  keyboardSafe: {
    flex: 1,
  },
  scrollContent: {
    paddingTop: 24,
    paddingBottom: 40,
  },
  stack: {
    width: "100%",
    alignSelf: "center",
    gap: 20,
  },
  hero: {
    gap: 12,
    paddingTop: 6,
  },
  heroEyebrow: {
    color: "#8c5a2b",
    fontSize: 12,
    fontWeight: "700",
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  heroTitle: {
    color: "#121826",
    fontSize: 34,
    lineHeight: 40,
    fontWeight: "800",
  },
  heroSubtitle: {
    color: "#514738",
    fontSize: 16,
    lineHeight: 24,
  },
  inputCard: {
    width: "100%",
    backgroundColor: "#fffaf3",
    borderRadius: 24,
    borderWidth: 1,
    borderColor: "#eadcc8",
    padding: 22,
    gap: 16,
    shadowColor: "#1f1304",
    shadowOpacity: 0.08,
    shadowRadius: 18,
    shadowOffset: { width: 0, height: 10 },
    elevation: 3,
  },
  inputLabel: {
    color: "#121826",
    fontSize: 18,
    fontWeight: "700",
  },
  inputHelper: {
    color: "#62584c",
    fontSize: 14,
    lineHeight: 21,
  },
  input: {
    width: "100%",
    borderWidth: 1,
    borderColor: "#d9ccb8",
    borderRadius: 18,
    paddingHorizontal: 16,
    paddingVertical: 16,
    backgroundColor: "#ffffff",
    color: "#111827",
    fontSize: 15,
    lineHeight: 23,
  },
  textarea: {
    minHeight: 220,
  },
  uploadButton: {
    minHeight: 54,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: "#d7c5aa",
    backgroundColor: "#fff6ea",
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 16,
  },
  uploadButtonLabel: {
    color: "#4d3a24",
    fontSize: 15,
    fontWeight: "700",
  },
  ctaButton: {
    minHeight: 58,
    borderRadius: 18,
    backgroundColor: "#111827",
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 18,
  },
  ctaLabel: {
    color: "#ffffff",
    fontSize: 16,
    fontWeight: "800",
  },
  statusMessage: {
    color: "#1e3a2d",
    fontSize: 14,
    lineHeight: 20,
    fontWeight: "600",
  },
  usageMeta: {
    color: "#6a6258",
    fontSize: 13,
    lineHeight: 18,
  },
  card: {
    width: "100%",
    backgroundColor: "#fffaf3",
    borderRadius: 22,
    padding: 20,
    gap: 14,
    borderWidth: 1,
    borderColor: "#eadcc8",
  },
  resultCard: {
    width: "100%",
    backgroundColor: "#121826",
    borderRadius: 28,
    padding: 22,
    gap: 18,
    shadowColor: "#121826",
    shadowOpacity: 0.18,
    shadowRadius: 18,
    shadowOffset: { width: 0, height: 12 },
    elevation: 4,
  },
  resultCardPrepared: {
    paddingTop: 24,
    paddingBottom: 26,
  },
  revealLoading: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  revealLoadingText: {
    color: "#d8e1ef",
    fontSize: 14,
    lineHeight: 20,
    fontWeight: "600",
  },
  resultHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: 12,
  },
  resultHeaderCopy: {
    flex: 1,
    gap: 8,
  },
  resultEyebrow: {
    color: "#d9dfe8",
    fontSize: 12,
    fontWeight: "700",
    letterSpacing: 0.8,
    textTransform: "uppercase",
  },
  resultHeadline: {
    color: "#ffffff",
    fontSize: 30,
    lineHeight: 36,
    fontWeight: "800",
  },
  signalPill: {
    borderRadius: 999,
    backgroundColor: "#243246",
    paddingVertical: 9,
    paddingHorizontal: 12,
  },
  signalPillLabel: {
    color: "#f8fafc",
    fontSize: 12,
    fontWeight: "700",
  },
  resultPattern: {
    color: "#f7f9fb",
    fontSize: 16,
    lineHeight: 24,
  },
  resultSummary: {
    color: "#b4c0cf",
    fontSize: 14,
    lineHeight: 21,
  },
  suggestionText: {
    color: "#9dc3b0",
    fontSize: 13,
    lineHeight: 20,
    fontWeight: "600",
  },
  sectionBlock: {
    gap: 14,
  },
  sectionEyebrow: {
    color: "#c8d1dd",
    fontSize: 12,
    fontWeight: "700",
    letterSpacing: 0.8,
    textTransform: "uppercase",
  },
  bulletRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 10,
  },
  bulletDot: {
    width: 7,
    height: 7,
    borderRadius: 999,
    backgroundColor: "#7dd3a6",
    marginTop: 7,
  },
  bulletText: {
    flex: 1,
    color: "#eef2f7",
    fontSize: 15,
    lineHeight: 22,
  },
  spanCard: {
    backgroundColor: "#1b2636",
    borderRadius: 18,
    padding: 14,
    gap: 8,
    borderWidth: 1,
    borderColor: "#2b3950",
  },
  spanHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 8,
  },
  spanLabel: {
    color: "#ffffff",
    fontSize: 13,
    fontWeight: "700",
  },
  spanNote: {
    color: "#9fd8bc",
    fontSize: 12,
    fontWeight: "700",
  },
  spanExcerpt: {
    color: "#c6d2e0",
    fontSize: 13,
    lineHeight: 20,
  },
  disclosureText: {
    color: "#b4c0cf",
    fontSize: 12,
    lineHeight: 18,
  },
  buttonRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  flexButton: {
    flexGrow: 1,
  },
  primaryButton: {
    minHeight: 50,
    backgroundColor: "#111827",
    borderRadius: 14,
    paddingVertical: 12,
    paddingHorizontal: 16,
    alignItems: "center",
    justifyContent: "center",
  },
  secondaryButton: {
    minHeight: 50,
    backgroundColor: "#ffffff",
    borderRadius: 14,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderWidth: 1,
    borderColor: "#dbc9af",
    alignItems: "center",
    justifyContent: "center",
  },
  ghostButton: {
    minHeight: 50,
    borderRadius: 14,
    paddingVertical: 12,
    paddingHorizontal: 14,
    backgroundColor: "#1b2636",
    alignItems: "center",
    justifyContent: "center",
  },
  buttonPressed: {
    opacity: 0.92,
    transform: [{ scale: 0.985 }],
  },
  buttonPressedLight: {
    opacity: 0.88,
    transform: [{ scale: 0.99 }],
  },
  buttonPressedDark: {
    opacity: 0.84,
    transform: [{ scale: 0.99 }],
  },
  actionDisabled: {
    opacity: 0.45,
  },
  primaryLabel: {
    color: "#ffffff",
    fontWeight: "700",
  },
  secondaryLabel: {
    color: "#1f2937",
    fontWeight: "700",
    textAlign: "center",
  },
  ghostLabel: {
    color: "#eef2f7",
    fontWeight: "700",
    textAlign: "center",
  },
  sectionTitle: {
    fontSize: 19,
    fontWeight: "700",
    color: "#121826",
  },
  helper: {
    color: "#5d5447",
    fontSize: 14,
    lineHeight: 21,
  },
  recentList: {
    gap: 10,
  },
  historyRow: {
    borderRadius: 16,
    borderWidth: 1,
    borderColor: "#e4d8c7",
    backgroundColor: "#ffffff",
    padding: 14,
    gap: 6,
  },
  historyHeadline: {
    color: "#121826",
    fontSize: 16,
    fontWeight: "700",
  },
  historyPattern: {
    color: "#4d5a6c",
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
    backgroundColor: "#efe3cf",
  },
  providerButtonSelected: {
    backgroundColor: "#bfdcc9",
  },
  providerLabel: {
    color: "#121826",
    fontWeight: "700",
  },
  savedState: {
    color: "#2a3340",
    fontSize: 14,
    lineHeight: 20,
  },
  statusPanel: {
    padding: 14,
    borderRadius: 16,
    backgroundColor: "#f8f1e6",
    gap: 6,
  },
  statusPanelSuccess: {
    backgroundColor: "#e7f4eb",
  },
  statusPanelWarning: {
    backgroundColor: "#fbede5",
  },
  statusTitle: {
    color: "#121826",
    fontSize: 16,
    fontWeight: "700",
  },
  sectionToggle: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: 12,
    borderRadius: 14,
  },
  sectionToggleCopy: {
    flex: 1,
    gap: 4,
  },
  toggleLabel: {
    color: "#8c5a2b",
    fontWeight: "700",
  },
  externalSection: {
    gap: 14,
  },
  resultBox: {
    padding: 14,
    borderRadius: 16,
    backgroundColor: "#edf4ee",
    gap: 8,
  },
  resultBoxWarning: {
    backgroundColor: "#faeee8",
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
    fontWeight: "700",
    textTransform: "uppercase",
    letterSpacing: 0.6,
  },
  summaryIntro: {
    color: "#55606f",
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
  bulletLine: {
    color: "#374151",
    fontSize: 14,
    lineHeight: 20,
  },
  comparePrompt: {
    color: "#374151",
    fontSize: 13,
    lineHeight: 18,
  },
  checkboxRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 12,
    borderRadius: 14,
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: "#c9baa1",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#ffffff",
    marginTop: 1,
  },
  checkboxChecked: {
    backgroundColor: "#111827",
    borderColor: "#111827",
  },
  checkboxMark: {
    color: "#ffffff",
    fontSize: 14,
    fontWeight: "700",
  },
  checkboxLabel: {
    flex: 1,
    color: "#4b5563",
    fontSize: 14,
    lineHeight: 20,
  },
});
