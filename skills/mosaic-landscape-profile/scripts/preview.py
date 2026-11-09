"""A one-page HTML review of a landscape profile, to read before the pull request.

    python preview.py --code SEN-FK            # writes <work>/SEN-FK/preview.html

Shows what the website will build from the profile, without running the website: the page and its
sections, the map (centre, limits), every layer with its legend colours, click and files (with the
result of check_data.py when it has been run), the side list (groups, toggles, panels), the story
chapters, the study cards, the sources and licences, the TODO placeholders and the validator's result.
Open the file in a browser.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PROFILE_FILES, add_workspace_args, assets, load_profile, load_yaml, todos, workspace

CSS = """
:root{--ink:#1c2b3a;--muted:#5d6b78;--line:#d9dee3;--bg:#f6f7f8;--card:#fff;--ok:#1f7a4d;--bad:#b3261e;--warn:#9a6700;--accent:#0b5d75}
@media (prefers-color-scheme:dark){:root{--ink:#e6eaee;--muted:#a3adb7;--line:#33404c;--bg:#11181f;--card:#18222c;--ok:#5fc48f;--bad:#ff8a80;--warn:#e3b341;--accent:#6cc4dc}}
*{box-sizing:border-box}body{margin:0;font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;color:var(--ink);background:var(--bg)}
main{max-width:1080px;margin:0 auto;padding:24px 16px 64px}h1{font-size:26px;margin:0 0 4px}h2{font-size:18px;margin:32px 0 8px;border-bottom:1px solid var(--line);padding-bottom:4px}
.muted{color:var(--muted)}.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 16px;margin:8px 0}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;vertical-align:top;padding:6px 8px;border-bottom:1px solid var(--line)}th{font-weight:600;color:var(--muted)}
.sw{display:inline-block;width:12px;height:12px;border-radius:2px;margin-right:2px;vertical-align:-1px;border:1px solid rgba(0,0,0,.15)}
.pill{display:inline-block;border-radius:10px;padding:0 8px;font-size:12px;border:1px solid var(--line)}.ok{color:var(--ok)}.bad{color:var(--bad)}.warn{color:var(--warn)}
code{font-size:13px;word-break:break-all}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px}
"""


def esc(x: Any) -> str:
    return html.escape("" if x is None else str(x))


def todo_mark(text: Any) -> str:
    s = esc(text)
    return f'<span class="warn">{s}</span>' if "TODO" in s else s


def colours(legend: dict[str, Any] | None) -> str:
    if not legend:
        return '<span class="muted">no legend</span>'
    if legend.get("kind") == "classes":
        items = legend.get("classes") or []
        sw = "".join(
            f'<span class="sw" title="{esc(c.get("name"))}" style="background:{esc(c.get("color") or ("rgb(" + ",".join(map(str, c["rgb"])) + ")" if c.get("rgb") else "#999"))}"></span>'
            for c in items[:24]
        )
        return f"{sw} <span class=muted>{len(items)} classes</span>"
    sw = "".join(f'<span class="sw" style="background:{esc(c)}"></span>' for c in legend.get("colors") or [])
    labels = legend.get("labels") or []
    return f"{sw} <span class=muted>{esc(labels[0] if labels else '')} – {esc(labels[1] if len(labels) > 1 else '')}</span>"


def file_list(paths: list[str], checks: dict[str, dict[str, Any]]) -> str:
    if not paths:
        return '<span class="muted">—</span>'
    out = []
    for p in paths[:6]:
        c = checks.get(p)
        mark = (
            ""
            if c is None
            else (
                ' <span class="ok">✓</span>'
                if c.get("ok")
                else f' <span class="bad" title="{esc(c.get("problem"))}">✗</span>'
            )
        )
        out.append(f"<code>{esc(p)}</code>{mark}")
    more = f' <span class="muted">+{len(paths) - 6} more</span>' if len(paths) > 6 else ""
    return "<br>".join(out) + more


def validator(ws: Any, code: str) -> tuple[str, list[str]]:
    cmd = [sys.executable, "-m", "mosaic_catalog", "--catalog", str(ws.catalog), "validate-landscapes", code, "-v"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    lines = [ln.strip() for ln in res.stdout.splitlines() if re.match(r"\s*\[(error|warning)\]", ln)]
    head = next(
        (ln for ln in res.stdout.splitlines() if f" {code} " in ln and ln.startswith(("OK", "ERR"))),
        "validator did not run",
    )
    return head, lines


def build(ws: Any, code: str) -> str:
    folder = ws.landscape_dir(code)
    docs = load_profile(folder)
    prof = docs["profile"]
    ex = docs.get("explorer") or {}
    check_file = ws.work_dir(code) / "data-check.json"
    checks = (
        {f["path"]: f for f in json.loads(check_file.read_text(encoding="utf-8"))["files"]}
        if check_file.exists()
        else {}
    )
    head, problems = validator(ws, code)
    left = {n: todos(load_yaml(folder / n)) for n in PROFILE_FILES if (folder / n).exists()}
    n_todo = sum(len(v) for v in left.values())
    parts = [
        f"<h1>{todo_mark(prof.get('title'))} <span class='pill'>{esc(code)}</span> <span class='pill'>{esc(prof.get('status', 'draft'))}</span></h1>"
    ]
    parts.append(f"<p>{todo_mark(prof.get('summary', ''))}</p>")
    status_cls = "ok" if head.startswith("OK") and not n_todo else "bad" if head.startswith("ERR") else "warn"
    parts.append(
        f"<div class='card'><b class='{status_cls}'>{esc(head)}</b> · {n_todo} TODO left"
        + (
            f" · data check: {sum(1 for c in checks.values() if c.get('ok'))}/{len(checks)} files OK"
            if checks
            else " · data not checked yet (check_data.py)"
        )
        + "".join(f"<br><span class='{'bad' if '[error]' in p else 'warn'}'>{esc(p)}</span>" for p in problems)
        + "</div>"
    )
    parts.append(
        "<h2>Page sections</h2><table><tr><th>#</th><th>id</th><th>kind</th><th>title</th></tr>"
        + "".join(
            f"<tr><td>{i + 1}</td><td><code>{esc(s.get('id'))}</code></td><td>{esc(s.get('kind'))}</td><td>{todo_mark(s.get('title'))}</td></tr>"
            for i, s in enumerate(prof.get("sections") or [])
        )
        + "</table>"
    )
    if ex:
        m = ex.get("map") or {}
        parts.append(
            f"<h2>Map explorer: {todo_mark(ex.get('title'))}</h2><p class=muted>{todo_mark(ex.get('tagline'))}</p>"
        )
        parts.append(
            "<div class='grid'>"
            f"<div class='card'><b>Map</b><br>centre {esc(m.get('center'))} · zoom {esc(m.get('zoom'))}<br>limits {esc(m.get('max_bounds'))}<br>terrain: {'yes' if m.get('terrain') else 'no'}</div>"
            f"<div class='card'><b>Data roots</b><br>{'<br>'.join(f'{esc(k)}: {todo_mark(v)}' for k, v in (ex.get('data') or {}).get('roots', {}).items())}</div>"
            f"<div class='card'><b>Side list</b><br>groups: {esc(', '.join(ex.get('groups') or []))}<br>toggles: {esc(', '.join(t.get('title', t['id']) for t in ex.get('toggles') or [])) or '—'}<br>panels: {esc(', '.join(p.get('title', p['id']) for p in ex.get('panels') or [])) or '—'}</div>"
            "</div>"
        )
        base = list(dict.fromkeys(p for src in (m.get("sources") or {}).values() for p in assets(src)))
        if base:
            parts.append(f"<div class='card'><b>Base map files</b><br>{file_list(base, checks)}</div>")
        rows = []
        for o in ex.get("overlays") or []:
            insp = (o.get("inspect") or {}).get("kind") or ("built in" if "grid" in str(o.get("kind")) else "—")
            rows.append(
                f"<tr><td><span class='sw' style='background:{esc(o.get('swatch') or '#999')}'></span><b>{todo_mark(o.get('title'))}</b><br><code class=muted>{esc(o['id'])}</code> · {esc(o.get('group'))}</td>"
                f"<td>{esc(o.get('kind'))}</td><td>{colours(o.get('legend'))}<br><span class=muted>{todo_mark((o.get('legend') or {}).get('title', ''))}</span></td>"
                f"<td>{esc(insp)}</td><td>{file_list(assets(o), checks)}</td></tr>"
            )
        parts.append(
            "<h2>Layers</h2><table><tr><th>layer</th><th>kind</th><th>legend</th><th>click</th><th>files</th></tr>"
            + "".join(rows)
            + "</table>"
        )
    story = docs.get("story")
    if story:
        parts.append(
            f"<h2>Story: {todo_mark(story.get('title'))}</h2><table><tr><th>chapter</th><th>layers</th><th>extras</th></tr>"
            + "".join(
                f"<tr><td><b>{todo_mark(c.get('title'))}</b><br><span class=muted>{todo_mark(c.get('text', ''))[:220]}</span></td>"
                f"<td>{esc(', '.join((c.get('visual') or {}).get('layers') or [])) or '—'}</td>"
                f"<td>{esc(', '.join(k for k in ('charts', 'steps', 'compare', 'figure', 'focus') if (c.get('visual') or {}).get(k)))}"
                f"{' · ' + str(len(c.get('numbers') or [])) + ' numbers' if c.get('numbers') else ''}</td></tr>"
                for c in story.get("chapters") or []
            )
            + "</table>"
        )
    studies = docs.get("studies")
    if studies:
        parts.append(
            "<h2>Study cards</h2><table><tr><th>question</th><th>kind</th><th>layers</th></tr>"
            + "".join(
                f"<tr><td>{todo_mark(c.get('question'))}<br><span class=muted>{todo_mark(c.get('citation', ''))}</span></td><td>{esc(c.get('kind'))}</td><td>{esc(', '.join(c.get('layers') or [])) or '—'}</td></tr>"
                for c in studies.get("cards") or []
            )
            + "</table>"
        )
    sources = docs.get("sources")
    if sources:
        parts.append(
            "<h2>Sources and licences</h2><table><tr><th>layer</th><th>source</th><th>licence</th><th>catalogue record</th></tr>"
            + "".join(
                f"<tr><td>{todo_mark(s.get('title'))}</td><td>{todo_mark(s.get('source', ''))}</td><td>{todo_mark(s.get('licence', '—'))}</td><td>{esc(s.get('record') or 'not registered')}</td></tr>"
                for s in sources.get("layers") or []
            )
            + "</table>"
        )
    if n_todo:
        parts.append(
            "<h2>Still to fill in</h2>"
            + "".join(
                f"<div class=card><b>{esc(n)}</b><br>{'<br>'.join(f'<code>{esc(p)}</code>' for p in v)}</div>"
                for n, v in left.items()
                if v
            )
        )
    return (
        f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>{esc(code)} profile review</title><style>{CSS}</style></head><body><main>"
        + "".join(parts)
        + "<p class=muted style='margin-top:40px'>Generated by the mosaic-landscape-profile skill (preview.py). The website draws the real page once the pull request is merged.</p>"
        "</main></body></html>"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--code", required=True)
    add_workspace_args(ap)
    args = ap.parse_args(argv)
    ws = workspace(args)
    code = args.code.upper()
    if not (ws.landscape_dir(code) / "profile.yaml").exists():
        print(f"{code} has no profile yet.")
        return 2
    out = ws.work_dir(code) / "preview.html"
    out.write_text(build(ws, code), encoding="utf-8")
    print(f"Preview: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
