"""Shared helpers of the mosaic-landscape-profile scripts.

The scripts work on two checkouts:

- the MOSAIC standard (MOSAIC-mfl/mosaic-standard): schemas, vocabularies, the validator
  (``python -m mosaic_catalog``) and this skill;
- the MOSAIC catalogue (MOSAIC-mfl/catalog): ``records/`` and ``landscapes/<CODE>/``.

``setup.py`` writes their paths to ``~/.mosaic/workspace.json``; every script reads it, and
``--standard`` / ``--catalog`` override it. Files the scripts produce for the person (inventory,
data check, preview, pull request text) go to ``<workspace>/work/<CODE>/``, never into the repos.
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any
from urllib.parse import quote

import yaml

CONFIG = Path(os.environ.get("MOSAIC_WORKSPACE_FILE", Path.home() / ".mosaic" / "workspace.json"))
PROFILE_FILES = ("profile.yaml", "explorer.yaml", "story.yaml", "studies.yaml", "sources.yaml")
TODO = "TODO"


class Workspace:
    def __init__(self, standard: Path, catalog: Path, work: Path, base: str = "metadata-standard-v0.1") -> None:
        self.standard = standard
        self.catalog = catalog
        self.work = work
        self.base = base  # the catalogue branch pull requests go to (setup.py)

    def landscape_dir(self, code: str) -> Path:
        return self.catalog / "landscapes" / code

    def work_dir(self, code: str) -> Path:
        d = self.work / code
        d.mkdir(parents=True, exist_ok=True)
        return d

    def vocab(self) -> dict[str, dict[str, Any]]:
        """The living landscapes of the standard: code -> {label, countries, bbox}."""
        data = json.loads((self.standard / "vocab" / "landscapes.json").read_text(encoding="utf-8"))
        return {c["id"]: c for c in data["concepts"]}


def add_workspace_args(ap: ArgumentParser) -> None:
    ap.add_argument("--standard", type=Path, help="checkout of mosaic-standard (default: from setup.py)")
    ap.add_argument("--catalog", type=Path, help="checkout of the catalogue (default: from setup.py)")
    ap.add_argument("--work", type=Path, help="folder for the files made for you (default: <workspace>/work)")


def workspace(args: Namespace) -> Workspace:
    saved: dict[str, str] = {}
    if CONFIG.exists():
        saved = json.loads(CONFIG.read_text(encoding="utf-8"))
    standard = args.standard or (Path(saved["standard"]) if saved.get("standard") else None)
    catalog = args.catalog or (Path(saved["catalog"]) if saved.get("catalog") else None)
    if not standard or not catalog:
        sys.exit("No workspace yet: run scripts/setup.py first (or pass --standard and --catalog).")
    work = args.work or Path(saved.get("work") or (Path(catalog).resolve().parent / "work"))
    ws = Workspace(
        Path(standard).resolve(),
        Path(catalog).resolve(),
        Path(work).resolve(),
        saved.get("base") or "metadata-standard-v0.1",
    )
    if not (ws.catalog / "records").is_dir():
        sys.exit(f"{ws.catalog} is not a catalogue checkout (no records/ folder).")
    if not (ws.standard / "schema" / "landscape").is_dir():
        sys.exit(f"{ws.standard} is not a mosaic-standard checkout (no schema/landscape/ folder).")
    return ws


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else None


def dump_yaml(data: Any) -> str:
    """Same layout as the profiles already in the catalogue."""
    try:
        from mosaic_catalog.yamlio import dump

        return dump(data)
    except ImportError:  # the standard is not installed yet: plain PyYAML
        return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100)


def write_yaml(path: Path, data: Any, header: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    head = "".join(f"# {line}\n" if line else "#\n" for line in header.splitlines())
    path.write_text(head + dump_yaml(data), encoding="utf-8")


def load_profile(folder: Path) -> dict[str, Any]:
    """profile.yaml and the explorer files it names (keys: profile, explorer, story, studies, sources)."""
    out: dict[str, Any] = {"profile": load_yaml(folder / "profile.yaml") or {}}
    for sec in out["profile"].get("sections") or []:
        if sec.get("kind") == "map-explorer" and sec.get("source"):
            explorer = load_yaml(folder / sec["source"]) or {}
            out["explorer"] = explorer
            for key in ("story", "studies"):
                ref = explorer.get(key) or {}
                if ref.get("file"):
                    out[key] = load_yaml(folder / ref["file"])
            about = explorer.get("about") or {}
            if about.get("sources"):
                out["sources"] = load_yaml(folder / about["sources"])
    return out


def todos(node: Any, path: str = "") -> list[str]:
    """Paths of every value that still says TODO (placeholders the person must fill in)."""
    found: list[str] = []
    if isinstance(node, dict):
        for k, v in node.items():
            found += todos(v, f"{path}.{k}" if path else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            found += todos(v, f"{path}[{i}]")
    elif isinstance(node, str) and TODO in node:
        found.append(path)
    return found


def camera_for_bbox(bbox: list[float]) -> dict[str, Any]:
    """Map centre, zoom and limits that frame a landscape's bbox [w, s, e, n] (about 1000 px wide)."""
    w, s, e, n = bbox
    lng, lat = (w + e) / 2, (s + n) / 2

    def merc(y: float) -> float:
        return math.log(math.tan(math.pi / 4 + math.radians(y) / 2))

    dx = max(e - w, 0.01) / 360
    dy = max(abs(merc(n) - merc(s)), 0.0002) / (2 * math.pi)
    zoom = math.log2(min(900 / 512 / dx, 650 / 512 / dy))
    zoom = round(min(max(zoom, 3.0), 13.0), 2)
    pad_x, pad_y = max(e - w, 0.2), max(n - s, 0.2)
    return {
        "center": [round(lng, 4), round(lat, 4)],
        "zoom": zoom,
        "min_zoom": round(max(zoom - 1, 2.0), 2),
        "max_bounds": [
            [round(w - pad_x, 3), round(max(s - pad_y, -85), 3)],
            [round(e + pad_x, 3), round(min(n + pad_y, 85), 3)],
        ],
    }


