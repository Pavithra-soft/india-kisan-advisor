import AsyncStorage from "@react-native-async-storage/async-storage";

import type { FarmerProfile } from "../api/client";

const KEY = "kisan.profile";

const DEFAULT: FarmerProfile = {
  regionId: "ap",
  cropIds: ["rice"],
  language: "en",
};

export async function loadProfile(): Promise<FarmerProfile> {
  const raw = await AsyncStorage.getItem(KEY);
  if (!raw) return DEFAULT;
  try {
    return { ...DEFAULT, ...JSON.parse(raw) };
  } catch {
    return DEFAULT;
  }
}

export async function saveProfile(profile: FarmerProfile): Promise<void> {
  await AsyncStorage.setItem(KEY, JSON.stringify(profile));
}
