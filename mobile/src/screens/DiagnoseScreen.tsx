import * as ImagePicker from "expo-image-picker";
import { useState } from "react";
import { Button, Image, ScrollView, StyleSheet, Text, View } from "react-native";

import { diagnoseImage } from "../api/client";
import { ConfidenceBadge } from "../components/ConfidenceBadge";
import { loadProfile } from "../storage/profile";

export function DiagnoseScreen() {
  const [uri, setUri] = useState<string | null>(null);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function pickImage() {
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) {
      setError("Camera permission required");
      return;
    }
    const shot = await ImagePicker.launchCameraAsync({ quality: 0.8 });
    if (!shot.canceled && shot.assets[0]?.uri) {
      setUri(shot.assets[0].uri);
      setResult(null);
    }
  }

  async function onDiagnose() {
    if (!uri) return;
    setError(null);
    const profile = await loadProfile();
    try {
      const data = await diagnoseImage(uri, profile.cropIds[0]);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed");
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text>Take a clear photo of the affected leaf or pest.</Text>
      <Button title="Take photo" onPress={pickImage} />
      {uri ? <Image source={{ uri }} style={styles.preview} /> : null}
      <Button title="Diagnose" onPress={onDiagnose} disabled={!uri} />
      {error ? <Text style={styles.error}>{error}</Text> : null}
      {result ? (
        <View style={styles.card}>
          {result.not_sure ? (
            <Text>{String(result.suggested_next_step ?? result.message ?? "Not sure")}</Text>
          ) : (
            <>
              <ConfidenceBadge level={String(result.confidence)} />
              <Text>Possible: {(result.prediction_set as string[]).join(", ")}</Text>
              <Text style={styles.hint}>Field models not certified yet — treat as advisory only.</Text>
            </>
          )}
        </View>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, gap: 12 },
  preview: { width: "100%", height: 220, borderRadius: 8 },
  card: { backgroundColor: "#f5f5f5", padding: 12, borderRadius: 8, gap: 8 },
  hint: { fontSize: 12, color: "#666" },
  error: { color: "#c62828" },
});
