#!/usr/bin/env python3
"""Migrate MOSAIC schema-1 records (old `catalog` repo) to the MOSAIC standard (v0.2).

Two steps: schema 1 -> v0.1 (this file, crosswalks/mosaic-schema1.yaml), then v0.1 -> v0.2
(src/mosaic_catalog/v02.py, the same conversion as scripts/migrate_v02.py).

The old repository is only READ, through `git show <ref>:records/<file>` and `git log`;
its working tree, branches and files are never touched.

    python3 scripts/migrate_schema1.py --source ../catalog            # ref main -> records/
    python3 scripts/migrate_schema1.py --source ../catalog --dry-run  # print the summary only

Nothing is invented. Values the old record does not have stay empty; the validator lists
them in review/minimum_gaps.*. Conversions a person should look at go to
review/migration_notes.*. The mapping is documented in crosswalks/mosaic-schema1.yaml.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from mosaic_catalog.v02 import convert  # noqa: E402

VOCAB = ROOT / "vocab"

URL_RE = re.compile(r"(?:https?|ftp)://[^\s)\],;]+")
# Style files (symbology for GIS software): they help to display the data but are not the data.
STYLE_EXT = re.compile(r"\.(qml|sld|lyr|lyrx|style)(\?|$)", re.IGNORECASE)
FILE_EXT = re.compile(
    r"\.(zip|tif|tiff|csv|xlsx?|gpkg|shp|nc|geojson|json|kml|kmz|qml|rar|7z|parquet|fgb)(\?|$)", re.IGNORECASE
)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
YEAR = r"(1[89]\d\d|20\d\d)"

ACCESS = {"Open": "public", "Restricted": "restricted", "Internal": "internal"}
KIND = {"Vector": "vector", "Raster": "raster", "Tabular": "tabular", "Mixed": "mixed"}
FREQUENCY = {
    "Unknown": "unknown",
    "Static": "static",
    "Annual": "annual",
    "Seasonal": "seasonal",
    "On-demand": "irregular",
}
SPDX = {
    "CC BY 4.0": "CC-BY-4.0",
    "CC BY-SA 4.0": "CC-BY-SA-4.0",
    "CC0 1.0": "CC0-1.0",
    "CC BY-IGO 3.0": "CC-BY-3.0-IGO",  # KEN-LVB boundary (OCHA COD-AB), catalog main #16
}
# Values that mean "not known" in schema-1 free-text fields.
PLACEHOLDERS = {"NA", "N/A", "None", "none", "-"}
# Placeholders that carry no licence information.
LICENSE_PLACEHOLDERS = {"Other (specify in notes)"}
# Old country values that are not ISO country names in UN M49.
GEOGRAPHY_ALIASES = {"Global": "global", "Laos": "LAO", "Vietnam": "VNM", "Latin America and the Caribbean": "m49:419"}
NOT_LANDSCAPES = {"NATIONAL", "GLOBAL"}
DROPPED = ("migration_status", "current_location", "server_path", "last_updated")


class Notes:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []

    def add(self, rid: str, field: str, note: str) -> None:
        self.rows.append((rid, field, note))


def vocab(name: str) -> list[dict[str, Any]]:
    data: list[dict[str, Any]] = json.loads((VOCAB / f"{name}.json").read_text(encoding="utf-8"))["concepts"]
    return data


THEME_BY_LABEL = {c["legacy_label"]: c["id"] for c in vocab("themes") if "legacy_label" in c}
LANDSCAPES = {c["id"] for c in vocab("landscapes")}
GEO_BY_LABEL = {c["label"]: c["id"] for c in vocab("geography")}


# -- old repository (read only) ----------------------------------------------------------------
def git(source: Path, *args: str) -> str:
    res = subprocess.run(["git", "-C", str(source), *args], capture_output=True, text=True, check=True)  # noqa: S603, S607
    return res.stdout


def old_records(source: Path, ref: str) -> list[tuple[str, dict[str, Any]]]:
    names = [
        n for n in git(source, "ls-tree", "--name-only", ref, "records/").split() if re.search(r"MFL-.*\.ya?ml$", n)
    ]
    return [(n, yaml.safe_load(git(source, "show", f"{ref}:{n}"))) for n in sorted(names)]


def history_dates(source: Path, ref: str, path: str) -> tuple[str | None, str | None]:
    dates = git(source, "log", "--follow", "--format=%as", ref, "--", path).split()
    return (dates[-1], dates[0]) if dates else (None, None)


# -- field conversions ---------------------------------------------------------------------------
def clean(v: Any) -> Any:
    if isinstance(v, str):
        v = v.replace("\xa0", " ").strip()
        return v or None
    return v


def to_geography(country: str | None, rid: str, notes: Notes) -> list[str] | None:
    if not country:
        return None
    code = GEOGRAPHY_ALIASES.get(country) or GEO_BY_LABEL.get(country) or GEO_BY_LABEL.get(country.replace("'", "’"))
    if code is None:
        notes.add(rid, "geography", f"country {country!r} not found in vocab/geography.json")
        return None
    return [code]


def to_license(text: str | None, rid: str, notes: Notes) -> dict[str, Any]:
    if not text or text in LICENSE_PLACEHOLDERS:
        if text:
            notes.add(rid, "license", f"old value {text!r} is a placeholder with no licence terms")
        return {"spdx": None, "url": None, "text": None}
    spdx = SPDX.get(text)
    url = f"https://spdx.org/licenses/{spdx}.html" if spdx else None
    if not spdx:
        found = URL_RE.findall(text)
        url = found[0].rstrip(".,;") if found else None
        if text.lower().startswith("restricted"):
            notes.add(
                rid, "license", "the licence text describes access, not licence terms: confirm the terms with the owner"
            )
    return {"spdx": spdx, "url": url, "text": None if spdx else text}


def to_contacts(contact: str | None, source: str | None) -> list[dict[str, Any]] | None:
    out: list[dict[str, Any]] = []
    if source:
        out.append({"organization": source, "roles": ["producer"]})
    for line in (contact or "").splitlines():
        line = line.strip()
        if not line:
            continue
        email = EMAIL_RE.search(line)
        if not email:
            out.append({"organization": line, "roles": ["point-of-contact"]})
            continue
        name = clean(re.sub(r"[\s(),\-–]+$", "", line[: email.start()]).strip(" (,-–"))
        entry: dict[str, Any] = {"name": name} if name else {}
        entry["email"] = email.group(0)
        entry["roles"] = ["point-of-contact"]
        out.append(entry)
    return out or None


def to_temporal(text: str | None) -> dict[str, Any] | None:
    if not text or text in PLACEHOLDERS:
        return None
    years = re.findall(YEAR, text)
    open_end = bool(re.search(r"present|présent|current", text, re.IGNORECASE))
    temporal: dict[str, Any] = {}
    if re.match(r"^\s*till\s+" + YEAR, text, re.IGNORECASE):
        temporal = {"end": years[0]}
    elif years:
        temporal = {"start": years[0], "end": None if open_end else years[-1]}
    temporal["text"] = text
    return temporal


def to_resolution(text: str | None) -> dict[str, Any] | None:
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*m(?:\s*\(original dataset\))?\s*", text or "")
    return {"value": float(m.group(1)) if "." in m.group(1) else int(m.group(1)), "unit": "m"} if m else None


def style_links(old: dict[str, Any]) -> list[dict[str, Any]]:
    """Style files linked in download_url become related resources, not access points."""
    raw = clean(old.get("download_url")) or ""
    return [
        {
            "relation": "IsSupplementedBy",
            "scheme": "url",
            "value": u,
            "title": "GIS style file (symbology), not the data",
        }
        for u in (x.rstrip(".,;") for x in URL_RE.findall(raw))
        if STYLE_EXT.search(urlparse(u).path)
    ]


def to_data(old: dict[str, Any], access: str | None, rid: str, notes: Notes) -> tuple[list[dict[str, Any]], str | None]:
    raw = clean(old.get("download_url")) or ""
    kind = KIND.get(old.get("data_type") or "")
    if old.get("data_type") == "Mixed":
        notes.add(rid, "data", "schema-1 data_type 'Mixed': access points marked kind mixed; describe or split them")
    points: list[dict[str, Any]] = []
    styles = 0
    for url in URL_RE.findall(raw):
        url = url.rstrip(".,;")
        if STYLE_EXT.search(urlparse(url).path):
            styles += 1
            continue
        is_file = bool(FILE_EXT.search(urlparse(url).path))
        host = urlparse(url).netloc
        point: dict[str, Any] = {
            "name": f"Download from {host}" if is_file else f"Page at {host}",
            "kind": kind or "other",
            "method": "download" if is_file else "landing_page",
            "url": url,
        }
        points.append(point)
    rest = URL_RE.sub("", raw).strip(" \n()-:,;")
    access_note = None
    if rest and not points:
        if access in ("restricted", "internal"):
            access_note = raw  # e.g. "Internal Available on Request": how the data is obtained
        else:
            notes.add(rid, "data", f"download text without a URL on a public record: {raw!r}")
    elif rest:
        notes.add(rid, "data", f"download field mixes links and text, text not migrated: {rest!r}")
    if len(points) > 1:
        notes.add(rid, "data", f"{len(points)} links in one field: check names and which is primary")
    if styles and not points and access == "public":
        notes.add(rid, "data", f"only {styles} style file link(s), no link to the data: add how to get the data")
        # Kind is known from schema 1; how to reach the data is not, so method and url stay empty.
        points.append({"name": "Data (access not stated in the schema-1 record)", "kind": kind or "other"})
    if not points and access in ("restricted", "internal"):
        points.append(
            {
                "name": "Data held by the owner (on request)",
                "kind": kind or "other",
                "method": "request",
                "access": access,
            }
        )
    if points:
        first = points[0]
        if old.get("file_names"):
            first["files"] = clean(str(old["file_names"]))
        if old.get("file_size"):
            first["size"] = clean(str(old["file_size"]))
        res = to_resolution(old.get("spatial_resolution"))
        if res and first.get("kind") == "raster":
            first["raster"] = {"resolution": res}
    if old.get("gee_asset_id"):
        # The asset is not public yet, so no URL is published (decision of 2026-09-29: the Earth Engine
        # URL is added once the asset is public). The asset id is kept in the description.
        points.append(
            {
                "name": "Earth Engine asset (MOSAIC project)",
                "kind": kind or "other",
                "method": "service",
                "description": f"Earth Engine asset {old['gee_asset_id']}; not public yet.",
                "access": "internal",
                "service": {"service_type": "earth-engine", "auth_required": True},
            }
        )
    return points, access_note


def migrate(old: dict[str, Any], dates: tuple[str | None, str | None], notes: Notes) -> dict[str, Any]:
    old = {k: clean(v) for k, v in old.items()}
    rid = str(old["id"])
    access = ACCESS.get(old.get("access_level") or "")
    if old.get("access_level") and not access:
        notes.add(rid, "access", f"unknown access level {old['access_level']!r}")
    data, access_note = to_data(old, access, rid, notes)
    theme = THEME_BY_LABEL.get(old.get("theme") or "")
    if old.get("theme") and not theme:
        notes.add(rid, "themes", f"theme {old['theme']!r} not in vocab/themes.json")
    rec: dict[str, Any] = {
        "id": rid,
        "title": old.get("title"),
        "description": old.get("description"),
        "resource_type": "dataset",
        "themes": [theme] if theme else None,
        "geography": to_geography(old.get("country"), rid, notes),
        "license": to_license(old.get("license"), rid, notes),
        "contacts": to_contacts(old.get("contact"), old.get("source")),
        "citation": old.get("citation"),
        "doi": re.sub(r"^https?://(dx\.)?doi\.org/", "", old["doi"]) if old.get("doi") else None,
        "access": access,
        "access_note": access_note,
        "processing_status": (old.get("processing_status") or "").lower() or None,
        "data": data or None,
        "related": style_links(old) or None,
        "temporal": to_temporal(old.get("temporal_coverage")),
        "spatial": None,
        "update_frequency": FREQUENCY.get(old.get("update_frequency") or ""),
        "source_updated": None,
        "created": old.get("date_registered") or dates[0],
        "updated": dates[1],
    }
    sr = old.get("spatial_resolution")
    if sr and sr not in PLACEHOLDERS:
        res = to_resolution(sr)
        rec["spatial"] = {"resolution": res if res else {"text": sr}}
    if isinstance(old.get("bbox"), dict):
        b = old["bbox"]
        rec["spatial"] = {**(rec["spatial"] or {}), "bbox": [b["xmin"], b["ymin"], b["xmax"], b["ymax"]]}
    if old.get("crs") and re.fullmatch(r"(EPSG|ESRI|OGC):[A-Za-z0-9.]+", str(old["crs"])):
        rec["spatial"] = {**(rec["spatial"] or {}), "crs": old["crs"]}
    if old.get("update_frequency") and not rec["update_frequency"]:
        notes.add(rid, "update_frequency", f"value {old['update_frequency']!r} not in the vocabulary")
    tc = old.get("temporal_coverage")
    if tc and tc not in PLACEHOLDERS and not (rec["temporal"] or {}).keys() - {"text"}:
        notes.add(rid, "temporal", f"period {old['temporal_coverage']!r} has no year: kept as text only")
    mosaic: dict[str, Any] = {"intake": {"status": "published"}}
    if old.get("date_registered"):
        mosaic["intake"]["submitted_on"] = old["date_registered"]
    ls = old.get("living_landscape")
    if ls in LANDSCAPES:
        mosaic = {"landscapes": [ls], **mosaic}
    elif ls:
        notes.add(rid, "mosaic.landscapes", f"schema-1 value {ls!r} is not a living landscape: left out")
    rec["mosaic"] = mosaic
    if old.get("id") in ("MFL-2026-053", "MFL-2026-070"):
        notes.add(rid, "resource_type", "set to dataset as in schema 1; the title suggests a document: confirm")
    lu = str(old["last_updated"]) if old.get("last_updated") else None
    if lu and re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?", lu):
        rec["source_updated"] = lu
    elif lu and lu not in PLACEHOLDERS:
        notes.add(rid, "source_updated", f"schema-1 last_updated {lu!r} is not a date: not migrated")
    return {k: v for k, v in rec.items() if v not in (None, [], {})}


# -- output ----------------------------------------------------------------------------------------
HEADER = (
    "# MOSAIC record (standard v0.2). Migrated from the schema-1 record {src} on {ref} by\n"
    "# scripts/migrate_schema1.py. Fields the old record did not have are absent: see review/.\n"
)


class _Dumper(yaml.SafeDumper):
    pass


def _str_presenter(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
    style = ">" if len(value) > 90 and "\n" not in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


_Dumper.add_representer(str, _str_presenter)


def dump(rec: dict[str, Any]) -> str:
    return yaml.dump(rec, Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=100)


def write_notes(notes: Notes, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(notes.rows)
    with path.with_suffix(".csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["record", "field", "note", "decision"])
        w.writerows([(*r, "") for r in rows])
    md = [
        "# Migration notes (schema 1 -> v0.2)",
        "",
        f"{len({r[0] for r in rows})} records, {len(rows)} notes. Things a person should look at; "
        "they do not make a record incomplete. Missing minimum fields are in minimum_gaps.md.",
        "",
        "| Record | Field | Note |",
        "|---|---|---|",
    ]
    md += [f"| {r} | `{f}` | {n.replace('|', '/')} |" for r, f, n in rows]
    path.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", type=Path, required=True, help="path to the old catalog repo (read only)")
    ap.add_argument("--ref", default="main", help="git ref to read (default: main)")
    ap.add_argument("--out", type=Path, required=True, help="records folder of the catalogue checkout")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    notes = Notes()
    written = 0
    for path, old in old_records(args.source, args.ref):
        rec = migrate(old, history_dates(args.source, args.ref, path), notes)
        rec, v02_notes = convert(rec)
        for f, n in v02_notes:
            notes.add(rec["id"], f, n)
        if not args.dry_run:
            folder = args.out / rec["id"]
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "record.yaml").write_text(HEADER.format(src=path, ref=args.ref) + dump(rec), encoding="utf-8")
        written += 1
    if not args.dry_run:
        write_notes(notes, ROOT / "review" / "migration_notes")
    print(f"{written} records migrated from {args.source} @ {args.ref}; {len(notes.rows)} migration notes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
