"""Walmart store network parsed into structured dicts.

Fields: chain, name, address, city, state, zip, phone(None), hours, store_code.
Hours: Mon-Sun 6am-11pm. store_code = "WM-" + store number.
Geocoding is applied in locator.py via approx_latlon(zip, store_code).
"""
WM_HOURS = {d: ["06:00", "23:00"] for d in ("mon", "tue", "wed", "thu", "fri", "sat", "sun")}

RAW = """
Alamo Supercenter
Walmart Supercenter #5165
1421 Frontage Rd, Alamo, TX 78516

Edinburg University Drive Supercenter
Walmart Supercenter #429
1724 W University Dr, Edinburg, TX 78539

Edinburg Canton Supercenter
Walmart Supercenter #5809
2812 S Expressway 281, Edinburg, TX 78542

Edinburg Mccoll Rd Supercenter
Walmart Supercenter #3886
4101 S Mccoll Rd, Edinburg, TX 78539

Mcallen E Jackson Ave Supercenter
Walmart Supercenter #397
1200 E Jackson Ave, Mcallen, TX 78503

Mcallen W Nolana Ave Supercenter
Walmart Supercenter #452
2800 W Nolana Ave, Mcallen, TX 78504

Donna Supercenter
Walmart Supercenter #2763
900 N Salinas Boulevard, Donna, TX 78537

Weslaco N Texas Blvd Supercenter
Walmart Supercenter #1041
1310 N Texas Blvd, Weslaco, TX 78599

Mission Sharyland Expressway 83 Supercenter
Walmart Supercenter #395
2410 E Expressway 83, Mission, TX 78572
"""


def _build() -> list[dict]:
    stores = []
    for blk in RAW.strip().split("\n\n"):
        desc, label, addrline = [ln.strip() for ln in blk.strip().splitlines()]
        num = label.split("#")[-1].strip()
        address, city, statezip = [p.strip() for p in addrline.split(",")]
        state, zipc = statezip.split()
        stores.append({
            "chain": "Walmart", "name": f"Walmart #{num} ({desc})",
            "address": address, "city": city, "state": state, "zip": zipc,
            "phone": None, "hours": WM_HOURS, "store_code": f"WM-{num}",
            "store_cookie": f"assortment={num}",
        })
    return stores


STORES = _build()
