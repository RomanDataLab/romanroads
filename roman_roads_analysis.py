"""
Do All the Roads Lead to Rome? — network analysis of the Roman road network.

Pipeline (after Janosov, 2023, milanjanosov.substack.com):
  1. Load DARMC Roman Road Network (2008) shapefile, reproject to EPSG:4326.
  2. Build an undirected graph from linestring endpoints.
  3. Compute degree and betweenness centrality per node.
  4. Aggregate node scores into H3 hexagons (res 3) covering the Empire's extent.
  5. Load Roman cities (Hanson 2016, OxREP) and check road access (nearest road <= 5 km).
  6. Emit maps (PNG), interactive map (HTML), GEXF for Gephi, CSVs, findings.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.colors import to_hex
from matplotlib.patches import Patch
from shapely.geometry import Point, mapping, shape

import h3

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "roman_roads_v2008.shp"
CITIES_DATA = ROOT / "data" / "hanson2016_cities.csv"
WIKI_CACHE = ROOT / "data" / "city_wiki_links.csv"
FOUNDERS_CACHE = ROOT / "data" / "city_founders.csv"

# Approximate year each province came under Roman control (negative = BC);
# a city whose Start Date is earlier was founded before the conquest.
PROVINCE_CONQUEST = {
    "Italia": -270, "Sicilia": -241, "Silicia": -241, "Corsica": -238, "Sardinia": -238,
    "Hispania": -197, "Baetica": -206, "Lusitania": -25, "Gallia Narbonensis": -121,
    "Gallia": -51, "Germania": 85, "Raetia": -15, "Noricum": -15, "Alpes": -15,
    "Pannonia": 9, "Dalmatia": -32, "Dacia": 106, "Macedonia": -148, "Achaea": -146,
    "Thracia": 46, "Asia": -129, "Bithynia": -74, "Cilicia": -67, "Creta": -67,
    "Lycia": 43, "Pamphylia": 43, "Cappadocia": -25, "Galatia": -25, "Syria": -63,
    "Arabia": 106, "Aegyptus": -30, "Cyrenaica": -74, "Africa": -146, "Numidia": -46,
    "Mauretania": 40, "Britannia": 43, "Moesia": -27,
}

# Pre-Roman power per province (longest-prefix match) — fallback "founded by" label
# for pre-conquest cities with no Wikidata founder.
PRE_ROMAN_PEOPLE = {
    "Italia (VII Etruria)": "the Etruscans",
    "Italia (I Latium": "the Latins",
    "Italia (IV Samnium": "the Samnites",
    "Italia (II Apulia": "the Iapygians",
    "Italia (III Lucania": "the Lucanians",
    "Italia (V Picenum": "the Picentes",
    "Italia (VI Umbria": "the Umbrians",
    "Italia (VIII Aemilia": "the Boii",
    "Italia (IX Liguria": "the Ligures",
    "Italia (X Venetia": "the Veneti",
    "Italia (XI Transpadana": "the Insubres",
    "Italia": "the Italic peoples",
    "Sicilia": "the ancient Greeks", "Silicia": "the ancient Greeks",
    "Corsica": "the Nuragic Sardinians",
    "Hispania": "the Iberians", "Baetica": "the Iberians", "Lusitania": "the Lusitanians",
    "Gallia": "the Gauls",
    "Britannia": "the Britons",
    "Germania": "the Germanic tribes",
    "Raetia": "the Raeti", "Noricum": "the Norici", "Alpes": "the Celto-Ligurians",
    "Pannonia": "the Pannonians", "Dalmatia": "the Illyrians",
    "Moesia": "the Thracians", "Dacia": "the Dacians", "Thracia": "the Thracians",
    "Macedonia": "the Macedonians", "Achaea": "the ancient Greeks", "Epirus": "the Epirotes",
    "Asia": "the Attalid Greeks", "Bithynia": "the Bithynians",
    "Cappadocia": "the Cappadocians", "Galatia": "the Galatians",
    "Cilicia": "the Cilicians", "Lycia": "the Lycians",
    "Creta": "the ancient Greeks",
    "Syria Palestina": "the Hasmonean Judaeans", "Syria": "the Seleucids",
    "Arabia": "the Nabataeans", "Aegyptus": "the ancient Egyptians",
    "Africa": "the Carthaginians", "Numidia": "the Numidians",
    "Mauretania": "the Mauretanians",
}
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

ROME_POINT = (41.9028, 12.4964)  # (lat, lng) fallback if geocoding fails
H3_RES = 3
BUFFER_KM = 20
CITY_CONNECT_KM = 5  # max distance from a city to the nearest road to count as connected

# Barrington rank 1 (Rome-sized) -> 5 (minor): deep red to pale yellow
RANK_COLORS = {r: to_hex(plt.get_cmap("YlOrRd")(v)) for r, v in
               zip(range(1, 6), [0.95, 0.75, 0.55, 0.35, 0.15])}


def load_roads() -> gpd.GeoDataFrame:
    roads = gpd.read_file(DATA)
    print(f"loaded {len(roads)} features, CRS {roads.crs.to_epsg() or 'custom'}")
    return roads.to_crs(4326)


def load_cities() -> gpd.GeoDataFrame:
    """Hanson 2016 catalogue of Roman cities, 100 BC - AD 300 (OxREP Cities Database)."""
    df = pd.read_csv(CITIES_DATA, encoding="latin-1")
    df = df.dropna(subset=["Longitude (X)", "Latitude (Y)"]).copy()
    # Barrington Atlas Rank: 1 (Rome-sized) .. 5 (minor); "4 or 5" / "-" -> 5
    df["rank"] = df["Barrington Atlas Rank"].astype(str).str[0].where(
        df["Barrington Atlas Rank"].astype(str).str[0].str.isdigit(), "5"
    ).astype(int)
    cities = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df["Longitude (X)"], df["Latitude (Y)"]), crs=4326
    )
    print(f"loaded {len(cities)} Roman cities, {df['Province'].nunique()} provinces")
    return cities


def connect_cities(cities: gpd.GeoDataFrame, roads_metric: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Nearest-road distance per city (metres), computed in the roads' metric CRS."""
    cities_m = cities.to_crs(roads_metric.crs)
    nearest = gpd.sjoin_nearest(
        cities_m, roads_metric[["geometry"]].reset_index(drop=True), distance_col="dist_m"
    )
    dist = nearest.groupby(level=0)["dist_m"].min() / 1000.0
    cities = cities.copy()
    cities["dist_road_km"] = cities.index.map(dist)
    cities["connected"] = cities["dist_road_km"] <= CITY_CONNECT_KM
    cities.drop(columns=["geometry"]).to_csv(OUT / "cities_road_access.csv", index=False)
    n = int(cities["connected"].sum())
    print(f"{n}/{len(cities)} cities within {CITY_CONNECT_KM} km of a road")
    return cities


