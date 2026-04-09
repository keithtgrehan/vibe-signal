import React from "react";
import { Linking, Pressable, StyleSheet, Text, View } from "react-native";

import { buildPaywallViewModel } from "./paywallViewModel.js";

export function PaywallCard({
  visible = false,
  premiumActive = false,
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
    priceDisplay,
    purchaseAvailable,
    restoreAvailable,
    storeMetadata,
    statusMessage,
  });

  return (
    <View style={[styles.card, premiumActive && styles.cardPremium]}>
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
                ? "Continue with Premium"
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
    backgroundColor: "#fff4e8",
    borderWidth: 1,
    borderColor: "#e8d7bf",
    borderRadius: 16,
    padding: 16,
    gap: 10,
  },
  cardPremium: {
    backgroundColor: "#edf6ef",
    borderColor: "#c8dec8",
  },
  title: {
    color: "#111827",
    fontSize: 18,
    fontWeight: "700",
  },
  body: {
    color: "#374151",
    fontSize: 14,
    lineHeight: 20,
  },
  price: {
    color: "#111827",
    fontSize: 20,
    fontWeight: "700",
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
  primaryLabel: {
    color: "#ffffff",
    fontWeight: "600",
  },
  secondaryLabel: {
    color: "#1f2937",
    fontWeight: "600",
  },
  linkLabel: {
    color: "#1f2937",
    fontWeight: "600",
    textDecorationLine: "underline",
  },
  disabled: {
    opacity: 0.45,
  },
});
