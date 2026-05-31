"use client";
import { useEffect, useMemo, useState } from "react";
import { api, StoreSummary } from "@/lib/api";
import { StoreCard } from "@/components/StoreCard";
import { HeaderBar } from "@/components/HeaderBar";
import { SkeletonList } from "@/components/Skeleton";
import { Icon } from "@/components/ui/Icon";

type Sort = "nearest" | "behavior" | "hot";

export default function StoresPage() {
  const [stores, setStores] = useState<StoreSummary[]>([]);
  const [q, setQ] = useState("");
  const [sort, setSort] = useState<Sort>("nearest");
  const [loading, setLoading] = useState(true);

  useEffect(() => { api.stores().then(setStores).finally(() => setLoading(false)); }, []);

  const view = useMemo(() => {
    const v = stores.filter((s) => `${s.name} ${s.city} ${s.chain}`.toLowerCase().includes(q.toLowerCase()));
    return [...v].sort((a, b) =>
      sort === "behavior" ? (b.behavior_score ?? 0) - (a.behavior_score ?? 0) :
      sort === "hot" ? b.high_score_count - a.high_score_count :
      (a.distance_miles ?? 1e9) - (b.distance_miles ?? 1e9));
  }, [stores, q, sort]);

  const chip = (active: boolean) =>
    `px-3 py-1 rounded-full text-xs font-semibold capitalize ${active ? "bg-primary text-white" : "bg-card dark:bg-slate-800 text-slate-500 border border-black/5"}`;

  return (
    <div>
      <HeaderBar title="Stores" subtitle={`${stores.length} in range`} />
      <div className="mx-auto max-w-2xl px-4 pt-4 -mt-4 pb-4 space-y-4">
        <div className="flex items-center gap-2 bg-card dark:bg-slate-900 rounded-xl shadow-card px-3 py-2">
          <Icon name="search" size={18} className="text-slate-400" />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search store, city, chain"
            className="flex-1 bg-transparent outline-none text-sm dark:text-white" />
        </div>
        <div className="flex gap-2">
          {(["nearest", "behavior", "hot"] as Sort[]).map((s) => (
            <button key={s} onClick={() => setSort(s)} className={chip(sort === s)}>{s}</button>
          ))}
        </div>
        {loading ? <SkeletonList /> : (
          <div className="grid gap-3">{view.map((s) => <StoreCard key={s.id} s={s} />)}</div>
        )}
      </div>
    </div>
  );
}