def rank_marker_size(rank) -> float:
    return {1: 40, 2: 18, 3: 6, 4: 3, 5: 2}.get(rank, 2)


def fmt_year(y) -> str:
    """Hanson 'Start Date': negative = BC, positive = AD."""
    y = int(y)
    return f"{-y} BC" if y < 0 else f"AD {y}"


def _clean_toponym(name: str) -> str:
    """Strip trailing disambiguation groups: 'Antiochia (Syria) (1)' -> 'Antiochia'."""
    prev = None
    while prev != name:
        prev = name
        name = re.sub(r"\s*\([^()]*\)\s*$", "", name).strip()
    return name


def resolve_wiki_links(cities) -> dict:
    """English Wikipedia URL per city (Primary Key -> url), cached in data/city_wiki_links.csv.

    Candidate titles in priority order: ancient toponym, '(ancient city)' / '(ancient site)'
    variants (enwiki conventions for archaeology articles), then modern toponym.
    Falls back to a Wikipedia search URL for the ancient city.
    """
    cache = {}
    if WIKI_CACHE.exists():
        cached = pd.read_csv(WIKI_CACHE)
        cache = dict(zip(cached["primary_key"].astype(str), cached["url"]))
    missing = cities[~cities["Primary Key"].astype(str).isin(cache)]
    if not len(missing):
        return cache

    print(f"resolving Wikipedia links for {len(missing)} cities ...")
    order = {}  # primary key -> candidate titles, best first
    title_owners = {}
    for _, c in missing.iterrows():
        anc = _clean_toponym(str(c["Ancient Toponym"]))
        cands = [anc, f"{anc} (ancient city)", f"{anc} (ancient site)",
                 str(c["Modern Toponym"])]
        cands = [t for t in dict.fromkeys(cands) if t and t.lower() not in ("unknown", "nan")]
        order[str(c["Primary Key"])] = cands
        for t in cands:
            title_owners.setdefault(t, 0)

    # batch existence check via MediaWiki API (50 titles per query), throttled
    resolved = {}  # original title -> canonical existing title
    titles = list(title_owners)
    api = "https://en.wikipedia.org/w/api.php"
    for i in range(0, len(titles), 50):
        batch = titles[i:i + 50]
        q = urllib.parse.urlencode({
            "action": "query", "format": "json", "redirects": 1,
            "titles": "|".join(t.replace(" ", "_") for t in batch)})
        for attempt in range(4):
            try:
                req = urllib.request.Request(f"{api}?{q}",
                                             headers={"User-Agent": "romanroads-analysis/1.0"})
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code != 429 or attempt == 3:
                    raise
                time.sleep(int(e.headers.get("Retry-After", 10 * (attempt + 1))))
        else:
            continue
        query = data.get("query", {})
        norm = {n["from"]: n["to"] for n in query.get("normalized", [])}
        reds = {r_["from"]: r_["to"] for r_ in query.get("redirects", [])}
        existing = {p["title"] for p in query.get("pages", {}).values() if "missing" not in p}
        for t in batch:
            final = reds.get(norm.get(t, t), norm.get(t, t))
            final = reds.get(final, final)  # follow one chained redirect
            if final in existing:
                resolved[t] = final
        time.sleep(0.5)

    # second pass: flag disambiguation pages — never link to those
    disambig = set()
    finals = sorted(set(resolved.values()))
    for i in range(0, len(finals), 50):
        batch = finals[i:i + 50]
        q = urllib.parse.urlencode({
            "action": "query", "format": "json", "prop": "pageprops",
            "ppprop": "disambiguation",
            "titles": "|".join(t.replace(" ", "_") for t in batch)})
        for attempt in range(4):
            try:
                req = urllib.request.Request(f"{api}?{q}",
                                             headers={"User-Agent": "romanroads-analysis/1.0"})
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code != 429 or attempt == 3:
                    raise
                time.sleep(int(e.headers.get("Retry-After", 10 * (attempt + 1))))
        else:
            continue
        for p in data.get("query", {}).get("pages", {}).values():
            if "missing" not in p and "disambiguation" in p.get("pageprops", {}):
                disambig.add(p["title"])
        time.sleep(0.5)

    def to_url(title: str) -> str:
        return "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))

    new_rows = []
    direct, fallback = 0, 0
    for pk, cands in order.items():
        hit = next((resolved[t] for t in cands
                    if t in resolved and resolved[t] not in disambig), None)
        if hit:
            url = to_url(hit)
            direct += 1
        else:
            anc = cands[0]
            url = ("https://en.wikipedia.org/wiki/Special:Search?search="
                   + urllib.parse.quote(f"{anc} ancient Roman city"))
            fallback += 1
        cache[pk] = url
        new_rows.append((pk, url))

    pd.DataFrame(new_rows, columns=["primary_key", "url"]).to_csv(
        WIKI_CACHE, mode="a", header=not WIKI_CACHE.exists(), index=False)
    print(f"wiki links: {direct} direct articles, {fallback} search fallbacks")
    return cache


