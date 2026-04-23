import React from "react";
import { StyleSheet, Text, View } from "react-native";

export function SignalShareCard({
  headline = "",
  highlights = [],
  suggestion = "",
  prepared = false,
} = {}) {
  const visibleHighlights = Array.isArray(highlights) ? highlights.filter(Boolean).slice(0, 3) : [];

  return (
    <View style={[styles.card, prepared && styles.cardPrepared]}>
      <View style={styles.header}>
        <Text style={styles.label}>VibeSignal</Text>
        <Text style={styles.mode}>{prepared ? "Screenshot ready" : "Share card"}</Text>
      </View>
      <Text style={styles.headline}>{headline}</Text>
      <View style={styles.highlightList}>
        {visibleHighlights.map((item) => (
          <View key={item} style={styles.highlightRow}>
            <View style={styles.bullet} />
            <Text style={styles.highlightText}>{item}</Text>
          </View>
        ))}
      </View>
      {!!suggestion ? <Text style={styles.suggestion}>{suggestion}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 22,
    backgroundColor: "#0f1724",
    padding: 18,
    gap: 14,
    borderWidth: 1,
    borderColor: "#25344a",
  },
  cardPrepared: {
    padding: 22,
    borderColor: "#7dd3a6",
    shadowColor: "#0b1220",
    shadowOpacity: 0.2,
    shadowRadius: 18,
    shadowOffset: { width: 0, height: 10 },
    elevation: 5,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 12,
  },
  label: {
    color: "#d8e1ef",
    fontSize: 12,
    fontWeight: "700",
    letterSpacing: 0.9,
    textTransform: "uppercase",
  },
  mode: {
    color: "#8ecfb0",
    fontSize: 12,
    fontWeight: "700",
  },
  headline: {
    color: "#ffffff",
    fontSize: 28,
    lineHeight: 34,
    fontWeight: "800",
  },
  highlightList: {
    gap: 10,
  },
  highlightRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 10,
  },
  bullet: {
    width: 7,
    height: 7,
    borderRadius: 999,
    backgroundColor: "#7dd3a6",
    marginTop: 8,
  },
  highlightText: {
    flex: 1,
    color: "#d6dfeb",
    fontSize: 15,
    lineHeight: 22,
  },
  suggestion: {
    color: "#9fb0c5",
    fontSize: 13,
    lineHeight: 20,
  },
});
