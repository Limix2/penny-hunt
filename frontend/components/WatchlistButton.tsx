"use client";
import { useEffect, useState } from "react";
import { Icon } from "./ui/Icon";

const KEY = "ph-watchlist";

export function WatchlistButton({ id }: { id: number }) {
  const [on, setOn] = useState(false);
  useEffect(() => {
    try { setOn(JSON.parse(localStorage.getItem(KEY) || "[]").includes(id)); } catch {}
  }, [id]);
  const toggle = () => {
    let list: number[] = [];
    try { list = JSON.parse(localStorage.getItem(KEY) || "[]"); } catch {}
    const next = on ? list.filter((x) => x !== id) : [...list, id];
    localStorage.setItem(KEY, JSON.stringify(next));
    setOn(!on);
  };
  return (
    <button onClick={toggle} aria-label="Watchlist"
      className={`grid place-items-center w-11 h-11 rounded-full transition-all active:scale-90 ${on ? "bg-white text-danger" : "bg-white/20 text-white"}`}>
      <Icon name="heart" size={22} filled={on} />
    </button>
  );
}