def _wiki_api_get(api: str, params: dict) -> dict:
    q = urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            req = urllib.request.Request(f"{api}?{q}",
                                         headers={"User-Agent": "romanroads-analysis/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.load(r)
            time.sleep(0.5)
            return data
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == 4:
                raise
            time.sleep(int(e.headers.get("Retry-After", 10 * (attempt + 1))))
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            if attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))
    return {}


def _conquest_year(province: str):
    p = province or ""
    for prefix, year in sorted(PROVINCE_CONQUEST.items(), key=lambda kv: -len(kv[0])):
        if p.startswith(prefix):
            return year
    return None


def _pre_roman_people(province: str):
    p = province or ""
    for prefix, people in sorted(PRE_ROMAN_PEOPLE.items(), key=lambda kv: -len(kv[0])):
        if p.startswith(prefix):
            return people
    return None


def resolve_founders(cities, wiki_urls: dict) -> dict:
    """Primary Key -> founder label, for pre-conquest cities with a known founder.

    A city qualifies when its Start Date precedes its province's Roman conquest
    year. Founders come from Wikidata property P112 ('founded by') via the
    already-resolved English Wikipedia articles. Cached in data/city_founders.csv.
    """
    checked = {}
    if FOUNDERS_CACHE.exists():
        c = pd.read_csv(FOUNDERS_CACHE, keep_default_na=False)
        checked = dict(zip(c["primary_key"].astype(str), c["founder"]))

    todo = []  # (primary key, enwiki title) qualifying for a Wikidata lookup
    unmatched = set()
    for _, c in cities.iterrows():
        pk = str(c["Primary Key"])
        if pk in checked:
            continue
        conquest = _conquest_year(c["Province"])
        url = (wiki_urls or {}).get(pk, "")
        if conquest is None:
            unmatched.add(c["Province"])
            checked[pk] = ""
        elif int(c["Start Date"]) >= conquest or "/wiki/Special:Search" in url:
            checked[pk] = ""  # Roman-era foundation or no article to query
        else:
            todo.append((pk, urllib.parse.unquote(url.split("/wiki/")[-1]).replace("_", " ")))
    if unmatched:
        print(f"WARNING: no conquest year for provinces: {sorted(unmatched)}")

    if todo:
        print(f"fetching founders from Wikidata for {len(todo)} pre-conquest cities ...")
        # 1) enwiki title -> Wikidata QID
        qids = {}
        api = "https://en.wikipedia.org/w/api.php"
        for i in range(0, len(todo), 50):
            batch = todo[i:i + 50]
            data = _wiki_api_get(api, {"action": "query", "format": "json",
                                       "prop": "pageprops", "ppprop": "wikibase_item",
                                       "titles": "|".join(t for _, t in batch)})
            for p in data.get("query", {}).get("pages", {}).values():
                qid = p.get("pageprops", {}).get("wikibase_item")
                if qid and "missing" not in p:
                    qids[p["title"].replace("_", " ")] = qid

        # 2) QID -> P112 'founded by' QIDs
        founder_qs = {}
        wd = "https://www.wikidata.org/w/api.php"
        qlist = sorted(set(qids.values()))
        for i in range(0, len(qlist), 50):
            data = _wiki_api_get(wd, {"action": "wbgetentities", "format": "json",
                                      "ids": "|".join(qlist[i:i + 50]), "props": "claims"})
            for qid, ent in data.get("entities", {}).items():
                claims = [cl for cl in ent.get("claims", {}).get("P112", [])
                          if cl.get("mainsnak", {}).get("snaktype") == "value"]
                qs = [cl["mainsnak"]["datavalue"]["value"]["id"] for cl in claims]
                if qs:
                    founder_qs[qid] = qs[:3]

        # 3) founder QIDs -> labels + life dates (reject anachronistic article matches)
        labels, lifespans = {}, {}
        fl = sorted({f for v in founder_qs.values() for f in v})
        for i in range(0, len(fl), 50):
            data = _wiki_api_get(wd, {"action": "wbgetentities", "format": "json",
                                      "ids": "|".join(fl[i:i + 50]),
                                      "props": "labels|claims", "languages": "en"})
            for qid, ent in data.get("entities", {}).items():
                lab = ent.get("labels", {}).get("en", {}).get("value")
                if lab:
                    labels[qid] = lab
                years = []
                for prop in ("P569", "P570"):  # birth / death
                    for cl in ent.get("claims", {}).get(prop, []):
                        if cl.get("mainsnak", {}).get("snaktype") == "value":
                            t = cl["mainsnak"]["datavalue"]["value"].get("time", "")
                            if len(t) >= 5 and t[0] in "+-":
                                try:
                                    year = int(t[1:5])
                                    years.append(-year if t[0] == "-" else year)
                                except ValueError:
                                    pass
                if years:
                    lifespans[qid] = years

        n_found = 0
        for pk, title in todo:
            qs = founder_qs.get(qids.get(title, ""), [])
            # a founder who lived after AD 600 cannot have founded a pre-conquest
            # Roman-era city — the article match was wrong (e.g. a modern namesake)
            names = [labels[q] for q in qs
                     if q in labels and max(lifespans.get(q, [0])) <= 600]
            checked[pk] = " and ".join(names) if names else ""
            if names:
                n_found += 1
        print(f"founders known for {n_found} of {len(todo)} pre-conquest cities")

    pd.DataFrame(sorted(checked.items()), columns=["primary_key", "founder"]).to_csv(
        FOUNDERS_CACHE, index=False)
    return checked


