import React from "react";
import { Linking, Pressable, StyleSheet, Text, View } from "react-native";

import { buildPaywallViewModel } from "./paywallViewModel.js";

export function PaywallCard({
  visible = false,
  premiumActive = false,
  softPrompt = false,
  priceDisplay = "",
  purchaseAvailable = false,
  storeMetadata = {},
  purchaseInProgress = false,
  restoreInProgress = false,
  statusMessage = "",
  onContinuePremium,
  onRestorePurchases,
  restoreAvailable = true,
} = {}) {
  if (!visible && !premiumActive) {
    return null;
  }

  const model = buildPaywallViewModel({
    premiumActive,
    softPrompt,
    priceDisplay,
    purchaseAvailable,
    restoreAvailable,
    storeMetadata,
    statusMessage,
  });

  return (
    <View style={[styles.card, premiumActive && styles.cardPremium]}>
      <Text style={styles.eyebrow}>{premiumActive ? "Premium" : softPrompt ? "Upgrade" : "Continue"}</Text>
      <Text style={styles.title}>{model.title}</Text>
      <Text style={styles.body}>{model.body}</Text>
      {!premiumActive ? <Text style={styles.price}>{model.priceDisplay || "Price unavailable"}</Text> : null}
      {model.disclosureLines.map((line) => (
        <Text key={line} style={styles.helper}>
          {line}
        </Text>
      ))}
      {!!model.statusMessage ? <Text style={styles.helper}>{model.statusMessage}</Text> : null}
      {!!model.legalLinksMessage ? <Text style={styles.helper}>{model.legalLinksMessage}</Text> : null}
      {model.legalLinks.length ? (
        <View style={styles.linkRow}>
          {model.legalLinks.map((link) => (
            <Pressable key={link.label} onPress={() => void Linking.openURL(link.url)}>
              <Text style={styles.linkLabel}>{link.label}</Text>
            </Pressable>
          ))}
        </View>
      ) : null}
      {!premiumActive ? (
        <View style={styles.row}>
          <Pressable
            style={[
              styles.primaryButton,
              (!model.purchaseEnabled || purchaseInProgress) && styles.disabled,
            ]}
            disabled={!model.purchaseEnabled || purchaseInProgress}
            onPress={onContinuePremium}
          >
            <Text style={styles.primaryLabel}>
              {purchaseInProgress
                ? "Connecting to App Store..."
                : model.purchaseEnabled
                ? softPrompt
                  ? "Unlock premium"
                  : "Continue with Premium"
                : "Premium unavailable in this build"}
            </Text>
          </Pressable>
          <Pressable
            style={[styles.secondaryButton, (!model.restoreEnabled || restoreInProgress) && styles.disabled]}
            disabled={!model.restoreEnabled || restoreInProgress}
            onPress={onRestorePurchases}
          >
            <Text style={styles.secondaryLabel}>
              {restoreInProgress
                ? "Restoring..."
                : model.restoreEnabled
                ? "Restore purchases"
                : "Restore unavailable"}
            </Text>
          </Pressable>
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#fff7ed",
    borderWidth: 1,
    borderColor: "#ead8bf",
    borderRadius: 22,
    padding: 18,
    gap: 10,
  },
  cardPremium: {
    backgroundColor: "#eaf5ee",
    borderColor: "#c9decc",
  },
  eyebrow: {
    color: "#8c5a2b",
    fontSize: 12,
    fontWeight: "700",
    letterSpacing: 0.8,
    textTransform: "uppercase",
  },
  title: {
    color: "#111827",
    fontSize: 22,
    fontWeight: "800",
  },
  body: {
    color: "#3f454f",
    fontSize: 15,
    lineHeight: 22,
  },
  price: {
    color: "#111827",
    fontSize: 26,
    fontWeight: "800",
  },
  helper: {
    color: "#6b7280",
    fontSize: 13,
    lineHeight: 18,
  },
  row: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  linkRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 14,
  },
  primaryButton: {
    backgroundColor: "#111827",
    borderRadius: 14,
    paddingVertical: 14,
    paddingHorizontal: 16,
  },
  secondaryButton: {
    backgroundColor: "#ffffff",
    borderRadius: 14,
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderWidth: 1,
    borderColor: "#d9c9b0",
  },
  primaryLabel: {
    color: "#ffffff",
    fontWeight: "700",
  },
  secondaryLabel: {
    color: "#1f2937",
    fontWeight: "700",
  },
  linkLabel: {
    color: "#1f2937",
    fontWeight: "700",
    textDecorationLine: "underline",
  },
  disabled: {
    opacity: 0.45,
  },
});
