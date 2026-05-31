export function ScoreBadge({ score, size = "sm" }: { score?: number; size?: "sm" | "lg" }) {
  const s = Math.round(score ?? 0);
  const color = s >= 80 ? "bg-danger" : s >= 50 ? "bg-accent" : "bg-slate-400";
  if (size === "lg")
    return (
      <div className={`${color} text-white w-12 h-12 rounded-full grid place-items-center text-lg font-extrabold shadow-card border-2 border-white ${s >= 90 ? "animate-pennyPulse" : ""}`}>
        {s}
      </div>
    );
  return <span className={`${color} text-white text-xs font-bold px-2.5 py-1 rounded-full`}>{s}</span>;
}
