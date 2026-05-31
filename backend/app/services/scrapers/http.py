"""Shared async HTTP layer for scrapers.

Anti-bot/stability features (free + local only, no proxies, no paid services):
- rotating user agents (11 common browser strings)
- randomized per-request delay/jitter (200-600ms)
- retry with exponential backoff (default 3 attempts)
- concurrency throttling via a semaphore

NOTE: these are good-citizen stability measures; they do NOT defeat enterprise
anti-bot (Akamai/PerimeterX). Live scraping requires reachable endpoints + ToS review.
"""
import asyncio
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 Edg/124.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36 OPR/109.0",
]


class Fetcher:
    def __init__(self, concurrency: int = 4, retries: int = 3, delay=(0.2, 0.6)):
        self._sem = asyncio.Semaphore(concurrency)
        self.retries = retries
        self.delay = delay

    async def get(self, url, params=None, headers=None, as_json=False):
        import httpx  # lazy import so mock-only runs don't require httpx
        async with self._sem:  # concurrency throttle
            for attempt in range(self.retries):
                await asyncio.sleep(random.uniform(*self.delay))  # jitter / throttle
                try:
                    h = {"User-Agent": random.choice(USER_AGENTS),
                         "Accept-Language": "en-US,en;q=0.9", **(headers or {})}
                    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
                        r = await c.get(url, params=params, headers=h)
                        r.raise_for_status()
                        return r.json() if as_json else r.text
                except Exception:
                    await asyncio.sleep(0.4 * (2 ** attempt))  # exponential backoff
            return None
