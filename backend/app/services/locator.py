"""Store locator backed by the full store network (app.data.stores_full.STORES).

On first run (or when the 24h cache is stale) every store is upserted with an
approximate geocode (Option B). get_stores_near() returns stores within `radius`
miles of the target ZIP.
"""
from datetime import datetime, timedelta
from sqlalchemy import select
from app.geo import latlon, approx_latlon, haversine_miles
from app.models import Store, StoreCache
from app.data.stores_full import STORES
from app.data.stores_walmart import STORES as WALMART_STORES
from app.data.stores_heb import HEB_STORES
from app.core.config import settings


def _upsert(db, raw: dict) -> Store:
    s = db.execute(select(Store).where(Store.store_code == raw["store_code"])).scalar_one_or_none()
    lat, lon = raw.get("lat"), raw.get("lon")
    if lat is None or lon is None:
        lat, lon = approx_latlon(raw["zip"], raw["store_code"])
    if not s:
        s = Store(chain=raw["chain"], name=raw["name"], address=raw["address"],
                  city=raw["city"], state=raw["state"], zip=raw["zip"],
                  phone=raw.get("phone"), hours_json=raw.get("hours"), store_cookie=raw.get("store_cookie"),
                  store_code=raw["store_code"], lat=lat, lon=lon)
        db.add(s)
        db.flush()
    else:
        s.phone, s.hours_json = raw.get("phone"), raw.get("hours")
        s.store_cookie = raw.get("store_cookie") or s.store_cookie
        if s.lat is None:
            s.lat, s.lon = lat, lon
    return s


async def get_stores_near(db, zipcode: str | None = None, radius: float | None = None) -> list[Store]:
    zipcode = zipcode or settings.TARGET_ZIP
    radius = radius if radius is not None else settings.RADIUS_MILES
    cache = db.execute(select(StoreCache).where(StoreCache.zip == zipcode)
                       .order_by(StoreCache.fetched_at.desc())).scalars().first()
    fresh = cache and cache.fetched_at > datetime.utcnow() - timedelta(hours=24)
    if not fresh:
        for raw in STORES + WALMART_STORES + HEB_STORES:
            _upsert(db, raw)
        db.add(StoreCache(zip=zipcode, radius_miles=radius,
                          payload_json={"count": len(STORES) + len(WALMART_STORES) + len(HEB_STORES)}))
        db.commit()
    lat0, lon0 = latlon(zipcode)
    out = []
    for s in db.execute(select(Store)).scalars().all():
        if s.lat is None or s.lon is None:
            continue
        if haversine_miles(lat0, lon0, s.lat, s.lon) <= radius:
            out.append(s)
    return out
