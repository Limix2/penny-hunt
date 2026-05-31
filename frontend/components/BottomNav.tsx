"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Icon } from "./ui/Icon";

const TABS = [
  ["/", "Radar", "radar"], ["/scan", "Scan", "scan"], ["/map", "Map", "map"],
  ["/stores", "Stores", "store"], ["/admin", "Admin", "bell"],
] as const;

export function BottomNav() {
  const path = usePathname();
  return (
    <nav className="fixed bottom-0 inset-x-0 z-50 bg-card/90 dark:bg-slate-900/90 backdrop-blur border-t border-black/5 dark:border-white/10 safe-bottom">
      <div className="mx-auto max-w-2xl grid grid-cols-5">
        {TABS.map(([href, label, icon]) => {
          const active = href === "/" ? path === "/" : path.startsWith(href);
          return (
            <Link key={href} href={href}
              className={`flex flex-col items-center gap-1 py-2.5 text-[11px] font-semibold transition-colors ${active ? "text-primary" : "text-slate-400"}`}>
              <span className={`grid place-items-center rounded-xl px-3 py-1 transition-colors ${active ? "bg-primary/10" : ""}`}>
                <Icon name={icon} size={22} />
              </span>
              {label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
