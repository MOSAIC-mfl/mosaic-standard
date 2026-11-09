"""Check that every data file of a profile can be read by the website.

    python check_data.py --code SEN-FK
    python check_data.py --code SEN-FK --origin https://mosaic-mfl.github.io --limit 50

For each file the explorer (and its story) names, it resolves the URL with the profile's data
roots and routes (as the website does) and asks for its first bytes the way a browser would:

- reachable over HTTPS (status 200 or 206);
- CORS: the server answers ``Access-Control-Allow-Origin`` for the MOSAIC website;
- byte ranges for tiled and cloud-optimized files (.pmtiles, .tif, .bin): status 206, so the map
  reads only the parts it shows;
- size, when the server says it.

Files listed under ``data.withheld`` are skipped (never requested). Results: a table, and
<work>/<CODE>/data-check.json for preview.py. Exit code 1 when a file fails.
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import AssetRouter, add_workspace_args, assets, load_profile, md_table, workspace

RANGED = (".pmtiles", ".tif", ".tiff", ".bin")


def check(url: str, origin: str, timeout: float) -> dict[str, Any]:
    if (
        not url.startswith("https://")
        and not url.startswith("http://127.0.0.1")
        and not url.startswith("http://localhost")
    ):
        return {"ok": False, "problem": "not served over HTTPS"}
    if "TODO" in url:
        return {"ok": False, "problem": "data root still TODO"}
    req = urllib.request.Request(
        url, headers={"Range": "bytes=0-15", "Origin": origin, "User-Agent": "mosaic-landscape-profile"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as resp:
            status, headers = resp.status, resp.headers
    except urllib.error.HTTPError as err:
        return {
            "ok": False,
            "status": err.code,
            "problem": f"HTTP {err.code}" + (" (file not found)" if err.code == 404 else ""),
        }
    except (urllib.error.URLError, TimeoutError, OSError) as err:
        return {"ok": False, "problem": f"unreachable ({getattr(err, 'reason', err)})"}
    cors = headers.get("Access-Control-Allow-Origin")
    size = None
    cr = headers.get("Content-Range")
    if cr and "/" in cr and cr.rsplit("/", 1)[1].isdigit():
        size = int(cr.rsplit("/", 1)[1])
    elif headers.get("Content-Length", "").isdigit() and status == 200:
        size = int(headers["Content-Length"])
    problems = []
    if cors not in ("*", origin):
        problems.append("no CORS for the website (Access-Control-Allow-Origin missing)")
    if url.lower().split("?")[0].endswith(RANGED) and status != 206:
        problems.append("no byte ranges (status 200 instead of 206): the map would download the whole file")
    return {"ok": not problems, "status": status, "cors": cors, "size": size, "problem": "; ".join(problems)}


def human(n: int | None) -> str:
    if n is None:
        return ""
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1000 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n = n / 1000  # type: ignore[assignment]
    return ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--code", required=True)
    ap.add_argument("--origin", default="https://mosaic-mfl.github.io", help="the website asking for the files")
    ap.add_argument("--limit", type=int, default=0, help="check at most this many files (0 = all)")
    ap.add_argument("--timeout", type=float, default=20)
    add_workspace_args(ap)
    args = ap.parse_args(argv)
    ws = workspace(args)
    code = args.code.upper()
    docs = load_profile(ws.landscape_dir(code))
    explorer = docs.get("explorer")
    if not explorer:
        print(f"{code} has no map explorer: there are no data files to check.")
        return 0
    router = AssetRouter(explorer.get("data") or {})
    paths = assets(
        explorer, ((docs.get("story") or {}).get("map") or {}, (docs.get("story") or {}).get("chapters") or [])
    )
    if args.limit:
        paths = paths[: args.limit]
    todo = [p for p in paths if p not in router.withheld]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(
            pool.map(
                lambda p: {"path": p, "url": router.url(p), **check(router.url(p), args.origin, args.timeout)}, todo
            )
        )
    results += [
        {"path": p, "url": router.url(p), "ok": True, "problem": "withheld: never requested"}
        for p in paths
        if p in router.withheld
    ]
    bad = [r for r in results if not r["ok"]]
    rows = [["OK" if r["ok"] else "FAIL", r["path"], human(r.get("size")), r.get("problem") or ""] for r in results]
    print(md_table(rows, ["", "file", "size", "problem"]))
    print(f"\n{len(results) - len(bad)} of {len(results)} files OK.")
    if bad:
        print("How to fix: references/data-hosting.md (where to put the files, CORS, byte ranges).")
    out = ws.work_dir(code) / "data-check.json"
    out.write_text(json.dumps({"origin": args.origin, "files": results}, indent=1), encoding="utf-8")
    print(f"Saved: {out}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
