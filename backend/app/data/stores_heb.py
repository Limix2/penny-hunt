HEB_STORES = [
    {
        "chain": "H-E-B",
        "name": "H-E-B Donna",
        "address": "2301 E Expressway 83",
        "city": "Donna",
        "state": "TX",
        "zip": "78537",
        "lat": 26.1703,
        "lon": -98.0348,
        "store_code": "HEB-Donna",
        "store_cookie": None
    },
    {
        "chain": "H-E-B",
        "name": "H-E-B Alamo",
        "address": "1212 E Duranta Ave",
        "city": "Alamo",
        "state": "TX",
        "zip": "78516",
        "lat": 26.1837,
        "lon": -98.1132,
        "store_code": "HEB-Alamo",
        "store_cookie": None
    },
    {
        "chain": "H-E-B",
        "name": "H-E-B San Juan",
        "address": "1110 S Raul Longoria Rd",
        "city": "San Juan",
        "state": "TX",
        "zip": "78589",
        "lat": 26.1898,
        "lon": -98.1534,
        "store_code": "HEB-SanJuan",
        "store_cookie": None
    },
    {
        "chain": "H-E-B",
        "name": "H-E-B Pharr",
        "address": "1300 S Cage Blvd",
        "city": "Pharr",
        "state": "TX",
        "zip": "78577",
        "lat": 26.1882,
        "lon": -98.1827,
        "store_code": "HEB-Pharr",
        "store_cookie": None
    },
    {
        "chain": "H-E-B",
        "name": "H-E-B McAllen (Nolana)",
        "address": "3601 N 23rd St",
        "city": "McAllen",
        "state": "TX",
        "zip": "78501",
        "lat": 26.2431,
        "lon": -98.2367,
        "store_code": "HEB-McAllen-Nolana",
        "store_cookie": None
    },
    {
        "chain": "H-E-B",
        "name": "H-E-B McAllen (10th St)",
        "address": "901 Trenton Rd",
        "city": "McAllen",
        "state": "TX",
        "zip": "78504",
        "lat": 26.2622,
        "lon": -98.2181,
        "store_code": "HEB-McAllen-Trenton",
        "store_cookie": None
    },
    {
        "chain": "H-E-B",
        "name": "H-E-B Edinburg",
        "address": "1212 S Closner Blvd",
        "city": "Edinburg",
        "state": "TX",
        "zip": "78539",
        "lat": 26.2891,
        "lon": -98.1634,
        "store_code": "HEB-Edinburg",
        "store_cookie": None
    },
    {
        "chain": "H-E-B",
        "name": "H-E-B Mission",
        "address": "2409 E Expressway 83",
        "city": "Mission",
        "state": "TX",
        "zip": "78572",
        "lat": 26.2048,
        "lon": -98.2791,
        "store_code": "HEB-Mission",
        "store_cookie": None
    },
    {
        "chain": "H-E-B",
        "name": "H-E-B Weslaco",
        "address": "310 N Texas Blvd",
        "city": "Weslaco",
        "state": "TX",
        "zip": "78596",
        "lat": 26.1628,
        "lon": -97.9901,
        "store_code": "HEB-Weslaco",
        "store_cookie": None
    }
]



# Default H-E-B hours: 6am-11pm daily. Stored in the project's canonical
# [open, close] 24h format so is_open() and the hours table keep working.
HEB_HOURS = {d: ["06:00", "23:00"] for d in ("mon", "tue", "wed", "thu", "fri", "sat", "sun")}
for _s in HEB_STORES:
    _s.setdefault("hours", HEB_HOURS)
