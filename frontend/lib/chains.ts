export interface ChainMeta { key: string; code: string; label: string; color: string; }

// Color scheme: DG=yellow, Walmart=blue, Home Depot=orange, H-E-B=red
export const CHAINS: ChainMeta[] = [
  { key: "Dollar General", code: "DG", label: "DG", color: "#FFB800" },
  { key: "Walmart", code: "WMT", label: "Walmart", color: "#2563EB" },
  { key: "Home Depot", code: "HD", label: "Home Depot", color: "#F96302" },
  { key: "H-E-B", code: "HEB", label: "H-E-B", color: "#E4002B" },
];
export const CHAIN_BY_CODE: Record<string, ChainMeta> = Object.fromEntries(CHAINS.map((c) => [c.code, c]));
export const CHAIN_COLOR: Record<string, string> = Object.fromEntries(CHAINS.map((c) => [c.key, c.color]));

export function reliabilityTier(r?: number) {
  const pct = Math.round((r ?? 0) * 100); // reliability stored 0..1
  if (pct >= 80) return { label: "High Reliability", cls: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300" };
  if (pct >= 50) return { label: "Medium Reliability", cls: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300" };
  return { label: "Low Reliability", cls: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300" };
}

export function timeAgo(iso?: string | null) {
  if (!iso) return "never";
  const ms = new Date(iso.endsWith("Z") ? iso : iso + "Z").getTime(); // backend sends UTC, no suffix
  const s = Math.max(0, (Date.now() - ms) / 1000);
  if (s < 60) return `${Math.floor(s)}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)} min ago`;
  return `${Math.floor(s / 3600)}h ago`;
}
