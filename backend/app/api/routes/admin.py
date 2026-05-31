"""Admin endpoints (auth required)."""
import time
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models import User
from app.services.ingest import run_ingest_async
from app.realtime.hub import hub

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/run-ingest")
async def run_ingest_now(user: User = Depends(get_current_user)):
    """Run one ingest cycle now and broadcast its events. Returns a summary."""
    t0 = time.perf_counter()
    events = await run_ingest_async()
    for e in events:
        await hub.broadcast(e)
    return {"events_created": len(events), "duration_seconds": round(time.perf_counter() - t0, 2)}
