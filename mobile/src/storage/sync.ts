import AsyncStorage from "@react-native-async-storage/async-storage";

const BUNDLE_KEY = "kisan.offline_bundle";
const META_KEY = "kisan.sync_meta";

export type SyncMeta = {
  lastSyncedAt: string;
  recordCount: number;
  signature: string;
};

export async function saveOfflineBundle(payload: unknown, meta: SyncMeta): Promise<void> {
  await AsyncStorage.setItem(BUNDLE_KEY, JSON.stringify(payload));
  await AsyncStorage.setItem(META_KEY, JSON.stringify(meta));
}

export async function loadSyncMeta(): Promise<SyncMeta | null> {
  const raw = await AsyncStorage.getItem(META_KEY);
  if (!raw) return null;
  return JSON.parse(raw) as SyncMeta;
}

export async function loadOfflineRecords(): Promise<unknown[] | null> {
  const raw = await AsyncStorage.getItem(BUNDLE_KEY);
  if (!raw) return null;
  const data = JSON.parse(raw) as { records?: unknown[] };
  return data.records ?? null;
}
