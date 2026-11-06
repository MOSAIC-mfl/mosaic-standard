#!/usr/bin/env python3
"""Build the canonical living-landscape boundary GeoJSONs from the delineation
shapefiles, and regenerate spec/bbox_lookup.json with REAL bboxes.

Run LOCALLY only (the shapefiles live outside this repo and are not in CI):

    python3 scripts/build_boundaries.py [--source ../MOSAIC_LLV_delim]

Outputs (committed to the repo; build_catalog.py copies them into stac/):
    boundaries/<CODE>.geojson      one dissolved, simplified boundary per landscape, carrying
                                   source/license/license_url/attribution from
                                   spec/boundary_provenance.json; not written when that file
                                   says publish=false (the licence forbids redistribution)
    boundaries/landscapes.geojson  all published landscapes in one FeatureCollection
    spec/bbox_lookup.json          real bboxes/centroids (replaces the approximate ones)

The canonical landscape list below was approved by Lizeth on 2026-07-21.
Peru (PER-PCL) is pending confirmation with the Peru team (the reference map
says Apurimac but the delivered shapefile is Pucallpa/Ucayali).
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import geopandas as gpd
from shapely.ops import polygonize, unary_union

REPO = Path(__file__).resolve().parent.parent
BOUNDARIES_DIR = REPO / "boundaries"
SPEC_BBOX = REPO / "spec" / "bbox_lookup.json"
# Source, licence and attribution per code; publish=false withholds the geometry.
SPEC_PROVENANCE = REPO / "spec" / "boundary_provenance.json"
PROVENANCE_KEYS = ("source", "license", "license_url", "attribution")

# Vertex budget per boundary: simplify (topology-preserving) with a growing
# tolerance until the geometry fits, so files stay small enough to commit.
MAX_VERTICES = 1500

# code -> (name, system, [countries], source shapefile)
CANONICAL = {
    "COL-CUM": ("Cumbal (Narino)", "Amazon", ["Colombia"], "aoiCUM_COL.shp"),
    "PER-PCL": ("Pucallpa - Ucayali", "Amazon", ["Peru"], "aoiPCL_PER.shp"),
    "SEN-FK": ("Fatick Department", "Sudan-Sahelian and Guinea Forest-Savanna Transition",
               ["Senegal"], "MFL_Senegal_LL_SEN.shp"),
    "CIV-NZ": ("N'Zi Watershed", "Sudan-Sahelian and Guinea Forest-Savanna Transition",
               ["Côte d'Ivoire"], "MFLLL_Nzi_watershed_Cote_d_Ivoire_CIV.shp"),
    "TUN-NW": ("Northwestern Tunisia", "Dryland Mediterranean", ["Tunisia"], "Tunisia_ALL_TUN.shp"),
    "ETH-OG": ("Omo-Gibe Basin", "East-South Africa Highland-Lowland-Rift Valley System",
               ["Ethiopia"], "Omo_Gibe_LL_ETH.shp"),
    "KEN-LVB": ("Lake Victoria Basin (Kenya)", "East-South Africa Highland-Lowland-Rift Valley System",
                ["Kenya"], "LVB-2_KEN.shp"),
    "KEN-LEI": ("LEILA (Southern Kenya Rangelands)", "East-South Africa Highland-Lowland-Rift Valley System",
                ["Kenya"], "Zone1_KEN.shp"),
    "ZWE-MB": ("Mbire - Lower Zambezi Valley", "East-South Africa Highland-Lowland-Rift Valley System",
               ["Zimbabwe"], "mfl_aoi_ZWE.shp"),
    "IND-CH": ("Central India Highlands", "Deccan Plateau Forest-Dryland Transition Zone",
               ["India"], "MFL_India_LL_Boundary_IND.shp"),
    "MEK-3S": ("3S Basins (Sekong, Sesan, Srepok)", "Three S Rivers Sub-basin in the Mekong Basin",
               ["Laos", "Cambodia", "Vietnam"], "3sbasins_LAO.shp"),
}

PENDING_CONFIRMATION = {"PER-PCL"}


def count_vertices(geom) -> int:
    return sum(len(p.exterior.coords) + sum(len(r.coords) for r in p.interiors)
               for p in getattr(geom, "geoms", [geom]))


def simplify_to_budget(geom, budget: int = MAX_VERTICES):
    if count_vertices(geom) <= budget:
        return geom, 0.0
    tol = 0.0005
    while tol <= 0.1:
        simp = geom.simplify(tol, preserve_topology=True)
        if count_vertices(simp) <= budget:
            return simp, tol
        tol *= 2
    return simp, tol


def round_coords(obj, ndigits: int = 5):
    if isinstance(obj, float):
        return round(obj, ndigits)
    if isinstance(obj, (list, tuple)):
        return [round_coords(v, ndigits) for v in obj]
    return obj


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=str(REPO.parent / "MOSAIC_LLV_delim"),
                    help="Folder holding the delineation shapefiles")
    args = ap.parse_args()
    src = Path(args.source)
    if not src.is_dir():
        raise SystemExit(f"Source folder not found: {src}")

    BOUNDARIES_DIR.mkdir(exist_ok=True)
    today = date.today().isoformat()
    features, lookup = [], {}
    provenance = json.loads(SPEC_PROVENANCE.read_text(encoding="utf-8"))
    missing = [c for c in CANONICAL if c not in provenance]
    if missing:
        raise SystemExit(f"No provenance in {SPEC_PROVENANCE.name} for: {', '.join(missing)}")

    for code, (name, system, countries, shp) in CANONICAL.items():
        gdf = gpd.read_file(src / shp).to_crs(epsg=4326)
        dissolved = gdf.geometry.union_all()
        # Some deliveries trace the outline as a thin stroke polygon (near-zero
        # area, e.g. the India LL boundary). Rebuild the filled region from the
        # linework when the area is implausibly small for the bbox.
        w0, s0, e0, n0 = dissolved.bounds
        if dissolved.area < 0.01 * (e0 - w0) * (n0 - s0):
            dissolved = unary_union(list(polygonize(unary_union(dissolved.boundary))))
            print(f"  {code}: stroke-like outline detected -> refilled via polygonize")
        # bbox/centroid from the FULL-resolution dissolve; simplify only for display.
        w, s, e, n = dissolved.bounds
        cx, cy = dissolved.centroid.x, dissolved.centroid.y
        simp, tol = simplify_to_budget(dissolved)

        props = {
            "code": code,
            "name": name,
            "landscape_system": system,
            "countries": countries,
            "source_file": shp,
            "source_features_dissolved": len(gdf),
            "simplify_tolerance_deg": tol,
            "generated": today,
        }
        props.update({k: provenance[code].get(k) for k in PROVENANCE_KEYS})
        if code in PENDING_CONFIRMATION:
            props["pending_confirmation"] = True

        feature = {
            "type": "Feature",
            "properties": props,
            "bbox": round_coords([w, s, e, n]),
            "geometry": round_coords(simp.__geo_interface__ | {}),
        }
        # __geo_interface__ nests tuples; normalise via json round-trip.
        feature["geometry"] = json.loads(json.dumps(
            {"type": simp.geom_type, "coordinates": round_coords(simp.__geo_interface__["coordinates"])}))

        out = BOUNDARIES_DIR / f"{code}.geojson"
        if provenance[code]["publish"]:
            out.write_text(json.dumps(feature, ensure_ascii=False, separators=(",", ":")) + "\n",
                           encoding="utf-8")
            features.append(feature)
        else:
            # The licence forbids stand-alone redistribution: no geometry file
            # (the bbox below is still derived; the STAC collection cites the source).
            out.unlink(missing_ok=True)

        entry = {
            "bbox": round_coords([w, s, e, n], 4),
            "centroid": round_coords([cx, cy], 4),
            "name": name,
            "landscape_system": system,
            "countries": countries,
            "delineated": True,
        }
        if code in PENDING_CONFIRMATION:
            entry["pending_confirmation"] = True
        lookup[code] = entry
        size = f"{out.stat().st_size / 1024:7.1f} KB" if out.exists() else "withheld (licence)"
        print(f"  {code:8s} {name[:38]:38s} {len(gdf):3d} src feats  tol={tol:<7g} {size}")

    combined = {"type": "FeatureCollection",
                "name": "MFL Living Landscapes - canonical delineations",
                "features": features}
    (BOUNDARIES_DIR / "landscapes.geojson").write_text(
        json.dumps(combined, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    # Rebuild spec/bbox_lookup.json: real landscape boxes + keep country fallbacks.
    old = json.loads(SPEC_BBOX.read_text(encoding="utf-8"))
    new = {
        "_meta": {
            "file": "bbox_lookup.json",
            "purpose": "Bounding boxes + centroids per living-landscape CODE, with a "
                       "country-level fallback. Frontend plots centroids; STAC export "
                       "seeds extent.spatial.bbox.",
            "crs": "EPSG:4326 (WGS84)",
            "bbox_order": "[west, south, east, north]  (minLon, minLat, maxLon, maxLat)",
            "centroid_order": "[lon, lat]",
            "accuracy": "Landscape entries marked delineated:true are derived from the "
                        "REAL delineation shapefiles (MOSAIC_LLV_delim, dissolved, "
                        "EPSG:4326) - authoritative for discovery extents. GLB-UNSPEC "
                        "and country_fallback remain coarse locators only.",
            "status": f"CANONICAL - built from delineation shapefiles by "
                      f"scripts/build_boundaries.py on {today}. Approved by Lizeth "
                      f"2026-07-21; PER-PCL pending confirmation with the Peru team.",
            "lookup_rule": old["_meta"].get("lookup_rule", ""),
        },
        "landscapes": lookup,
        "country_fallback": old["country_fallback"],
    }
    # Keep a world-ish box for truly global/unresolvable records.
    new["landscapes"]["GLB"] = {
        "bbox": [-180, -60, 180, 72], "centroid": [0, 10],
        "name": "Global / cross-landscape", "delineated": False,
    }
    SPEC_BBOX.write_text(json.dumps(new, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nWrote {len(features)} boundaries ({len(CANONICAL) - len(features)} withheld) "
          f"+ landscapes.geojson + spec/bbox_lookup.json")


if __name__ == "__main__":
    main()
