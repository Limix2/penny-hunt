"use client";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api, Candidate, distMiles } from "@/lib/api";
import { useLiveScores } from "@/lib/useLiveScores";
import { ProductCard } from "@/components/ProductCard";
import { HeaderBar } from "@/components/HeaderBar";
import { LiveAlertBanner } from "@/components/LiveAlertBanner";
import { SkeletonList } from "@/components/Skeleton";
import { ChainFilter } from "@/components/ChainFilter";
import { CHAINS, CHAIN_BY_CODE, timeAgo } from "@/lib/chains";
import { Icon } from "@/components/ui/Icon";

type Mode = "All" | "PennyRadar" | "DealStorm";
type Sort = "all" | "nearest" | "reliable" | "spike";

function RadarInner() {
  const [items, setItems] = useState<Candidate[]>([]);
  const [mode, setMode] = useState<Mode>("All");
  const [sort, setSort] = useState<Sort>("all");
  const [inStore, setInStore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [updated, setUpdated] = useState<string | null>(null);
  const { events, connected } = useLiveScores();
  const sp = useSearchParams();
  const chains = (sp.get("chains") || "").split(",").filter(Boolean);

  const load = () => api.topItems(24, 0, 200).then(setItems).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);
  useEffect(() => { if (events.length) load(); }, [events.length]);
  useEffect(() => {
    const poll = () => api.status().then((s) => setUpdated(s.last_ingest_at)).catch(() => {});
    poll();
    const id = setInterval(poll, 30000); // auto-update "last updated" every 30s
    return () => clearInterval(id);
  }, []);

  let view = items.filter((c) =>
    mode === "PennyRadar" ? (c.current_price ?? 9) <= 0.05 :
    mode === "DealStorm" ? (c.score ?? 0) >= 80 : true);
  if (chains.length) {
    const keys = new Set(chains.map((code) => CHAIN_BY_CODE[code]?.key).filter(Boolean));
    view = view.filter((c) => keys.has(c.store.chain));
  }
  if (sort === "reliable") view = view.filter((c) => (c.store.reliability ?? 0) >= 0.8);
  if (sort === "spike") view = view.filter((c) => (c.store.behavior_score ?? 0) >= 40);
  if (sort === "nearest")
    view = [...view].sort((a, b) => distMiles(a.store.lat, a.store.lon) - distMiles(b.store.lat, b.store.lon));

  const groups = CHAINS.map((ch) => ({ ch, items: view.filter((c) => c.store.chain === ch.key) }))
    .filter((g) => g.items.length);
  const modes: Mode[] = ["All", "PennyRadar", "DealStorm"];
  const sorts: Sort[] = ["all", "nearest", "reliable", "spike"];

  return (
    <div>
      <HeaderBar title="PennyRadar" subtitle="Live penny & clearance feed"
        right={<span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${connected ? "bg-white/20 text-white" : "bg-white/10 text-white/60"}`}>{connected ? "● live" : "○ offline"}</span>} />

      <div className="mx-auto max-w-2xl px-4 pt-4 -mt-4 pb-4 space-y-4">
        <p className="text-xs text-slate-400">Last updated: {timeAgo(updated)}</p>

        <div className="flex gap-2 overflow-x-auto no-scrollbar">
          {modes.map((m) => (
            <button key={m} onClick={() => setMode(m)}
              className={`px-3.5 py-1.5 rounded-full text-sm font-semibold whitespace-nowrap transition-colors ${mode === m ? "bg-primary text-white" : "bg-card dark:bg-slate-800 border border-black/5 text-slate-600 dark:text-slate-300"}`}>{m}</button>
          ))}
        </div>

        <ChainFilter />

        <div className="flex items-center gap-2 overflow-x-auto no-scrollbar">
          {sorts.map((s) => (
            <button key={s} onClick={() => setSort(s)}
              className={`px-3 py-1 rounded-full text-xs font-semibold capitalize ${sort === s ? "bg-amber-500 text-white" : "bg-card dark:bg-slate-800 border border-black/5 text-slate-500"}`}>{s}</button>
          ))}
          <button onClick={() => setInStore((v) => !v)}
            className={`ml-auto shrink-0 px-3 py-1 rounded-full text-xs font-semibold ${inStore ? "bg-success text-white" : "bg-card dark:bg-slate-800 border border-black/5 text-slate-500"}`}>In-store</button>
        </div>

        <button onClick={() => api.refresh()}
          className="w-full bg-primary text-white font-semibold py-3 rounded-xl shadow-card active:scale-[0.99] transition-transform flex items-center justify-center gap-2">
          <Icon name="radar" size={18} /> Scan now
        </button>

        <LiveAlertBanner events={events} />

        {loading ? <SkeletonList /> : groups.length === 0 ? (
          <p className="text-center text-sm text-slate-400 py-8">No candidates match your filters.</p>
        ) : (
          <div className="space-y-5">
            {groups.map((g) => (
              <section key={g.ch.key} className="animate-fadeIn">
                <div className="flex items-center gap-2 mb-2">
                  <span className="w-1.5 h-4 rounded-full" style={{ backgroundColor: g.ch.color }} />
                  <h2 className="font-bold text-sm dark:text-white">{g.ch.key}</h2>
                  <span className="text-xs text-slate-400">({g.items.length})</span>
                </div>
                <div className="grid gap-3">{g.items.map((c) => <ProductCard key={c.id} c={c} lowData={inStore} />)}</div>
              </section>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function Radar() {
  return (
    <Suspense fallback={<div className="p-10 text-center text-slate-400">Loading…</div>}>
      <RadarInner />
    </Suspense>
  );
}
