# Records changelog — 2026-11-10 (KEN-LVB boundary)

New delineation of the Lake Victoria Basin (Kenya) living landscape, shared with Lizeth Llanos on
2026-11-10 as `LVB Counties.zip` (shapefile `LVB_Counties`, 5 county polygons, EPSG:4326). It is the
Kenya admin-1 layer of OCHA's COD-AB (source IEBC, valid 2019-10-31), licensed CC BY-IGO 3.0
(licence read from the HDX API, dataset `cod-ab-ken`, 2026-11-10).

| | Before (2026-10-14) | After (2026-11-10) |
|---|---|---|
| Counties | Kakamega, Kisumu, Siaya, Vihiga | Kericho, Kisumu, Nandi, Siaya, Vihiga |
| Source | GADM 4.1, level 1 | OCHA COD-AB Kenya (IEBC), admin 1 |
| Licence | `other` (GADM terms) | `CC-BY-3.0-IGO` |
| Area (EPSG:6933) | 9,163 km2 | 12,095 km2 |
| bbox | 33.9499, -0.4244, 35.3430, 0.6557 | 33.9480, -0.6615, 35.6750, 0.5631 |

Kakamega county is no longer part of the landscape; Kericho and Nandi are new.

**Files changed.** `MOSAIC_LLV_delim/LVB_Counties_KEN.*` (new source file; the old `LVB-2_KEN.*` is kept,
unused), `scripts/build_boundaries.py` (source file name), `spec/boundary_provenance.json` (KEN-LVB),
`boundaries/KEN-LVB.geojson`, `boundaries/landscapes.geojson` (KEN-LVB feature only; the other ten
are byte-identical), `spec/bbox_lookup.json`, record **MFL-2026-102** (description, licence, citation,
bbox, file, download link → release `boundaries-2026-11-10`). The KEN-LVB items whose extent is the
landscape bbox (083, 085–092) take the new bbox through the build.

**New release** `boundaries-2026-11-10` (all 11 landscapes, full detail). Only KEN-LVB's geometry and
credit changed; the other ten differ only in the README. `boundaries-2026-10-14` stays published, and
records 093–101 still point to it.
