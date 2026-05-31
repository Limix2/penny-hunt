import * as React from "react";

type IconName =
  | "radar" | "scan" | "map" | "store" | "clock" | "nav" | "drop"
  | "tag" | "coin" | "search" | "bell" | "heart" | "chevron" | "sparkles" | "x";

const PATHS: Record<IconName, React.ReactNode> = {
  radar: <><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="3.5" /><path d="M12 12 18 8" /></>,
  scan: <><path d="M4 7V5a1 1 0 0 1 1-1h2" /><path d="M17 4h2a1 1 0 0 1 1 1v2" /><path d="M20 17v2a1 1 0 0 1-1 1h-2" /><path d="M7 20H5a1 1 0 0 1-1-1v-2" /><path d="M4 12h16" /></>,
  map: <><path d="M12 21s-7-6.5-7-11a7 7 0 1 1 14 0c0 4.5-7 11-7 11Z" /><circle cx="12" cy="10" r="2.5" /></>,
  store: <><path d="M3 9 4.2 4h15.6L21 9" /><path d="M5 9v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9" /><path d="M9 20v-6h6v6" /></>,
  clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
  nav: <path d="m3 11 18-8-8 18-2-8-8-2Z" />,
  drop: <><path d="m22 17-8.5-8.5-5 5L2 7" /><path d="M16 17h6v-6" /></>,
  tag: <><path d="M20.6 13.4 12 22l-9-9V4a1 1 0 0 1 1-1h8l8.6 8.6a2 2 0 0 1 0 2.8Z" /><circle cx="7.5" cy="7.5" r="1.4" /></>,
  coin: <><circle cx="12" cy="12" r="9" /><path d="M12 7.5v9" /><path d="M14.3 9.7H10.6a1.6 1.6 0 0 0 0 3.2h2.8a1.6 1.6 0 0 1 0 3.2H9.5" /></>,
  search: <><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" /></>,
  bell: <><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9Z" /><path d="M10 21a2 2 0 0 0 4 0" /></>,
  heart: <path d="M20.8 5.6a5 5 0 0 0-7.1 0L12 7.3l-1.7-1.7a5 5 0 1 0-7.1 7.1L12 21l8.8-8.3a5 5 0 0 0 0-7.1Z" />,
  chevron: <path d="m9 6 6 6-6 6" />,
  sparkles: <><path d="M12 3l1.8 4.2L18 9l-4.2 1.8L12 15l-1.8-4.2L6 9l4.2-1.8Z" /><path d="M5 16l.9 2.1L8 19l-2.1.9L5 22l-.9-2.1L2 19l2.1-.9Z" /></>,
  x: <path d="M6 6l12 12M18 6 6 18" />,
};

export function Icon({ name, size = 20, className = "", filled = false }:
  { name: IconName; size?: number; className?: string; filled?: boolean }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={filled ? "currentColor" : "none"}
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className={className}>
      {PATHS[name]}
    </svg>
  );
}
