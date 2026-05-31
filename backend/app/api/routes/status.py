"""Public status endpoint (last updated timestamp)."""
from fastapi import APIRouter
from app.services import runtime

router = APIRouter(tags=["status"])


@router.get("/status")
def status():
    return {"last_ingest_at": runtime.STATE.get("last_ingest_at")}
