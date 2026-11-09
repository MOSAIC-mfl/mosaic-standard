"""Start the profile of a landscape: landscapes/<CODE>/ in the catalogue.

    python new_profile.py --code SEN-FK --template default            # page without a map explorer
    python new_profile.py --code SEN-FK --template explorer           # empty map explorer to fill in
    python new_profile.py --code SEN-FK --template explorer --with-story --with-studies
    python new_profile.py --code SEN-FK --like PER-PCL                # same structure as an existing profile
    python new_profile.py --code SEN-FK --like PER-PCL --only landcover,precip,spi3

Values the person must provide are written as 'TODO: …' and listed in <work>/<CODE>/checklist.md;
validate.py reports any that remain. With --like, the layers keep the configuration of the profile
they come from (kinds, legends, clicks) but every data location points to a TODO root: replace it
with where the new landscape's files are served. The story and the studies are not copied (they are
about the other landscape).

The landscape code must exist in the standard's vocabulary (vocab/landscapes.json). A new code is a
change to mosaic-standard, not to the catalogue: see references/recipes.md, case E.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    add_workspace_args,
    camera_for_bbox,
    load_yaml,
    md_table,
    todos,
    workspace,
    write_yaml,
)

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
TODO_ROOT = "https://TODO.example.org/data/"


def header(what: str, code: str, origin: str) -> str:
    return (
        f"{what} of the {code} landscape profile (MOSAIC).\n"
        f"Started {origin} with the mosaic-landscape-profile skill.\n"
        f"Check: python -m mosaic_catalog --catalog <catalogue> validate-landscapes {code} -v"
    )


def fill(text: str, values: dict[str, Any]) -> str:
    for k, v in values.items():
        text = text.replace(f"__{k}__", str(v))
    return text


def from_template(dest: Path, code: str, concept: dict[str, Any], args: argparse.Namespace) -> list[str]:
    cam = camera_for_bbox(concept["bbox"])
    values = {
        "CODE": code,
        "LABEL": concept["label"],
        "CENTER": cam["center"],
        "ZOOM": cam["zoom"],
        "MIN_ZOOM": cam["min_zoom"],
        "MAX_BOUNDS": cam["max_bounds"],
        "LNG": cam["center"][0],
        "LAT": cam["center"][1],
    }
    import yaml

    def load(name: str) -> Any:
        return yaml.safe_load(fill((TEMPLATES / name).read_text(encoding="utf-8"), values))

    written = []
    origin = f"from the '{args.template}' template"
    profile = load(f"profile-{args.template}.yaml")
    if args.title:
        profile["title"] = args.title
    if args.summary:
        profile["summary"] = args.summary
    write_yaml(dest / "profile.yaml", profile, header("Page", code, origin))
    written.append("profile.yaml")
    if args.template == "explorer":
        explorer = load("explorer.yaml")
        if args.with_story:
            explorer["story"] = {"file": "story.yaml"}
            write_yaml(dest / "story.yaml", load("story.yaml"), header("Story", code, origin))
            written.append("story.yaml")
        if args.with_studies:
            explorer["studies"] = {"file": "studies.yaml"}
            write_yaml(dest / "studies.yaml", load("studies.yaml"), header("Study cards", code, origin))
            written.append("studies.yaml")
        write_yaml(dest / "explorer.yaml", explorer, header("Map explorer", code, origin))
        write_yaml(dest / "sources.yaml", load("sources.yaml"), header("Sources of the layers", code, origin))
        written += ["explorer.yaml", "sources.yaml"]
    return written


def from_profile(dest: Path, src: Path, code: str, concept: dict[str, Any], args: argparse.Namespace) -> list[str]:
    origin = f"from the {src.name} profile"
    profile = load_yaml(src / "profile.yaml")
    profile["landscape"] = code
    profile["title"] = args.title or concept["label"]
    profile["summary"] = (
        args.summary or f"TODO: what this page shows (was, for {src.name}: {profile.get('summary', '')})"
    )
    profile["status"] = "draft"
    profile["credits"] = [{"name": "TODO: who prepared this page", "role": "TODO: what they did"}]
    profile["origin"] = {"note": f"Structure copied from the {src.name} profile; data and texts replaced for {code}."}
    for section in profile["sections"]:
        if section.get("kind") == "map-explorer":
            section["title"] = f"TODO: section title (was: {section.get('title', '')})"
        if section.get("intro"):
            section["intro"] = f"TODO: section intro (was: {section['intro']})"[:400]
    written = []
    explorer_file = next((s["source"] for s in profile["sections"] if s.get("kind") == "map-explorer"), None)
    if explorer_file:
        ex = load_yaml(src / explorer_file)
        cam = camera_for_bbox(concept["bbox"])
        ex["map"].update({k: cam[k] for k in ("center", "zoom", "min_zoom", "max_bounds")})
        ex["title"] = f"TODO: explorer title (was: {ex.get('title', '')})"
        ex["tagline"] = f"TODO: what it shows · period (was: {ex.get('tagline', '')})"
        data = ex["data"]
        data["roots"] = {name: TODO_ROOT for name in data.get("roots") or {"main": ""}}
        data.pop("withheld", None)
        data.pop("withheld_reason", None)
        data["report"] = "TODO: link to the data report of this explorer (or remove this line)"
        if args.only:
            keep = set(args.only.split(","))
            unknown = keep - {o["id"] for o in ex["overlays"]}
            if unknown:
                sys.exit(
                    f"--only: {', '.join(sorted(unknown))} not in {src.name} "
                    f"(overlays: {', '.join(o['id'] for o in ex['overlays'])})"
                )
            ex["overlays"] = [o for o in ex["overlays"] if o["id"] in keep]
            used = {o.get("group") for o in ex["overlays"]} | {t.get("group") for t in ex.get("toggles") or []}
            ex["groups"] = [g for g in ex["groups"] if g in used]
            ex["panels"] = [p for p in ex.get("panels") or [] if p.get("group") in used]
        ex.pop("story", None)
        ex.pop("studies", None)
        if isinstance(ex.get("click"), dict):
            ex["click"]["title"] = concept["label"]
        write_yaml(dest / explorer_file, ex, header("Map explorer", code, origin))
        written.append(explorer_file)
        sources = load_yaml(src / "sources.yaml") or {"layers": []}
        refs = {o.get("source_ref") for o in ex["overlays"]} | {t.get("source_ref") for t in ex.get("toggles") or []}
        refs |= {p.get("source_ref") for p in ex.get("panels") or []}
        layers = []
        for layer in sources["layers"]:
            if layer["id"] not in refs:
                continue
            layers.append(
                {
                    "id": layer["id"],
                    "title": layer.get("title", layer["id"]),
                    "group": layer.get("group", ""),
                    **{
                        k: f"TODO: {k} of the {code} data (was: {layer.get(k, '')})"[:300]
                        for k in ("source", "period", "licence", "citation")
                    },
                    "record": None,
                }
            )
        write_yaml(dest / "sources.yaml", {"layers": layers}, header("Sources of the layers", code, origin))
        written.append("sources.yaml")
    write_yaml(dest / "profile.yaml", profile, header("Page", code, origin))
    written.insert(0, "profile.yaml")
    return written


def checklist(dest: Path, code: str, written: list[str], like: str | None) -> str:
    lines = [f"# Checklist: {code} landscape profile", ""]
    if like:
        lines += [
            f"Structure copied from {like}. Every layer still has the configuration of {like} (kind, legend, "
            "click, colours) and its texts (layer title, legend title, notes): check each one against the new data, "
            "rewrite any text that names the other landscape or its sources, and replace each data location.",
            "",
        ]
    for name in written:
        doc = load_yaml(dest / name)
        items = todos(doc)
        if items:
            lines += [f"## {name}", "", *[f"- [ ] `{p}`" for p in items], ""]
    ex_path = dest / "explorer.yaml"
    if ex_path.exists():
        from _common import assets

        ex = load_yaml(ex_path)
        rows = [
            [o["id"], o.get("title", ""), o.get("kind", ""), ", ".join(assets(o))[:200]]
            for o in ex.get("overlays") or []
        ]
        lines += ["## Layers and the files they read", "", md_table(rows, ["id", "title", "kind", "files"]), ""]
        base = [
            [sid, src.get("type", ""), ", ".join(assets(src))]
            for sid, src in (ex.get("map", {}).get("sources") or {}).items()
        ]
        if base:
            lines += [
                "## Base map files (boundary, mask, imagery, terrain, labels)",
                "",
                "Shown under every layer. With --like they are the other landscape's: replace or remove them.",
                "",
                md_table(base, ["source", "type", "files"]),
                "",
            ]
    text = "\n".join(lines) + "\n"
    return text


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--code", required=True, help="landscape code, e.g. SEN-FK")
    how = ap.add_mutually_exclusive_group(required=True)
    how.add_argument("--template", choices=("default", "explorer"))
    how.add_argument("--like", help="copy the structure of this existing profile (e.g. KEN-LVB, PER-PCL)")
    ap.add_argument("--only", help="with --like: keep only these overlay ids (comma-separated)")
    ap.add_argument("--with-story", action="store_true", help="with --template explorer: add story.yaml")
    ap.add_argument("--with-studies", action="store_true", help="with --template explorer: add studies.yaml")
    ap.add_argument("--title")
    ap.add_argument("--summary")
    ap.add_argument("--force", action="store_true", help="replace an existing profile folder")
    add_workspace_args(ap)
    args = ap.parse_args(argv)
    ws = workspace(args)
    code = args.code.strip().upper()
    vocab = ws.vocab()
    if code not in vocab:
        print(
            f"{code} is not a living landscape of the standard (vocab/landscapes.json): {', '.join(sorted(vocab))}.\n"
            "A new landscape is added to mosaic-standard first (references/recipes.md, case E)."
        )
        return 3
    dest = ws.landscape_dir(code)
    if dest.exists() and any(dest.iterdir()):
        if not args.force:
            print(f"{dest} already exists: edit it (case D) or pass --force to start again.")
            return 4
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    if args.like:
        src = ws.landscape_dir(args.like.upper())
        if not (src / "profile.yaml").exists():
            curated = sorted(p.name for p in (ws.catalog / "landscapes").iterdir() if (p / "profile.yaml").exists())
            print(f"No profile {args.like} in the catalogue. Curated profiles: {', '.join(curated)}")
            return 2
        written = from_profile(dest, src, code, vocab[code], args)
    else:
        written = from_template(dest, code, vocab[code], args)
    text = checklist(dest, code, written, args.like)
    out = ws.work_dir(code) / "checklist.md"
    out.write_text(text, encoding="utf-8")
    print(f"Wrote {', '.join(written)} in {dest}")
    print(f"To fill in: {out}")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
