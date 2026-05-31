# 🪙 Penny Hunt

Penny item & deep-clearance detection platform: locate stores near a ZIP, scrape
prices, score "penny likelihood" (rules + optional LLM), and surface candidates in a
mobile-first PWA with live updates, barcode scanning, AI vision, and a store map.

**Stack:** FastAPI + SQLAlchemy (SQLite dev / Postgres prod) · Next.js 14 App Router +
TypeScript + Tailwind · WebSocket live feed · PWA.

> ⚠️ **Scraper & locator notes:** Real Dollar General / Home Depot store-locator and
> product endpoints are not publicly stable and scraping them may violate each
> retailer's Terms of Service. This project ships **runnable mock/seeded data** by
> default and only performs real HTTP when you set `DG_LOCATOR_URL` / `HD_LOCATOR_URL`
> and implement the real product fetch. Review each site's ToS and robots.txt before
> enabling live scraping.

## Run locally (SQLite, no Docker)
```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy ..\.env.example .env        # macOS/Linux: cp ../.env.example .env  (SQLite by default)
uvicorn app.main:app --reload    # http://localhost:8000/docs

# Seed data immediately (optional): POST http://localhost:8000/scores/refresh

# Frontend (new terminal)
cd frontend
copy .env.local.example .env.local
npm install
npm run dev                      # http://localhost:3000
```

## Run with Docker (Postgres)
```bash
# set the Postgres DATABASE_URL line in .env (copy from .env.example)
docker compose up --build        # db + backend + frontend, with healthchecks
# open http://localhost:3000
```

## Mobile usage
- Open `http://<your-LAN-ip>:3000` on your phone (same Wi-Fi); set
  `NEXT_PUBLIC_API_BASE`/`NEXT_PUBLIC_WS_URL` to your machine's LAN IP.
- Bottom tab bar: **Radar / Scan / Map / Stores**. Modes: Radar, DealStorm
  (score ≥ 80), PennyRadar (≤ $0.05). **In-store** toggle trims detail for low data.
- **Barcode scanner** (`/scan`) is camera-based and free (html5-qrcode); a scanned UPC
  hits `/items/lookup`. Camera requires HTTPS or `localhost`.

## PWA install
- `frontend/public/manifest.json` + `sw.js` provide offline caching and installability.
- Chrome/Android: ⋮ → *Install app*. iOS Safari: Share → *Add to Home Screen*.
- Replace `public/icon.svg` with 192/512 PNG icons for best store/install support.

## AI Vision configuration & model switcher
`POST /vision/analyze` (multipart: `image`, `model`). Models:
- `local` — free on-device heuristic, **no network, no key** (default/fallback).
- `deepseek` — DeepSeek Vision; set `DEEPSEEK_API_KEY`.
- `claude` — Claude Opus 4.8 Vision; set `ANTHROPIC_API_KEY`.

The `/scan` page has a dropdown switcher and shows per-request + daily cost.

### Cost limits
`VISION_DAILY_COST_LIMIT_USD` caps paid spend per rolling 24h (summed from
`vision_logs`). If a paid request would exceed it, the server **auto-falls back to
`local`**. Missing API keys also fall back to `local` at zero cost.

## Scoring Engine v2 (`services/scoring/engine.py`)
Rules: near-zero ≤$0.05 (+40), penny ≤$0.01 (+10), ≥50% drop (+20), clearance flag
(+30), markdown cycle (+10), store penny spike (+10), stale >30d (−10), weighted by
store reliability, clamped 0–100. Optional Claude refinement via `scoring/llm.py`
(`ENABLE_LLM_SCORING=true`). Scores ≥ `SCORE_BROADCAST_THRESHOLD` broadcast over
`/ws/live` as `new_candidate` / `store_spike` (DealStorm) events.

## Key endpoints
`/health` · `/auth/register|login` · `/items/top` · `/items/lookup?upc=` ·
`/items/{id}` · `/stores` · `/stores/near?zip=` · `/stores/{id}/items` ·
`/scores/refresh` · `/vision/analyze` · `/watchlists` · WS `/ws/live`.

## Security note
v1 read endpoints and `/scores/refresh` are **unauthenticated** for demo convenience.
Gate them behind `get_current_user` and add rate limiting before any public deploy.

## Scale-up roadmap
Redis pub/sub for multi-replica WebSockets · Celery/RQ workers + `python -m app.worker`
cron · Alembic migrations · real scraper integrations with proxy rotation & UPC dedupe
· calibrated per-chain models · PNG PWA icons + push notifications.
