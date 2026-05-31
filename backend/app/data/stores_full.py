"""Full store network parsed into structured dicts.

Fields per store: chain, name, address, city, state, zip, phone, hours, store_code.
Hours: DG = 7am-10pm daily; HD = Mon-Sat 6am-10pm, Sun 8am-8pm.
store_code: HD uses the real store number (HD-0506); DG is a stable md5 of address+zip.
"""
from hashlib import md5

DG_HOURS = {d: ["07:00", "22:00"] for d in ("mon", "tue", "wed", "thu", "fri", "sat", "sun")}
HD_HOURS = {d: ["06:00", "22:00"] for d in ("mon", "tue", "wed", "thu", "fri", "sat")}
HD_HOURS["sun"] = ["08:00", "20:00"]

RAW_DG = """
10830 Mile 7 Rd
Mcallen, TX 78573
(956) 663-0701

1200 W Dove Ave
Mcallen, TX 78504-4460
(956) 515-2210

4100 S Ware Rd
Mcallen, TX 78503-7787
(956) 515-2065

7129 State Highway 107
Mcallen, TX 78573
(956) 529-1120

7900 N 23rd St
Mcallen, TX 78504-6167
(956) 603-1315

11300 N 23rd St
Mcallen, TX 78504
(956) 762-3891

4215 N. F.M. 493
Donna, TX 78537
(956) 420-3322

717 W Bus Hwy 83
Donna, TX 78537-9051
(956) 420-3203

7900 N Fm 493
Donna, TX 78537-5082
(956) 377-2861

6500 N Val Verde Rd
Donna, TX 78537
(956) 377-0305

209 S 8th St # 227
Donna, TX 78537-3136
(956) 420-3084

1600 S Salinas Blvd
Donna, TX 78537
(956) 377-4155

11750 N Val Verde Rd
Donna, TX 78537
(956) 420-3172

4201 N Val Verde Rd
Donna, TX 78537-5280
(956) 597-3980

807 Ridge Rd
Alamo, TX 78516-9596
(956) 666-1510

1011 E Frontage Rd Ste C
Alamo, TX 78516-2320
(956) 666-1256

1218 S Tower Rd
Alamo, TX 78516
(956) 783-2449

1018 N Alamo Rd
Alamo, TX 78516-6800
(956) 666-1265

2111 West Business Hwy 83
Weslaco, TX 78596-5639
(956) 351-6669

6202 N Fm 1015
Weslaco, TX 78599
(956) 332-1500

2905 N. Westgate Drive
Weslaco, TX 78599-4970
(956) 246-4726

900 N International Blvd
Weslaco, TX 78596-7275
(956) 520-4890

1301 South Internation Bouleva
Weslaco, TX 78596
(956) 332-1250

5525 N Fm 88
Weslaco, TX 78596-2276
(956) 903-7780

2100 S. Texas
Weslaco, TX 78596-2952
(956) 363-9600

106 E Mile 14 N
Weslaco, TX 78596
(956) 255-0281

9625 N Fm 1015
Weslaco, TX 78596
(956) 647-4281

518 S Bridge Ave
Weslaco, TX 78596-6422
(956) 332-1239

12829 Mile 2 W
Weslaco, TX 78570
(956) 261-4177

8920 E. Highway 107
Edinburg, TX 78542
(956) 603-1645

7204 E Fm 2812
Edinburg, TX 78542
(956) 513-0214

3815 E. Fm. 2812 Road
Edinburg, TX 78542-3209
(956) 603-1231

1225 N Mccoll Rd
Edinburg, TX 78541
(956) 587-0085

3007 S Sugar Rd
Edinburg, TX 78539-2117
(956) 513-0035

4406 S Raul Longoria Rd
Edinburg, TX 78542-2026
(956) 603-1290

1821 S. Alamo Road
Edinburg, TX 78539-5525
(956) 378-6560

302 E Cano St
Edinburg, TX 78539-4512
(956) 603-1540

5204 N Doolittle Rd
Edinburg, TX 78542
(956) 587-0050

5125 S Alamo Rd
Edinburg, TX 78539-8732
(956) 603-1050

1406 W Monte Cristo Rd
Edinburg, TX 78541-7329
(956) 513-0910

5107 W Monte Cristo Rd
Edinburg, TX 78541-8852
(956) 513-0553

1121 S Raul Longoria Rd
Edinburg, TX 78539-2716
(956) 603-1077

1311 W Owassa Rd
Edinburg, TX 78539-7054
(956) 603-1575

400 E Fm 2812
Edinburg, TX 78542-7316
(956) 884-4771

1801 E Monte Cristo Rd
Edinburg, TX 78542-0350
(956) 603-1235

4611 E Richardson Rd
Edinburg, TX 78542
(956) 587-0111

3000 W Mile 3 Rd
Mission, TX 78574-5049
(956) 271-8214

10805 N Moorefield Rd
Mission, TX 78574
(956) 379-6611

7000 Mile 7 Rd
Mission, TX 78573-6022
(956) 997-4700

1011 W. Business Hwy. 83
Mission, TX 78572
(956) 997-4055

4401 W 7 Mile Line
Mission, TX 78572
(956) 379-6500

307 W Griffin Parkway
Mission, TX 78572-2215
(956) 997-3872

2105 W Griffin Pkwy
Mission, TX 78572-7393
(956) 529-1092

1700 E Griffin Pkwy
Mission, TX 78572-3104
(956) 529-1145

3702 N Inspiration Rd
Mission, TX 78573
(956) 581-0407

6229 W Mile 3 Rd
Mission, TX 78574
(956) 271-8080

610 S Inspiration Rd
Mission, TX 78572
(956) 391-2585

5410 W Mile 5 Road
Mission, TX 78574-6185
(956) 271-8680
"""

RAW_HD = """
Mcallen #0506
409 N Jackson Ave
Pharr, TX 78577
(956) 994-1419

N Mcallen #0516
801 Trenton Rd
Mcallen, TX 78504
(956) 668-8783

Weslaco #6577
1500 W Expressway 83
Weslaco, TX 78599
(956) 447-2645

Mission #8519
120 S Shary Road
Mission, TX 78572
(956) 583-4194
"""


def _records(raw: str) -> list[list[str]]:
    return [[ln.strip() for ln in blk.strip().splitlines()]
            for blk in raw.strip().split("\n\n") if blk.strip()]


def _city_state_zip(line: str):
    city, rest = line.split(",", 1)
    parts = rest.split()
    return city.strip(), parts[0], parts[1].split("-")[0]


def _dg_code(address: str, zipc: str) -> str:
    return "DG-" + md5(f"{address}|{zipc}".encode()).hexdigest()[:6].upper()


def _build() -> list[dict]:
    stores: list[dict] = []
    for addr, csz, phone in _records(RAW_DG):
        city, state, zipc = _city_state_zip(csz)
        stores.append({
            "chain": "Dollar General", "name": f"Dollar General - {addr}",
            "address": addr, "city": city, "state": state, "zip": zipc,
            "phone": phone, "hours": DG_HOURS, "store_code": _dg_code(addr, zipc),
        })
    for label, addr, csz, phone in _records(RAW_HD):
        city, state, zipc = _city_state_zip(csz)
        area, num = label.split("#")
        num = num.strip()
        stores.append({
            "chain": "Home Depot", "name": f"Home Depot #{num} ({area.strip()})",
            "address": addr, "city": city, "state": state, "zip": zipc,
            "phone": phone, "hours": HD_HOURS, "store_code": f"HD-{num}",
        })
    return stores


STORES = _build()
