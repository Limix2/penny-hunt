"use client";
import dynamic from "next/dynamic";
import { HeaderBar } from "@/components/HeaderBar";

const MapView = dynamic(() => import("@/components/MapView"), {
  ssr: false,
  loading: () => <div className="grid place-items-center h-full text-slate-400">Loading map…</div>,
});

const LEGEND = [["#FF3B30", "Penny"], ["#FFB800", "Clearance"], ["#4C3AFF", "Normal"]] as const;

export default function MapPage() {
  return (
    <div>
      <HeaderBar title="Store Map" subtitle="Tap a pin for details"
        right={
          <div className="flex gap-2">
            {LEGEND.map(([c, l]) => (
              <span key={l} className="flex items-center gap-1 text-[11px] text-white/90">
                <span className="w-2.5 h-2.5 rounded-full" style={{ background: c }} />{l}
              </span>
            ))}
          </div>
        } />
      <div className="mx-auto max-w-2xl px-4 pt-4 -mt-4">
        <div className="rounded-2xl overflow-hidden shadow-card h-[calc(100dvh-13rem)]">
          <MapView />
        </div>
      </div>
    </div>
  );
}
