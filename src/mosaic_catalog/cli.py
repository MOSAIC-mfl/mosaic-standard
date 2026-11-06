"""Command line: ``python -m mosaic_catalog [--catalog PATH] validate | validate-landscapes | build | infer``.

The catalogue (records/, landscapes/) is a checkout of MOSAIC-mfl/catalog: ``--catalog PATH`` or the
environment variable MOSAIC_CATALOG. The standard is this repository.

Exit codes: 0 = no invalid record (incomplete records are allowed and reported),
1 = at least one invalid record or catalogue-level problem, 2 = usage error.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from .config import ROOT, CatalogNotSet, Config, records_dir, set_catalog
from .records import catalogue_issues, iter_record_files, load_record
from .standard import Issue, Report, Standard, Status


def _validate(args: argparse.Namespace) -> int:
    cfg = Config.load()
    std = Standard(enforced_profiles=cfg.enforced_profiles)
    if std.version != cfg.standard_version:
        print(f"config standard_version {cfg.standard_version} != schemas {std.version}", file=sys.stderr)
        return 2
    paths = [Path(p) for p in args.paths] or [records_dir()]
    loaded = [load_record(f) for f in iter_record_files(paths)]
    reports: list[Report] = []
    owners: dict[str, str] = {}
    for rec in loaded:
        if rec.data is None:
            r = Report(rec.path.stem)
            r.issues.append(Issue("structure", "", rec.error or "unreadable"))
        else:
            r = std.check(rec.data)
        r.source = rec.path.as_posix()
        reports.append(r)
        if rec.data:
            owners[r.record_id] = _owner(rec.data)
    cat = catalogue_issues(loaded, records_dir().resolve())
    for rid, msg in cat:
        for r in reports:
            if r.record_id == rid:
                r.issues.append(Issue("structure", "id", msg))

    if args.gaps:
        _write_gaps(reports, Path(args.gaps), owners)
    if args.format == "json":
        print(json.dumps([r.as_dict() for r in reports], indent=2, ensure_ascii=False))
    else:
        _print_text(reports, verbose=args.verbose)
    return 1 if any(r.status is Status.INVALID for r in reports) else 0


def _print_text(reports: list[Report], verbose: bool) -> None:
    for r in reports:
        mark = {"complete": "OK ", "incomplete": "INC", "invalid": "ERR"}[r.status.value]
        comp = " ".join(f"{k}={v:.0%}" for k, v in r.completeness.items())
        print(f"{mark} {r.record_id}  {comp}  ({r.source})")
        for i in r.issues:
            if verbose or i.level in ("structure", "minimum") or i.level.startswith("extension:"):
                where = i.path.replace("/", ".") if i.path and i.path != i.field else i.field
                print(f"     [{i.level}] {where}: {i.message}")
    n = {s: sum(r.status is s for r in reports) for s in Status}
    print(
        f"\n{len(reports)} records: {n[Status.COMPLETE]} complete, "
        f"{n[Status.INCOMPLETE]} incomplete, {n[Status.INVALID]} invalid"
    )


def _owner(data: dict[str, Any]) -> str:
    """Who can complete the record: its point of contact, else its first contact."""
    contacts = [c for c in data.get("contact") or [] if isinstance(c, dict)]
    pick = [c for c in contacts if "point-of-contact" in (c.get("roles") or [])] or contacts
    if not pick:
        return ""
    c = pick[0]
    return " ".join(
        x for x in (c.get("name") or c.get("organization"), f"<{c['email']}>" if c.get("email") else "") if x
    )


CLASSIFICATION = "data_classification"


def _write_gaps(reports: list[Report], path: Path, owners: dict[str, str]) -> None:
    """Review lists (CSV + Markdown), one row per record and gap, with the person to ask:

    * <path>: fields missing for the minimum;
    * <dir>/classification_gaps: data the website cannot classify yet (geometry type of vector
      data) - recommended, not minimum, but needed to show and describe the data.
    """
    minimum = [(r.record_id, i.field, i.message) for r in reports for i in r.by_level("minimum")]
    classification = [
        (r.record_id, i.path.replace("/", "."), i.message)
        for r in reports
        for i in r.by_level("recommended")
        if i.field == CLASSIFICATION
    ]
    _write_list(
        path,
        minimum,
        owners,
        "Records below the MOSAIC minimum",
        "Decision per row: complete / publish incomplete / withdraw.",
    )
    _write_list(
        path.parent / "classification_gaps",
        classification,
        owners,
        "Data the website cannot classify yet",
        "Not part of the minimum, but needed to show and describe the data. A tool fills "
        "them when it can read the file (python -m mosaic_catalog infer); the rest needs a person.",
    )


def _write_list(path: Path, rows: list[tuple[str, str, str]], owners: dict[str, str], title: str, intro: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix(".csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["record", "field", "problem", "suggestion", "owner", "decision"])
        w.writerows([(rid, f, m, "", owners.get(rid, ""), "") for rid, f, m in rows])
    lines = [
        f"# {title}",
        "",
        f"{len({r for r, *_ in rows})} records, {len(rows)} rows. {intro}",
        "",
        "| Record | Field | Problem | Owner |",
        "|---|---|---|---|",
    ]
    lines += [f"| {rid} | `{f}` | {m} | {owners.get(rid, '')} |" for rid, f, m in rows]
    path.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _validate_landscapes(args: argparse.Namespace) -> int:
    from . import landscapes as ls

    profiles = ls.load_all(Config.load().landscape_sections)
    for p in profiles:
        if args.code and p.code not in args.code:
            continue
        kinds = ", ".join(str(s.get("kind")) for s in p.sections)
        mark = "OK " if p.ok else "ERR"
        print(f"{mark} {p.code}  {'curated' if p.curated else 'default'}  [{kinds}]")
        for pr in p.problems:
            if pr.level == "error" or args.verbose:
                print(f"     {pr}")
    bad = sum(not p.ok for p in profiles)
    print(f"\n{len(profiles)} landscapes: {sum(p.curated for p in profiles)} curated profiles, {bad} with errors")
    return 1 if bad else 0


def _build(args: argparse.Namespace) -> int:
    from .build import LandscapeError, build

    try:
        res = build(Path(args.records) if args.records else records_dir(), Path(args.out))
    except LandscapeError as exc:
        print("Build stopped: invalid landscape profiles", file=sys.stderr)
        for line in exc.problems:
            print(f"  {line}", file=sys.stderr)
        return 1
    if res.invalid:
        print("Build stopped: invalid records", file=sys.stderr)
        for r in res.invalid:
            print(f"  {r.record_id} ({r.source})", file=sys.stderr)
            for i in r.issues:
                if i.level == "structure" or i.level.startswith("extension:"):
                    print(f"     {i.field}: {i.message}", file=sys.stderr)
        return 1
    print(f"Published {res.published} records to {args.out} (skipped: {res.skipped or 'none'})")
    return 0


def _infer(args: argparse.Namespace) -> int:
    import tempfile

    from .infer import apply, fetch, inspect_file
    from .yamlio import write_record

    lines = ["# Inference report", "", "Values read from the data files (python -m mosaic_catalog infer).", "",
             "| Record | Access point | Filled | Conflicts / problems |", "|---|---|---|---|"]  # fmt: skip
    changed = 0
    for path in sorted((Path(args.records) if args.records else records_dir()).glob("*/record.yaml")):
        rec = load_record(path)
        if rec.data is None or (args.record and rec.data.get("id") not in args.record):
            continue
        data = rec.data
        if data.get("access") != "public":
            continue
        touched = False
        for i, point in enumerate(data.get("data") or []):
            url = next((loc.get("url") for loc in point.get("locations") or [] if loc.get("url")), None)
            if point.get("access_method") != "download" or not url or point.get("access", "public") != "public":
                continue
            with tempfile.TemporaryDirectory() as tmp:
                try:
                    found = inspect_file(fetch(url, Path(tmp)))
                except Exception as exc:  # any fetch or read failure is reported, not fatal
                    lines.append(f"| {data['id']} | {i} | | could not read: {exc} |")
                    continue
            res = apply(data, i, found)
            notes = "; ".join(res.conflicts + res.problems)
            lines.append(f"| {data['id']} | {i} | {', '.join(res.filled)} | {notes} |")
            touched |= bool(res.filled)
        if touched and not args.dry_run:
            write_record(path, data)
            changed += 1
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{changed} records updated; report: {report}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="mosaic_catalog")
    ap.add_argument("--catalog", help="checkout of MOSAIC-mfl/catalog (default: $MOSAIC_CATALOG)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="check records against the MOSAIC standard")
    v.add_argument("paths", nargs="*", help="record files or folders (default: records/)")
    v.add_argument("--format", choices=("text", "json"), default="text")
    v.add_argument("--verbose", "-v", action="store_true", help="also show warnings")
    v.add_argument("--gaps", metavar="FILE", help="write the review list to FILE.csv and FILE.md")
    lv = sub.add_parser("validate-landscapes", help="check the landscape profiles (landscapes/<CODE>/)")
    lv.add_argument("code", nargs="*", help="only these landscape codes")
    lv.add_argument("--verbose", "-v", action="store_true", help="also show warnings")
    b = sub.add_parser("build", help="publish dist/catalog.json and dist/manifest.json")
    b.add_argument("--records", help="records folder (default: <catalog>/records)")
    b.add_argument("--out", default=str(ROOT / "dist"))
    inf = sub.add_parser("infer", help="read public downloadable files and fill classification fields")
    inf.add_argument("--records", help="records folder (default: <catalog>/records)")
    inf.add_argument("--record", action="append", help="only this record id (repeatable)")
    inf.add_argument("--report", default=str(ROOT / "review" / "inference_report.md"))
    inf.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    if args.catalog:
        set_catalog(args.catalog)
    try:
        return _run(args)
    except CatalogNotSet as err:
        print(err, file=sys.stderr)
        return 2


def _run(args: argparse.Namespace) -> int:
    if args.cmd == "infer":
        return _infer(args)
    if args.cmd == "validate":
        return _validate(args)
    if args.cmd == "validate-landscapes":
        return _validate_landscapes(args)
    if args.cmd == "build":
        return _build(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
