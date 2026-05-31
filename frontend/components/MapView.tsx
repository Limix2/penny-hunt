"use client";
import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { api, StoreSummary, TARGET } from "@/lib/api";
import { CHAIN_COLOR, reliabilityTier } from "@/lib/chains";

// Pins are color-coded by chain; a glow marks stores with multiple hot items.
function icon(s: StoreSummary) {
  const c = CHAIN_COLOR[s.chain] || "#4C3AFF";
  const glow = s.high_score_count >= 2;
  return L.divIcon({
    className: "",
    html: `<span style="display:block;width:18px;height:18px;border-radius:50%;background:${c};border:2px solid #fff;box-shadow:${glow ? `0 0 0 6px ${c}44,` : ""}0 1px 4px rgba(0,0,0,.45)"></span>`,
    iconSize: [18, 18], iconAnchor: [9, 9],
  });
}

export default function MapView() {
  const [stores, setStores] = useState<StoreSummary[]>([]);
  useEffect(() => { api.stores().then(setStores).catch(() => {}); }, []);
  return (
    <MapContainer center={TARGET} zoom={11} className="h-full w-full">
      <TileLayer attribution="&copy; OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {stores.filter((s) => s.lat && s.lon).map((s) => {
        const t = reliabilityTier(s.reliability);
        return (
          <Marker key={s.id} position={[s.lat!, s.lon!]} icon={icon(s)}>
            <Popup>
              <div className="text-sm space-y-1 min-w-[180px]">
                <p className="font-semibold">{s.name}</p>
                <p className="text-slate-500">{s.address || `${s.city || ""}, ${s.state || ""} ${s.zip || ""}`}</p>
                <span className={`inline-block text-[10px] font-semibold px-2 py-0.5 rounded-full ${t.cls}`}>{t.label}</span>
                <div><a className="text-primary font-semibold" href={`/stores/${s.id}`}>View Store →</a></div>
              </div>
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
}
