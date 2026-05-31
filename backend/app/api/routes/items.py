from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas import Candidate, StoreOut, ItemOut, ItemDetail, PricePoint, ScorePoint
from app.services import queries

router = APIRouter(prefix="/items", tags=["items"])


def make_candidate(si, sc, st, it) -> Candidate:
    return Candidate(id=si.id, store=StoreOut.model_validate(st), item=ItemOut.model_validate(it),
                     current_price=si.current_price, regular_price=si.regular_price,
                     clearance_flag=si.clearance_flag, last_seen_at=si.last_seen_at,
                     score=sc.score if sc else None, model_version=sc.model_version if sc else None,
                     explanation=sc.explanation if sc else None,
                     scored_at=sc.created_at if sc else None)


@router.get("/top", response_model=list[Candidate])
def top_items(hours: int = 24, limit: int = Query(50, le=200), min_score: float = 0.0,
              db: Session = Depends(get_db)):
    return [make_candidate(*r) for r in queries.top_candidates(db, hours, limit, min_score)]


@router.get("/lookup", response_model=Candidate)
def lookup(upc: str, db: Session = Depends(get_db)):
    r = queries.lookup_by_upc(db, upc)
    if not r:
        raise HTTPException(404, "UPC not found")
    return make_candidate(*r)


@router.get("/{store_item_id}", response_model=ItemDetail)
def detail(store_item_id: int, db: Session = Depends(get_db)):
    res = queries.candidate_detail(db, store_item_id)
    if not res:
        raise HTTPException(404, "Not found")
    si, latest, prices, scores = res
    base = make_candidate(si, latest, si.store, si.item)
    return ItemDetail(**base.model_dump(),
                      price_history=[PricePoint.model_validate(p) for p in prices],
                      score_history=[ScorePoint.model_validate(s) for s in scores])
