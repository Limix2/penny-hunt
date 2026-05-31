"use client";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [dark, setDark] = useState(false);
  useEffect(() => { setDark(document.documentElement.classList.contains("dark")); }, []);
  const toggle = () => {
    const next = !dark;
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("ph-theme", next ? "dark" : "light");
    setDark(next);
  };
  return (
    <button onClick={toggle} aria-label="Toggle theme"
      className="fixed top-3 right-3 z-[60] w-10 h-10 rounded-full bg-card/90 dark:bg-slate-800/90 backdrop-blur shadow-card grid place-items-center text-lg transition-colors active:scale-90">
      {dark ? "☀️" : "🌙"}
    </button>
  );
}
