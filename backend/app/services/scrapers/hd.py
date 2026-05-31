"""Ultimate Home Depot scraper — live HTML path + mock fallback.

HONEST NOTES:
- Home Depot is behind enterprise anti-bot (Akamai). UA rotation + delays are
  "good citizen" stability measures, NOT a bypass — many requests will still be
  blocked (403/429).
- HD product pods are largely React/GraphQL-hydrated, so a plain HTML GET often
  contains few/no server-rendered pods. The HTML parser below targets server-rendered
  product-pod markup (selectors derived from Special-Values / category pages); for
  full coverage you would use HD's GraphQL JSON (also bot-protected).
- Live scraping must respect Home Depot's Terms of Service. Enable at your discretion.

Live path is ON when HD_SCRAPE_BASE is set; otherwise the realistic mock runs.
Store-specific pricing: set HD_STORE_COOKIE (e.g. "THD_STORE=6561") -> sent as Cookie.
"""
import asyncio
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

CATEGORIES = ["clearance", "special-buy", "tools", "lighting", "plumbing"]
_PRICE_RE = re.compile(r"\$\s*([\d,]+\.\d{2}|\d[\d,]*)")
_ID_RE = re.compile(r"/(\d{6,})")
_CATALOG = [
    {"sku": "100123", "upc": "HD-100123", "name": "Husky 3-Drawer Tool Chest", "brand": "Husky", "cat": "Tools", "reg": 149.00},
    {"sku": "100456", "upc": "HD-100456", "name": "Hampton Bay LED Flood Light", "brand": "Hampton Bay", "cat": "Lighting", "reg": 24.97},
    {"sku": "100789", "upc": "HD-100789", "name": "Glacier Bay Faucet", "brand": "Glacier Bay", "cat": "Plumbing", "reg": 89.00},
    {"sku": "100999", "upc": "HD-100999", "name": "Ryobi Drill Bit Set", "brand": "Ryobi", "cat": "Tools", "reg": 19.97},
]
_PENNY = [0.03, 0.06, 0.04]


class HomeDepotScraper(BaseScraper):
    chain = "Home Depot"

    def __init__(self, stores):
        super().__init__(stores)
        self.http = Fetcher(concurrency=settings.SCRAPE_CONCURRENCY)

    async def fetch(self) -> list[ScrapedProduct]:
        groups = await asyncio.gather(*(self._scrape_store(s) for s in self.stores))
        return [p for g in groups for p in g]

    async def _scrape_store(self, store) -> list[ScrapedProduct]:
        if not settings.HD_SCRAPE_BASE:
            return self._mock(store)
        headers = {"Cookie": store.store_cookie} if store.store_cookie else None
        out: list[ScrapedProduct] = []
        for cat in CATEGORIES:
            for page in range(1, settings.SCRAPE_MAX_PAGES + 1):  # pagination (Nao offset)
                params = {"Nao": (page - 1) * 24} if page > 1 else None
                html = await self.http.get(f"{settings.HD_SCRAPE_BASE}/b/{cat}",
                                           params=params, headers=headers)
                items = self._parse_html(html, store, cat)
                if not items:
                    break
                out += items
        if not out:
            log.warning("HD live scrape returned no products for %s; falling back to mock",
                        store.store_code)
            return self._mock(store)
        return out

    @staticmethod
    def _text(node, sel):
        el = node.select_one(sel)
        return el.get_text(" ", strip=True) if el else None

    @classmethod
    def _price(cls, text):
        m = _PRICE_RE.search(text or "")
        if not m:
            return None
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            return None

    def _parse_html(self, html, store, cat) -> list[ScrapedProduct]:
        if not html or not BeautifulSoup:
            return []
        soup = BeautifulSoup(html, "html.parser")
        pods = soup.select('[data-testid="product-pod"], [data-automation-id="product-pod"], .product-pod')
        out = []
        for pod in pods:
            title_el = pod.select_one('[data-testid="attribute-product-label"], .product-pod__title, a[aria-label]')
            name = (title_el.get("aria-label") if title_el and title_el.get("aria-label")
                    else (title_el.get_text(" ", strip=True) if title_el else None))
            price = self._price(self._text(pod, '[data-testid="price-format__main-price"], .price-format__main-price, [class*="price"]')
                                or pod.get_text(" ", strip=True))
            if not name or price is None:
                continue
            was = self._price(self._text(pod, '.price-format__was-price, [class*="was"], [class*="original"]') or "")
            blob = pod.get_text(" ", strip=True).lower()
            special = any(k in blob for k in ("special buy", "savings", "clearance"))
            link = pod.select_one('a[href*="/p/"]')
            m = _ID_RE.search(link["href"]) if link and link.get("href") else None
            sku = m.group(1) if m else ""
            img = pod.select_one("img")
            image = (img.get("src") or img.get("data-src")) if img else None
            brand = self._text(pod, '[data-testid="attribute-brandname"], .product-pod__brand-name')
            clearance = special or (was is not None and price < was)
            out.append(ScrapedProduct(self.chain, store.store_code, None, sku, name, brand,
                                      cat, image, price, was, clearance, price <= 0.05))
        return out

    def _mock(self, store) -> list[ScrapedProduct]:
        rng = random.Random()
        out = []
        for p in _CATALOG:
            roll = rng.random()
            if roll < 0.20:
                price, clr = rng.choice(_PENNY), True   # HD penny pattern
            elif roll < 0.50:
                price, clr = round(p["reg"] * rng.uniform(0.1, 0.4), 2), True
            else:
                price, clr = p["reg"], False
            out.append(ScrapedProduct(self.chain, store.store_code, p["upc"], p["sku"],
                                      p["name"], p["brand"], p["cat"], None, price, p["reg"],
                                      clr or price < p["reg"], price <= 0.05))
        return out
