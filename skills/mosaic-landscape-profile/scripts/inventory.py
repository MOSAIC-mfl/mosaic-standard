"""List the layers of an existing map explorer and suggest how each one becomes part of a profile.

    python inventory.py --source D:/Code/Mosaic/mosaic-ucayali --code PER-PCL
    python inventory.py --layers path/to/layers.json --code SEN-FK

Reads the explorer's own files (read only): data/meta/layers.json, and if present
data/meta/story_chapters.json and data/meta/studies.json, plus site/js/config.js for where the data
is served. Writes <work>/<CODE>/inventory.md and inventory.json: one row per layer with its type,
files, licence and the suggested website module (references/modules.md). The suggestion is a
starting point to discuss with the person, not a decision.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import add_workspace_args, md_table, workspace

BASE_IDS = {"terrain", "s2_rgb", "osm_labels", "admin_boundaries", "department", "basin", "rivers"}


def files_of(urls: Any) -> list[str]:
    out: list[str] = []
    if isinstance(urls, str):
        out.append(urls)
    elif isinstance(urls, dict):
        for v in urls.values():
            out += files_of(v)
    elif isinstance(urls, list):
        for v in urls:
            out += files_of(v)
    return out


def suggest(layer: dict[str, Any]) -> tuple[str, str, str]:
    """(role, module, click) for one layer of an explorer's layers.json."""
    lid, typ = layer.get("id", ""), str(layer.get("type", ""))
    urls = layer.get("urls") or {}
    yearly = any(isinstance(v, dict) and v and all(re.fullmatch(r"\d{4}", str(k)) for k in v) for v in urls.values())
    yearly = yearly or bool(layer.get("years"))
    has_query = any(k in urls for k in ("query", "query_cog"))
    classes = bool(layer.get("classes"))
    if typ == "raster-dem" or lid == "terrain":
        return "base map", "map.sources (raster-dem) + map.terrain", "—"
    if lid in ("s2_rgb",) or (typ == "raster" and set(urls) == {"pmtiles"} and not has_query and "s2" in lid):
        return "base map", "map.sources (raster imagery)", "—"
    if lid in BASE_IDS or (
        typ == "vector" and any(k in urls for k in ("boundary", "mask", "labels", "adm1", "provinces"))
    ):
        return (
            "base map / toggle",
            "map.sources + map.layers (+ a toggle)",
            "click.admin (place names)" if "admin" in lid else "—",
        )
    if typ in ("climate",):
        return "overlay", "climate-grid", "built in (cell series)"
    if typ in ("climate-monthly",) or "spi" in lid:
        return "overlay", "index-grid", "built in (cell series)"
    if typ == "timeseries-point":
        return "panel", "panels: series-summary (open_on_click)", "—"
    if typ == "vector":
        return "overlay", "style-layers (fill/line/circle)", "feature-attributes"
    if "footprints" in urls:
        return "overlay", "style-layers (raster grid + vector points)", "combined (feature-attributes + value-at-point)"
    if yearly:
        click = (
            "class-at-point (band_per_year)"
            if classes and has_query
            else "annual-series"
            if "series" in urls or layer.get("id") in ("fire", "burned_area")
            else "—"
        )
        return "overlay", "year-tiles" + (" + points" if "points" in urls else ""), click
    click = (
        "class-at-point"
        if classes and has_query
        else "value-at-point"
        if has_query
        else "series-values / annual-series"
        if "series" in urls
        else "—"
    )
    return (
        "overlay",
        "raster-tiles" + (" (variants)" if len([v for v in urls.values() if str(v).endswith(".pmtiles")]) > 1 else ""),
        click,
    )


def data_roots(source: Path) -> dict[str, Any]:
    """Where the explorer serves its files, read from site/js/config.js when it has one."""
    cfg = source / "site" / "js" / "config.js"
    if not cfg.exists():
        return {}
    text = cfg.read_text(encoding="utf-8", errors="replace")
    hf = re.search(r"https://huggingface\.co/datasets/[^\"'`]+", text)
    site_list = re.search(r"SITE\s*=\s*\[([^\]]*)\]", text, re.S)
    return {
        "hugging_face": hf.group(0) if hf else None,
        "site_files": re.findall(r"[\"']([^\"']+)[\"']", site_list.group(1)) if site_list else [],
        "note": "SITE files are served by the explorer's GitHub Pages (<pages url>/data/), the rest by Hugging Face",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--source", type=Path, help="checkout of the explorer (read only)")
    src.add_argument("--layers", type=Path, help="a layers.json file")
    ap.add_argument("--code", required=True, help="landscape code the profile is for")
    add_workspace_args(ap)
    args = ap.parse_args(argv)
    ws = workspace(args)
    layers_file = args.layers or args.source / "data" / "meta" / "layers.json"
    if not layers_file.exists():
        print(
            f"No layers.json at {layers_file}. Ask the person for the list of layers instead (references/recipes.md)."
        )
        return 2
    reg = json.loads(layers_file.read_text(encoding="utf-8"))
    layers = reg.get("layers", reg) if isinstance(reg, dict) else reg
    rows, out = [], []
    for layer in layers:
        role, module, click = suggest(layer)
        files = files_of(layer.get("urls"))
        item = {
            "id": layer.get("id"),
            "title": layer.get("title"),
            "type": layer.get("type"),
            "role": role,
            "module": module,
            "click": click,
            "files": files,
            "years": layer.get("years"),
            "licence": layer.get("licence"),
            "source": layer.get("source"),
            "period": layer.get("period"),
        }
        out.append(item)
        rows.append(
            [
                str(item["id"]),
                str(item["title"] or ""),
                str(item["type"] or ""),
                module,
                click,
                str(len(files)),
                str(item["licence"] or "TODO")[:60],
            ]
        )
    meta = args.source / "data" / "meta" if args.source else layers_file.parent
    story = meta / "story_chapters.json"
    studies = meta / "studies.json"
    extras = {
        "story_chapters": len(json.loads(story.read_text(encoding="utf-8")).get("chapters", []))
        if story.exists()
        else 0,
        "study_cards": len(json.loads(studies.read_text(encoding="utf-8")).get("stories", []))
        if studies.exists()
        else 0,
        "data": data_roots(args.source) if args.source else {},
    }
    work = ws.work_dir(args.code.upper())
    (work / "inventory.json").write_text(
        json.dumps({"layers": out, **extras}, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    md = [
        f"# Inventory for {args.code.upper()} (from {layers_file})",
        "",
        md_table(rows, ["id", "title", "type", "suggested module", "click", "files", "licence"]),
        "",
        f"Story chapters: {extras['story_chapters']} · study cards: {extras['study_cards']}",
    ]
    if extras["data"]:
        md += [
            "",
            f"Data: Hugging Face {extras['data']['hugging_face']}; "
            f"GitHub Pages: {', '.join(extras['data']['site_files'])}",
        ]
    (work / "inventory.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\nSaved: {work / 'inventory.md'} and inventory.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
