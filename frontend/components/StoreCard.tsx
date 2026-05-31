import Link from "next/link";
import { StoreSummary } from "@/lib/api";
import { Icon } from "./ui/Icon";
import { ReliabilityBadge } from "./ReliabilityBadge";
import { CHAIN_COLOR } from "@/lib/chains";

export function StoreCard({ s }: { s: StoreSummary }) {
  const accent = CHAIN_COLOR[s.chain] || "#4C3AFF";
  return (
    <Link href={`/stores/${s.id}`} style={{ borderLeftColor: accent }}
      className="block bg-card dark:bg-slate-900 rounded-2xl border-l-4 shadow-card hover:shadow-hover transition-all active:scale-[0.99] p-4 animate-fadeIn">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="font-semibold leading-tight dark:text-white">{s.name}</p>
          <p className="text-xs text-slate-500 mt-0.5">{s.chain} · {s.city}, {s.state}</p>
        </div>
        <span className={`shrink-0 text-[11px] font-bold px-2.5 py-1 rounded-full ${s.open_now ? "bg-success/15 text-success" : "bg-slate-100 text-slate-500 dark:bg-slate-800"}`}>
          {s.open_now ? "Open" : "Closed"}
        </span>
      </div>
      <div className="mt-2"><ReliabilityBadge reliability={s.reliability} /></div>
      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-600 dark:text-slate-300">
        {s.distance_miles != null && <span className="flex items-center gap-1"><Icon name="nav" size={13} /> {s.distance_miles} mi · ~{s.eta_min} min</span>}
        <span className="flex items-center gap-1"><Icon name="radar" size={13} /> behavior {Math.round(s.behavior_score ?? 0)}</span>
        <span className="flex items-center gap-1 text-danger font-semibold"><Icon name="coin" size={13} /> {s.high_score_count} hot</span>
      </div>
    </Link>
  );
}
