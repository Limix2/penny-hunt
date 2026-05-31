export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws/live";
export const TARGET: [number, number] = [26.262, -98.131]; // ZIP 78542 centroid

export interface Store {
  id: number; chain: string; name: string; address?: string; city?: string; state?: string; zip?: string;
  lat?: number; lon?: number; phone?: string; hours_json?: Record<string, string[]>;
  reliability?: number; behavior_score?: number;
}
export interface Item { id: number; name: string; upc?: string; sku?: string; brand?: string; category?: string; image_url?: string; }
export interface Candidate {
  id: number; store: Store; item: Item;
  current_price?: number; regular_price?: number; clearance_flag: boolean;
  last_seen_at?: string; score?: number; model_version?: string; explanation?: string; scored_at?: string;
}
export interface PricePoint { price: number; observed_at: string; source?: string; }
export interface ScorePoint { score: number; model_version?: string; explanation?: string; created_at: string; }
export interface ItemDetail extends Candidate { price_history: PricePoint[]; score_history: ScorePoint[]; }
export interface StoreSummary extends Store { high_score_count: number; open_now: boolean; distance_miles?: number; eta_min?: number; }
export interface VisionResult {
  model: string; product_guess: string; penny_likelihood: number;
  clearance_likelihood: number; confidence: number; explanation: string;
  cost_usd: number; daily_spent_usd: number;
}

const TOKEN_KEY = "ph-token";
export const setToken = (t: string) => { if (typeof window !== "undefined") localStorage.setItem(TOKEN_KEY, t); };
export const getToken = () => (typeof window !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null);

export function distMiles(lat?: number, lon?: number): number {
  if (lat == null || lon == null) return Infinity;
  const [a, b] = TARGET, R = 3958.8, rad = Math.PI / 180;
  const dLat = (lat - a) * rad, dLon = (lon - b) * rad;
  const s = Math.sin(dLat / 2) ** 2 + Math.cos(a * rad) * Math.cos(lat * rad) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.asin(Math.sqrt(s));
}

async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!r.ok) throw new Error(`${path} -> ${r.status}`);
  return r.json();
}

export const api = {
  topItems: (hours = 24, minScore = 0, limit = 50) =>
    get<Candidate[]>(`/items/top?hours=${hours}&min_score=${minScore}&limit=${limit}`),
  itemDetail: (id: number) => get<ItemDetail>(`/items/${id}`),
  lookupUpc: (upc: string) => get<Candidate>(`/items/lookup?upc=${encodeURIComponent(upc)}`),
  stores: () => get<StoreSummary[]>(`/stores`),
  storeDetail: (id: number) => get<StoreSummary>(`/stores/${id}`),
  storeItems: (id: number, minScore = 0) => get<Candidate[]>(`/stores/${id}/items?min_score=${minScore}`),
  refresh: () => fetch(`${API_BASE}/scores/refresh`, { method: "POST" }),
  status: () => get<{ last_ingest_at: string | null }>(`/status`),
  vision: async (file: File, model: string): Promise<VisionResult> => {
    const fd = new FormData();
    fd.append("image", file);
    fd.append("model", model);
    const r = await fetch(`${API_BASE}/vision/analyze`, { method: "POST", body: fd });
    if (!r.ok) throw new Error(`vision -> ${r.status}`);
    return r.json();
  },
  login: async (email: string, password: string) => {
    const body = new URLSearchParams({ username: email, password });
    const r = await fetch(`${API_BASE}/auth/login`, {
      method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body,
    });
    if (!r.ok) throw new Error("login failed");
    const data = await r.json(); setToken(data.access_token); return data;
  },
  register: async (email: string, password: string) => {
    const r = await fetch(`${API_BASE}/auth/register`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!r.ok) throw new Error("register failed");
    const data = await r.json(); setToken(data.access_token); return data;
  },
  runIngest: async (): Promise<{ events_created: number; duration_seconds: number }> => {
    const r = await fetch(`${API_BASE}/admin/run-ingest`, {
      method: "POST", headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!r.ok) throw new Error(`run-ingest ${r.status}`);
    return r.json();
  },
};
