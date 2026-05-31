"""H-E-B scraper — live JSON/HTML path + mock fallback.

HONEST NOTES:
- H-E-B's site structure (Next.js) changes frequently and is bot-protected; JSON/HTML
  parsing here is best-effort.
- Store-level pricing/availability may require a valid store cookie (Store.store_cookie),
  sent as the Cookie header when present.
- UA rotation + delays are "good citizen" stability measures, NOT a bypass.
- Live scraping must respect H-E-B's Terms of Service. Enable at your discretion.

Live path is ON when HEB_SCRAPE_BASE is set; otherwise the realistic mock runs.
"""
import asyncio
import json
import logging
import random
import re
from app.core.config import settings
from app.services.scrapers.base import BaseScraper, ScrapedProduct
from app.services.scrapers.http import Fetcher

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

log = logging.getLogger(__name__)

CATEGORIES = ["clearance", "grocery", "household", "beauty", "home", "seasonal"]
_SCRIPT_RE = re.compile(r"<script[^>]*>(.*?)</script>", re.S)
_PRICE_RE = re.compile(r"\$\s*([\d,]+\.\d{2}|\d[\d,]*)")
_ID_RE = re.compile(r"/(\d{5,})")
_PENNY = [0.01, 0.03, 0.04, 0.05]
_CATALOG = [
    {"upc": "HEB-0001", "sku": "20001", "name": "H-E-B Tortilla Chips", "brand": "H-E-B", "cat": "Grocery", "reg": 2.48},
    {"upc": "HEB-0002", "sku": "20002", "name": "H-E-B Laundry Detergent", "brand": "H-E-B", "cat": "Household", "reg": 7.97},
    {"upc": "HEB-0003", "sku": "20003", "name": "H-E-B Flour Tortillas", "brand": "H-E-B", "cat": "Grocery", "reg": 1.98},
    {"upc": "HEB-0004", "sku": "20004", "name": "H-E-B Restaurant Salsa", "brand": "H-E-B", "cat": "Grocery", "reg": 2.78},
    {"upc": "HEB-0005", "sku": "20005", "name": "H-E-B Home Bath Towel", "brand": "H-E-B Home", "cat": "Home", "reg": 6.99},
]


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


