import { StyleSheet, Text, View } from "react-native";

const COLORS: Record<string, string> = {
  high: "#2e7d32",
  medium: "#f9a825",
  low: "#ef6c00",
  low_medium: "#fb8c00",
  not_sure: "#757575",
};

export function ConfidenceBadge({ level }: { level: string }) {
  const bg = COLORS[level] ?? COLORS.not_sure;
  return (
    <View style={[styles.badge, { backgroundColor: bg }]}>
      <Text style={styles.text}>{level.replace("_", " ").toUpperCase()}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: { alignSelf: "flex-start", paddingHorizontal: 10, paddingVertical: 4, borderRadius: 6 },
  text: { color: "#fff", fontSize: 12, fontWeight: "600" },
});
