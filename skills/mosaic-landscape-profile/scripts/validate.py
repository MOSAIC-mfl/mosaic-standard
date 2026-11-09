"""Validate a landscape profile and explain each problem in plain words.

    python validate.py --code SEN-FK

Runs the standard's validator (python -m mosaic_catalog --catalog <catalogue> validate-landscapes
<CODE> -v), the same check the catalogue's pull requests run, and lists:

- errors: the pull request would fail; each with what it means and how to fix it;
- warnings: allowed, but worth a look;
- TODO placeholders still in the files (the page would show them).

Exit code 0 only when there are no errors and no TODO left (--allow-todo accepts TODOs, for drafts).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PROFILE_FILES, add_workspace_args, load_yaml, todos, workspace

# validator message (regex) -> (what it means, how to fix it). Keep in step with references/errors.md.
EXPLAIN: list[tuple[str, str, str]] = [
    (
        r"is not one of the roots",
        "data.default_root names a root that data.roots does not define.",
        "Use one of the names under data.roots, or add that root.",
    ),
    (
        r"unknown root",
        "A data route sends files to a root that does not exist.",
        "Fix the route's 'root' to a name under data.roots.",
    ),
    (
        r"layer id '.*' used \d+ times",
        "Two map layers have the same id.",
        "Rename one of them (ids must be unique across the base map, the story and the overlays).",
    ),
    (
        r"unknown source '",
        "A map layer uses a source that is not declared.",
        "Add the source under map.sources (or the overlay's sources), or fix the layer's 'source'.",
    ),
    (
        r"rail id '.*' used \d+ times",
        "Two layers, toggles or panels in the side list share an id.",
        "Give each one its own id.",
    ),
    (
        r"group '.*' is not in groups",
        "A layer belongs to a group that is not in the list of groups.",
        "Add the group to 'groups' (in the order of the side list) or fix the layer's group.",
    ),
    (
        r"is not in sources.yaml",
        "A layer points to a source entry (source_ref) that sources.yaml does not have.",
        "Add an entry with that id to sources.yaml (source, licence, citation), or fix source_ref.",
    ),
    (
        r"catalogue record .* does not exist",
        "A layer links a catalogue record that does not exist.",
        "Check the id (mosaic:MFL-YYYY-NNN) or set record: null until the dataset is registered.",
    ),
    (
        r"is not in map.layers",
        "Something names a base map layer that does not exist.",
        "Use the id of a layer under map.layers (e.g. 'labels-start' to draw an overlay under the labels).",
    ),
    (
        r"is not an overlay",
        "The story or a study card names a layer that is not in the overlays.",
        "Use the id of one of the overlays, or remove the reference.",
    ),
    (
        r"is not in story.map.highlights",
        "A chapter asks to show a highlight the story does not define.",
        "Add it under story.map.highlights or remove it from the chapter's 'show'.",
    ),
    (
        r"is not a panel",
        "A study card opens a panel that does not exist.",
        "Use the id of a panel or remove open_panel.",
    ),
    (
        r"is not in the story or base map layers",
        "story.map.focus names layers that do not exist.",
        "Add those layers to story.map.layers or fix the ids.",
    ),
    (
        r"must be relative, without '\.\.'",
        "A data path is absolute or leaves the data folder.",
        "Write paths relative to the data root, e.g. tiles/landcover_2020.pmtiles.",
    ),
    (
        r"!= folder",
        "profile.yaml says a different landscape than its folder.",
        "Set 'landscape' to the folder name (the landscape code).",
    ),
    (
        r"not a landscape of vocab/landscapes.json",
        "The folder is not a landscape code of the standard.",
        "Use an existing code; a new landscape is added to mosaic-standard first (case E).",
    ),
    (r"section id '.*' used", "Two sections of the page share an id.", "Give each section its own id."),
    (
        r"cannot read|not a YAML mapping",
        "A file is not valid YAML (indentation, a missing quote or colon).",
        "Open the file at the line given and fix the syntax; "
        "quote texts that contain ': ' or start with special characters.",
    ),
    (
        r"is not a core renderer",
        "The layer uses a kind the website does not have yet.",
        "Use a core kind (references/modules.md) or ask the developers for a new module.",
    ),
    (
        r"is a required property",
        "A required field is missing.",
        "Add the field named in the message (references/modules.md lists what each block needs).",
    ),
    (
        r"Additional properties are not allowed",
        "A field name is not known (often a typo).",
        "Fix the spelling or remove the field.",
    ),
    (
        r"does not match '\^https://",
        "A data root is not an https:// address ending with '/'.",
        "Write the root as https://…/ (with the final slash).",
    ),
    (
        r"no 'verified' list",
        "A published study card has no 'verified' list.",
        "Allowed when the finding cites its pages; otherwise add verified: [{claim, where}].",
    ),
    (
        r"explore card states no claims",
        "An explore card has a finding.",
        "Keep it a question; the text may only describe, not claim results.",
    ),
]


def explain(message: str) -> tuple[str, str]:
    for pattern, what, fix in EXPLAIN:
        if re.search(pattern, message):
            return what, fix
    return "See the message.", "references/errors.md; if unclear, ask the MOSAIC team."


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--code", required=True)
    ap.add_argument("--allow-todo", action="store_true", help="do not fail on TODO placeholders (drafts)")
    add_workspace_args(ap)
    args = ap.parse_args(argv)
    ws = workspace(args)
    code = args.code.upper()
    cmd = [sys.executable, "-m", "mosaic_catalog", "--catalog", str(ws.catalog), "validate-landscapes", code, "-v"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode not in (0, 1):
        print(f"The validator did not run ({' '.join(cmd)}):\n{res.stderr[-1500:] or res.stdout[-1500:]}")
        print("Run scripts/setup.py again (it installs the validator).")
        return 2
    errors, warnings = [], []
    for line in res.stdout.splitlines():
        m = re.match(r"\s*\[(error|warning)\] (.*?): (.*)$", line)
        if m:
            (errors if m.group(1) == "error" else warnings).append((m.group(2), m.group(3)))
    head = next((ln for ln in res.stdout.splitlines() if ln.startswith(("OK ", "ERR")) and f" {code} " in ln), "")
    print(f"Validator: {head.strip() or 'no result for ' + code}")
    if " default " in head:
        print(f"Note: {code} has no profile.yaml yet, so it gets the default page.")
    for title, items in (("Errors (the pull request would fail)", errors), ("Warnings (allowed)", warnings)):
        if not items:
            continue
        print(f"\n{title}:")
        for where, msg in items:
            what, fix = explain(msg)
            print(f"- {where}: {msg}\n  means: {what}\n  fix: {fix}")
    folder = ws.landscape_dir(code)
    left = {name: todos(load_yaml(folder / name)) for name in PROFILE_FILES if (folder / name).exists()}
    left = {k: v for k, v in left.items() if v}
    if left:
        print("\nTODO placeholders still to fill in:")
        for name, paths in left.items():
            print(f"- {name}: {', '.join(paths)}")
    ok = not errors and (args.allow_todo or not left)
    print(
        "\nResult: "
        + ("ready" if ok else "not ready")
        + f" ({len(errors)} errors, {len(warnings)} warnings, {sum(map(len, left.values()))} TODO)"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
