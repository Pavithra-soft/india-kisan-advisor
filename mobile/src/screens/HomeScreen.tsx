import { useEffect, useState } from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";

import { checkHealth } from "../api/client";
import { loadSyncMeta } from "../storage/sync";

export function HomeScreen() {
  const [apiOk, setApiOk] = useState<string>("checking…");
  const [syncLine, setSyncLine] = useState<string>("No offline data yet");

  useEffect(() => {
    checkHealth()
      .then(() => setApiOk("API reachable"))
      .catch(() => setApiOk("API offline — use last synced data"));
    loadSyncMeta().then((m) => {
      if (m) setSyncLine(`Last updated: ${new Date(m.lastSyncedAt).toLocaleString()} (${m.recordCount} records)`);
    });
  }, []);

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>India Kisan Advisor</Text>
      <Text style={styles.sub}>Verified facts first. Numbers from the calculator, not chat.</Text>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Connection</Text>
        <Text>{apiOk}</Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Data on this phone</Text>
        <Text>{syncLine}</Text>
        <Text style={styles.hint}>Sync daily from Settings (Wi‑Fi friendly).</Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>How to use</Text>
        <Text>• Ask — crop questions with sources and confidence</Text>
        <Text>• Fertilizer — soil-test based doses (deterministic)</Text>
        <Text>• Diagnose — photo check (restricted until models pass field gates)</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 12 },
  title: { fontSize: 24, fontWeight: "700", color: "#1b5e20" },
  sub: { color: "#444", marginBottom: 8 },
  card: { backgroundColor: "#f5f5f5", padding: 14, borderRadius: 10, gap: 6 },
  cardTitle: { fontWeight: "600" },
  hint: { fontSize: 12, color: "#666", marginTop: 4 },
});
