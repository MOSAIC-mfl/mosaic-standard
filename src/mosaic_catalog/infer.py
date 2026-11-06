"""Fill classification fields by reading the data itself, when it can be read.

For each PUBLIC data entry with access_method ``download`` and a location, the file is fetched
(size and time limited) and inspected:

* zip with a Shapefile, GeoJSON, GeoPackage or CSV inside, or one of those files directly;
* vector -> ``data[].geometry_type``, ``feature_count``, ``spatial.crs`` and the attributes as the
  entry's data dictionary (``structures[]``: variables);
* table  -> ``feature_count`` (rows) and its columns, coordinate columns (x / y dimensions) or
  geometry column as the entry's data dictionary;
* geographic WGS84 data -> record ``spatial.bbox`` / ``spatial.crs`` when the record has none.

Rules (docs/standard.md, "authored values win"):

* a value written by a person is never replaced; when the file disagrees, it is reported;
* every value filled here is listed in the record's ``derived``;
* nothing is guessed: a format that cannot be read is reported and left alone.

Raster files are not read yet (they would need GDAL/rasterio); they are reported.
"""

from __future__ import annotations

import csv
import io
import json
import sqlite3
import tempfile
import urllib.request
import zipfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse

MAX_BYTES = 50 * 1024 * 1024
TIMEOUT_S = 30
LAT_NAMES = {"lat", "latitude", "lat_dd", "y_lat", "decimallatitude", "latitud"}
LON_NAMES = {"lon", "long", "lng", "longitude", "lon_dd", "x_lon", "decimallongitude", "longitud"}
GEOM_NAMES = {"wkt", "geometry", "geom", "the_geom", "wkb_geometry", "geojson"}

SHP_TYPES = {1: "point", 8: "point", 11: "point", 18: "point", 21: "point", 28: "point",
             3: "line", 13: "line", 23: "line", 5: "polygon", 15: "polygon", 25: "polygon", 31: "polygon"}  # fmt: skip
GEOJSON_TYPES = {"Point": "point", "MultiPoint": "point", "LineString": "line", "MultiLineString": "line",
                 "Polygon": "polygon", "MultiPolygon": "polygon"}  # fmt: skip
DBF_TYPES = {"C": "string", "N": "number", "F": "number", "L": "boolean", "D": "date"}


@dataclass
class Findings:
    """What a file says about itself: ``kind`` of data, values for the data entry (``point``, dot
    paths relative to data[i]), for its data dictionary (``structure``: variables, dimensions,
    geometry_column) and for the record (``record``)."""

    kind: str | None = None
    point: dict[str, Any] = field(default_factory=dict)
    structure: dict[str, Any] = field(default_factory=dict)
    record: dict[str, Any] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)


# -- readers (pure: path -> Findings) ---------------------------------------------------------------
def _merge_types(types: set[str]) -> str | None:
    if not types:
        return None
    return types.pop() if len(types) == 1 else "mixed"


def _is_wgs84(prj: str | None) -> bool:
    return bool(prj) and "PROJCS" not in prj and ("WGS_1984" in prj or "WGS 84" in prj)  # type: ignore[operator]


def read_shapefile(shp: Path) -> Findings:
    import shapefile  # pyshp; optional dependency (extra "infer")

    f = Findings(kind="vector")
    with shapefile.Reader(str(shp)) as r:
        gtype = SHP_TYPES.get(r.shapeType)
        if gtype is None:
            f.problems.append(f"shapefile geometry type {r.shapeTypeName} not classified")
        else:
            f.point["geometry_type"] = gtype
        f.point["feature_count"] = len(r)
        attrs = []
        for name, ftype, _size, decimals in r.fields[1:]:
            t = "integer" if ftype == "N" and decimals == 0 else DBF_TYPES.get(ftype, "other")
            attrs.append({"name": name, "data_type": t})
        if attrs:
            f.structure["variables"] = attrs
        prj = shp.with_suffix(".prj")
        wkt = prj.read_text(encoding="utf-8", errors="replace") if prj.exists() else None
        if _is_wgs84(wkt):
            f.point["spatial.crs"] = "EPSG:4326"
            f.record["spatial.crs"] = "EPSG:4326"
            f.record["spatial.bbox"] = [round(v, 6) for v in r.bbox]
        else:
            f.problems.append("CRS is not geographic WGS84 (or no .prj): CRS and bbox not derived")
    return f