def plot_base_map(roads: gpd.GeoDataFrame, cities: gpd.GeoDataFrame = None) -> None:
    fig, ax = plt.subplots(figsize=(14, 10), dpi=150)
    if "CERTAINTY" in roads.columns:
        cats = sorted(roads["CERTAINTY"].fillna("unknown").unique())
        cmap = plt.get_cmap("viridis", len(cats))
        colors = {c: to_hex(cmap(i)) for i, c in enumerate(cats)}
        for cat, color in colors.items():
            roads[roads["CERTAINTY"].fillna("unknown") == cat].plot(
                ax=ax, color=color, linewidth=0.4, label=cat
            )
        leg_roads = ax.legend(title="Certainty", loc="lower left", fontsize=8)
        ax.add_artist(leg_roads)
    else:
        roads.plot(ax=ax, color="dimgray", linewidth=0.4)
    if cities is not None:
        cities.plot(ax=ax, color=[RANK_COLORS[r] for r in cities["rank"]], edgecolor="black",
                    linewidth=0.2, markersize=[rank_marker_size(r) for r in cities["rank"]], zorder=3)
        rank_handles = [Patch(facecolor=c, edgecolor="black", label=f"rank {r}")
                        for r, c in RANK_COLORS.items()]
        ax.legend(handles=rank_handles, title="Cities by Barrington rank\n(1 = largest)",
                  loc="upper left", fontsize=8)
    ax.set_title("Roman Road Network (DARMC 2008) with Roman cities")
    ax.set_xlabel("longitude"); ax.set_ylabel("latitude")
    fig.tight_layout()
    fig.savefig(OUT / "01_roman_roads_map.png"); plt.close(fig)
    print("saved 01_roman_roads_map.png")


