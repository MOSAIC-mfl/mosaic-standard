"""Prepare the workspace: the MOSAIC standard and the catalogue, ready to write a landscape profile.

    python setup.py                          # clones both into ~/mosaic (or updates them)
    python setup.py --workspace D:/Code/Mosaic
    python setup.py --standard D:/Code/Mosaic/mosaic-standard --catalog D:/Code/Mosaic/_publish/catalog

What it does:
1. clones MOSAIC-mfl/mosaic-standard and MOSAIC-mfl/catalog (or uses the checkouts you name) and,
   when they have no local changes, brings them up to date;
2. puts the catalogue on the branch that holds the landscape profiles (main once it has
   landscapes/, otherwise metadata-standard-v0.1);
3. installs the standard's tool for this Python (pip install -e), so the validator runs;
4. writes the paths to ~/.mosaic/workspace.json for the other scripts;
5. checks git and the GitHub CLI (gh) for the pull request at the end.

It never changes a file you edited and never pushes anything.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import CONFIG

STANDARD_REPO = "https://github.com/MOSAIC-mfl/mosaic-standard.git"
CATALOG_REPO = "https://github.com/MOSAIC-mfl/catalog.git"
CATALOG_BRANCH_BEFORE_MERGE = "metadata-standard-v0.1"


def git(repo: Path, *args: str, check: bool = True) -> str:
    res = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} in {repo}: {res.stderr.strip()}")
    return res.stdout.strip()


def ensure_clone(path: Path, url: str) -> str:
    if (path / ".git").exists():
        return "found"
    path.parent.mkdir(parents=True, exist_ok=True)
    res = subprocess.run(["git", "clone", "--quiet", url, str(path)], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"git clone {url}: {res.stderr.strip()}")
    return "cloned"


def update(path: Path) -> str:
    if git(path, "status", "--porcelain"):
        return "has local changes: not updated"
    git(path, "fetch", "--quiet", "origin", check=False)
    branch = git(path, "rev-parse", "--abbrev-ref", "HEAD")
    if not git(path, "ls-remote", "--heads", "origin", branch, check=False):
        return f"on {branch} (not on GitHub yet)"
    res = subprocess.run(
        ["git", "-C", str(path), "merge", "--ff-only", "--quiet", f"origin/{branch}"], capture_output=True, text=True
    )
    return (
        f"up to date on {branch}"
        if res.returncode == 0
        else f"on {branch}: could not fast-forward ({res.stderr.strip()[:80]})"
    )


def base_branch(path: Path) -> str:
    """The catalogue branch pull requests go to: main once it has landscapes/, else the review branch."""
    has = subprocess.run(["git", "-C", str(path), "cat-file", "-e", "origin/main:landscapes"], capture_output=True)
    return "main" if has.returncode == 0 else CATALOG_BRANCH_BEFORE_MERGE


def catalog_branch(path: Path, base: str) -> str:
    """Stay on a branch that has the profiles (the base or your own landscape/... branch); else switch to the base."""
    if (path / "landscapes").is_dir() and not (path / "mosaic.config.yaml").exists():
        return git(path, "rev-parse", "--abbrev-ref", "HEAD")
    if git(path, "status", "--porcelain"):
        raise RuntimeError(f"{path} has local changes and is not on the branch with landscapes/")
    git(path, "fetch", "--quiet", "origin", base, check=False)
    git(path, "checkout", "--quiet", base)
    return base


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workspace", type=Path, default=Path.home() / "mosaic", help="where to clone (default ~/mosaic)")
    ap.add_argument("--standard", type=Path, help="an existing checkout of mosaic-standard")
    ap.add_argument("--catalog", type=Path, help="an existing checkout of the catalogue")
    ap.add_argument("--no-install", action="store_true", help="do not pip install the standard")
    args = ap.parse_args(argv)

    if not shutil.which("git"):
        print("git is not installed: install it from https://git-scm.com/ and run this again.")
        return 2
    ws = args.workspace.expanduser().resolve()
    standard = (args.standard or ws / "mosaic-standard").expanduser().resolve()
    catalog = (args.catalog or ws / "catalog").expanduser().resolve()
    report: list[str] = []
    try:
        report.append(f"standard: {standard} ({ensure_clone(standard, STANDARD_REPO)}, {update(standard)})")
        report.append(f"catalogue: {catalog} ({ensure_clone(catalog, CATALOG_REPO)}, {update(catalog)})")
        base = base_branch(catalog)
        branch = catalog_branch(catalog, base)
        report.append(f"catalogue: working on branch {branch}; pull requests go to {base}")
    except RuntimeError as err:
        print(f"Setup stopped: {err}")
        return 1

    if not args.no_install:
        res = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "-e", str(standard)], capture_output=True, text=True
        )
        if res.returncode != 0:
            print(f"pip install failed:\n{res.stderr[-1500:]}")
            return 1
        report.append(f"validator installed for {sys.executable}")

    work = catalog.parent / "work"
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(
        json.dumps(
            {
                "standard": str(standard),
                "catalog": str(catalog),
                "work": str(work),
                "base": base,
                "python": sys.executable,
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    report.append(f"workspace saved in {CONFIG}; files made for you go to {work}")

    gh = shutil.which("gh")
    if not gh:
        report.append("GitHub CLI (gh) not found: the pull request will have to be opened on github.com (see SKILL.md)")
    else:
        auth = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
        report.append("gh: signed in" if auth.returncode == 0 else "gh: not signed in (run: gh auth login)")
    landscapes = (
        sorted(p.name for p in (catalog / "landscapes").iterdir() if p.is_dir())
        if (catalog / "landscapes").is_dir()
        else []
    )
    report.append(f"curated profiles in the catalogue: {', '.join(landscapes) or 'none'}")
    print("\n".join(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
