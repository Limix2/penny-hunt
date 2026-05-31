from fastapi import APIRouter
from app.services.ingest import run_ingest_async
from app.realtime.hub import hub

router = APIRouter(prefix="/scores", tags=["scores"])


@router.post("/refresh")
async def refresh():
    events = await run_ingest_async()
    for e in events:
        await hub.broadcast(e)
    return {"events": len(events)}
