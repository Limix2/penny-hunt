"""Locate stores -> scrape -> upsert -> signals (incl. penny spike) -> score v2.
Also updates per-store behavior_score (v3). Returns realtime events."""
import asyncio
from datetime import datetime
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models import Store, Item, StoreItem, PriceHistory, PennySignal, AiScore
from app.services.locator import get_stores_near
from app.services.scrapers import all_scrapers
from app.services.scoring.engine import score_store_item
from app.services.scoring import llm
from app.services.store_logic import update_behavior
from app.services import runtime
from app.core.config import settings


def _upsert_item(db, p):
    item = db.execute(select(Item).where(Item.upc == p.upc)).scalar_one_or_none() if p.upc else None
    if not item:
        item = Item(upc=p.upc, sku=p.sku, name=p.name, brand=p.brand, category=p.category)
        db.add(item); db.flush()
    return item


def _upsert_store_item(db, store, item, p):
    si = db.execute(select(StoreItem).where(StoreItem.store_id == store.id,
                                            StoreItem.item_id == item.id)).scalar_one_or_none()
    now = datetime.utcnow()
    if not si:
        si = StoreItem(store_id=store.id, item_id=item.id, current_price=p.price,
                       regular_price=p.regular_price, clearance_flag=p.clearance,
                       first_seen_at=now, last_seen_at=now)
        db.add(si); db.flush()
        return si, True
    changed = si.current_price != p.price
    si.current_price, si.regular_price = p.price, p.regular_price or si.regular_price
    si.clearance_flag, si.last_seen_at = p.clearance, now
    return si, changed


def _signals(db, si, p, penny_spike):
    sigs = []
    if p.price is not None and p.price <= 0.05:
        sigs.append(PennySignal(store_item_id=si.id, signal_type="near_zero", signal_value=p.price))
    if p.regular_price and (p.regular_price - p.price) / p.regular_price >= 0.5:
        sigs.append(PennySignal(store_item_id=si.id, signal_type="price_drop",
                                signal_value=round((p.regular_price - p.price) / p.regular_price, 3)))
    if p.clearance:
        sigs.append(PennySignal(store_item_id=si.id, signal_type="clearance_flag", signal_value=1.0))
    if penny_spike:
        sigs.append(PennySignal(store_item_id=si.id, signal_type="penny_spike", signal_value=1.0))
    for s in sigs:
        db.add(s)
    return sigs


async def run_ingest_async() -> list[dict]:
    db = SessionLocal()
    try:
        stores = await get_stores_near(db)
        events: list[dict] = []
        for scraper in all_scrapers(stores):
            store_map = {s.store_code: s for s in scraper.stores}
            products = await scraper.fetch()
            spike = {}
            for p in products:
                if p.price is not None and p.price <= 0.05:
                    spike[p.store_code] = spike.get(p.store_code, 0) + 1
            for code, st in store_map.items():
                update_behavior(st, spike.get(code, 0))  # behavior modeling v3
            for p in products:
                store = store_map.get(p.store_code) or db.execute(
                    select(Store).where(Store.store_code == p.store_code)).scalar_one()
                item = _upsert_item(db, p)
                si, changed = _upsert_store_item(db, store, item, p)
                if changed:
                    db.add(PriceHistory(store_item_id=si.id, price=p.price,
                                        observed_at=datetime.utcnow(), source=scraper.chain))
                is_spike = spike.get(p.store_code, 0) >= 2
                sigs = _signals(db, si, p, is_spike)
                prices = [ph.price for ph in db.execute(
                    select(PriceHistory).where(PriceHistory.store_item_id == si.id)
                    .order_by(PriceHistory.observed_at)).scalars().all()]
                res = score_store_item(si, prices, sigs, store.reliability or 0.8)
                score, mv, expl = await llm.refine(res.score, res.explanation,
                                                   {"price": p.price, "chain": scraper.chain})
                db.add(AiScore(store_item_id=si.id, score=score, model_version=mv, explanation=expl))
                db.flush()
                if score >= settings.SCORE_BROADCAST_THRESHOLD:
                    events.append({"type": "store_spike" if is_spike else "new_candidate",
                                   "id": si.id, "score": score, "explanation": expl,
                                   "current_price": si.current_price, "regular_price": si.regular_price,
                                   "store": {"name": store.name, "chain": store.chain,
                                             "city": store.city, "state": store.state,
                                             "lat": store.lat, "lon": store.lon,
                                             "behavior_score": store.behavior_score},
                                   "item": {"name": item.name, "upc": item.upc},
                                   "timestamp": datetime.utcnow().isoformat()})
            db.commit()
        runtime.STATE["last_ingest_at"] = datetime.utcnow().isoformat()
        return events
    finally:
        db.close()


def run_ingest() -> list[dict]:
    return asyncio.run(run_ingest_async())
