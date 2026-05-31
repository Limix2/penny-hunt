"use client";
import { useEffect, useState } from "react";
import { Icon } from "./ui/Icon";

export function PWAInstall() {
  const [evt, setEvt] = useState<any>(null);
  const [show, setShow] = useState(false);
  useEffect(() => {
    const h = (e: any) => { e.preventDefault(); setEvt(e); setShow(true); };
    window.addEventListener("beforeinstallprompt", h);
    return () => window.removeEventListener("beforeinstallprompt", h);
  }, []);
  if (!show) return null;
  return (
    <div className="fixed bottom-24 inset-x-3 z-50 max-w-2xl mx-auto bg-card dark:bg-slate-900 rounded-2xl shadow-hover p-3 flex items-center gap-3 animate-slideUp">
      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary grid place-items-center text-white font-bold">1¢</div>
      <div className="flex-1 text-sm">
        <p className="font-semibold dark:text-white">Install Penny Hunt</p>
        <p className="text-xs text-slate-500">Add to your home screen for offline access.</p>
      </div>
      <button onClick={async () => { await evt?.prompt(); setShow(false); }}
        className="bg-primary text-white text-sm font-semibold px-3 py-2 rounded-xl">Install</button>
      <button onClick={() => setShow(false)} className="text-slate-400 px-1" aria-label="Dismiss"><Icon name="x" size={18} /></button>
    </div>
  );
}
