import { reliabilityTier } from "@/lib/chains";

export function ReliabilityBadge({ reliability }: { reliability?: number }) {
  const t = reliabilityTier(reliability);
  return <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${t.cls}`}>{t.label}</span>;
}
