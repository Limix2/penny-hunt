import { Icon } from "./ui/Icon";
import { LiveEvent } from "@/lib/useLiveScores";

export function LiveAlertBanner({ events }: { events: LiveEvent[] }) {
  if (!events.length) return null;
  return (
    <div className="rounded-2xl bg-gradient-to-r from-success to-emerald-400 text-white p-3 shadow-card animate-slideUp">
      <p className="flex items-center gap-2 font-semibold text-sm mb-1.5"><Icon name="bell" size={16} /> Live penny alerts</p>
      <div className="space-y-1">
        {events.slice(0, 4).map((e, i) => (
          <div key={i} className="text-sm flex items-center justify-between gap-2">
            <span className="truncate">{e.item.name} · {e.store.name}</span>
            <span className="font-bold shrink-0">${e.current_price?.toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
