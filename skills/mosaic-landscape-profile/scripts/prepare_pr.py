"""Write the title and description of the pull request for a landscape profile (in English).

    python prepare_pr.py --code SEN-FK              # writes <work>/SEN-FK/pr.md and prints it

The description lists what the profile contains, where its data is served, the licences and the
layers that are not catalogue records yet (for the reviewers), the result of the data check and of
the validator. SKILL.md then commits, pushes a branch and opens the pull request with it.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PROFILE_FILES, add_workspace_args, load_profile, load_yaml, md_table, todos, workspace


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--code", required=True)
    ap.add_argument("--change", default="", help="one line on what changed, for an edited profile")
    add_workspace_args(ap)
    args = ap.parse_args(argv)
    ws = workspace(args)
    code = args.code.upper()
    folder = ws.landscape_dir(code)
    if not (folder / "profile.yaml").exists():
        print(f"{code} has no profile.")
        return 2
    docs = load_profile(folder)
    prof, ex = docs["profile"], docs.get("explorer") or {}
    is_new = (
        subprocess.run(
            ["git", "-C", str(ws.catalog), "cat-file", "-e", f"HEAD:landscapes/{code}/profile.yaml"],
            capture_output=True,
        ).returncode
        != 0
    )
    title = f"{'Add' if is_new else 'Update'} the {code} landscape profile" + (
        f": {args.change}" if args.change else ""
    )
    lines = [f"## {prof.get('title')} ({code})", "", prof.get("summary", ""), ""]
    if args.change:
        lines += [f"**Change:** {args.change}", ""]
    lines += [
        "**Sections:** "
        + ", ".join(f"{s.get('title') or s.get('id')} (`{s.get('kind')}`)" for s in prof.get("sections") or []),
        "",
    ]
    if ex:
        rows = [
            [
                o.get("title", ""),
                o.get("group", ""),
                f"`{o.get('kind')}`",
                f"`{(o.get('inspect') or {}).get('kind', '—')}`",
            ]
            for o in ex.get("overlays") or []
        ]
        lines += ["### Map explorer layers", "", md_table(rows, ["layer", "group", "kind", "click"]), ""]
        lines += [
            "**Data served from:** "
            + ", ".join(f"`{v}`" for v in dict.fromkeys((ex.get("data") or {}).get("roots", {}).values())),
            "",
        ]
        if docs.get("story"):
            lines.append(f"**Story:** {len(docs['story'].get('chapters') or [])} chapters")
        if docs.get("studies"):
            lines.append(f"**Study cards:** {len(docs['studies'].get('cards') or [])}")
        lines.append("")
    sources = (docs.get("sources") or {}).get("layers") or []
    if sources:
        rows = [[s.get("title", ""), s.get("licence", "—"), s.get("record") or "not registered"] for s in sources]
        lines += [
            "### Licences and catalogue records (for review)",
            "",
            md_table(rows, ["layer", "licence as stated by the source", "record"]),
            "",
        ]
    check = ws.work_dir(code) / "data-check.json"
    if check.exists():
        files = json.loads(check.read_text(encoding="utf-8"))["files"]
        bad = [f for f in files if not f.get("ok")]
        lines += [
            f"**Data check:** {len(files) - len(bad)} of {len(files)} files readable by the website "
            "(HTTPS, CORS, byte ranges)."
        ]
        lines += [f"- `{f['path']}`: {f.get('problem')}" for f in bad[:15]]
        lines.append("")
    res = subprocess.run(
        [sys.executable, "-m", "mosaic_catalog", "--catalog", str(ws.catalog), "validate-landscapes", code, "-v"],
        capture_output=True,
        text=True,
    )
    verdict = next(
        (ln.strip() for ln in res.stdout.splitlines() if f" {code} " in ln and ln.startswith(("OK", "ERR"))), "not run"
    )
    left = sum(len(todos(load_yaml(folder / n))) for n in PROFILE_FILES if (folder / n).exists())
    lines += [f"**Validator:** `{verdict}` · TODO left: {left}", ""]
    lines += [
        "### Checklist for the reviewer",
        "",
        "- [ ] Texts are the data authors' (nothing invented); numbers cite their source",
        "- [ ] Licences allow showing each layer on the MOSAIC website",
        "- [ ] Data files are served over HTTPS with CORS and byte ranges",
        "- [ ] The page reads well (preview attached or described)",
        "",
        "Prepared with the mosaic-landscape-profile skill (mosaic-standard).",
    ]
    body = "\n".join(lines) + "\n"
    out = ws.work_dir(code) / "pr.md"
    out.write_text(f"{title}\n\n{body}", encoding="utf-8")
    (ws.work_dir(code) / "pr-title.txt").write_text(title + "\n", encoding="utf-8")
    (ws.work_dir(code) / "pr-body.md").write_text(body, encoding="utf-8")
    branch = f"landscape/{code.lower()}-{'profile' if is_new else 'update'}"
    commands = [
        f'cd "{ws.catalog}"',
        f"git switch -c {branch}",
        f"git add landscapes/{code}",
        f'git commit -m "{title}"',
        "git push -u origin HEAD",
        f'gh pr create --base {ws.base} --title "{title}" --body-file "{ws.work_dir(code) / "pr-body.md"}"',
    ]
    print(f"Title: {title}\n\n{body}\nSaved: {out}\n\nCommands (after the person agrees):\n" + "\n".join(commands))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
