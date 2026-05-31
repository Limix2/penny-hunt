"use client";
import { useEffect, useState } from "react";
import { api, getToken } from "@/lib/api";
import { HeaderBar } from "@/components/HeaderBar";
import { timeAgo } from "@/lib/chains";

export default function Admin() {
  const [authed, setAuthed] = useState(false);
  const [email, setEmail] = useState("");
  const [pwd, setPwd] = useState("");
  const [busy, setBusy] = useState(false);
  const [toast, setToast] = useState("");
  const [updated, setUpdated] = useState<string | null>(null);

  const refreshStatus = () => api.status().then((s) => setUpdated(s.last_ingest_at)).catch(() => {});
  useEffect(() => { setAuthed(!!getToken()); refreshStatus(); }, []);

  const signIn = async () => {
    setBusy(true); setToast("");
    try { await api.login(email, pwd); setAuthed(true); }
    catch {
      try { await api.register(email, pwd); setAuthed(true); }
      catch { setToast("Sign-in failed. Check credentials."); }
    } finally { setBusy(false); }
  };

  const run = async () => {
    setBusy(true); setToast("");
    try {
      const r = await api.runIngest();
      setToast(`✓ ${r.events_created} events created in ${r.duration_seconds}s`);
      await refreshStatus();
    } catch { setToast("Ingest failed — please sign in again."); }
    finally { setBusy(false); }
  };

  return (
    <div>
      <HeaderBar title="Admin" subtitle="Manual ingest control" />
      <div className="mx-auto max-w-md px-4 pt-4 -mt-4 pb-4 space-y-4">
        <p className="text-xs text-slate-400">Last updated: {timeAgo(updated)}</p>

        {!authed ? (
          <div className="bg-card dark:bg-slate-900 rounded-2xl shadow-card p-4 space-y-3 animate-fadeIn">
            <p className="font-semibold dark:text-white">Sign in</p>
            <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="email" type="email"
              className="w-full rounded-xl border border-slate-300 dark:border-slate-700 dark:bg-slate-800 px-3 py-2 text-sm" />
            <input value={pwd} onChange={(e) => setPwd(e.target.value)} placeholder="password" type="password"
              className="w-full rounded-xl border border-slate-300 dark:border-slate-700 dark:bg-slate-800 px-3 py-2 text-sm" />
            <button onClick={signIn} disabled={busy}
              className="w-full bg-primary text-white font-semibold py-2.5 rounded-xl disabled:opacity-50">
              {busy ? "…" : "Sign in / Register"}
            </button>
          </div>
        ) : (
          <button onClick={run} disabled={busy}
            className="w-full bg-primary text-white font-semibold py-3 rounded-xl shadow-card flex items-center justify-center gap-2 disabled:opacity-60 active:scale-[0.99] transition-transform">
            {busy && <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />}
            {busy ? "Running ingest…" : "Run ingest now"}
          </button>
        )}

        {toast && <div className="rounded-xl bg-card dark:bg-slate-900 shadow-card p-3 text-sm dark:text-white animate-slideUp">{toast}</div>}
      </div>
    </div>
  );
}
