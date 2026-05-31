from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas import StoreSummary, StoreOut, Candidate, NoteIn, NoteOut
from app.services import queries
from app.services.locator import get_stores_near
from app.services.store_logic import is_open, distance_eta
from app.api.routes.items import make_candidate
from app.api.deps import get_current_user
from app.geo import latlon
from app.models import Store, StoreNote, User
from app.core.config import settings

router = APIRouter(prefix="/stores", tags=["stores"])


def _summary(st, count, lat0, lon0) -> StoreSummary:
    d, eta = distance_eta(lat0, lon0, st.lat, st.lon)
    return StoreSummary(**StoreOut.model_validate(st).model_dump(), high_score_count=count,
                        open_now=is_open(st.hours_json), distance_miles=d, eta_min=eta)


@router.get("", response_model=list[StoreSummary])
def list_stores(db: Session = Depends(get_db)):
    lat0, lon0 = latlon(settings.TARGET_ZIP)
    rows = queries.store_summaries(db, settings.SCORE_BROADCAST_THRESHOLD)
    return [_summary(st, c, lat0, lon0) for (st, c) in rows]


@router.get("/near", response_model=list[StoreSummary])
async def near(zip: str | None = None, radius: float | None = None, db: Session = Depends(get_db)):
    stores = await get_stores_near(db, zip, radius)
    lat0, lon0 = latlon(zip or settings.TARGET_ZIP)
    items = [_summary(s, 0, lat0, lon0) for s in stores]
    return sorted(items, key=lambda x: x.distance_miles if x.distance_miles is not None else 1e9)


@router.get("/{store_id}", response_model=StoreSummary)
def store_detail(store_id: int, db: Session = Depends(get_db)):
    st = db.get(Store, store_id)
    if not st:
        raise HTTPException(404, "Not found")
    lat0, lon0 = latlon(settings.TARGET_ZIP)
    count = len(queries.store_candidates(db, store_id, settings.SCORE_BROADCAST_THRESHOLD))
    return _summary(st, count, lat0, lon0)


@router.get("/{store_id}/items", response_model=list[Candidate])
def store_items(store_id: int, min_score: float = 0.0, db: Session = Depends(get_db)):
    return [make_candidate(*r) for r in queries.store_candidates(db, store_id, min_score)]


@router.get("/{store_id}/notes", response_model=list[NoteOut])
def list_notes(store_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (db.query(StoreNote)
            .filter(StoreNote.store_id == store_id, StoreNote.user_id == user.id)
            .order_by(StoreNote.created_at.desc()).all())


@router.post("/{store_id}/notes", response_model=NoteOut)
def add_note(store_id: int, data: NoteIn, db: Session = Depends(get_db),
             user: User = Depends(get_current_user)):
    n = StoreNote(store_id=store_id, user_id=user.id, text=data.text)
    db.add(n); db.commit(); db.refresh(n)
    return n
