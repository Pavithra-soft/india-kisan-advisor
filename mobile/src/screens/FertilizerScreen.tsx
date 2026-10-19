import { useState } from "react";
import { Button, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";

import { recommendFertilizer } from "../api/client";
import { ConfidenceBadge } from "../components/ConfidenceBadge";
import { loadProfile } from "../storage/profile";

export function FertilizerScreen() {
  const [yieldQ, setYieldQ] = useState("50");
  const [n, setN] = useState("");
  const [p, setP] = useState("");
  const [k, setK] = useState("");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onCalc() {
    setError(null);
    const profile = await loadProfile();
    const soilTest =
      n && p && k
        ? { n_kg_ha: parseFloat(n), p2o5_kg_ha: parseFloat(p), k2o_kg_ha: parseFloat(k) }
        : undefined;
    try {
      const data = await recommendFertilizer({
        crop_id: profile.cropIds[0] ?? "rice",
        region_id: profile.regionId,
        season: "kharif",
        target_yield_q_per_ha: parseFloat(yieldQ),
        soil_test: soilTest,
      });
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed");
    }
  }

  const nutrients = result?.nutrient_requirement as Record<string, number> | undefined;

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.label}>Target yield (quintal/ha)</Text>
      <TextInput style={styles.input} value={yieldQ} onChangeText={setYieldQ} keyboardType="decimal-pad" />
      <Text style={styles.label}>Soil test (optional) — N, P₂O₅, K₂O kg/ha</Text>
      <View style={styles.row}>
        <TextInput style={styles.small} placeholder="N" value={n} onChangeText={setN} keyboardType="decimal-pad" />
        <TextInput style={styles.small} placeholder="P₂O₅" value={p} onChangeText={setP} keyboardType="decimal-pad" />
        <TextInput style={styles.small} placeholder="K₂O" value={k} onChangeText={setK} keyboardType="decimal-pad" />
      </View>
      <Button title="Calculate" onPress={onCalc} />
      {error ? <Text style={styles.error}>{error}</Text> : null}
      {result && nutrients ? (
        <View style={styles.card}>
          <ConfidenceBadge level={String(result.confidence)} />
          <Text>N: {nutrients.n_kg_ha} kg/ha</Text>
          <Text>P₂O₅: {nutrients.p2o5_kg_ha} kg/ha</Text>
          <Text>K₂O: {nutrients.k2o_kg_ha} kg/ha</Text>
          {(result.cautions as string[] | undefined)?.map((c, i) => (
            <Text key={i} style={styles.caution}>{c}</Text>
          ))}
        </View>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 10 },
  label: { fontWeight: "600" },
  input: { borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 10 },
  row: { flexDirection: "row", gap: 8 },
  small: { flex: 1, borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 10 },
  card: { backgroundColor: "#f5f5f5", padding: 12, borderRadius: 8, gap: 6, marginTop: 8 },
  caution: { fontSize: 12, color: "#6d4c41" },
  error: { color: "#c62828" },
});
