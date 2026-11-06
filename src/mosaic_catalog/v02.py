"""Convert a MOSAIC v0.1 record to the standard v0.2 (aligned with the Climate Data Hub core).

Only moves and renames what the record already says; nothing is invented. What cannot be carried
over as it is, is written down as a note (field, what happened) for review/.

Main changes (see docs/standard.md, "From v0.1 to v0.2"):

* geography, mosaic.landscapes, update_frequency -> spatial.geography, spatial.landscapes,
  temporal.update_frequency; temporal.start / end -> start_date / end_date;
* license {spdx, url, text} -> license (SPDX, or LicenseRef-source-terms) + license_text +
  additional_links (rel: license);
* contacts -> contact; citation as text -> citation.text; access internal -> non-public;
* data[]: method -> access_method, url -> locations[].url, size -> file_size; the raster / vector /
  tabular / service blocks -> geometry_type, feature_count, spatial.crs, service and one data
  dictionary (structures[]); data[].derived -> derived;
* dropped: slug, mosaic.intake (workflow state, kept in git), document.pages, tabular.spatial,
  service.auth_required, citation.version.
"""

from __future__ import annotations

import re
from typing import Any

VERSION = "0.2.0"
LICENSE_REF = "LicenseRef-source-terms"
FILE_SIZE = re.compile(r"^\d+(\.\d+)?\s?(B|KB|MB|GB|TB|PB)$")
SERVICE_TYPES = {"ogc-api-features": "ogc-api", "ogc-api-records": "ogc-api", "earth-engine": "gee", "rest": "other"}
FIELD_TYPES = {
    "string": "string",
    "integer": "integer",
    "number": "number",
    "boolean": "boolean",
    "date": "date",
    "datetime": "datetime",
    "other": "other",
}
DERIVED = {  # v0.1 path inside a data entry -> v0.2 path in the record
    "vector.attributes": "structures",
    "vector.crs": "data[].spatial.crs",
    "vector.feature_count": "data[].feature_count",
    "vector.geometry_type": "data[].geometry_type",
    "raster.crs": "data[].spatial.crs",
    "raster.resolution": "spatial.resolution",
    "raster.bands": "structures",
    "tabular.columns": "structures",
    "tabular.row_count": "data[].feature_count",
    "tabular.geometry_column": "structures",
    "tabular.coordinate_columns": "structures",
}
ORDER = [
    "schema_version",
    "id",
    "title",
    "description",
    "note",
    "resource_type",
    "version",
    "language",
    "themes",
    "keywords",
    "spatial",
    "temporal",
    "license",
    "license_text",
    "access",
    "access_note",
    "contact",
    "citation",
    "doi",
    "funding",
    "related_publications",
    "additional_links",
    "data",
    "structures",
    "derived",
    "created",
    "updated",
    "source_updated",
    "extensions",
]


def _access(v: Any) -> Any:
    return "non-public" if v == "internal" else v


def is_v02(rec: dict[str, Any]) -> bool:
    return "schema_version" in rec or "contact" in rec or isinstance(rec.get("license"), str)


