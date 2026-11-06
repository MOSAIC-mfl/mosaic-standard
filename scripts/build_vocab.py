#!/usr/bin/env python3
"""Build the controlled vocabularies in vocab/*.json.

Hand-curated vocabularies are defined in this file, so a change to a term is a
reviewable diff here. The geography vocabulary is generated from the UN M49
table in vocab/sources/un-m49.csv (UNSD, published for public use).

    python3 scripts/build_vocab.py          # write vocab/*.json
    python3 scripts/build_vocab.py --check  # exit 1 if vocab/ is out of date (CI)
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOCAB = ROOT / "vocab"
STANDARD_VERSION = "0.2.0"
# Where the schemas are published (GitHub Pages of this repo).
SCHEMA_BASE = f"https://mosaic-mfl.github.io/catalog/schema/v{STANDARD_VERSION}/"


def concepts(rows: list[tuple]) -> list[dict]:
    keys = ("id", "label", "description")
    return [dict(zip(keys, r, strict=True)) for r in rows]


# MOSAIC themes: the 13 MFL categories of the schema-1 records, then 3 climate themes. `legacy_label` is the exact
# string used in the schema-1 records, so the migration can map them 1:1.
THEMES = [
    (
        "boundaries-admin-units",
        "Boundaries / admin units",
        "Administrative units, landscape and watershed boundaries used to delineate or aggregate data.",
    ),
    (
        "land-cover-land-use",
        "Land cover / land use",
        "What covers the land and how it is used, including change between dates.",
    ),
    (
        "ecosystem-condition",
        "Ecosystem condition",
        "State of ecosystems: vegetation, soil and water condition indicators.",
    ),
    ("degradation-land-health", "Degradation / land health", "Soil properties, erosion and land degradation."),
    (
        "water-hydrology",
        "Water / hydrology",
        "Water bodies, river networks, rainfall and other hydro-climatic observations.",
    ),
    ("biodiversity-ecosystems", "Biodiversity / ecosystems", "Species, habitats, protected and conservation areas."),
    (
        "pressures-drivers",
        "Pressures / drivers",
        "Pressures on the landscape: deforestation, fire, human footprint, vulnerability.",
    ),
    ("ecosystem-services", "Ecosystem services", "Benefits people obtain from ecosystems and their assessment."),
    (
        "hotspots-leverage-points",
        "Hotspots / leverage points",
        "Places or factors where intervention has the largest effect.",
    ),
    ("scenarios-future-risks", "Scenarios / future risks", "Projections, scenarios and future risk assessments."),
    (
        "decision-support-outputs",
        "Decision-support outputs",
        "Products made to inform decisions: plans, prioritisation maps, dashboards.",
    ),
    ("agrobiodiversity-crops", "Agrobiodiversity / crops", "Crops, crop fields, varieties, production and yield."),
    (
        "socio-economic-livelihoods",
        "Socio-economic / livelihoods",
        "Population, livelihoods, markets, institutions and other socio-economic data.",
    ),
    # Added in v0.1 following the Climate Data Hub domains, so climate records have a theme.
    (
        "climate",
        "Climate",
        "Observed, reanalysis, projected and scenario climate data: temperature, precipitation and other variables.",
    ),
    (
        "climate-adaptation",
        "Climate adaptation",
        "Vulnerability, exposure, climate risk assessment and adaptation planning.",
    ),
    ("climate-mitigation", "Climate mitigation", "Emissions, carbon stocks, sequestration and mitigation pathways."),
]

LEGACY_THEMES = 13  # the first 13 themes are the MFL categories of the schema-1 records

# bbox [west, south, east, north] computed from the delineations in the old catalog repo
# (catalog/boundaries/<code>.geojson @ main 91949d7, read only, 2026-10-30). Used by the API to
# derive landscapes for records from other catalogues.
LANDSCAPES = [
    ("COL-CUM", "Cumbal (Nariño)", ["COL"], [-78.0702, 0.8386, -77.7535, 1.0784]),
    ("PER-PCL", "Pucallpa – Ucayali", ["PER"], [-75.9479, -9.4181, -74.3225, -7.9501]),
    ("SEN-FK", "Fatick Department", ["SEN"], [-16.7921, 13.9284, -16.1055, 14.6084]),
    ("CIV-NZ", "N'Zi Watershed", ["CIV"], [-5.3792, 5.95, -3.8583, 9.4333]),
    ("TUN-NW", "Northwestern Tunisia", ["TUN"], [8.9235, 35.7384, 9.4464, 36.4324]),
    ("ETH-OG", "Omo-Gibe Basin", ["ETH"], [34.9533, 4.431, 38.4128, 9.3685]),
    ("KEN-LVB", "Lake Victoria Basin (Kenya)", ["KEN"], [33.9499, -0.4243, 35.343, 0.6557]),
    ("KEN-LEI", "LEILA (Southern Kenya Rangelands)", ["KEN"], [35.9962, -3.1869, 38.5194, -0.7526]),
    ("ZWE-MB", "Mbire – Lower Zambezi Valley", ["ZWE"], [28.8445, -17.4339, 32.0584, -15.6073]),
    ("IND-CH", "Central India Highlands", ["IND"], [78.2942, 22.2022, 81.1975, 25.9555]),
    ("MEK-3S", "3S Basins (Sekong, Sesan, Srepok)", ["KHM", "LAO", "VNM"], [105.95, 11.8519, 108.7757, 16.3852]),
]

SIMPLE = {
    "resource_type": (
        "Kind of resource a record describes.",
        [
            ("dataset", "Dataset", "Data in any form: raster, vector, tabular or a mix."),
            ("service", "Service", "An endpoint that serves data: WMS/WFS, OGC API, STAC API, Earth Engine, REST."),
            ("document", "Document", "A report, plan, manual or article that is the resource itself."),
            ("software", "Software", "Code, scripts, notebooks or tools."),
            ("model", "Model", "A trained or calibrated model and its parameters."),
        ],
    ),
    "access": (
        "Access condition of a resource or of one of its data entries. Always explicit in MOSAIC: it is never assumed "
        "to be public. Same values as the Climate Data Hub (DCAT / EU access rights).",
        [
            ("public", "Public", "Anyone can obtain the data without asking."),
            (
                "restricted",
                "Restricted",
                "The record is public, but the data needs a request, an account or an agreement.",
            ),
            (
                "non-public",
                "Non-public",
                "Catalogued for the network; the data is not available outside the team that holds it (v0.1: internal).",
            ),
        ],
    ),
    "data_kind": (
        "What kind of data a data entry leads to. Drives the 'data type' facet and which detail block applies.",
        [
            ("raster", "Raster", "Gridded data: GeoTIFF/COG, NetCDF, Zarr, Earth Engine images."),
            ("vector", "Vector", "Points, lines or polygons: Shapefile, GeoPackage, GeoJSON, FlatGeobuf."),
            ("tabular", "Tabular", "Tables: CSV, Excel, Parquet, with or without a geometry column."),
            ("document", "Document", "A report, plan or article meant to be read (PDF, Word, web page)."),
            ("mixed", "Mixed", "Several kinds of data behind one access point; describe them in the description."),
            ("other", "Other", "Anything else (code, model files...); say what in the description."),
        ],
    ),
    "access_method": (
        "How a data entry is reached: download a file, call a service, visit a page, or ask for the data.",
        [
            ("download", "Download", "A direct link to a file or a bundle of files."),
            ("landing_page", "Landing page", "A page at the source that describes the data and links to it."),
            ("service", "Service", "An API or map service (WMS/WFS, OGC API, STAC API, Earth Engine, REST)."),
            ("request", "Request", "The data is obtained by asking; see access_note."),
        ],
    ),
    "contact_role": (
        "Role a person or organization plays for a resource.",
        [
            ("producer", "Producer", "Created the data."),
            ("licensor", "Licensor", "Granted the licence under which the data is shared."),
            ("host", "Host", "Stores and serves the data (a repository, portal or server)."),
            ("processor", "Processor", "Transformed, cleaned or derived the data."),
            ("point-of-contact", "Point of contact", "Answers questions and access requests."),
            ("maintainer", "Maintainer", "Keeps the record and the data up to date."),
            ("funder", "Funder", "Paid for producing the data (prefer the funding field when only a name is known)."),
        ],
    ),
    "service_type": (
        "Protocol of a web service behind a data entry.",
        [
            ("wms", "WMS", "OGC Web Map Service."),
            ("wmts", "WMTS", "OGC Web Map Tile Service."),
            ("wfs", "WFS", "OGC Web Feature Service."),
            ("wcs", "WCS", "OGC Web Coverage Service."),
            ("ogc-api", "OGC API", "OGC API Features, Coverages, Tiles or Maps."),
            ("arcgis-rest", "ArcGIS REST", "Esri ArcGIS Server or Online REST service."),
            ("xyz", "XYZ tiles", "Map tiles by {z}/{x}/{y} URL template."),
            ("stac-api", "STAC API", "SpatioTemporal Asset Catalog API."),
            ("gee", "Google Earth Engine", "An Earth Engine asset or app."),
            ("other", "Other", "Another API; describe it in the data entry."),
        ],
    ),
    "update_frequency": (
        "How often the data is updated at its source.",
        [
            ("static", "Static", "Not updated."),
            ("continual", "Continual", "Updated continually."),
            ("daily", "Daily", ""),
            ("weekly", "Weekly", ""),
            ("monthly", "Monthly", ""),
            ("quarterly", "Quarterly", ""),
            ("semiannual", "Semiannual", "Twice a year."),
            ("seasonal", "Seasonal", "Once per season."),
            ("annual", "Annual", ""),
            ("irregular", "Irregular", "Updated when needed, with no fixed schedule."),
            ("unknown", "Unknown", "The source does not say."),
        ],
    ),
}


def scheme(sid: str, title: str, description: str) -> dict:
    return {"id": f"mosaic-{sid.replace('_', '-')}", "title": title, "description": description}


def build() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for name, (desc, rows) in SIMPLE.items():
        out[name] = {"scheme": scheme(name, name.replace("_", " ").title(), desc), "concepts": concepts(rows)}
    out["themes"] = {
        "scheme": scheme(
            "themes",
            "MOSAIC themes",
            "Closed list used to browse and filter the catalogue. A record has one or more; "
            "the first is its primary theme. v0.1: the 13 MFL categories plus climate, "
            "adaptation and mitigation (guided by the Climate Data Hub domains).",
        ),
        "concepts": [
            dict(id=i, label=lab, description=d) | ({"legacy_label": lab} if n < LEGACY_THEMES else {})
            for n, (i, lab, d) in enumerate(THEMES)
        ],
    }
    out["landscapes"] = {
        "scheme": scheme(
            "landscapes",
            "MOSAIC living landscapes",
            "Living landscapes of the MFL programme. Boundaries are published by the catalogue.",
        ),
        "concepts": [dict(id=c, label=lab, countries=cs, bbox=bb) for c, lab, cs, bb in LANDSCAPES],
    }
    out["geography"] = build_geography()
    return out


def build_geography() -> dict:
    """Countries by ISO 3166-1 alpha-3, regions as m49:<code>, plus 'global'."""
    path = VOCAB / "sources" / "un-m49.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig"), delimiter=";"))
    countries, regions = [], {}
    for r in rows:
        for code_key, name_key in (
            ("Region Code", "Region Name"),
            ("Sub-region Code", "Sub-region Name"),
            ("Intermediate Region Code", "Intermediate Region Name"),
        ):
            if r[code_key]:
                regions[r[code_key]] = r[name_key]
        if r["ISO-alpha3 Code"]:
            countries.append({"id": r["ISO-alpha3 Code"], "label": r["Country or Area"], "m49": r["M49 Code"]})
    concepts_ = [{"id": "global", "label": "Global", "m49": "001"}]
    concepts_ += [{"id": f"m49:{c}", "label": n, "m49": c} for c, n in sorted(regions.items())]
    concepts_ += sorted(countries, key=lambda c: c["id"])
    return {
        "scheme": scheme(
            "geography",
            "Geography",
            "Where a resource applies. Countries use ISO 3166-1 alpha-3 codes (e.g. PER); "
            "regions use UN M49 codes prefixed with m49: (e.g. m49:419); 'global' for worldwide.",
        ),
        "source": "UN M49 Standard Country or Area Codes (UNSD), vocab/sources/un-m49.csv",
        "concepts": concepts_,
    }


SCHEMA_DEFS = {  # $defs name in schema/vocab.schema.json -> vocabulary file
    "theme": "themes",
    "landscape": "landscapes",
    "geography": "geography",
    "resourceType": "resource_type",
    "access": "access",
    "dataKind": "data_kind",
    "accessMethod": "access_method",
    "contactRole": "contact_role",
    "serviceType": "service_type",
    "updateFrequency": "update_frequency",
}


def vocab_schema(vocabs: dict[str, dict]) -> dict:
    """JSON Schema fragment with one enum per vocabulary, so the record schema
    stays standalone for editors while the vocabularies stay the single source."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": SCHEMA_BASE + "vocab.schema.json",
        "title": "MOSAIC controlled vocabularies (generated by scripts/build_vocab.py; do not edit)",
        "$defs": {
            d: {
                "type": "string",
                "enum": [c["id"] for c in vocabs[v]["concepts"]],
                "description": vocabs[v]["scheme"]["description"],
            }
            for d, v in SCHEMA_DEFS.items()
        },
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    stale = []
    vocabs = build()
    targets = {VOCAB / f"{n}.json": d for n, d in vocabs.items()}
    targets[ROOT / "schema" / "vocab.schema.json"] = vocab_schema(vocabs)
    for path, data in targets.items():
        text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(path.name)
        else:
            path.write_text(text, encoding="utf-8")
    if stale:
        print("Out of date (run scripts/build_vocab.py):", ", ".join(stale))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
