from hashlib import md5
from math import radians, sin, cos, asin, sqrt

# Approximate ZIP centroids for the Rio Grande Valley (Option B geocoding).
ZIP_COORDS: dict[str, tuple[float, float]] = {
    "78501": (26.203, -98.230),
    "78503": (26.188, -98.255),
    "78504": (26.270, -98.245),
    "78516": (26.182, -98.118),
    "78537": (26.180, -98.060),
    "78539": (26.281, -98.201),
    "78541": (26.353, -98.162),
    "78542": (26.262, -98.131),
    "78570": (26.165, -97.950),
    "78572": (26.216, -98.350),
    "78573": (26.300, -98.300),
    "78574": (26.320, -98.360),
    "78577": (26.192, -98.183),
    "78596": (26.159, -97.990),
    "78599": (26.190, -97.990),
}


def latlon(zipcode: str) -> tuple[float, float]:
    return ZIP_COORDS.get(zipcode, ZIP_COORDS["78542"])


def approx_latlon(zipcode: str, key: str) -> tuple[float, float]:
    """ZIP centroid + deterministic jitter (~+/-0.01 deg) so multiple stores in the
    same ZIP do not overlap on the map. Stable per `key` (the store_code)."""
    base_lat, base_lon = latlon(zipcode)
    h = int(md5(key.encode()).hexdigest(), 16)
    dlat = ((h % 1000) / 1000 - 0.5) * 0.02
    dlon = (((h // 1000) % 1000) / 1000 - 0.5) * 0.02
    return round(base_lat + dlat, 5), round(base_lon + dlon, 5)


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 3958.8 * 2 * asin(sqrt(a))
