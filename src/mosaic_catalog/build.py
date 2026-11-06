"""Build the published catalogue: dist/catalog.json + dist/manifest.json (+ schema/, vocab/, landscapes/).

This is what `mosaic-api` reads. The build:

* checks every record and stops if one is invalid;
* leaves out withdrawn records, and incomplete ones when ``include_incomplete`` is false;
* adds ``meta`` to each record: status, completeness and the minimum fields still missing;
* fills ``created`` / ``updated`` from git history when the record does not state them;
* writes a manifest with a SHA-256 per record, so a reader only reprocesses what changed;
* writes one landscape profile per living landscape (landscapes.py) and stops if one is invalid.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import ROOT, Config
from .records import RECORD_FILE, catalogue_issues, load_record
from .standard import Report, Standard, Status


@dataclass(frozen=True)
class BuildResult:
    published: int
    skipped: dict[str, int]
    invalid: list[Report]


def _git(repo: Path, *args: str) -> str | None:
    try:
        res = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)  # noqa: S603, S607
    except (OSError, subprocess.CalledProcessError):
        return None
    return res.stdout.strip() or None


def _history(path: Path) -> tuple[str | None, str | None]:
    """created / updated of a record file from the git history of the repository that holds it."""
    repo = path.resolve().parent
    top = _git(repo, "rev-parse", "--show-toplevel")
    if not top:
        return (None, None)
    out = _git(Path(top), "log", "--follow", "--format=%as", "--", str(path.resolve().relative_to(Path(top).resolve())))
    dates = out.split() if out else []
    return (dates[-1], dates[0]) if dates else (None, None)


def canonical(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def build(records_dir: Path, out_dir: Path, cfg: Config | None = None) -> BuildResult:
    cfg = cfg or Config.load()
    std = Standard(enforced_profiles=cfg.enforced_profiles)
    files = sorted(records_dir.glob(f"*/{RECORD_FILE}"))
    loaded = [load_record(f) for f in files]
    dup = catalogue_issues(loaded, records_dir.resolve())
    invalid: list[Report] = []
    published: list[dict[str, Any]] = []
    skipped: Counter[str] = Counter()
    for rec in loaded:
        if rec.data is None:
            r = Report(rec.path.parent.name, source=rec.path.as_posix())
            invalid.append(r)
            continue
        report = std.check(rec.data)
        report.source = rec.path.as_posix()
        if report.status is Status.INVALID or any(rid == report.record_id for rid, _ in dup):
            invalid.append(report)
            continue
        if report.status is Status.INCOMPLETE and not cfg.include_incomplete:
            skipped["incomplete"] += 1
            continue
        data = dict(rec.data)
        data.setdefault("schema_version", std.version)
        created, updated = _history(rec.path)
        if created:
            data.setdefault("created", created)
        if updated:
            data.setdefault("updated", updated)
        data["meta"] = {
            "status": report.status.value,
            "completeness": report.completeness,
            "missing_minimum": sorted({i.field for i in report.by_level("minimum")}),
            "standard_version": std.version,
        }
        published.append(data)
    if invalid:
        return BuildResult(0, dict(skipped), invalid)

    out_dir.mkdir(parents=True, exist_ok=True)
    published.sort(key=lambda d: str(d["id"]))
    (out_dir / "catalog.json").write_bytes(
        json.dumps({"records": published}, ensure_ascii=False, indent=1).encode("utf-8") + b"\n"
    )
    status = Counter(d["meta"]["status"] for d in published)
    manifest = {
        "catalogue": "mosaic",
        "standard_version": std.version,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit": _git(records_dir, "rev-parse", "HEAD"),  # the catalogue (records, landscapes)
        "standard_commit": _git(ROOT, "rev-parse", "HEAD"),  # mosaic-standard (schemas, vocabularies)
        "counts": {
            "published": len(published),
            **{s: status.get(s, 0) for s in ("complete", "incomplete")},
            "skipped": dict(skipped),
        },
        "include_incomplete": cfg.include_incomplete,
        "files": {
            "catalog": "catalog.json",
            "schema": "schema/",
            "vocab": "vocab/",
            "crosswalks": "crosswalks/",
            "landscapes": "landscapes/index.json",
        },
        "records": [
            {"id": d["id"], "sha256": hashlib.sha256(canonical(d)).hexdigest(), "status": d["meta"]["status"]}
            for d in published
        ],
    }
    manifest["landscapes"] = _build_landscapes(out_dir, cfg)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for sub in ("schema", "vocab", "crosswalks"):
        shutil.rmtree(out_dir / sub, ignore_errors=True)
        shutil.copytree(ROOT / sub, out_dir / sub, ignore=shutil.ignore_patterns("sources", "_template"))
    return BuildResult(len(published), dict(skipped), [])


def _build_landscapes(out_dir: Path, cfg: Config) -> dict[str, Any]:
    """dist/landscapes/index.json + one <CODE>.json per landscape (profile and its configuration files)."""
    from . import landscapes as ls

    profiles = ls.load_all(cfg.landscape_sections)
    bad = [p for p in profiles if not p.ok]
    if bad:
        raise LandscapeError([str(pr) for p in bad for pr in p.problems if pr.level == "error"])
    vocab = ls.vocab()
    target = out_dir / "landscapes"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True)
    entries = []
    for p in profiles:
        doc = ls.bundle(p, vocab)
        (target / f"{p.code}.json").write_bytes(json.dumps(doc, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
        entries.append(
            {
                **ls.summary(p, vocab),
                "file": f"landscapes/{p.code}.json",
                "sha256": hashlib.sha256(canonical(doc)).hexdigest(),
            }
        )
    (target / "index.json").write_text(
        json.dumps({"landscapes": entries}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return {"index": "landscapes/index.json", "count": len(entries), "curated": sum(e["curated"] for e in entries)}


class LandscapeError(Exception):
    def __init__(self, problems: list[str]) -> None:
        super().__init__("; ".join(problems[:5]))
        self.problems = problems