def read_geojson(path: Path) -> Findings:
    f = Findings(kind="vector")
    data = json.loads(path.read_text(encoding="utf-8"))
    feats = data.get("features", []) if data.get("type") == "FeatureCollection" else [data]
    types: set[str] = set()
    xs: list[float] = []
    ys: list[float] = []

    def walk(c: Any) -> None:
        if isinstance(c, list) and c and isinstance(c[0], int | float):
            xs.append(float(c[0]))
            ys.append(float(c[1]))
        elif isinstance(c, list):
            for x in c:
                walk(x)

    for ft in feats:
        g = (ft or {}).get("geometry") or {}
        if g.get("type") in GEOJSON_TYPES:
            types.add(GEOJSON_TYPES[g["type"]])
        walk(g.get("coordinates"))
    gtype = _merge_types(types)
    if gtype:
        f.point["geometry_type"] = gtype
    f.point["feature_count"] = len(feats)
    f.point["spatial.crs"] = "EPSG:4326"  # RFC 7946
    if xs:
        f.record["spatial.crs"] = "EPSG:4326"
        f.record["spatial.bbox"] = [round(min(xs), 6), round(min(ys), 6), round(max(xs), 6), round(max(ys), 6)]
    return f


def read_geopackage(path: Path) -> Findings:
    f = Findings(kind="vector")
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        rows = con.execute(
            "SELECT g.geometry_type_name, s.organization, s.organization_coordsys_id "
            "FROM gpkg_geometry_columns g JOIN gpkg_spatial_ref_sys s ON g.srs_id = s.srs_id"
        ).fetchall()
    finally:
        con.close()
    names = {"POINT": "point", "MULTIPOINT": "point", "LINESTRING": "line", "MULTILINESTRING": "line",
             "POLYGON": "polygon", "MULTIPOLYGON": "polygon"}  # fmt: skip
    types = {names.get(str(r[0]).upper(), "mixed") for r in rows}
    gtype = _merge_types(types)
    if gtype:
        f.point["geometry_type"] = gtype
    crs = {f"{r[1]}:{r[2]}" for r in rows if r[1]}
    if len(crs) == 1:
        f.point["spatial.crs"] = crs.pop().upper()
    return f


def read_csv(path: Path) -> Findings:
    f = Findings(kind="tabular")
    raw = path.read_bytes()[:2_000_000].decode("utf-8-sig", errors="replace")
    try:
        dialect: Any = csv.Sniffer().sniff(raw.splitlines()[0] if raw else ",", delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.reader(io.StringIO(raw), dialect))
    if not rows:
        f.problems.append("empty table")
        return f
    header = [h.strip() for h in rows[0]]
    low = {h.lower(): h for h in header}
    lat = next((low[n] for n in low if n in LAT_NAMES), None)
    lon = next((low[n] for n in low if n in LON_NAMES), None)
    geom = next((low[n] for n in low if n in GEOM_NAMES), None)
    if lat and lon:
        # latitude / longitude columns are geographic coordinates, in degrees by definition
        f.structure["dimensions"] = [
            {"name": lon, "type": "x", "unit": "degree", "description": "Longitude column"},
            {"name": lat, "type": "y", "unit": "degree", "description": "Latitude column"},
        ]
    elif geom:
        f.structure["geometry_column"] = geom
    skip = {lat, lon, geom}
    variables = [{"name": h} for h in header if h and h not in skip]
    if variables:
        f.structure["variables"] = variables
    if len(raw) < 2_000_000:
        f.point["feature_count"] = max(len(rows) - 1, 0)
    return f


READERS: dict[str, Callable[[Path], Findings]] = {
    ".shp": read_shapefile, ".geojson": read_geojson, ".json": read_geojson,
    ".gpkg": read_geopackage, ".csv": read_csv, ".tsv": read_csv,
}  # fmt: skip
RASTER_EXT = {".tif", ".tiff", ".nc", ".zarr", ".img", ".asc"}


