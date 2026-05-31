"""Ultimate Walmart scraper — live JSON/HTML path + mock fallback.

HONEST NOTES:
- Walmart.com is behind enterprise anti-bot (PerimeterX). UA rotation + delays are
  "good citizen" stability measures, NOT a bypass — many requests will be blocked.
- Walmart is a Next.js app: the real product data lives in the embedded
  <script id="__NEXT_DATA__"> JSON, so JSON hydration is parsed first; raw HTML tiles
  are a secondary fallback. Structures change often, so parsing is best-effort.
- Store-level pricing requires a valid store cookie (WALMART_STORE_COOKIE, e.g.
  "store=1234"), sent as the Cookie header.
- Live scraping must respect Walmart's Terms of Service. Enable at your discretion.

Live path is ON when WALMART_SCRAPE_BASE is set; otherwise the realistic mock runs.
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

CATEGORIES = ["clearance", "rollback", "grocery", "home", "electronics"]
_NEXT_RE = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)
_PRICE_RE = re.compile(r"\$\s*([\d,]+\.\d{2}|\d[\d,]*)")
_PENNY = [0.03, 0.06, 0.04, 0.01]
_CATALOG = [
    {"upc": "WM-0001", "sku": "5501", "name": "Mainstays Bath Towel", "brand": "Mainstays", "cat": "Home", "reg": 7.88},
    {"upc": "WM-0002", "sku": "5502", "name": "Great Value Coffee 30oz", "brand": "Great Value", "cat": "Grocery", "reg": 9.48},
    {"upc": "WM-0003", "sku": "5503", "name": "onn. 32\" Roku TV", "brand": "onn.", "cat": "Electronics", "reg": 128.00},
    {"upc": "WM-0004", "sku": "5504", "name": "Equate Hand Soap", "brand": "Equate", "cat": "Health", "reg": 3.97},
    {"upc": "WM-0005", "sku": "5505", "name": "Ozark Trail Tumbler", "brand": "Ozark Trail", "cat": "Outdoors", "reg": 14.97},
]


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


class WalmartScraper(BaseScraper):
    chain = "Walmart"

    def __init__(self, stores):
        super().__init__(stores)
        self.http = Fetcher(concurrency=settings.SCRAPE_CONCURRENCY)

    async def fetch(self) -> list[ScrapedProduct]:
        groups = await asyncio.gather(*(self._scrape_store(s) for s in self.stores))
        return [p for g in groups for p in g]

    async def _scrape_store(self, store) -> list[ScrapedProduct]:
        if not settings.WALMART_SCRAPE_BASE:
            return self._mock(store)
        headers = {"Cookie": store.store_cookie} if store.store_cookie else None
        base = settings.WALMART_SCRAPE_BASE
        out: list[ScrapedProduct] = []
        for cat in CATEGORIES:
            for page in range(1, settings.SCRAPE_MAX_PAGES + 1):  # pagination
                if cat in ("clearance", "rollback"):
                    url, params = f"{base}/shop/deals/clearance", {"q": cat.capitalize(), "page": page}
                else:
                    url, params = f"{base}/search", {"q": cat, "page": page}
                html = await self.http.get(url, params=params, headers=headers)
                items = self._parse_page(html, store, cat)
                if not items:
                    break
                out += items
        if not out:
            log.warning("Walmart live scrape returned no products for %s; falling back to mock",
                        store.store_code)
            return self._mock(store)
        return out

    def _parse_page(self, html, store, cat) -> list[ScrapedProduct]:
        return self._parse_json(html, store, cat) or self._parse_html(html, store, cat)

    # ---- JSON hydration (primary) ----
    def _parse_json(self, html, store, cat) -> list[ScrapedProduct]:
        if not html:
            return []
        m = _NEXT_RE.search(html)
        raw = m.group(1) if m else (html if html.lstrip().startswith("{") else None)
        if not raw:
            return []
        try:
            data = json.loads(raw)
        except Exception:
            return []
        out, seen = [], set()
        for it in self._find_products(data):
            key = it.get("usItemId") or it.get("itemId") or it.get("productId")
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
                if (n.get("usItemId") or n.get("itemId") or n.get("productId")) and (n.get("name") or n.get("title")):
                    found.append(n)
                for v in n.values():
                    walk(v)
            elif isinstance(n, list):
                for v in n:
                    walk(v)
        walk(node)
        return found

    @staticmethod
    def _price_field(it, key, subkeys=("price", "amount")):
        for src in (it, it.get("priceInfo") or {}):
            node = src.get(key) if isinstance(src, dict) else None
            if isinstance(node, dict):
                for sk in subkeys:
                    v = _num(node.get(sk))
                    if v is not None:
                        return v
            else:
                v = _num(node)
                if v is not None:
                    return v
        return None

    def _map_json(self, store, cat, it):
        price = self._price_field(it, "currentPrice") or _num(it.get("price"))
        if price is None:
            return None
        was = (self._price_field(it, "wasPrice") or _num(it.get("listPrice"))
               or _num(it.get("regularPrice")))
        sku = str(it.get("usItemId") or it.get("itemId") or it.get("productId") or "")
        name = it.get("name") or it.get("title") or "Unknown"
        brand = it.get("brand") or it.get("brandName")
        img = it.get("imageInfo")
        image = img.get("thumbnailUrl") if isinstance(img, dict) else (it.get("image") or it.get("thumbnailUrl"))
        flags = json.dumps(it.get("badges") or it.get("flags") or it.get("flag") or "").lower()
        rollback = bool(it.get("rollback") or it.get("isRollback") or "rollback" in flags)
        clearance = bool(it.get("clearance") or "clearance" in flags
                         or (rollback and was and price < was) or (was and price < was))
        return ScrapedProduct(self.chain, store.store_code, it.get("upc"), sku, name, brand,
                              it.get("category") or cat, image if isinstance(image, str) else None,
                              price, was, clearance, price <= 0.05)

    # ---- HTML tiles (fallback) ----
    def _parse_html(self, html, store, cat) -> list[ScrapedProduct]:
        if not html or not BeautifulSoup:
            return []
        soup = BeautifulSoup(html, "html.parser")
        out = []
        for c in soup.select('[data-item-id], [data-automation-id="product-tile"], .product-tile'):
            name = c.get("data-name") or (c.select_one('[data-automation-id="product-title"], a[link-identifier]') or {})
            name = name if isinstance(name, str) else (name.get_text(" ", strip=True) if name else None)
            raw_price = c.get("data-price")
            price = _num(raw_price) if raw_price else self._html_price(self._text(c, '[data-automation-id="product-price"], [class*="price"]'))
            if not name or price is None:
                continue
            was = self._html_price(self._text(c, '[class*="was"], [class*="strike"], s'))
            blob = c.get_text(" ", strip=True).lower()
            rollback = "rollback" in blob
            clearance = "clearance" in blob or rollback or (was is not None and price < was)
            img = c.select_one("img")
            return_img = (img.get("src") or img.get("data-src")) if img else None
            out.append(ScrapedProduct(self.chain, store.store_code, c.get("data-upc"),
                                      c.get("data-item-id", ""), name, c.get("data-brand"), cat,
                                      return_img, price, was, clearance, price <= 0.05))
        return out

    @staticmethod
    def _text(node, sel):
        el = node.select_one(sel)
        return el.get_text(" ", strip=True) if el else None

    @classmethod
    def _html_price(cls, text):
        m = _PRICE_RE.search(text or "")
        if not m:
            return None
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            return None

    # ---- mock fallback (unchanged) ----
    def _mock(self, store) -> list[ScrapedProduct]:
        rng = random.Random()
        out = []
        for p in _CATALOG:
            roll = rng.random()
            if roll < 0.12:
                price, clr = rng.choice(_PENNY), True               # penny-like markdown
            elif roll < 0.30:
                price, clr = round(p["reg"] * rng.uniform(0.2, 0.5), 2), True   # clearance
            elif roll < 0.55:
                price, clr = round(p["reg"] * rng.uniform(0.6, 0.85), 2), False  # rollback (hidden)
            else:
                price, clr = p["reg"], False
            out.append(ScrapedProduct(self.chain, store.store_code, p["upc"], p["sku"],
                                      p["name"], p["brand"], p["cat"], None, price, p["reg"],
                                      clr or price < p["reg"], price <= 0.05))
        return out
