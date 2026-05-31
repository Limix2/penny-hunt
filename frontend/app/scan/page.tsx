"use client";
import { useEffect, useRef, useState } from "react";
import { api, Candidate, VisionResult } from "@/lib/api";
import { HeaderBar } from "@/components/HeaderBar";
import { ProductCard } from "@/components/ProductCard";
import { Icon } from "@/components/ui/Icon";

export default function Scan() {
  const scannerRef = useRef<any>(null);
  const [upc, setUpc] = useState("");
  const [hit, setHit] = useState<Candidate | null>(null);
  const [msg, setMsg] = useState("");
  const [model, setModel] = useState("local");
  const [vision, setVision] = useState<VisionResult | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    (async () => {
      const { Html5Qrcode } = await import("html5-qrcode");
      const sc = new Html5Qrcode("reader");
      scannerRef.current = sc;
      try {
        await sc.start({ facingMode: "environment" }, { fps: 10, qrbox: 230 },
          async (text: string) => {
            if (!active) return;
            setUpc(text);
            try { setHit(await api.lookupUpc(text)); setMsg(""); }
            catch { setHit(null); setMsg(`No match for ${text}`); }
          }, () => {});
      } catch { setMsg("Camera unavailable — use Vision photo mode below."); }
    })();
    return () => { active = false; scannerRef.current?.stop?.().catch(() => {}); };
  }, []);

  const onPhoto = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setBusy(true); setMsg("Analyzing…");
    try { setVision(await api.vision(f, model)); setMsg(""); }
    catch { setMsg("Vision request failed."); }
    finally { setBusy(false); }
  };

  const models = [["local", "Local · free"], ["deepseek", "DeepSeek · cheap"], ["claude", "Claude 4.8 · premium"]];

  return (
    <div>
      <HeaderBar title="Scan" subtitle="Barcode & AI vision lookup" />
      <div className="mx-auto max-w-2xl px-4 pt-4 -mt-4 pb-4 space-y-4">
        {/* Camera frame */}
        <div className="relative rounded-2xl overflow-hidden bg-black shadow-card aspect-square max-w-sm mx-auto">
          <div id="reader" className="w-full h-full [&_video]:object-cover" />
          <div className="pointer-events-none absolute inset-0">
            <span className="absolute top-3 left-3 w-7 h-7 border-t-4 border-l-4 border-white/90 rounded-tl-lg" />
            <span className="absolute top-3 right-3 w-7 h-7 border-t-4 border-r-4 border-white/90 rounded-tr-lg" />
            <span className="absolute bottom-3 left-3 w-7 h-7 border-b-4 border-l-4 border-white/90 rounded-bl-lg" />
            <span className="absolute bottom-3 right-3 w-7 h-7 border-b-4 border-r-4 border-white/90 rounded-br-lg" />
            <span className="absolute left-6 right-6 top-6 h-0.5 bg-accent shadow-[0_0_12px_2px_#FFB800] animate-scan" />
          </div>
        </div>
        {upc && <p className="text-center text-sm text-slate-500">UPC: <span className="font-mono">{upc}</span></p>}
        {hit && <ProductCard c={hit} />}

        {/* Vision mode */}
        <div className="bg-card dark:bg-slate-900 rounded-2xl shadow-card p-4 space-y-3">
          <p className="font-semibold flex items-center gap-2 dark:text-white"><Icon name="sparkles" size={18} className="text-primary" /> AI Vision</p>
          <div className="flex gap-2 overflow-x-auto no-scrollbar">
            {models.map(([v, label]) => (
              <button key={v} onClick={() => setModel(v)}
                className={`px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap ${model === v ? "bg-primary text-white" : "bg-slate-100 dark:bg-slate-800 text-slate-500"}`}>{label}</button>
            ))}
          </div>
          <label className="flex items-center justify-center gap-2 bg-secondary text-white font-semibold py-3 rounded-xl active:scale-[0.99] transition-transform cursor-pointer">
            <Icon name="scan" size={18} /> {busy ? "Analyzing…" : "Take photo & analyze"}
            <input type="file" accept="image/*" capture="environment" onChange={onPhoto} className="hidden" />
          </label>
          {vision && (
            <div className="text-sm space-y-1 pt-1">
              <p className="font-semibold dark:text-white">{vision.product_guess}</p>
              <div className="flex flex-wrap gap-2 text-xs">
                <span className="bg-danger/10 text-danger px-2 py-0.5 rounded-full">Penny {(vision.penny_likelihood * 100).toFixed(0)}%</span>
                <span className="bg-accent/15 text-amber-700 px-2 py-0.5 rounded-full">Clearance {(vision.clearance_likelihood * 100).toFixed(0)}%</span>
                <span className="bg-primary/10 text-primary px-2 py-0.5 rounded-full">Conf {(vision.confidence * 100).toFixed(0)}%</span>
              </div>
              <p className="text-slate-500">{vision.explanation}</p>
              <p className="text-[11px] text-slate-400">model {vision.model} · ${vision.cost_usd.toFixed(3)} · today ${vision.daily_spent_usd.toFixed(3)}</p>
            </div>
          )}
        </div>
        {msg && <p className="text-center text-sm text-amber-600">{msg}</p>}
      </div>
    </div>
  );
}
