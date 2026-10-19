import { useEffect, useState } from "react";
import { Button, StyleSheet, Text, TextInput, View } from "react-native";

import { downloadSyncBundle, getApiBaseUrl, type FarmerProfile } from "../api/client";
import { loadProfile, saveProfile } from "../storage/profile";
import { loadSyncMeta, saveOfflineBundle } from "../storage/sync";

export function SettingsScreen() {
  const [regionId, setRegionId] = useState("ap");
  const [crops, setCrops] = useState("rice");
  const [syncStatus, setSyncStatus] = useState("");
  const [metaLine, setMetaLine] = useState("");

  useEffect(() => {
    loadProfile().then((p) => {
      setRegionId(p.regionId);
      setCrops(p.cropIds.join(","));
    });
    loadSyncMeta().then((m) => {
      if (m) setMetaLine(`Last sync: ${new Date(m.lastSyncedAt).toLocaleString()}`);
    });
  }, []);

  async function onSaveProfile() {
    const profile: FarmerProfile = {
      regionId,
      cropIds: crops.split(",").map((s) => s.trim()).filter(Boolean),
      language: "en",
    };
    await saveProfile(profile);
    setSyncStatus("Profile saved");
  }

  async function onSync() {
    setSyncStatus("Syncing…");
    try {
      const profile = await loadProfile();
      const bundle = await downloadSyncBundle(profile);
      const payload = bundle.payload as { records: unknown[] };
      const manifest = bundle.manifest as { record_count?: number };
      await saveOfflineBundle(payload, {
        lastSyncedAt: new Date().toISOString(),
        recordCount: manifest.record_count ?? payload.records?.length ?? 0,
        signature: String(bundle.signature),
      });
      setMetaLine(`Last sync: ${new Date().toLocaleString()}`);
      setSyncStatus("Sync complete");
    } catch (e) {
      setSyncStatus(e instanceof Error ? e.message : "Sync failed");
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.label}>API URL</Text>
      <Text style={styles.mono}>{getApiBaseUrl()}</Text>
      <Text style={styles.hint}>On a physical phone, set EXPO_PUBLIC_API_URL to your laptop LAN IP:8090</Text>
      <Text style={styles.label}>Region ID</Text>
      <TextInput style={styles.input} value={regionId} onChangeText={setRegionId} autoCapitalize="none" />
      <Text style={styles.label}>Crops (comma-separated IDs)</Text>
      <TextInput style={styles.input} value={crops} onChangeText={setCrops} autoCapitalize="none" />
      <Button title="Save profile" onPress={onSaveProfile} />
      <Button title="Sync offline data" onPress={onSync} />
      <Text>{metaLine}</Text>
      <Text>{syncStatus}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, gap: 10 },
  label: { fontWeight: "600", marginTop: 8 },
  input: { borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 10 },
  mono: { fontFamily: "monospace", fontSize: 12 },
  hint: { fontSize: 11, color: "#666" },
});
