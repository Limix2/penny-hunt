"use client";
import { useEffect, useRef, useState } from "react";
import { WS_URL } from "./api";

export interface LiveEvent {
  type: string; id: number; score: number; explanation: string;
  current_price: number; regular_price?: number; timestamp: string;
  store: { name: string; chain: string; city?: string; state?: string; lat?: number; lon?: number };
  item: { name: string; upc?: string };
}

export function useLiveScores() {
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const ref = useRef<WebSocket | null>(null);
  useEffect(() => {
    let ws: WebSocket;
    try { ws = new WebSocket(WS_URL); } catch { return; }
    ref.current = ws;
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (e) => {
      try { const d = JSON.parse(e.data); setEvents((p) => [d, ...p].slice(0, 50)); } catch {}
    };
    return () => ws.close();
  }, []);
  return { events, connected };
}
