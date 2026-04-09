import React from "react";
import { StyleSheet, Text, View } from "react-native";

export function QuotaBadge({
  usesLeft = "",
  periodLabel = "",
  resetTiming = "",
  premiumActive = false,
} = {}) {
  return (
    <View style={[styles.badge, premiumActive && styles.badgePremium]}>
      <Text style={styles.eyebrow}>{premiumActive ? "Premium" : periodLabel || "Usage"}</Text>
      <Text style={styles.value}>{premiumActive ? "Unlimited" : usesLeft || "0 left"}</Text>
      <Text style={styles.helper}>{resetTiming || "Refreshes automatically"}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    backgroundColor: "#f6f1e8",
    borderRadius: 16,
    padding: 14,
    gap: 4,
  },
  badgePremium: {
    backgroundColor: "#e7f2e8",
  },
  eyebrow: {
    color: "#6b7280",
    fontSize: 12,
    fontWeight: "700",
    textTransform: "uppercase",
    letterSpacing: 0.6,
  },
  value: {
    color: "#111827",
    fontSize: 22,
    fontWeight: "700",
  },
  helper: {
    color: "#4b5563",
    fontSize: 13,
    lineHeight: 18,
  },
});
