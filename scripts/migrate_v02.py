#!/usr/bin/env python3
"""Convert the records from the MOSAIC standard v0.1 to v0.2 (in place).

    python scripts/migrate_v02.py                 # records/, examples/ and tests/fixtures/
    python scripts/migrate_v02.py --dry-run

Moves and renames only (src/mosaic_catalog/v02.py); what cannot be carried over is listed in
review/migration_v02.md. A record already in v0.2 is left as it is.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from mosaic_catalog.config import records_dir, set_catalog  # noqa: E402
from mosaic_catalog.v02 import convert  # noqa: E402
from mosaic_catalog.yamlio import header_of, write_record  # noqa: E402

HEADER_OLD = "(standard v0.1)"
HEADER_NEW = "(standard v0.2; v0.1 -> v0.2 by scripts/migrate_v02.py)"


def files() -> list[Path]:
    out = sorted(records_dir().glob("*/record.yaml")) + sorted((ROOT / "examples").glob("*.yaml"))
    out += sorted((ROOT / "tests" / "fixtures").glob("*/*.yaml"))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--catalog", type=Path, help="checkout of MOSAIC-mfl/catalog (default: $MOSAIC_CATALOG)")
    args = ap.parse_args(argv)
    set_catalog(args.catalog)
    rows: list[tuple[str, str, str]] = []
    changed = 0
    for path in files():
        old = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(old, dict):
            continue
        new, notes = convert(old)
        if new == old:
            continue
        changed += 1
        rid = str(old.get("id") or path.stem)
        if path.parts[-3:-1][0] == "records":
            rows += [(rid, f, n) for f, n in notes]
        if not args.dry_run:
            write_record(path, new, header_of(path).replace(HEADER_OLD, HEADER_NEW))
    if not args.dry_run:
        md = [
            "# Conversion notes (v0.1 -> v0.2)",
            "",
            f"{len({r[0] for r in rows})} records, {len(rows)} notes. Things that changed form or were dropped; "
            "nothing was invented. In every record mosaic.intake (workflow state) was dropped: it lives in the "
            "issue / pull request and in git. Missing minimum fields are in minimum_gaps.md.",
            "",
            "| Record | Field | Note |",
            "|---|---|---|",
        ]
        md += [f"| {r} | `{f}` | {n.replace('|', '/')} |" for r, f, n in sorted(rows)]
        (ROOT / "review" / "migration_v02.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"{changed} files converted to v0.2; {len(rows)} notes on records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
