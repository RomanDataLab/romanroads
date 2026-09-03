"""Build data/city_populations.csv for the Roman roads project.

Sources:
  1. Hanson & Ortman 2017 (J. R. Soc. Interface supplement) — direct estimates, 210 cities.
  2. Hanson 2016 Areas table (885 cities) — populations predicted with a density
     relation calibrated on the JRSI overlap (same-era 1st-2nd c. AD basis).
  3. Reba/Reitsma/Seto 2016 (Chandler & Modelski digitized) — per-year values for
     cities missing from the Areas table, anchored to the AD 100 column
     (nearest year to AD 150 within BC 200 - AD 300 otherwise).
"""
import math
import re
import unicodedata

import numpy as np
import pandas as pd

ROOT = __file__.rsplit("\\", 1)[0]
DATA = ROOT + "\\data"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def clean_toponym(name: str) -> str:
    prev = None
    while prev != name:
        prev = name
        name = re.sub(r"\s*\([^()]*\)\s*$", "", str(name)).strip()
    return name


def year_of(col: str) -> int:
    v = col.replace("BC_", "-").replace("AD_", "")
    return int(v)


# ---------- load ----------
cities = pd.read_csv(f"{DATA}\\hanson2016_cities.csv", encoding="latin-1")
areas = pd.read_csv(f"{DATA}\\hanson2016_areas.csv", encoding="latin-1")
jrsi = pd.read_excel(f"{DATA}\\rsif_si.xlsx", sheet_name="Associations")

cities = pd.read_csv(f"{DATA}\\hanson2016_cities.csv", encoding="latin-1")
areas = pd.read_csv(f"{DATA}\\hanson2016_areas.csv", encoding="latin-1")
jrsi = pd.read_excel(f"{DATA}\\rsif_si.xlsx", sheet_name="Associations")

cities["pk"] = cities["Primary Key"].astype(str)          # already 'Hanson2016_N'
areas["pk"] = areas["Primary Key"].astype(str)            # already 'Hanson2016_N'
jrsi["pk"] = "Hanson2016_" + jrsi["Primary key"].astype(str)  # bare number here

area_map = dict(zip(areas["pk"], pd.to_numeric(areas["Area"], errors="coerce")))
jrsi_map = dict(zip(jrsi["pk"], pd.to_numeric(jrsi["Population"], errors="coerce")))

rows = []  # pk, population, estimate_year, source

# ---------- tier 1: JRSI direct estimates ----------
for pk, pop in jrsi_map.items():
    if pk in set(cities["pk"]) and pop == pop and pop > 0:
        rows.append((pk, int(pop), "c. AD 165", "Hanson & Ortman 2017 (JRSI)"))

# ---------- tier 2: density calibration on overlap ----------
ov = [(area_map[pk], pop) for pk, pop in jrsi_map.items()
      if pk in area_map and pop == pop and area_map[pk] == area_map[pk] and area_map[pk] > 0]
x = np.log10([a for a, _ in ov])
y = np.log10([p for _, p in ov])
b, a = np.polyfit(x, y, 1)
r2 = np.corrcoef(x, y)[0, 1] ** 2
print(f"density fit: pop = {10**a:.1f} * area^{b:.3f}  (n={len(ov)}, r2={r2:.3f}, "
      f"density@20ha={10**a * 20**(b-1):.0f}/ha, @200ha={10**a * 200**(b-1):.0f}/ha)")

t1 = {r[0] for r in rows}
n_pred = 0
for pk, area in area_map.items():
    if pk in t1 or area != area or area <= 0:
        continue
    pop = 10 ** (a + b * math.log10(area))
    rows.append((pk, int(round(max(pop, 150))), "c. AD 165",
                 f"Hanson 2016 area x density fit ({10**a:.0f}*ha^{b:.2f}, H&O-calibrated)"))
    n_pred += 1

# ---------- tier 3: Chandler / Modelski gap-fill ----------
YEAR_WINDOW = (-200, 300)
ANCHOR = 150


def melt(path):
    df = pd.read_csv(path, low_memory=False, encoding="latin-1")
    meta = df[["City", "OtherName", "Country", "Latitude", "Longitude"]]
    ycols = [c for c in df.columns if c.startswith(("BC_", "AD_"))]
    vals = df[ycols].apply(pd.to_numeric, errors="coerce")
    out = []
    for i in range(len(df)):
        recs = {}
        for c in ycols:
            v = vals.iloc[i][c]
            if v == v:
                recs[year_of(c)] = v
        recs = {yy: v for yy, v in recs.items() if YEAR_WINDOW[0] <= yy <= YEAR_WINDOW[1]}
        if recs:
            name = str(meta.iloc[i]["City"])
            alias = str(meta.iloc[i]["OtherName"]) if meta.iloc[i]["OtherName"] == meta.iloc[i]["OtherName"] else ""
            lat, lon = meta.iloc[i]["Latitude"], meta.iloc[i]["Longitude"]
            for nm in {norm(name), norm(alias)} - {""}:
                out.append((nm, float(lat), float(lon), recs))
    return out


chandler = melt(f"{DATA}\\chandler.csv") + melt(f"{DATA}\\modelski_ancient.csv")
have = {r[0] for r in rows}
n_lit = 0
for _, c in cities.iterrows():
    pk = c["pk"]
    if pk in have:
        continue
    cands = {norm(clean_toponym(c["Ancient Toponym"])), norm(c["Modern Toponym"])} - {""}
    best = None
    for nm, lat, lon, recs in chandler:
        if nm not in cands:
            continue
        try:
            if abs(lat - c["Latitude (Y)"]) > 1.2 or abs(lon - c["Longitude (X)"]) > 1.2:
                continue
        except (TypeError, ValueError):
            continue
        yy = min(recs, key=lambda v: abs(v - ANCHOR))
        src = "Chandler (Reba et al. 2016)" if yy in (100, 260) else "Modelski (Reba et al. 2016)"
        best = (int(recs[yy]), yy, src)
        break
    if best:
        rows.append((pk, best[0], f"AD {best[1]}", best[2]))
        n_lit += 1

out = pd.DataFrame(rows, columns=["primary_key", "population", "estimate_year", "source"])
out.to_csv(f"{DATA}\\city_populations.csv", index=False)
print(f"saved city_populations.csv: {len(out)} cities "
      f"(210 JRSI + {n_pred} area-fit + {n_lit} Chandler/Modelski)")
print(out.nlargest(8, "population").to_string(index=False))
