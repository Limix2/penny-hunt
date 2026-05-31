import asyncio
import contextlib
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import Base, engine
from app.realtime.hub import hub
from app.services.ingest import run_ingest_async
from app.api.routes import auth, items, stores, scores, vision, watchlists, admin, status

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("penny_hunt")
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Penny Hunt API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
for r in (auth.router, items.router, stores.router, scores.router, vision.router,
          watchlists.router, admin.router, status.router):
    app.include_router(r)


@app.get("/health")
def health():
    return {"status": "ok", "target_zip": settings.TARGET_ZIP, "radius_miles": settings.RADIUS_MILES}


@app.websocket("/ws/live")
async def ws_live(ws: WebSocket):
    await hub.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await hub.disconnect(ws)


async def _scheduler():
    while True:
        try:
            for e in await run_ingest_async():
                await hub.broadcast(e)
        except Exception:
            log.exception("ingest cycle failed")
        await asyncio.sleep(settings.SCRAPE_INTERVAL_SECONDS)


@app.on_event("startup")
async def _startup():
    app.state.task = asyncio.create_task(_scheduler())


@app.on_event("shutdown")
async def _shutdown():
    t = getattr(app.state, "task", None)
    if t:
        t.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await t
