import { api } from "@/lib/api";
import { HeaderBar } from "@/components/HeaderBar";
import { StoreCard } from "@/components/StoreCard";
import { WatchlistButton } from "@/components/WatchlistButton";
import { ScoreBadge } from "@/components/ScoreBadge";
import { Icon } from "@/components/ui/Icon";
import { notFound } from "next/navigation";

function AreaChart({ points, color = "#2ECC71" }: { points: number[]; color?: string }) {
  if (points.length < 2) return <p className="text-sm text-slate-400">Not enough data yet.</p>;
  const w = 300, h = 80, max = Math.max(...points), min = Math.min(...points), span = max - min || 1;
  const xy = points.map((p, i) => [(i / (points.length - 1)) * w, h - ((p - min) / span) * h] as const);
  const line = xy.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-20" preserveAspectRatio="none">
      <polygon points={`0,${h} ${line} ${w},${h}`} fill={color} opacity="0.12" />
      <polyline points={line} fill="none" stroke={color} strokeWidth="2" />
    </svg>
  );
}

export default async function ItemDetailPage({ params }: { params: { id: string } }) {
  const id = Number(params.id);
  const detail = await api.itemDetail(id).catch(() => null);
  if (!detail) notFound();
  const store = await api.storeDetail(detail.store.id).catch(() => null);
  const penny = (detail.current_price ?? 9) <= 0.05;

  return (
    <div>
      <HeaderBar title={detail.item.name}
        subtitle={`${detail.store.chain} · ${detail.store.name}`}
        right={<WatchlistButton id={detail.id} />} />

      <div className="mx-auto max-w-2xl px-4 pt-4 -mt-4 pb-4 space-y-4">
        <div className="bg-card dark:bg-slate-900 rounded-2xl shadow-card p-4 flex items-center justify-between animate-fadeIn">
          <div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-success">${detail.current_price?.toFixed(2)}</span>
              {detail.regular_price != null && <span className="text-sm text-slate-400 line-through">${detail.regular_price.toFixed(2)}</span>}
            </div>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {penny && <span className="inline-flex items-center gap-1 text-[11px] font-bold bg-danger/10 text-danger px-2 py-0.5 rounded-full"><Icon name="coin" size={12} /> Penny</span>}
              {detail.clearance_flag && <span className="inline-flex items-center gap-1 text-[11px] font-bold bg-accent/15 text-amber-700 px-2 py-0.5 rounded-full"><Icon name="tag" size={12} /> Clearance</span>}
            </div>
          </div>
          <ScoreBadge score={detail.score} size="lg" />
        </div>

        {detail.explanation && (
          <div className="bg-gradient-to-br from-primary/10 to-secondary/10 rounded-2xl p-4">
            <p className="flex items-center gap-2 font-semibold text-primary mb-1">
              <Icon name="sparkles" size={16} /> AI insight
              <span className="text-xs text-slate-400 font-normal">({detail.model_version})</span>
            </p>
            <p className="text-sm text-slate-600 dark:text-slate-300">{detail.explanation}</p>
          </div>
        )}

        <div className="bg-card dark:bg-slate-900 rounded-2xl shadow-card p-4">
          <p className="font-semibold mb-2 flex items-center gap-2 dark:text-white"><Icon name="drop" size={16} /> Price history</p>
          <AreaChart points={detail.price_history.map((p) => p.price)} />
        </div>

        <div className="bg-card dark:bg-slate-900 rounded-2xl shadow-card p-4">
          <p className="font-semibold mb-2 flex items-center gap-2 dark:text-white"><Icon name="radar" size={16} /> Score history</p>
          <AreaChart points={detail.score_history.map((s) => s.score)} color="#4C3AFF" />
        </div>

        <div>
          <p className="font-semibold mb-2 dark:text-white">Availability</p>
          {store ? <StoreCard s={store} /> : <p className="text-sm text-slate-400">Store info unavailable.</p>}
        </div>
      </div>
    </div>
  );
}
