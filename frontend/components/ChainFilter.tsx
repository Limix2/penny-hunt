"use client";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import { CHAINS } from "@/lib/chains";

export function ChainFilter() {
  const router = useRouter();
  const pathname = usePathname();
  const sp = useSearchParams();
  const selected = (sp.get("chains") || "").split(",").filter(Boolean);

  const toggle = (code: string) => {
    const next = selected.includes(code) ? selected.filter((c) => c !== code) : [...selected, code];
    const params = new URLSearchParams(Array.from(sp.entries()));
    if (next.length) params.set("chains", next.join(",")); else params.delete("chains");
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  };

  return (
    <div className="flex flex-wrap gap-2">
      {CHAINS.map((c) => {
        const on = selected.includes(c.code);
        return (
          <button key={c.code} onClick={() => toggle(c.code)}
            style={{ borderColor: c.color, backgroundColor: on ? c.color : "transparent" }}
            className={`px-3 py-1 rounded-full text-xs font-semibold border-2 transition-all duration-200 ${on ? "text-white scale-105" : "text-slate-600 dark:text-slate-300"}`}>
            {c.label}
          </button>
        );
      })}
    </div>
  );
}
