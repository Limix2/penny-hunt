from datetime import datetime, timedelta
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session
from app.models import Store, Item, StoreItem, PriceHistory, AiScore


def _latest():
    return (select(AiScore.store_item_id.label("sid"), func.max(AiScore.created_at).label("mx"))
            .group_by(AiScore.store_item_id).subquery())


def _join(extra_where):
    sub = _latest()
    return (select(StoreItem, AiScore, Store, Item)
            .join(sub, sub.c.sid == StoreItem.id)
            .join(AiScore, (AiScore.store_item_id == sub.c.sid) & (AiScore.created_at == sub.c.mx))
            .join(Store, Store.id == StoreItem.store_id)
            .join(Item, Item.id == StoreItem.item_id)
            .where(*extra_where))


def top_candidates(db: Session, hours=24, limit=50, min_score=0.0):
    q = (_join([AiScore.created_at >= datetime.utcnow() - timedelta(hours=hours),
                AiScore.score >= min_score])
         .order_by(desc(AiScore.score), desc(AiScore.created_at)).limit(limit))
    return db.execute(q).all()


def store_candidates(db: Session, store_id: int, min_score=0.0):
    q = _join([StoreItem.store_id == store_id, AiScore.score >= min_score]).order_by(desc(AiScore.score))
    return db.execute(q).all()


def lookup_by_upc(db: Session, upc: str):
    q = _join([Item.upc == upc]).order_by(desc(AiScore.created_at)).limit(1)
    return db.execute(q).first()


def store_summaries(db: Session, min_score=80.0):
    sub = _latest()
    latest = (select(AiScore.store_item_id.label("sid"), AiScore.score.label("score"))
              .join(sub, (AiScore.store_item_id == sub.c.sid) & (AiScore.created_at == sub.c.mx))
              .subquery())
    q = (select(Store, func.count(latest.c.sid))
         .outerjoin(StoreItem, StoreItem.store_id == Store.id)
         .outerjoin(latest, (latest.c.sid == StoreItem.id) & (latest.c.score >= min_score))
         .group_by(Store.id).order_by(desc(func.count(latest.c.sid))))
    return db.execute(q).all()


def candidate_detail(db: Session, sid: int):
    si = db.get(StoreItem, sid)
    if not si:
        return None
    latest = db.execute(select(AiScore).where(AiScore.store_item_id == sid)
                        .order_by(desc(AiScore.created_at)).limit(1)).scalar_one_or_none()
    prices = db.execute(select(PriceHistory).where(PriceHistory.store_item_id == sid)
                        .order_by(PriceHistory.observed_at)).scalars().all()
    scores = db.execute(select(AiScore).where(AiScore.store_item_id == sid)
                        .order_by(AiScore.created_at)).scalars().all()
    return si, latest, prices, scores