def inspect_file(path: Path) -> Findings:
    """Read a downloaded file (or a zip of files) and return what it says about itself."""
    if zipfile.is_zipfile(path):
        with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(path) as z:
            members = [m for m in z.namelist() if not m.endswith("/") and ".." not in PurePosixPath(m).parts]
            total = sum(z.getinfo(m).file_size for m in members)
            if total > 4 * MAX_BYTES:
                return Findings(problems=[f"zip expands to {total} bytes: not inspected"])
            for m in members:
                z.extract(m, tmp)
            files = [Path(tmp) / m for m in members]
            readable = [p for p in files if p.suffix.lower() in READERS]
            rasters = [p for p in files if p.suffix.lower() in RASTER_EXT]
            if len(readable) == 1 or (readable and all(p.suffix.lower() == ".shp" for p in readable[:1])):
                return READERS[readable[0].suffix.lower()](readable[0])
            if len(readable) > 1:
                return Findings(problems=[f"zip holds {len(readable)} data files: classify by hand"])
            if rasters:
                return Findings(problems=["raster inside zip: raster files are not read yet"])
            return Findings(problems=["no readable data file in the zip"])
    ext = path.suffix.lower()
    if ext in READERS:
        return READERS[ext](path)
    if ext in RASTER_EXT:
        return Findings(problems=["raster file: raster files are not read yet"])
    return Findings(problems=[f"format {ext or '(none)'} not readable"])


# -- fetching -------------------------------------------------------------------------------------
def fetch(url: str, dest_dir: Path) -> Path:
    """Download a public https file, refusing anything above MAX_BYTES."""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("only https URLs are fetched")
    name = PurePosixPath(parsed.path).name or "download"
    dest = dest_dir / name
    req = urllib.request.Request(url, headers={"User-Agent": "mosaic-catalog-infer/0.1"})  # noqa: S310 - https only
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp, dest.open("wb") as out:  # noqa: S310
        size = 0
        while chunk := resp.read(1 << 16):
            size += len(chunk)
            if size > MAX_BYTES:
                raise ValueError(f"file larger than {MAX_BYTES // (1024 * 1024)} MB: not inspected")
            out.write(chunk)
    return dest


# -- applying findings to a record ----------------------------------------------------------------
def _get(obj: dict[str, Any], dotted: str) -> Any:
    for part in dotted.split("."):
        if not isinstance(obj, dict) or part not in obj:
            return None
        obj = obj[part]
    return obj


def _set(obj: dict[str, Any], dotted: str, value: Any) -> None:
    *parents, last = dotted.split(".")
    for part in parents:
        obj = obj.setdefault(part, {})
    obj[last] = value


@dataclass
class Outcome:
    filled: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)


def apply(record: dict[str, Any], index: int, found: Findings) -> Outcome:
    """Fill absent values from ``found`` into data[index], its data dictionary and the record.
    Never overwrite a person's value; refresh a previous inference (listed in ``derived``)."""
    out = Outcome(problems=list(found.problems))
    point = record["data"][index]
    if found.kind and point.get("kind") not in (None, found.kind, "mixed"):
        out.conflicts.append(f"data[{index}].kind is {point.get('kind')!r} but the file holds {found.kind} data")
        return out
    derived = set(record.get("derived") or [])

    def fill(target: dict[str, Any], path: str, value: Any, mark: str, label: str) -> None:
        current = _get(target, path)
        if current is None:
            _set(target, path, value)
            derived.add(mark)
            out.filled.append(label)
        elif mark in derived:
            if current != value:  # a previous inference: refresh it
                _set(target, path, value)
                out.filled.append(label)
        elif current != value and not isinstance(value, list | dict):
            out.conflicts.append(f"{label}: record says {current!r}, the file says {value!r}")

    for path, value in found.point.items():
        fill(point, path, value, f"data[].{path}", f"data[{index}].{path}")
    if found.structure:
        name = str(point.get("name") or f"data {index + 1}")
        structures = record.setdefault("structures", [])
        st = next((s for s in structures if s.get("name") == name), None)
        if st is None:
            st = {"name": name}
            structures.append(st)
        for key, value in found.structure.items():
            fill(st, key, value, "structures", f"structures[{name}].{key}")
        point.setdefault("structures", [name])
    for path, value in found.record.items():
        fill(record, path, value, path, path)
    if derived:
        record["derived"] = sorted(derived)
    return out