# ---- where each data file is served (same rules as the website's AssetRouter) -----------------------
class AssetRouter:
    def __init__(self, data: dict[str, Any]) -> None:
        self.roots: dict[str, str] = data.get("roots") or {}
        self.default_root: str = data.get("default_root") or ""
        self.routes: list[dict[str, str]] = data.get("routes") or []
        self.withheld: set[str] = set(data.get("withheld") or [])

    def root(self, path: str) -> str:
        for r in self.routes:
            if (r.get("prefix") and path.startswith(r["prefix"])) or r.get("path") == path:
                return self.roots.get(r["root"], "")
        return self.roots.get(self.default_root, "")

    def url(self, path: str) -> str:
        return self.root(path) + "/".join(quote(p) for p in path.split("/"))


DATA_FILE = re.compile(r"^[\w .{}/-]+\.(pmtiles|tif|tiff|json|geojson|bin|pbf|png|jpe?g|webp|csv)$", re.I)
GRID_FILES = ("app_meta.json", "landmask.tif", "normals.tif")
GRID_RELATIVE = ("cells", "stack", "qc")


def assets(explorer: dict[str, Any], extra: tuple[Any, ...] = ()) -> list[str]:
    """Every data file an explorer (and its story) reads: relative paths, deduplicated, in order."""
    found: list[str] = []

    def add(p: str) -> None:
        if p not in found:
            found.append(p)

    def walk(node: Any, key: str = "") -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "grid" and isinstance(v, str):
                    for f in GRID_FILES:
                        add(v + f)
                walk(v, k)
        elif isinstance(node, list):
            for v in node:
                walk(v, key)
        elif key in GRID_RELATIVE:
            return  # named relative to the overlay's grid folder: added below
        elif isinstance(node, str) and DATA_FILE.match(node) and not node.startswith(("http", "/")):
            if "{fontstack}" in node:
                add(node.replace("{fontstack}", "Noto Sans Regular").replace("{range}", "0-255"))
            elif "{" not in node:
                add(node)

    walk(explorer)
    for doc in extra:
        walk(doc)
    for o in explorer.get("overlays") or []:  # files named relative to a grid folder (stack, cells, qc, variables)
        g = o.get("grid")
        if not g:
            continue
        for k in ("stack", "cells", "qc"):
            if isinstance(o.get(k), str):
                add(g + o[k])
        for v in o.get("variables") or []:
            if v.get("cells"):
                add(g + v["cells"])
    return found


def md_table(rows: list[list[str]], header: list[str]) -> str:
    def cell(x: str) -> str:
        return str(x).replace("|", "\\|").replace("\n", " ")

    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return "\n".join(out)
