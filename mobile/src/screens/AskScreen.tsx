import { useState } from "react";
import { Button, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";

import { askQuestion } from "../api/client";
import { ConfidenceBadge } from "../components/ConfidenceBadge";
import { loadProfile } from "../storage/profile";

export function AskScreen() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onAsk() {
    setLoading(true);
    setError(null);
    try {
      const profile = await loadProfile();
      const data = await askQuestion({
        question,
        crop_id: profile.cropIds[0],
        region_id: profile.regionId,
        season: "kharif",
      });
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Ask about price, schemes, or crop practice…"
        value={question}
        onChangeText={setQuestion}
        multiline
      />
      <Button title={loading ? "Loading…" : "Ask"} onPress={onAsk} disabled={loading || !question.trim()} />
      {error ? <Text style={styles.error}>{error}</Text> : null}
      {result ? (
        <View style={styles.card}>
          {result.not_sure ? (
            <>
              <Text style={styles.notSure}>Not sure</Text>
              <Text>{String(result.suggested_next_step ?? "")}</Text>
            </>
          ) : (
            <>
              <ConfidenceBadge level={String(result.confidence ?? "not_sure")} />
              {(result.sentences as string[] | undefined)?.map((s, i) => (
                <Text key={i} style={styles.answer}>{s}</Text>
              ))}
              {result.approximate ? <Text style={styles.warn}>Approximate — check source date.</Text> : null}
            </>
          )}
        </View>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 12 },
  input: { borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 12, minHeight: 80, textAlignVertical: "top" },
  card: { backgroundColor: "#f9f9f9", padding: 12, borderRadius: 8, gap: 8, marginTop: 8 },
  answer: { lineHeight: 22 },
  notSure: { fontSize: 18, fontWeight: "700", color: "#555" },
  warn: { color: "#e65100", fontSize: 12 },
  error: { color: "#c62828" },
});
