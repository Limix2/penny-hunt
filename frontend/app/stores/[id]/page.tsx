import { api } from "@/lib/api";
import { ProductCard } from "@/components/ProductCard";
import { NotesPanel } from "@/components/NotesPanel";
import { ReliabilityBadge } from "@/components/ReliabilityBadge";
import { HeaderBar } from "@/components/HeaderBar";
import { Icon } from "@/components/ui/Icon";

const DAYS: [string, string][] = [
  ["mon", "Mon"], ["tue", "Tue"], ["wed", "Wed"], ["thu", "Thu"],
  ["fri", "Fri"], ["sat", "Sat"], ["sun", "Sun"],
];

function Stat({ value, label }: { value: React.ReactNode; label: string }) {
  return (
    <div className="rounded-2xl border border-black/5 bg-card dark:bg-slate-900 p-3 text-center shadow-card">
      <p className="text-lg font-extrabold dark:text-white">{value}</p>
      <p className="text-[11px] text-slate-500">{label}</p>
    </div>
  );
}

export default async function StoreDetail({ params }: { params: { id: string } }) {
  const id = Number(params.id);
  const [store, items] = await Promise.all([
    api.storeDetail(id).catch(() => null),
    api.storeItems(id, 0).catch(() => []),
  ]);

  return (
    <div>
      <HeaderBar title={store ? store.name : `Store #${id}`}
        subtitle={store ? `${store.chain} · ${store.city}, ${store.state} ${store.zip}` : undefined}
        right={store && (
          <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${store.open_now ? "bg-white text-success" : "bg-white/20 text-white"}`}>
            {store.open_now ? "Open now" : "Closed"}
          </span>
        )} />

      <div className="mx-auto max-w-2xl px-4 pt-4 -mt-4 pb-4 space-y-5">
        {store && <ReliabilityBadge reliability={store.reliability} />}
        {store && (
          <div className="grid grid-cols-3 gap-2">
            <Stat value={store.distance_miles ?? "—"} label={`miles · ~${store.eta_min ?? "—"} min`} />
            <Stat value={Math.round(store.behavior_score ?? 0)} label="behavior" />
            <Stat value={<span className="text-danger">{store.high_score_count}</span>} label="hot items" />
          </div>
        )}

        {store?.phone && (
          <a href={`tel:${store.phone}`} className="flex items-center gap-2 bg-card dark:bg-slate-900 rounded-xl shadow-card p-3 text-sm text-primary font-medium">
            <Icon name="nav" size={16} /> {store.phone}
          </a>
        )}

        {store?.hours_json && (
          <section className="bg-card dark:bg-slate-900 rounded-2xl shadow-card p-4">
            <h2 className="font-semibold mb-2 flex items-center gap-2 dark:text-white"><Icon name="clock" size={16} /> Hours</h2>
            <table className="w-full text-sm">
              <tbody>
                {DAYS.map(([k, label]) => (
                  <tr key={k} className="border-t border-black/5">
                    <td className="py-1 text-slate-500">{label}</td>
                    <td className="text-right dark:text-slate-200">{store.hours_json![k] ? `${store.hours_json![k][0]} – ${store.hours_json![k][1]}` : "Closed"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}

        <section>
          <h2 className="font-semibold mb-2 dark:text-white">High-score items</h2>
          <div className="grid gap-3">{items.map((c) => <ProductCard key={c.id} c={c} />)}</div>
          {items.length === 0 && <p className="text-sm text-slate-400">No scored items yet — tap “Scan now” on the radar.</p>}
        </section>

        <section className="bg-card dark:bg-slate-900 rounded-2xl shadow-card p-4">
          <NotesPanel storeId={id} />
        </section>
      </div>
    </div>
  );
}
