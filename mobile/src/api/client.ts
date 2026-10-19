import Constants from "expo-constants";

export type FarmerProfile = {
  regionId: string;
  cropIds: string[];
  language: string;
};

const defaultUrl =
  (Constants.expoConfig?.extra as { apiUrl?: string })?.apiUrl ??
  process.env.EXPO_PUBLIC_API_URL ??
  "http://127.0.0.1:8090";

export function getApiBaseUrl(): string {
  return defaultUrl.replace(/\/$/, "");
}

async function parseJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export async function checkHealth(): Promise<{ status: string }> {
  const res = await fetch(`${getApiBaseUrl()}/health`);
  return parseJson(res);
}

export async function askQuestion(body: {
  question: string;
  crop_id?: string;
  region_id?: string;
  season?: string;
}): Promise<Record<string, unknown>> {
  const res = await fetch(`${getApiBaseUrl()}/qa`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return parseJson(res);
}

export async function recommendFertilizer(body: Record<string, unknown>): Promise<Record<string, unknown>> {
  const res = await fetch(`${getApiBaseUrl()}/fertilizer/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return parseJson(res);
}

export async function diagnoseImage(uri: string, cropId?: string): Promise<Record<string, unknown>> {
  const form = new FormData();
  form.append("file", {
    uri,
    name: "crop.jpg",
    type: "image/jpeg",
  } as unknown as Blob);
  const url = new URL(`${getApiBaseUrl()}/diagnose`);
  if (cropId) url.searchParams.set("crop_id", cropId);
  const res = await fetch(url.toString(), { method: "POST", body: form });
  return parseJson(res);
}

export async function downloadSyncBundle(profile: FarmerProfile, baseVersion?: string): Promise<Record<string, unknown>> {
  const params = new URLSearchParams({
    region_id: profile.regionId,
    crop_ids: profile.cropIds.join(","),
  });
  if (baseVersion) params.set("base_version", baseVersion);
  const res = await fetch(`${getApiBaseUrl()}/sync/bundle?${params}`);
  return parseJson(res);
}
