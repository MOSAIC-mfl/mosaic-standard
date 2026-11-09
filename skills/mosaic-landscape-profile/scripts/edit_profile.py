"""Common changes to an existing profile, done consistently across its files.

    python edit_profile.py list --code KEN-LVB
    python edit_profile.py remove-overlay --code KEN-LVB --id fire
    python edit_profile.py set-root --code PER-PCL --root hf --url https://huggingface.co/datasets/org/name/resolve/main/

- list: the groups, layers, toggles, panels, story chapters and study cards, with the files each layer reads.
- remove-overlay: removes a layer and every reference to it (story chapters, chapter chips, comparisons,
  study cards, its sources.yaml entry when nothing else uses it, a group left empty).
- set-root: changes where a group of files is served (a data root), e.g. after moving the data.

Other changes (texts, colours, legends, a new layer) are edited in the YAML files directly; validate.py
checks them. The first comment lines of each file are kept.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import add_workspace_args, assets, dump_yaml, load_profile, load_yaml, md_table, workspace


def leading_comments(path: Path) -> str:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("#"):
            break
        out.append(line + "\n")
    return "".join(out)


def write(path: Path, data: Any) -> None:
    path.write_text(leading_comments(path) + dump_yaml(data), encoding="utf-8")


def files(folder: Path) -> dict[str, Path]:
    profile = load_yaml(folder / "profile.yaml") or {}
    ex_name = next((s.get("source") for s in profile.get("sections") or [] if s.get("kind") == "map-explorer"), None)
    out = {"profile": folder / "profile.yaml"}
    if ex_name:
        out["explorer"] = folder / ex_name
        ex = load_yaml(out["explorer"]) or {}
        for key in ("story", "studies"):
            if (ex.get(key) or {}).get("file"):
                out[key] = folder / ex[key]["file"]
        if (ex.get("about") or {}).get("sources"):
            out["sources"] = folder / ex["about"]["sources"]
    return out


def cmd_list(folder: Path) -> int:
    docs = load_profile(folder)
    prof = docs["profile"]
    print(f"{prof.get('landscape')} · {prof.get('title')} · status {prof.get('status', 'draft')}")
    print("Sections: " + ", ".join(f"{s.get('id')} ({s.get('kind')})" for s in prof.get("sections") or []))
    ex = docs.get("explorer")
    if not ex:
        return 0
    print(f"\nGroups: {', '.join(ex.get('groups') or [])}\n")
    rows = [
        [
            o["id"],
            o.get("group", ""),
            o.get("title", ""),
            o.get("kind", ""),
            (o.get("inspect") or {}).get("kind", "—"),
            str(len(assets(o))),
        ]
        for o in ex.get("overlays") or []
    ]
    print(md_table(rows, ["layer", "group", "title", "kind", "click", "files"]))
    for label, key in (("Toggles", "toggles"), ("Panels", "panels")):
        items = ex.get(key) or []
        if items:
            print(f"\n{label}: " + ", ".join(f"{t['id']} ({t.get('title', '')})" for t in items))
    print("\nData roots: " + ", ".join(f"{k} = {v}" for k, v in (ex.get("data") or {}).get("roots", {}).items()))
    story = docs.get("story")
    if story:
        print(
            f"\nStory '{story.get('title')}': "
            + "; ".join(
                f"{c['id']} [{', '.join((c.get('visual') or {}).get('layers') or [])}]"
                for c in story.get("chapters") or []
            )
        )
    studies = docs.get("studies")
    if studies:
        print(
            "\nStudy cards: "
            + "; ".join(f"{c['id']} [{', '.join(c.get('layers') or [])}]" for c in studies.get("cards") or [])
        )
    return 0


def cmd_remove_overlay(folder: Path, oid: str) -> int:
    paths = files(folder)
    if "explorer" not in paths:
        print("This profile has no map explorer.")
        return 2
    ex = load_yaml(paths["explorer"])
    victim = next((o for o in ex["overlays"] if o["id"] == oid), None)
    if not victim:
        print(f"No layer '{oid}'. Layers: {', '.join(o['id'] for o in ex['overlays'])}")
        return 2
    if len(ex["overlays"]) == 1:
        print(
            "It is the only layer: a map explorer needs at least one. "
            "Replace it instead, or remove the explorer section."
        )
        return 2
    changes = [f"explorer: removed layer '{oid}'"]
    ex["overlays"] = [o for o in ex["overlays"] if o["id"] != oid]
    used_groups = (
        {o.get("group") for o in ex["overlays"]}
        | {t.get("group") for t in ex.get("toggles") or []}
        | {p.get("group") for p in ex.get("panels") or []}
    )
    if victim.get("group") not in used_groups:
        ex["groups"] = [g for g in ex["groups"] if g != victim.get("group")]
        changes.append(f"explorer: removed the empty group '{victim.get('group')}'")
    write(paths["explorer"], ex)
    if "story" in paths:
        story = load_yaml(paths["story"])
        for ch in story.get("chapters") or []:
            v = ch.get("visual") or {}
            if oid in (v.get("layers") or []):
                v["layers"] = [x for x in v["layers"] if x != oid]
                changes.append(f"story: chapter '{ch['id']}' no longer shows '{oid}'")
            steps = v.get("steps") or []
            kept = [s for s in steps if s.get("layer") != oid]
            if len(kept) != len(steps):
                v["steps"] = kept
                changes.append(f"story: chapter '{ch['id']}' lost {len(steps) - len(kept)} chip(s) for '{oid}'")
            for key in ("compare",):
                if (v.get(key) or {}).get("overlay") == oid:
                    v.pop(key)
                    changes.append(f"story: chapter '{ch['id']}' no longer compares '{oid}'")
            if (ch.get("compare_option") or {}).get("overlay") == oid:
                ch.pop("compare_option")
        write(paths["story"], story)
    if "studies" in paths:
        studies = load_yaml(paths["studies"])
        for card in studies.get("cards") or []:
            if oid in (card.get("layers") or []):
                card["layers"] = [x for x in card["layers"] if x != oid]
                changes.append(f"studies: card '{card['id']}' no longer opens '{oid}'")
            if card.get("steps"):
                card["steps"] = [s for s in card["steps"] if s.get("layer") != oid]
        write(paths["studies"], studies)
    ref = victim.get("source_ref")
    if ref and "sources" in paths:
        still = (
            {o.get("source_ref") for o in ex["overlays"]}
            | {t.get("source_ref") for t in ex.get("toggles") or []}
            | {p.get("source_ref") for p in ex.get("panels") or []}
        )
        if ref not in still:
            src = load_yaml(paths["sources"])
            src["layers"] = [s for s in src["layers"] if s["id"] != ref]
            write(paths["sources"], src)
            changes.append(f"sources: removed entry '{ref}'")
    print("\n".join(changes))
    print("\nThe data files of the layer are not touched (they live where they are served). Next: validate.py")
    return 0


def cmd_set_root(folder: Path, root: str, url: str) -> int:
    paths = files(folder)
    if "explorer" not in paths:
        print("This profile has no map explorer.")
        return 2
    if not url.startswith("https://") or not url.endswith("/"):
        print("A data root is an https:// address that ends with '/'.")
        return 2
    ex = load_yaml(paths["explorer"])
    roots = ex["data"].setdefault("roots", {})
    old = roots.get(root)
    roots[root] = url
    write(paths["explorer"], ex)
    print(f"data.roots.{root}: {old or '(new)'} -> {url}\nNext: check_data.py, then validate.py")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("list", "remove-overlay", "set-root"):
        p = sub.add_parser(name)
        p.add_argument("--code", required=True)
        add_workspace_args(p)
        if name == "remove-overlay":
            p.add_argument("--id", required=True, help="the layer id (see: list)")
        if name == "set-root":
            p.add_argument("--root", required=True, help="the root name under data.roots")
            p.add_argument("--url", required=True)
    args = ap.parse_args(argv)
    ws = workspace(args)
    folder = ws.landscape_dir(args.code.upper())
    if not (folder / "profile.yaml").exists():
        print(f"{args.code} has no profile yet (start one with new_profile.py).")
        return 2
    if args.cmd == "list":
        return cmd_list(folder)
    if args.cmd == "remove-overlay":
        return cmd_remove_overlay(folder, args.id)
    return cmd_set_root(folder, args.root, args.url)


if __name__ == "__main__":
    raise SystemExit(main())