def convert(old: dict[str, Any]) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    """(v0.2 record, notes). A record already in v0.2 is returned unchanged."""
    if is_v02(old):
        return dict(old), []
    notes: list[tuple[str, str]] = []
    rec: dict[str, Any] = {"schema_version": VERSION}
    for k in (
        "id",
        "title",
        "description",
        "note",
        "resource_type",
        "version",
        "language",
        "themes",
        "keywords",
        "access_note",
        "doi",
        "created",
        "updated",
        "source_updated",
        "extensions",
    ):
        if old.get(k) not in (None, "", [], {}):
            rec[k] = old[k]
    if old.get("slug"):
        notes.append(("slug", f"slug {old['slug']!r} dropped (not in v0.2; the id is the stable name)"))
    if old.get("access"):
        rec["access"] = _access(old["access"])

    # coverage
    spatial = dict(old.get("spatial") or {})
    if old.get("geography"):
        spatial["geography"] = old["geography"]
    mosaic = old.get("mosaic") or {}
    if mosaic.get("landscapes"):
        spatial["landscapes"] = mosaic["landscapes"]
    temporal: dict[str, Any] = {}
    t = old.get("temporal") or {}
    start, end = t.get("start"), t.get("end")
    if start and end and str(start) == str(end):
        temporal["date"] = str(start)
    else:
        if start:
            temporal["start_date"] = str(start)
        if "end" in t:
            temporal["end_date"] = None if end is None else str(end)
    if t.get("text"):
        temporal["text"] = t["text"]
    if old.get("update_frequency"):
        temporal["update_frequency"] = old["update_frequency"]

    # licence
    lic = old.get("license") or {}
    links: list[dict[str, Any]] = []
    if lic.get("spdx"):
        rec["license"] = lic["spdx"]
    elif lic.get("text") or lic.get("url"):
        rec["license"] = LICENSE_REF
        notes.append(
            (
                "license",
                f"no SPDX code: written as {LICENSE_REF} with the source's text/link; "
                "confirm whether an SPDX licence applies",
            )
        )
    if lic.get("text"):
        rec["license_text"] = lic["text"]
    if lic.get("url"):
        links.append({"rel": "license", "url": lic["url"]})

    # people and citation
    if old.get("contacts"):
        rec["contact"] = old["contacts"]
    cit = old.get("citation")
    if isinstance(cit, str):
        rec["citation"] = {"text": cit}
    elif isinstance(cit, dict):
        c = {k: v for k, v in cit.items() if k != "version"}
        if cit.get("version"):
            notes.append(
                ("citation", f"citation.version {cit['version']!r} dropped (the resource version is `version`)")
            )
        rec["citation"] = c
    if old.get("funding"):
        rec["funding"] = old["funding"]
    pubs: list[dict[str, Any]] = []
    for rel in old.get("related") or []:
        if rel.get("scheme") == "doi" and rel.get("relation") in (
            None,
            "IsDocumentedBy",
            "IsSupplementTo",
            "IsCitedBy",
            "References",
        ):
            pubs.append({"doi": rel["value"]})
        else:
            url = (
                rel["value"]
                if rel.get("scheme") in (None, "url")
                else f"https://doi.org/{rel['value']}"
                if rel.get("scheme") == "doi"
                else rel["value"]
            )
            link = {"rel": re.sub(r"(?<!^)(?=[A-Z])", "-", rel.get("relation") or "related").lower(), "url": url}
            if rel.get("title"):
                link["title"] = rel["title"]
            links.append(link)
    if pubs:
        rec["related_publications"] = pubs

    # data entries
    data: list[dict[str, Any]] = []
    structures: list[dict[str, Any]] = []
    derived: list[str] = list(old.get("derived") or [])
    for n, p in enumerate(old.get("data") or [], 1):
        d: dict[str, Any] = {}
        name = p.get("name") or f"data {n}"
        d["name"] = name
        desc = [p["description"]] if p.get("description") else []
        if p.get("url"):
            d["locations"] = [{"url": p["url"]}]
        if p.get("method"):
            d["access_method"] = p["method"]
        if p.get("kind"):
            d["kind"] = p["kind"]
        if p.get("access"):
            d["access"] = _access(p["access"])
        if p.get("media_type"):
            d["media_type"] = p["media_type"]
        if p.get("size"):
            size = str(p["size"]).strip()
            if FILE_SIZE.match(size):
                d["file_size"] = size
            else:
                desc.append(f"Size: {size}.")
        if p.get("files"):
            desc.append(f"Files: {p['files']}")
        dsp: dict[str, Any] = {}
        variables: list[dict[str, Any]] = []
        dims: list[dict[str, Any]] = []
        geometry_column = None
        r = p.get("raster") or {}
        if r.get("crs"):
            dsp["crs"] = r["crs"]
        if r.get("resolution"):
            if not spatial.get("resolution"):
                spatial["resolution"] = r["resolution"]
            elif spatial["resolution"] != r["resolution"]:
                notes.append(
                    (
                        "spatial.resolution",
                        f"{name}: resolution {r['resolution']} differs from the record's; kept the record's",
                    )
                )
        for b in r.get("bands") or []:
            variables.append(
                {k: v for k, v in b.items() if k in ("name", "description", "unit", "data_type", "nodata")}
            )
        v = p.get("vector") or {}
        if v.get("geometry_type"):
            d["geometry_type"] = v["geometry_type"]
        if v.get("feature_count") is not None:
            d["feature_count"] = v["feature_count"]
        if v.get("crs"):
            dsp["crs"] = v["crs"]
        for a in v.get("attributes") or []:
            if a.get("type") == "geometry":
                geometry_column = a["name"]
                continue
            var = {"name": a["name"]}
            if a.get("description"):
                var["description"] = a["description"]
            if a.get("type") in FIELD_TYPES:
                var["data_type"] = FIELD_TYPES[a["type"]]
            if a.get("unit"):
                var["unit"] = a["unit"]
            variables.append(var)
        tb = p.get("tabular") or {}
        if tb.get("row_count") is not None:
            d["feature_count"] = tb["row_count"]
        for col in tb.get("columns") or []:
            var = {"name": col["name"]}
            if col.get("description"):
                var["description"] = col["description"]
            if col.get("type") in FIELD_TYPES:
                var["data_type"] = FIELD_TYPES[col["type"]]
            if col.get("unit"):
                var["unit"] = col["unit"]
            variables.append(var)
        cc = tb.get("coordinate_columns") or {}
        unit = "degree" if str(cc.get("crs", "")).upper() in ("EPSG:4326", "OGC:CRS84") else None
        for axis in ("x", "y"):
            if cc.get(axis) and unit:
                dims.append(
                    {"name": cc[axis], "type": axis, "unit": unit, "description": f"{axis.upper()} coordinate column"}
                )
            elif cc.get(axis):
                notes.append(
                    ("data", f"{name}: coordinate column {cc[axis]!r} kept in the description (its unit is unknown)")
                )
                desc.append(f"{axis.upper()} coordinate column: {cc[axis]}.")
        if cc.get("crs"):
            dsp.setdefault("crs", cc["crs"])
        if tb.get("geometry_column"):
            geometry_column = tb["geometry_column"]
        if "spatial" in tb:
            notes.append(
                ("data", f"{name}: tabular.spatial dropped (deduced from geometry_column / coordinate columns)")
            )
        doc = p.get("document") or {}
        if doc.get("language") and not rec.get("language"):
            rec["language"] = [doc["language"]]
        sv = p.get("service") or {}
        if sv.get("service_type") or sv.get("layers"):
            s: dict[str, Any] = {}
            if sv.get("service_type"):
                s["type"] = SERVICE_TYPES.get(sv["service_type"], sv["service_type"])
            if sv.get("layers"):
                s["layers"] = sv["layers"]
            d["service"] = s
        if dsp:
            d["spatial"] = dsp
        if desc:
            d["description"] = " ".join(desc)
        if variables or dims or geometry_column:
            st: dict[str, Any] = {"name": name}
            if dims:
                st["dimensions"] = dims
            if variables:
                st["variables"] = variables
            if geometry_column:
                st["geometry_column"] = geometry_column
            structures.append(st)
            d["structures"] = [name]
        for path in p.get("derived") or []:
            tgt = DERIVED.get(path)
            if tgt and tgt not in derived:
                derived.append(tgt)
        data.append(d)
    if data:
        rec["data"] = data
    if structures:
        rec["structures"] = structures
    if links:
        rec["additional_links"] = links
    if spatial:
        rec["spatial"] = spatial
    if temporal:
        rec["temporal"] = temporal
    if derived:
        rec["derived"] = derived
    unknown = set(old) - {
        "id",
        "slug",
        "title",
        "description",
        "note",
        "resource_type",
        "version",
        "language",
        "themes",
        "keywords",
        "geography",
        "license",
        "contacts",
        "citation",
        "doi",
        "access",
        "access_note",
        "data",
        "temporal",
        "spatial",
        "update_frequency",
        "source_updated",
        "funding",
        "related",
        "created",
        "updated",
        "derived",
        "mosaic",
        "extensions",
    }
    for k in sorted(unknown):  # extension blocks travel as they are
        rec[k] = old[k]
    out = {k: rec[k] for k in ORDER if k in rec}
    out.update({k: v for k, v in rec.items() if k not in out})
    return out, notes
