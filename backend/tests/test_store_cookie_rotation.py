"""Store-cookie rotation tests (run: `python -m pytest` or `python <thisfile>`)."""
import os
import sys
import json
import types
import asyncio
import tempfile

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND)
os.environ.setdefault("DATABASE_URL", "sqlite:///" + os.path.join(tempfile.gettempdir(), "ph_cookie_test.db"))

from app.core.config import settings
from app.models import Store
from app.data.stores_walmart import STORES as WM_STORES
from app.services.scrapers.walmart import WalmartScraper

_NEXT = {"props": {"pageProps": {"initialData": {"searchResult": {"itemStacks": [{"items": [
    {"usItemId": "111", "name": "Mainstays Bath Towel", "brand": "Mainstays",
     "priceInfo": {"currentPrice": {"price": 0.03}, "wasPrice": {"price": 7.88}}, "badges": ["Clearance"]},
    {"usItemId": "222", "name": "onn. 32in Roku TV", "brandName": "onn.",
     "priceInfo": {"currentPrice": {"price": 98.0}, "wasPrice": {"price": 128.0}}, "rollback": True},
]}]}}}}}
JSON_HTML = '<script id="__NEXT_DATA__" type="application/json">' + json.dumps(_NEXT) + "</script>"
TILE_HTML = '<div data-item-id="111" data-name="Test Towel" data-price="0.03" data-brand="Mainstays">Clearance</div>'


def _store(code, cookie):
    return types.SimpleNamespace(store_code=code, store_cookie=cookie)


def test_a_model_has_store_cookie():
    assert "store_cookie" in Store.__table__.columns


def test_b_walmart_data_and_db_cookies_populated():
    for s in WM_STORES:
        num = s["store_code"].split("-")[1]
        assert s["store_cookie"] == f"assortment={num}"
    # locator upsert writes store_cookie into the DB (create_all-flow equivalent of the migration)
    from app.db.session import Base, engine, SessionLocal
    from app.services.locator import get_stores_near
    from sqlalchemy import select
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    asyncio.run(get_stores_near(db))
    wm = db.execute(select(Store).where(Store.chain == "Walmart")).scalars().all()
    db.close()
    assert wm and all(s.store_cookie and s.store_cookie.startswith("assortment=") for s in wm)


def test_c_scraper_uses_store_cookie():
    settings.WALMART_SCRAPE_BASE = "http://example.test"
    settings.SCRAPE_MAX_PAGES = 1
    st = _store("WM-5165", "assortment=5165")
    sc = WalmartScraper([st])
    captured = []

    async def stub(url, params=None, headers=None, as_json=False):
        captured.append(headers)
        return JSON_HTML

    sc.http.get = stub
    products = asyncio.run(sc._scrape_store(st))
    assert captured and captured[0] == {"Cookie": "assortment=5165"}
    assert products and all(p.store_code == "WM-5165" for p in products)


def test_d_multi_store_rotation():
    settings.WALMART_SCRAPE_BASE = "http://example.test"
    settings.SCRAPE_MAX_PAGES = 1
    for s in WM_STORES[:3]:
        st = _store(s["store_code"], s["store_cookie"])
        sc = WalmartScraper([st])
        seen = []

        async def stub(url, params=None, headers=None, as_json=False, _seen=seen):
            _seen.append(headers)
            return JSON_HTML

        sc.http.get = stub
        products = asyncio.run(sc._scrape_store(st))
        assert seen[0] == {"Cookie": st.store_cookie}
        assert products and all(p.store_code == st.store_code for p in products)
    # both JSON hydration and HTML fallback parse products
    probe = WalmartScraper([_store("WM-5165", "assortment=5165")])
    assert probe._parse_json(JSON_HTML, _store("WM-5165", "assortment=5165"), "clearance")
    assert probe._parse_html(TILE_HTML, _store("WM-5165", "assortment=5165"), "clearance")


def test_e_fallback_to_mock():
    settings.WALMART_SCRAPE_BASE = ""
    st = _store("WM-395", "assortment=395")
    sc = WalmartScraper([st])
    products = asyncio.run(sc._scrape_store(st))
    assert products and all(p.store_code == "WM-395" for p in products)


if __name__ == "__main__":
    for _name, _fn in sorted((n, f) for n, f in globals().items() if n.startswith("test_") and callable(f)):
        _fn()
        print("PASS", _name)
    print("ALL TESTS PASSED")
