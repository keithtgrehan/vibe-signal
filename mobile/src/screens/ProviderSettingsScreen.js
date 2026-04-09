import React, { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Switch,
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
  formatSavedCredentialLabel,
} from "../providers/providerViewModel.js";

const controller = createProviderFlowController();

const SAMPLE_SIGNALS = {
  shift_radar: { summary: "Later replies look shorter and less detailed than earlier ones." },
  consistency: { top_reasons: ["Direct answer style weakens after the midpoint."] },
};

export default function ProviderSettingsScreen() {
  const [state, setState] = useState(controller.buildBaseState());
  const [localAnalysisResult, setLocalAnalysisResult] = useState(null);
  const quota = useQuota();

  useEffect(() => {
    let cancelled = false;
    async function load() {
      const nextState = await controller.hydrateProviderState({
        providerName: state.selectedProvider,
        consentAcknowledged: state.consentAcknowledged,
        currentState: state,
      });
      if (!cancelled) {
        setState(nextState);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const actions = controller.deriveActions(state);
  const verificationModel = buildProviderVerificationModel({
    selectedProvider: state.selectedProvider,
    credentialPresent: state.credentialPresent,
    validationStatus: state.validationResult?.status || "",
    validationMessage: state.validationResult?.user_message || "",
    saveMessage: state.saveMessage,
    busy: state.busy,
    pendingAction: state.pendingAction,
  });
  const consentPayload = state.selectedProvider
    ? buildProviderConsentPayload(state.selectedProvider)
    : null;
  const verificationFailed = ["invalid_credentials"].includes(state.validationResult?.status || "");
  const providerUnavailable =
    ["provider_timeout", "rate_limited", "provider_unavailable", "unknown_error"].includes(
      state.lastRunResult?.status || state.validationResult?.status || ""
    );
  const canRunSummary = state.validationResult?.status === "ready" && actions.disableRun === false;
  const externalSummary = state.lastRunResult?.external_summary || null;

  async function withBusy(action, task) {
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

  async function handleLocalAnalysis() {
    const result = await quota.recordSuccessfulAnalysis({
      analysisId: `local_${Date.now().toString(16)}`,
      runAnalysis: async () => ({
        headline: "Local pattern analysis ready",
        summary:
          "Compared with earlier exchanges, later replies read a little shorter and less detailed.",
        highlights: [
          "Detail softens after the midpoint.",
          "Direct answer style is less steady than at the start.",
        ],
      }),
    });

    if (result.ok) {
      setLocalAnalysisResult(result.result);
    }
  }

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>Provider Settings</Text>
        <Text style={styles.subtitle}>
          Local analysis stays primary. External providers are optional and use BYOK stored
          securely on device.
        </Text>

        <View style={styles.monetizationRow}>
          <QuotaBadge
            usesLeft={quota.uses_left_label}
            periodLabel={quota.period_label}
            resetTiming={quota.reset_timing}
            premiumActive={quota.premium_active}
          />
        </View>

        <PaywallCard
          visible={quota.paywall_required}
          premiumActive={quota.premium_active}
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
          <Text style={styles.sectionTitle}>Local Analysis</Text>
          <Text style={styles.helper}>
            Local analysis remains the primary path. Free usage is counted only after a successful completed analysis.
          </Text>
          <Pressable
            style={[
              styles.primaryButton,
              (quota.loading || quota.usage_in_progress || quota.paywall_required) && styles.actionDisabled,
            ]}
            disabled={quota.loading || quota.usage_in_progress || quota.paywall_required}
            onPress={handleLocalAnalysis}
          >
            <Text style={styles.primaryLabel}>
              {quota.usage_in_progress ? "Running local analysis..." : "Run local analysis"}
            </Text>
          </Pressable>
          {!!quota.status_message && !quota.paywall_required ? (
            <Text style={styles.helper}>{quota.status_message}</Text>
          ) : null}
          {localAnalysisResult ? (
            <View style={styles.resultBox}>
              <Text style={styles.statusTitle}>{localAnalysisResult.headline}</Text>
              <Text style={styles.summaryParagraph}>{localAnalysisResult.summary}</Text>
              {localAnalysisResult.highlights.map((item) => (
                <Text key={item} style={styles.bulletLine}>
                  • {item}
                </Text>
              ))}
            </View>
          ) : null}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Choose Provider</Text>
          <View style={styles.providerRow}>
            {state.providers.map((provider) => (
              <Pressable
                key={provider.provider_name}
                style={[
                  styles.providerButton,
                  state.selectedProvider === provider.provider_name && styles.providerButtonSelected,
                ]}
                onPress={() =>
                  withBusy("select-provider", async () => {
                    const nextState = await controller.hydrateProviderState({
                      providerName: provider.provider_name,
                      consentAcknowledged: false,
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
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Optional External Provider</Text>
          <Text style={styles.helper}>{verificationModel.body}</Text>
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
            {!!verificationModel.helper ? (
              <Text style={styles.helper}>{verificationModel.helper}</Text>
            ) : null}
          </View>
          {state.busy && state.pendingAction === "verify" ? (
            <Text style={styles.helper}>
              This only checks whether the key works for this provider.
            </Text>
          ) : null}
          <View style={styles.buttonRow}>
            <Pressable
              style={[styles.primaryButton, actions.disableValidate && styles.actionDisabled]}
              disabled={actions.disableValidate}
              onPress={() =>
                withBusy("verify", async () => {
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
              <Text style={styles.primaryLabel}>
                {state.busy && state.pendingAction === "verify" ? "Checking key..." : "Verify key"}
              </Text>
            </Pressable>
            {actions.showRemove ? (
              <Pressable
                style={[styles.secondaryButton, actions.disableRemove && styles.actionDisabled]}
                disabled={actions.disableRemove}
                onPress={() =>
                  withBusy("remove", async () => {
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
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Consent</Text>
          {consentPayload ? <Text style={styles.helper}>{consentPayload.bullets[1]}</Text> : null}
          <View style={styles.switchRow}>
            <Text style={styles.helper}>I understand that selected content may be sent to this provider.</Text>
            <Switch
              value={state.consentAcknowledged}
              onValueChange={(value) =>
                setState((current) => ({
                  ...current,
                  consentAcknowledged: value,
                  validationResult: null,
                  lastRunResult: null,
                }))
              }
            />
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Readiness</Text>
          <Text style={styles.savedState}>{verificationModel.title}</Text>
          {!!verificationModel.body ? <Text style={styles.helper}>{verificationModel.body}</Text> : null}
          {state.credentialPresent && state.validationResult?.status === "ready" ? (
            <Text style={styles.savedState}>Ready to use</Text>
          ) : null}
          {verificationFailed ? <Text style={styles.helper}>Check the key and try again.</Text> : null}
        </View>

        <View style={styles.card}>
          <View style={styles.summaryHeader}>
            <Text style={styles.sectionTitle}>External AI Summary</Text>
            {externalSummary?.provider ? (
              <Text style={styles.providerMeta}>{externalSummary.provider}</Text>
            ) : null}
          </View>
          <Text style={styles.summaryIntro}>
            This is a secondary summary based on the selected provider. Local pattern analysis
            remains the primary result.
          </Text>
          {!state.credentialPresent ? (
            <Text style={styles.helper}>Verify a key to enable external summaries.</Text>
          ) : null}
          {!localAnalysisResult ? (
            <Text style={styles.helper}>Run local analysis first, then compare it with a secondary external summary.</Text>
          ) : null}
          {state.credentialPresent && state.validationResult?.status !== "ready" ? (
            <Text style={styles.helper}>Verify key to enable external summaries.</Text>
          ) : null}
          {canRunSummary && localAnalysisResult && !quota.paywall_required ? (
            <Pressable
              style={[styles.primaryButton, actions.disableRun && styles.actionDisabled]}
              disabled={actions.disableRun}
              onPress={() =>
                withBusy("summary", async () => {
                  const { state: nextState } = await controller.runExternalSummary({
                    providerName: state.selectedProvider,
                    consentAcknowledged: state.consentAcknowledged,
                    signalBundle: SAMPLE_SIGNALS,
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
              <Text style={styles.helper}>{externalSummary.intro}</Text>
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

        {state.busy ? <ActivityIndicator size="small" color="#111827" /> : null}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: "#f4efe5",
  },
  container: {
    padding: 20,
    gap: 16,
  },
  monetizationRow: {
    gap: 12,
  },
  title: {
    fontSize: 28,
    fontWeight: "700",
    color: "#111827",
  },
  subtitle: {
    color: "#374151",
    fontSize: 15,
    lineHeight: 22,
  },
  card: {
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
  helper: {
    color: "#4b5563",
    fontSize: 14,
    lineHeight: 20,
  },
  savedState: {
    color: "#1f2937",
    fontSize: 14,
    lineHeight: 20,
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
  statusTitle: {
    color: "#111827",
    fontSize: 16,
    fontWeight: "700",
  },
  input: {
    borderWidth: 1,
    borderColor: "#d1d5db",
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 12,
    backgroundColor: "#ffffff",
    color: "#111827",
  },
  buttonRow: {
    flexDirection: "row",
    gap: 10,
    flexWrap: "wrap",
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
  switchRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 12,
  },
  resultBox: {
    padding: 12,
    borderRadius: 12,
    backgroundColor: "#eef5ef",
    gap: 8,
  },
  resultBoxWarning: {
    backgroundColor: "#f8ece7",
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
  disclosureText: {
    color: "#6b7280",
    fontSize: 12,
    lineHeight: 17,
    marginTop: 4,
  },
});
