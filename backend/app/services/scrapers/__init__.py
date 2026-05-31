from app.services.scrapers.dg import DollarGeneralScraper
from app.services.scrapers.hd import HomeDepotScraper
from app.services.scrapers.walmart import WalmartScraper
from app.services.scrapers.heb import HEBScraper

_REGISTRY = [
    ("Dollar General", DollarGeneralScraper),
    ("Home Depot", HomeDepotScraper),
    ("Walmart", WalmartScraper),
    ("H-E-B", HEBScraper),
]


def all_scrapers(stores):
    """Return scraper instances bound to the located stores for each chain."""
    out = []
    for chain, cls in _REGISTRY:
        chain_stores = [s for s in stores if s.chain == chain]
        if chain_stores:
            out.append(cls(chain_stores))
    return out
