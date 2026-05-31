from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScrapedProduct:
    chain: str
    store_code: str
    upc: Optional[str]
    sku: Optional[str]
    name: str
    brand: Optional[str]
    category: Optional[str]
    image_url: Optional[str]
    price: float
    regular_price: Optional[float]
    clearance: bool
    penny: bool = False


class BaseScraper(ABC):
    chain: str = "base"

    def __init__(self, stores):
        self.stores = stores  # list[Store] for this chain

    @abstractmethod
    async def fetch(self) -> list[ScrapedProduct]:
        """Scrape every assigned store (in parallel) and return normalized products."""
        raise NotImplementedError