class HEBScraper(BaseScraper):
    chain = "H-E-B"

    def __init__(self, stores):
        super().__init__(stores)
        self.http = Fetcher(concurrency=settings.SCRAPE_CONCURRENCY)

    async def fetch(self) -> list[ScrapedProduct]:
        groups = await asyncio.gather(*(self._scrape_store(s) for s in self.stores))
        return [p for g in groups for p in g]

    async def _scrape_store(self, store) -> list[ScrapedProduct]:
        if not settings.HEB_SCRAPE_BASE:
            return self._mock(store)
        headers = {"Cookie": store.store_cookie} if store.store_cookie else None
        base = settings.HEB_SCRAPE_BASE
        out: list[ScrapedProduct] = []
        for cat in CATEGORIES:
            for page in range(1, settings.SCRAPE_MAX_PAGES + 1):  # pagination
                if cat == "clearance":
                    url, params = f"{base}/browse/clearance", {"page": page}
                else:
                    url, params = f"{base}/search", {"q": cat, "page": page}
                html = await self.http.get(url, params=params, headers=headers)
                items = self._parse_page(html, store, cat)
                if not items:
                    break
                out += items
        if not out:
            log.warning("H-E-B live scrape returned no products for %s; falling back to mock",
                        store.store_code)
            return self._mock(store)
        return out

    def _parse_page(self, html, store, cat) -> list[ScrapedProduct]:
        return self._parse_json(html, store, cat) or self._parse_html(html, store, cat)

    # ---- JSON hydration ----
    def _parse_json(self, html, store, cat) -> list[ScrapedProduct]:
        if not html:
            return []
        raw = None
        if html.lstrip()[:1] in ("{", "["):
            raw = html
        else:
            for block in _SCRIPT_RE.findall(html):
                b = block.strip()
                if b[:1] in ("{", "[") and ("price" in b.lower() or "product" in b.lower()):
                    raw = b
                    break
        if not raw:
            return []
        try:
            data = json.loads(raw)
        except Exception:
            return []
        out, seen = [], set()
        for it in self._find_products(data):
            key = it.get("sku") or it.get("productId") or it.get("itemNumber") or it.get("id")
            if key in seen:
                continue
            seen.add(key)
            p = self._map_json(store, cat, it)
            if p:
                out.append(p)
        return out

    @staticmethod
    def _find_products(node):
        found = []
        def walk(n):
            if isinstance(n, dict):
                has_id = n.get("sku") or n.get("productId") or n.get("itemNumber") or n.get("id")
                has_name = n.get("name") or n.get("title") or n.get("displayName")
                if has_id and has_name:
                    found.append(n)
                for v in n.values():
                    walk(v)
            elif isinstance(n, list):
                for v in n:
                    walk(v)
        walk(node)
        return found

    @staticmethod
    def _price_field(it, *keys):
        for src in (it, it.get("priceInfo") or {}):
            if not isinstance(src, dict):
                continue
            for key in keys:
                node = src.get(key)
                if isinstance(node, dict):
                    for sk in ("price", "amount", "value"):
                        v = _num(node.get(sk))
                        if v is not None:
                            return v
                else:
                    v = _num(node)
                    if v is not None:
                        return v
        return None

    def _map_json(self, store, cat, it):
        price = self._price_field(it, "currentPrice", "salePrice", "finalPrice", "price")
        if price is None:
            return None
        was = self._price_field(it, "regularPrice", "listPrice", "wasPrice", "originalPrice")
        sku = str(it.get("sku") or it.get("productId") or it.get("itemNumber") or it.get("id") or "")
        name = it.get("name") or it.get("title") or it.get("displayName") or "Unknown"
        brand = it.get("brand") or it.get("brandName")
        img = it.get("imageInfo")
        image = img.get("thumbnailUrl") if isinstance(img, dict) else (it.get("imageUrl") or it.get("image") or it.get("thumbnailUrl"))
        flags = json.dumps(it.get("badges") or it.get("flags") or it.get("dealType") or "").lower()
        clearance = bool(it.get("clearance") or "clearance" in flags or "deal" in flags
                         or (was and price < was))
        return ScrapedProduct(self.chain, store.store_code, it.get("upc"), sku, name, brand,
                              it.get("category") or cat, image if isinstance(image, str) else None,
                              price, was, clearance, price <= 0.05)

    # ---- HTML fallback ----
    def _parse_html(self, html, store, cat) -> list[ScrapedProduct]:
        if not html or not BeautifulSoup:
            return []
        soup = BeautifulSoup(html, "html.parser")
        out = []
        for c in soup.select('[data-sku], [data-product-id], .product-card, .product-tile'):
            name = c.get("data-name") or self._text(c, '.product-title, a[aria-label], a')
            raw_price = c.get("data-price")
            price = _num(raw_price) if raw_price else self._html_price(self._text(c, '[class*="price"]'))
            if not name or price is None:
                continue
            was = self._html_price(self._text(c, '[class*="was"], [class*="strike"], s, del'))
            blob = c.get_text(" ", strip=True).lower()
            flagged = any(k in blob for k in ("clearance", "deal", "sale"))
            link = c.select_one('a[href]')
            m = _ID_RE.search(link["href"]) if link and link.get("href") else None
            sku = c.get("data-sku") or c.get("data-product-id") or (m.group(1) if m else "")
            img = c.select_one("img")
            image = (img.get("src") or img.get("data-src")) if img else None
            clearance = flagged or (was is not None and price < was)
            out.append(ScrapedProduct(self.chain, store.store_code, c.get("data-upc"), sku,
                                      name, c.get("data-brand"), cat, image, price, was,
                                      clearance, price <= 0.05))
        return out

    @staticmethod
    def _text(node, sel):
        el = node.select_one(sel)
        if not el:
            return None
        return el.get("aria-label") or el.get_text(" ", strip=True) or None

    @classmethod
    def _html_price(cls, text):
        m = _PRICE_RE.search(text or "")
        if not m:
            return None
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            return None

    # ---- mock fallback ----
    def _mock(self, store) -> list[ScrapedProduct]:
        rng = random.Random()
        out = []
        for p in _CATALOG:
            roll = rng.random()
            if roll < 0.13:
                price, clr = rng.choice(_PENNY), True               # penny-like
            elif roll < 0.40:
                price, clr = round(p["reg"] * rng.uniform(0.4, 0.75), 2), True   # clearance
            elif roll < 0.67:
                price, clr = round(p["reg"] * rng.uniform(0.6, 0.9), 2), False   # hidden markdown
            else:
                price, clr = p["reg"], False
            out.append(ScrapedProduct(self.chain, store.store_code, p["upc"], p["sku"],
                                      p["name"], p["brand"], p["cat"], None, price, p["reg"],
                                      clr or price < p["reg"], price <= 0.05))
        return out
