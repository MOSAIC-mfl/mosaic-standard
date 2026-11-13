#!/usr/bin/env python3
"""Add the file format (data[].media_type, standard v0.2) to the records migrated from schema 1.

The schema-1 records (catalog repo @ <ref>, records/<id>.yaml) named their files (`file_names`), and
the first website showed the format read from the file extension (.tif -> GeoTIFF, .shp ->
Shapefile, .csv -> CSV, ...). The migration kept the file names in the data entry's description but
not the format; this script adds it as `media_type` to the data entries that have none.

Only extensions count: the first pipeline also guessed a format from the data type when there were
no file names (Raster -> GeoTIFF, Tabular -> CSV); those guesses are not copied. A record whose files
have several formats gets one per data entry when the entry's own link or description names the
file; a format with no media type here (e.g. DSSAT .SOL) is left out and listed.

    python3 scripts/recover_formats.py --catalog ../catalog [--ref 9abbfc6] [--check]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from itertools import pairwise
from pathlib import Path

import yaml

EXT_RE = re.compile(r"\.([A-Za-z0-9]{1,7})(?=[\s,;)'\"]|$)")
# extension -> IANA media type (the first pipeline's EXT_MAP, with the media types of its STAC build)
MEDIA_TYPE = {
    "tif": "image/tiff; application=geotiff",
    "tiff": "image/tiff; application=geotiff",
    "shp": "application/x-esri-shapefile",
    "gpkg": "application/geopackage+sqlite3",
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xls": "application/vnd.ms-excel",
    "nc": "application/x-netcdf",
    "geojson": "application/geo+json",
    "json": "application/json",
    "parquet": "application/vnd.apache.parquet",
    "zip": "application/zip",
}


def old_formats(catalog: Path, ref: str, rid: str) -> list[str]:
    cmd = ["git", "-C", str(catalog), "show", f"{ref}:records/{rid}.yaml"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)  # noqa: S603
    if res.returncode != 0:
        return []
    names = str((yaml.safe_load(res.stdout) or {}).get("file_names") or "")
    return [e.lower() for e in EXT_RE.findall(names)]


def entry_type(block: str, types: list[str]) -> str | None:
    """The media type of one data entry: from its own link or description, else the record's only one."""
    own = sorted({MEDIA_TYPE[e.lower()] for e in EXT_RE.findall(block) if e.lower() in MEDIA_TYPE})
    if len(own) == 1:
        return own[0]
    return types[0] if len(types) == 1 else None


def add_media_types(text: str, types: list[str]) -> tuple[str, int]:
    """Add `media_type` to each entry of the top-level `data:` list that has none (keeps the file as it is)."""
    lines = text.splitlines(keepends=True)
    start = next((i for i, x in enumerate(lines) if x.startswith("data:")), None)
    if start is None:
        return text, 0
    end = start + 1
    while end < len(lines) and (lines[end].startswith((" ", "-")) or not lines[end].strip()):
        end += 1
    entries = [i for i in range(start + 1, end) if lines[i].startswith("- ")] + [end]
    out, n = lines[: start + 1], 0
    for a, b in pairwise(entries):
        block = lines[a:b]
        mt = entry_type("".join(block), types)
        if mt and not any(x.startswith("  media_type:") for x in block):
            at = next((k for k, x in enumerate(block) if x.startswith("  kind:")), len(block) - 1)
            block = [*block[: at + 1], f"  media_type: '{mt}'\n", *block[at + 1 :]]
            n += 1
        out.extend(block)
    out.extend(lines[end:])
    return "".join(out), n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--ref", default="9abbfc6", help="last commit of the first pipeline (default 9abbfc6)")
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    args = ap.parse_args(argv)
    added, skipped = [], []
    for path in sorted((args.catalog / "records").glob("*/record.yaml")):
        text = path.read_text(encoding="utf-8")
        rec = yaml.safe_load(text) or {}
        exts = old_formats(args.catalog, args.ref, str(rec.get("id")))
        if not exts:
            continue
        unknown = sorted({e for e in exts if e not in MEDIA_TYPE})
        if unknown:
            skipped.append(f"{rec.get('id')} (.{', .'.join(unknown)})")
        types = sorted({MEDIA_TYPE[e] for e in exts if e in MEDIA_TYPE})
        if not types:
            continue
        new_text, n = add_media_types(text, types)
        if n:
            if not args.check:
                path.write_text(new_text, encoding="utf-8")
            added.append(str(rec.get("id")))
    print(f"{'would add' if args.check else 'added'} media_type to {len(added)} records")
    print(f"left as they are ({len(skipped)}): {', '.join(skipped) or '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
