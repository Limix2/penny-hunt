import Link from "next/link";
import { Candidate } from "@/lib/api";
import { ScoreBadge } from "./ScoreBadge";
import { ReliabilityBadge } from "./ReliabilityBadge";
import { Icon } from "./ui/Icon";
import { CHAIN_COLOR } from "@/lib/chains";

export function ProductCard({ c, lowData = false }: { c: Candidate; lowData?: boolean }) {
  const penny = (c.current_price ?? 9) <= 0.05;
  const accent = CHAIN_COLOR[c.store.chain] || "#4C3AFF";
  return (
    <Link href={`/items/${c.id}`} style={{ borderLeftColor: accent }}
      className={`group block bg-card dark:bg-slate-900 rounded-2xl border-l-4 shadow-card hover:shadow-hover transition-all duration-200 active:scale-[0.99] animate-fadeIn ${penny ? "ring-2 ring-danger/40" : ""}`}>
      <div className="flex gap-3 p-3">
        <div className="relative shrink-0">
          <div className="w-20 h-20 rounded-xl bg-gradient-to-br from-primary/10 to-secondary/10 grid place-items-center text-primary overflow-hidden">
            {c.item.image_url && !lowData
              ? <img src={c.item.image_url} alt="" className="w-full h-full object-cover" />
              : <Icon name="coin" size={30} />}
          </div>
          <div className="absolute -top-2 -right-2"><ScoreBadge score={c.score} size="lg" /></div>
        </div>
        <div className="min-w-0 flex-1">
          <p className="font-semibold leading-tight line-clamp-2 dark:text-white">{c.item.name}</p>
          <p className="text-xs text-slate-500 mt-0.5 flex items-center gap-1">
            <Icon name="store" size={13} /> {c.store.chain} · {c.store.name}
          </p>
          <div className="mt-1"><ReliabilityBadge reliability={c.store.reliability} /></div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-xl font-extrabold text-success">${c.current_price?.toFixed(2)}</span>
            {c.regular_price != null && <span className="text-xs text-slate-400 line-through">${c.regular_price.toFixed(2)}</span>}
          </div>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {penny && <span className="inline-flex items-center gap-1 text-[11px] font-bold bg-danger/10 text-danger px-2 py-0.5 rounded-full"><Icon name="coin" size={12} /> Penny</span>}
            {c.clearance_flag && <span className="inline-flex items-center gap-1 text-[11px] font-bold bg-accent/15 text-amber-700 px-2 py-0.5 rounded-full"><Icon name="tag" size={12} /> Clearance</span>}
          </div>
        </div>
      </div>
    </Link>
  );
}
