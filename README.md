# Do All the Roads Lead to Rome?

Network analysis of the Roman road network with city coverage — built after
Milan Janosov's 2023 analysis ([Towards Data Science](https://towardsdatascience.com/do-all-the-roads-lead-to-rome-5b6756ce7d52/)).

## What it does

1. Loads the **DARMC Roman Road Network (2008)** shapefile and reprojects to EPSG:4326.
2. Builds an undirected graph from road segment endpoints (unweighted, as in the original methodology) → 5,086 nodes / 7,048 edges / 100 components.
3. Computes **degree** and **betweenness centrality** per node.
4. Aggregates node scores into **H3 hexagons (resolution 3)** covering the Empire's extent (20 km buffer).
5. Loads **1,388 Roman cities** (Hanson 2016) and measures each city's distance to the nearest road.
6. Emits static maps (PNG), an interactive folium map (HTML), a GEXF graph for Gephi, CSVs, and findings.

## Findings

- Rome's hexagon ranks **#1 by both summed degree and summed betweenness** — the data says yes, all roads led to Rome.
- **1,105 of 1,388 cities (80%)** lie within 5 km of a digitized road.
- Major cities standing directly on a road: Damascus, Byzantium, Milan, Lepcis Magna, Lyon.
- The unconnected majors cluster in **Crete** and the **Peloponnesian interior** — a digitization gap in the DARMC layer, not an ancient reality.

## Outputs (`output/`)

| File | Content |
|---|---|
| `01_roman_roads_map.png` | Road network + cities colored by Barrington rank |
| `02_degree_hexmap.png` / `03_betweenness_hexmap.png` | H3 hexagon maps with roads + cities overlay |
| `04_italy_detail.png` | Italy zoom with labeled major cities |
| `roman_roads_interactive.html` | Interactive map (hexmaps and OSM background hidden by default; toggle in layer control) |
| `roman_roads_graph.gexf` | Graph for Gephi |
| `nodes_centrality.csv` / `cities_road_access.csv` | Per-node and per-city data |
| `findings.md` | Full results tables |

## Run

```bash
pip install geopandas folium networkx h3 matplotlib numpy pandas shapely osmnx
python roman_roads_analysis.py
```

## Data & credit

- Roman Road Network (version 2008), Digital Atlas of Roman and Medieval Civilizations — CC BY-NC 3.0. [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/TI0KAU)
- Hanson, J. W. (2016). Cities Database, Version 1.0 (OxREP), doi:10.5287/bodleian:eqapevAn8 — *An Urban Geography of the Roman World, 100 B.C. to A.D. 300*.
- Methodology: Janosov, M. (2023), "Do All the Roads Lead to Rome?".
