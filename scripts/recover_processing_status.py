#!/usr/bin/env python3
"""Add processing_status (standard v0.2) to the catalogue records migrated from schema 1.

The schema-1 records (catalog repo @ <ref>, records/<id>.yaml) carried the readiness the contributor
declared (Raw / Processed / Validated). The first migration left it out; this script copies it into
records/<id>/record.yaml as raw / processed / validated. The old repo is only read (git show); a
record whose old value is empty, or that has no schema-1 file, is left as it is - nothing is inferred.

    python3 scripts/recover_processing_status.py --catalog ../catalog [--ref 0dad25c] [--check]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

VALUES = {"raw", "processed", "validated"}


def old_value(catalog: Path, ref: str, rid: str) -> str | None:
    res = subprocess.run(
        ["git", "-C", str(catalog), "show", f"{ref}:records/{rid}.yaml"],
        capture_output=True, text=True, check=False,
    )  # fmt: skip
    if res.returncode != 0:
        return None
    value = (yaml.safe_load(res.stdout) or {}).get("processing_status")
    value = str(value).strip().lower() if value else None
    return value if value in VALUES else None


def insert_after(text: str, key: str, line: str) -> str:
    """Put `line` after the top-level `key:` block (keeps the file's order and comments)."""
    lines = text.splitlines(keepends=True)
    start = next((i for i, x in enumerate(lines) if x.startswith(f"{key}:")), None)
    if start is None:
        return text.rstrip("\n") + "\n" + line
    end = start + 1
    while end < len(lines) and (lines[end].startswith((" ", "-")) or not lines[end].strip()):
        end += 1
    return "".join([*lines[:end], line, *lines[end:]])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--ref", default="0dad25c")
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    args = ap.parse_args(argv)
    changed, missing = 0, []
    for path in sorted((args.catalog / "records").glob("*/record.yaml")):
        text = path.read_text(encoding="utf-8")
        rec = yaml.safe_load(text) or {}
        if rec.get("processing_status"):
            continue
        value = old_value(args.catalog, args.ref, str(rec.get("id")))
        if value is None:
            missing.append(str(rec.get("id")))
            continue
        anchor = "access_note" if "access_note" in rec else "access"
        if not args.check:
            path.write_text(insert_after(text, anchor, f"processing_status: {value}\n"), encoding="utf-8")
        changed += 1
    print(f"{'would add' if args.check else 'added'} processing_status to {changed} records; "
          f"{len(missing)} without a stated value: {', '.join(missing) or '-'}")  # fmt: skip
    return 0


if __name__ == "__main__":
    sys.exit(main())
