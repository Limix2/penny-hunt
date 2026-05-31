from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models import Watchlist, WatchlistItem, User
from app.schemas import WatchlistIn, WatchlistOut

router = APIRouter(prefix="/watchlists", tags=["watchlists"])


@router.post("", response_model=WatchlistOut)
def create(data: WatchlistIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    w = Watchlist(user_id=user.id, name=data.name)
    db.add(w); db.commit(); db.refresh(w)
    return w


@router.get("", response_model=list[WatchlistOut])
def mine(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Watchlist).filter(Watchlist.user_id == user.id).all()


@router.post("/{wid}/items")
def add_item(wid: int, store_item_id: int, db: Session = Depends(get_db),
             user: User = Depends(get_current_user)):
    db.add(WatchlistItem(watchlist_id=wid, store_item_id=store_item_id)); db.commit()
    return {"ok": True}