def build_graph(roads: gpd.GeoDataFrame) -> nx.Graph:
    G = nx.Graph()
    for geom in roads.geometry:
        (x0, y0), (x1, y1) = geom.coords[0], geom.coords[-1]
        u = (round(x0, 5), round(y0, 5))
        v = (round(x1, 5), round(y1, 5))
        if u != v:
            G.add_edge(u, v)
    for n in G.nodes:
        G.nodes[n]["x"], G.nodes[n]["y"] = n[0], n[1]
    print(f"graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def compute_centralities(G: nx.Graph) -> pd.DataFrame:
    print("computing betweenness centrality ...")
    bet = nx.betweenness_centrality(G, normalized=False)
    deg = dict(G.degree())
    df = pd.DataFrame(
        {
            "lon": [n[0] for n in G.nodes],
            "lat": [n[1] for n in G.nodes],
            "degree": [deg[n] for n in G.nodes],
            "betweenness": [bet[n] for n in G.nodes],
        }
    )
    df.to_csv(OUT / "nodes_centrality.csv", index=False)
    print("saved nodes_centrality.csv")
    return df


def empire_extent(roads_metric: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Concave-ish hull: roads buffered 20 km and dissolved."""
    extent = gpd.GeoSeries([roads_metric.unary_union.buffer(BUFFER_KM * 1000)], crs=roads_metric.crs)
    extent = extent.to_crs(4326).simplify(0.05)
    return extent


def hex_scores(nodes: pd.DataFrame, extent) -> pd.DataFrame:
    cells = set()
    extent_geom = extent.geometry[0]
    polys = list(extent_geom.geoms) if extent_geom.geom_type == "MultiPolygon" else [extent_geom]
    for poly in polys:
        ring = [(lat, lng) for lng, lat in poly.exterior.coords]
        cells.update(h3.polygon_to_cells(h3.LatLngPoly(ring), H3_RES))
    print(f"empire extent covered by {len(cells)} H3 cells (res {H3_RES})")

    nodes = nodes.copy()
    nodes["cell"] = [h3.latlng_to_cell(lat, lon, H3_RES) for lat, lon in zip(nodes["lat"], nodes["lon"])]
    agg = nodes.groupby("cell").agg(degree=("degree", "sum"), betweenness=("betweenness", "sum"),
                                    n_nodes=("degree", "size"))
    agg = agg.reindex(sorted(cells & set(agg.index))).fillna(0)  # keep only on-land cells

    geoms, lats, lngs = [], [], []
    for cell in agg.index:
        boundary = h3.cell_to_boundary(cell)  # (lat, lng) pairs
        ring = [(lng, lat) for lat, lng in boundary] + [ (boundary[0][1], boundary[0][0]) ]
        geoms.append(shape({"type": "Polygon", "coordinates": [ring]}))
        lat, lng = h3.cell_to_latlng(cell); lats.append(lat); lngs.append(lng)
    hexes = gpd.GeoDataFrame(agg.reset_index(), geometry=geoms, crs=4326)
    hexes["lat"], hexes["lng"] = lats, lngs
    hexes.to_file(OUT / "hex_scores.gpkg", driver="GPKG")
    return hexes


def get_rome_boundary():
    try:
        import osmnx as ox
        rome = ox.geocode_to_gdf("Roma, Italia")
        print("geocoded Rome boundary via Nominatim")
        return rome.to_crs(4326), "polygon"
    except Exception as e:
        print(f"Rome geocoding failed ({e}); using point marker")
        return gpd.GeoDataFrame(geometry=[Point(ROME_POINT[1], ROME_POINT[0])], crs=4326), "point"


def plot_hexmap(hexes: gpd.GeoDataFrame, roads: gpd.GeoDataFrame, rome, metric: str, fname: str,
                cities: gpd.GeoDataFrame = None) -> None:
    fig, ax = plt.subplots(figsize=(14, 10), dpi=150)
    hexes.plot(ax=ax, column=metric, cmap="RdYlGn", edgecolor="none", legend=True,
               legend_kwds={"label": f"summed {metric}", "shrink": 0.6}, missing_kwds={"color": "lightgrey"})
    roads.plot(ax=ax, color="black", linewidth=0.3)
    if cities is not None:
        cities.plot(ax=ax, color=[RANK_COLORS[r] for r in cities["rank"]], edgecolor="black",
                    linewidth=0.1, markersize=[rank_marker_size(r) * 0.8 for r in cities["rank"]], zorder=3)
    if rome is not None:
        rome.boundary.plot(ax=ax, color="white", linewidth=1.2)
    ax.set_title(f"Roman roads — summed {metric} per H3 hexagon")
    ax.set_xlabel("longitude"); ax.set_ylabel("latitude")
    fig.tight_layout()
    fig.savefig(OUT / fname); plt.close(fig)
    print(f"saved {fname}")


def plot_italy_detail(roads: gpd.GeoDataFrame, cities: gpd.GeoDataFrame) -> None:
    fig, ax = plt.subplots(figsize=(12, 12), dpi=150)
    roads.plot(ax=ax, color="dimgray", linewidth=1.0)
    major = cities[cities["rank"] <= 3]
    major.plot(ax=ax, color=[RANK_COLORS[r] for r in major["rank"]], edgecolor="black",
               linewidth=0.3, markersize=[rank_marker_size(r) for r in major["rank"]], zorder=3)
    for _, c in major[major["rank"] <= 2].iterrows():
        ax.annotate(c["Ancient Toponym"], (c.geometry.x, c.geometry.y),
                    xytext=(3, 3), textcoords="offset points", fontsize=8, color="black")
    ax.set_xlim(6, 20); ax.set_ylim(36, 48)
    ax.set_title("Italy detail — Roman roads and cities (DARMC 2008; Hanson 2016)")
    ax.set_xlabel("longitude"); ax.set_ylabel("latitude")
    fig.tight_layout()
    fig.savefig(OUT / "04_italy_detail.png"); plt.close(fig)
    print("saved 04_italy_detail.png")


def export_gexf(G: nx.Graph) -> None:
    for n in G.nodes:
        G.nodes[n]["viz"] = {"position": {"x": float(n[0]), "y": float(n[1]), "z": 0}}
    nx.write_gexf(G, OUT / "roman_roads_graph.gexf")
    print("saved roman_roads_graph.gexf")


def build_interactive(roads, hexes, rome, cities: gpd.GeoDataFrame = None,
                      wiki_urls: dict = None, founders: dict = None) -> None:
    esri_dark = folium.TileLayer(
        tiles=("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/"
               "World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"),
        attr="Esri, HERE, Garmin, FAO, NOAA, USGS", name="Esri Dark Gray",
    )
    m = folium.Map(location=[42.5, 12.5], zoom_start=5, tiles=esri_dark)
    folium.TileLayer(  # place labels / borders on top, always on
        tiles=("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/"
               "World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}"),
        attr="Esri, HERE, Garmin, FAO, NOAA, USGS",
        name="Esri labels", overlay=True, control=False,
    ).add_to(m)
    m.get_root().header.add_child(folium.Element(
        "<style>.city-link{color:#4d9fff;font-weight:600;text-decoration:none}"
        ".city-link:hover{color:#1a56db;text-decoration:underline}</style>"))
    folium.TileLayer("openstreetmap", name="OSM", show=False).add_to(m)

    roads_simpl = roads.copy()
    roads_simpl.geometry = roads.geometry.simplify(0.01)
    roads_json = roads_simpl.to_json()
    folium.GeoJson(
        roads_json, name="Roman roads",
        style_function=lambda _: {"color": "#bbbbbb", "weight": 0.6, "opacity": 0.55},
        tooltip=folium.GeoJsonTooltip(fields=["CERTAINTY"], aliases=["Certainty:"]) if "CERTAINTY" in roads.columns else None,
    ).add_to(m)

    cmap = plt.get_cmap("RdYlGn")
    for metric, label in [("degree", "Degree (summed)"), ("betweenness", "Betweenness (summed)")]:
        fg = folium.FeatureGroup(name=label, show=False)
        vmax = hexes[metric].max()
        for _, row in hexes.iterrows():
            if row[metric] <= 0:
                continue
            color = to_hex(cmap(row[metric] / vmax))
            folium.GeoJson(
                mapping(row.geometry),
                style_function=lambda _, c=color: {"fillColor": c, "color": c, "weight": 0.5, "fillOpacity": 0.65},
                tooltip=f"{label}<br>cell {row['cell']}<br>value {row[metric]:.0f}",
            ).add_to(fg)
        fg.add_to(m)

    if cities is not None:
        for connected, label in [
            (True, f"Cities on roads (<= {CITY_CONNECT_KM} km)"),
            (False, f"Cities off roads (> {CITY_CONNECT_KM} km)"),
        ]:
            fg = folium.FeatureGroup(name=label, show=connected)
            for _, c in cities[cities["connected"] == connected].iterrows():
                name = c["Ancient Toponym"]
                url = (wiki_urls or {}).get(str(c["Primary Key"]))
                if url:
                    name = (f'<a class="city-link" href="{url}" '
                            f'target="_blank" rel="noopener noreferrer">{name}</a>')
                founder = (founders or {}).get(str(c["Primary Key"]), "")
                if not founder:
                    # no Wikidata founder: fall back to who ruled the region before Rome
                    cq = _conquest_year(c["Province"])
                    if cq is not None and int(c["Start Date"]) < cq:
                        founder = _pre_roman_people(c["Province"]) or ""
                founded = f"<br>founded by {founder}" if founder else ""
                info = (f"<b>{name}</b> ({c['Modern Toponym']})<br>"
                        f"Established: {fmt_year(c['Start Date'])}{founded}<br>"
                        f"Province: {c['Province']}<br>Rank: {c['Barrington Atlas Rank']}")
                folium.CircleMarker(
                    location=[c.geometry.y, c.geometry.x],
                    radius={1: 7, 2: 4.5, 3: 2.5, 4: 1.8, 5: 1.5}.get(c["rank"], 1.5),
                    color="#333333", weight=0.4, fill=True,
                    fill_color=RANK_COLORS[c["rank"]], fill_opacity=0.9,
                    popup=folium.Popup(info, max_width=280),
                    tooltip=info,
                ).add_to(fg)
            fg.add_to(m)

    folium.Marker(ROME_POINT[::-1], tooltip="Rome", icon=folium.Icon(color="white", icon_color="black")).add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    m.fit_bounds([[hexes.lat.min() - 1, hexes.lng.min() - 1], [hexes.lat.max() + 1, hexes.lng.max() + 1]])
    m.save(OUT / "roman_roads_interactive.html")
    print("saved roman_roads_interactive.html")


def write_findings(hexes: pd.DataFrame, G: nx.Graph, cities: gpd.GeoDataFrame = None) -> None:
    rome_cell = h3.latlng_to_cell(*ROME_POINT, H3_RES)
    lines = ["# Do All the Roads Lead to Rome? — findings", "",
             f"Graph: **{G.number_of_nodes()} nodes / {G.number_of_edges()} edges** "
             f"({nx.number_connected_components(G)} connected components).", ""]

    for metric in ["degree", "betweenness"]:
        ranked = hexes.sort_values(metric, ascending=False).reset_index(drop=True)
        top = ranked.head(10)
        try:
            rome_rank = ranked.index[ranked["cell"] == rome_cell][0] + 1
            rome_note = f"Rome's hexagon ranks **#{rome_rank}** by summed {metric}."
        except IndexError:
            rome_note = "Rome's hexagon not present in table."
        lines += [f"## Top hexagons by summed {metric}", rome_note, "",
                  "| rank | cell | lat | lng | value |", "|---|---|---|---|---|"]
        for i, row in top.iterrows():
            lines.append(f"| {i + 1} | {row['cell']} | {row['lat']:.2f} | {row['lng']:.2f} | {row[metric]:.0f} |")
        lines.append("")

    top_deg = hexes.loc[hexes["degree"].idxmax(), "cell"]
    lines += ["## Verdict", "",
              f"The hexagon containing Rome (`{rome_cell}`) "
              + ("**is** the top-degree cell — all roads lead to Rome." if top_deg == rome_cell
                 else f"is not the top cell by degree (top is `{top_deg}`), but the analysis above shows how dominant Rome is."),
              ""]

    if cities is not None:
        n_total, n_conn = len(cities), int(cities["connected"].sum())
        lines += [f"## Roman cities connected by the roads", "",
                  f"Of **{n_total}** known Roman cities (Hanson 2016, 100 BC – AD 300), "
                  f"**{n_conn} ({n_conn / n_total:.0%})** lie within {CITY_CONNECT_KM} km of a DARMC road.", "",
                  "### Major cities (Barrington rank 1–2) and their nearest road", "",
                  "| city | modern name | province | rank | nearest road |", "|---|---|---|---|---|"]
        major = cities[cities["rank"] <= 2].sort_values("dist_road_km")
        for _, c in major.iterrows():
            lines.append(f"| {c['Ancient Toponym']} | {c['Modern Toponym']} | {c['Province']} | "
                         f"{c['Barrington Atlas Rank']} | {c['dist_road_km']:.1f} km |")
        off = major[~major["connected"]]
        if len(off):
            lines += ["", "Major cities **not** within "
                      f"{CITY_CONNECT_KM} km of any digitized road: "
                      + ", ".join(f"{c['Ancient Toponym']} ({c['dist_road_km']:.0f} km)"
                                  for _, c in off.iterrows()) + "."]
        lines += ["", "Data: DARMC Roman Road Network (2008), CC BY-NC 3.0; "
                  "Hanson 2016 Cities Database v1.0 (OxREP), doi:10.5287/bodleian:eqapevAn8."]
    else:
        lines += ["", "Data: DARMC Roman Road Network (2008), CC BY-NC 3.0."]

    (OUT / "findings.md").write_text("\n".join(lines), encoding="utf-8")
    print("saved findings.md")


def main() -> None:
    roads_raw = gpd.read_file(DATA)  # Lambert Conformal Conic, metres
    roads = load_roads()
    cities = connect_cities(load_cities(), roads_raw)
    plot_base_map(roads, cities)
    G = build_graph(roads)
    nodes = compute_centralities(G)
    extent = empire_extent(roads_raw)  # metric CRS buffer
    hexes = hex_scores(nodes, extent)
    rome, rome_kind = get_rome_boundary()
    plot_hexmap(hexes, roads, rome if rome_kind == "polygon" else None, "degree", "02_degree_hexmap.png", cities)
    plot_hexmap(hexes, roads, rome if rome_kind == "polygon" else None, "betweenness", "03_betweenness_hexmap.png", cities)
    plot_italy_detail(roads, cities)
    export_gexf(G)
    wiki_urls = resolve_wiki_links(cities)
    founders = resolve_founders(cities, wiki_urls)
    build_interactive(roads, hexes, rome, cities, wiki_urls, founders)
    write_findings(hexes, G, cities)
    print("done.")


if __name__ == "__main__":
    main()
