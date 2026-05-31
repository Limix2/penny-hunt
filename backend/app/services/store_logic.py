"""Store open/closed, distance/ETA, and behavior modeling v3."""
from datetime import datetime
from app.geo import haversine_miles

_DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def is_open(hours_json, now: datetime | None = None) -> bool:
    if not hours_json:
        return False
    now = now or datetime.now()
    win = hours_json.get(_DAYS[now.weekday()])
    if not win:
        return False
    return win[0] <= now.strftime("%H:%M") <= win[1]


def distance_eta(lat0, lon0, lat, lon, mph: float = 30.0):
    """Returns (miles, eta_minutes) from an origin to a store, or (None, None)."""
    if None in (lat0, lon0, lat, lon):
        return None, None
    miles = haversine_miles(lat0, lon0, lat, lon)
    return round(miles, 1), int(round(miles / mph * 60))


def update_behavior(store, near_zero_count: int) -> None:
    """Behavior v3: EMA of penny activity (0-100). Stores that repeatedly surface
    near-zero/penny prices trend toward a high behavior_score (a hot store)."""
    prev = store.behavior_score or 0.0
    signal = min(100.0, near_zero_count * 20.0)
    store.behavior_score = round(0.7 * prev + 0.3 * signal, 1)
