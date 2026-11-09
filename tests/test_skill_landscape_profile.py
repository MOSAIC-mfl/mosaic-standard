"""The scripts of the mosaic-landscape-profile skill (skills/mosaic-landscape-profile/scripts).

They run on copies in a temporary folder: a catalogue with records/ and landscapes/ (the real one
when MOSAIC_CATALOG is set, for the tests that copy KEN-LVB and PER-PCL), and a work folder."""

from __future__ import annotations

import importlib
import json
import os
import re
import shutil
import sys
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import ModuleType
from typing import Any, ClassVar

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "mosaic-landscape-profile"
SCRIPTS = SKILL / "scripts"


def script(name: str) -> ModuleType:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    return importlib.import_module(name)


@pytest.fixture(autouse=True)
def no_saved_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Never read or write the person's ~/.mosaic/workspace.json, and let the validator import this checkout."""
    monkeypatch.setenv("MOSAIC_WORKSPACE_FILE", str(tmp_path / "workspace.json"))
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join([str(ROOT / "src"), os.environ.get("PYTHONPATH", "")]))
    common = script("_common")
    monkeypatch.setattr(common, "CONFIG", tmp_path / "workspace.json")


def ws_args(cat: Path, work: Path) -> list[str]:
    return ["--standard", str(ROOT), "--catalog", str(cat), "--work", str(work)]


@pytest.fixture
def blank(tmp_path: Path) -> tuple[Path, Path]:
    """A catalogue with no records and no profiles, and a work folder."""
    cat = tmp_path / "catalog"
    (cat / "records").mkdir(parents=True)
    (cat / "landscapes").mkdir()
    return cat, tmp_path / "work"


@pytest.fixture
def real(catalog: Path, tmp_path: Path) -> Iterator[tuple[Path, Path]]:
    """A copy of the real catalogue (records + landscapes), so the scripts can change it."""
    cat = tmp_path / "catalog"
    shutil.copytree(catalog / "records", cat / "records")
    shutil.copytree(catalog / "landscapes", cat / "landscapes")
    yield cat, tmp_path / "work"


def validate(cat: Path, work: Path, code: str, *extra: str) -> int:
    rc: int = script("validate").main(["--code", code, *extra, *ws_args(cat, work)])
    return rc


def new(cat: Path, work: Path, *argv: str) -> int:
    rc: int = script("new_profile").main([*argv, *ws_args(cat, work)])
    return rc


def load(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def fill_todos(node: Any) -> Any:
    """Replace every TODO text with a plain value of the same kind (what the person would write)."""
    if isinstance(node, dict):
        return {k: fill_todos(v) for k, v in node.items()}
    if isinstance(node, list):
        return [fill_todos(v) for v in node]
    if isinstance(node, str) and "TODO" in node:
        if node.startswith("https://TODO"):
            return "https://data.example.org/data/"
        return node.replace("TODO", "Filled")
    return node


# --- new_profile -------------------------------------------------------------------------------


def test_template_default_is_valid_once_filled(blank: tuple[Path, Path], capsys: pytest.CaptureFixture[str]) -> None:
    cat, work = blank
    assert new(cat, work, "--code", "TUN-NW", "--template", "default") == 0
    folder = cat / "landscapes" / "TUN-NW"
    assert sorted(p.name for p in folder.iterdir()) == ["profile.yaml"]
    assert (work / "TUN-NW" / "checklist.md").exists()
    assert validate(cat, work, "TUN-NW", "--allow-todo") == 0
    assert validate(cat, work, "TUN-NW") == 1  # TODOs left
    out = capsys.readouterr().out
    assert "TODO placeholders still to fill in" in out


def test_template_explorer_with_story_and_studies(blank: tuple[Path, Path]) -> None:
    cat, work = blank
    assert new(cat, work, "--code", "COL-CUM", "--template", "explorer", "--with-story", "--with-studies") == 0
    folder = cat / "landscapes" / "COL-CUM"
    assert {p.name for p in folder.iterdir()} == {
        "profile.yaml",
        "explorer.yaml",
        "story.yaml",
        "studies.yaml",
        "sources.yaml",
    }
    ex = load(folder / "explorer.yaml")
    assert ex["map"]["center"] and "__" not in json.dumps(ex)  # placeholders of the camera filled in
    assert ex["story"] == {"file": "story.yaml"}
    assert validate(cat, work, "COL-CUM", "--allow-todo") == 0
    for f in folder.iterdir():
        f.write_text(yaml.safe_dump(fill_todos(load(f)), sort_keys=False, allow_unicode=True), encoding="utf-8")
    assert validate(cat, work, "COL-CUM") == 0


def test_unknown_code_and_existing_folder(blank: tuple[Path, Path]) -> None:
    cat, work = blank
    assert new(cat, work, "--code", "XXX-ZZ", "--template", "default") == 3
    assert new(cat, work, "--code", "TUN-NW", "--template", "default") == 0
    assert new(cat, work, "--code", "TUN-NW", "--template", "default") == 4
    assert new(cat, work, "--code", "TUN-NW", "--template", "default", "--force") == 0


def test_like_copies_structure_not_content(real: tuple[Path, Path]) -> None:
    cat, work = real
    assert new(cat, work, "--code", "SEN-FK", "--like", "PER-PCL", "--only", "landcover,precip,spi3") == 0
    folder = cat / "landscapes" / "SEN-FK"
    prof, ex = load(folder / "profile.yaml"), load(folder / "explorer.yaml")
    assert prof["landscape"] == "SEN-FK" and prof["status"] == "draft"
    assert "TODO" in prof["summary"] and "TODO" in prof["credits"][0]["name"]
    assert next(s for s in prof["sections"] if s["kind"] == "map-explorer")["title"].startswith("TODO")
    assert [o["id"] for o in ex["overlays"]] == ["landcover", "precip", "spi3"]
    assert set(ex["data"]["roots"].values()) == {"https://TODO.example.org/data/"}
    assert "withheld" not in ex["data"] and "story" not in ex and "studies" not in ex
    assert not (folder / "story.yaml").exists()
    sources = load(folder / "sources.yaml")["layers"]
    used = {o.get("source_ref") for o in ex["overlays"] + ex.get("toggles", []) + ex.get("panels", [])} - {None}
    assert {s["id"] for s in sources} == used
    assert all(s["licence"].startswith("TODO") and s["record"] is None for s in sources)
    # the camera is the new landscape's, not Ucayali's
    w, s, e, n = script("_common").Workspace(ROOT, cat, work).vocab()["SEN-FK"]["bbox"]
    assert w <= ex["map"]["center"][0] <= e and s <= ex["map"]["center"][1] <= n
    assert validate(cat, work, "SEN-FK", "--allow-todo") == 0


def test_like_rejects_unknown_overlay(real: tuple[Path, Path]) -> None:
    cat, work = real
    with pytest.raises(SystemExit, match="nope"):
        new(cat, work, "--code", "SEN-FK", "--like", "PER-PCL", "--only", "landcover,nope")


# --- edit_profile ------------------------------------------------------------------------------


def test_remove_overlay_cascades(real: tuple[Path, Path], capsys: pytest.CaptureFixture[str]) -> None:
    cat, work = real
    edit = script("edit_profile")
    folder = cat / "landscapes" / "KEN-LVB"
    head = (folder / "explorer.yaml").read_text(encoding="utf-8").splitlines()[0]
    assert edit.main(["remove-overlay", "--code", "KEN-LVB", "--id", "fire", *ws_args(cat, work)]) == 0
    out = capsys.readouterr().out
    assert "removed layer 'fire'" in out
    ex = load(folder / "explorer.yaml")
    assert "fire" not in {o["id"] for o in ex["overlays"]}
    assert "Fire" in ex["groups"]  # burned_area is still in it
    assert edit.main(["remove-overlay", "--code", "KEN-LVB", "--id", "population", *ws_args(cat, work)]) == 0
    assert "Exposure" not in load(folder / "explorer.yaml")["groups"]  # its only layer was removed
    assert (folder / "explorer.yaml").read_text(encoding="utf-8").splitlines()[0] == head  # comments kept
    text = (folder / "story.yaml").read_text(encoding="utf-8") + (folder / "studies.yaml").read_text(encoding="utf-8")
    assert not re.search(r"(layers:.*\bfire\b)|(layer: fire\b)", text)
    assert "fire" not in {s["id"] for s in load(folder / "sources.yaml")["layers"]}
    assert validate(cat, work, "KEN-LVB") == 0
    assert edit.main(["remove-overlay", "--code", "KEN-LVB", "--id", "fire", *ws_args(cat, work)]) == 2


def test_set_root_requires_https(blank: tuple[Path, Path]) -> None:
    cat, work = blank
    new(cat, work, "--code", "COL-CUM", "--template", "explorer")
    edit = script("edit_profile")
    assert (
        edit.main(["set-root", "--code", "COL-CUM", "--root", "main", "--url", "http://x.org/d/", *ws_args(cat, work)])
        == 2
    )
    assert (
        edit.main(["set-root", "--code", "COL-CUM", "--root", "main", "--url", "https://x.org/d/", *ws_args(cat, work)])
        == 0
    )
    assert load(cat / "landscapes" / "COL-CUM" / "explorer.yaml")["data"]["roots"]["main"] == "https://x.org/d/"


# --- inventory ---------------------------------------------------------------------------------


def test_inventory_suggests_modules(blank: tuple[Path, Path], tmp_path: Path) -> None:
    cat, work = blank
    layers = {
        "layers": [
            {"id": "terrain", "type": "raster-dem", "urls": {"pmtiles": "tiles/terrain.pmtiles"}},
            {
                "id": "landcover",
                "type": "raster",
                "classes": [{"value": 1}],
                "urls": {
                    "tiles": {"2020": "tiles/lc_2020.pmtiles", "2021": "tiles/lc_2021.pmtiles"},
                    "query": "query/lc.tif",
                },
            },
            {"id": "precip", "type": "climate", "urls": {"grid": "climate/app/"}},
            {"id": "spi3", "type": "climate-monthly", "urls": {"stack": "climate/app/spi3.tif"}},
            {
                "id": "canopy",
                "type": "raster",
                "urls": {"pmtiles": "tiles/canopy.pmtiles", "query": "query/canopy.tif"},
            },
            {"id": "parks", "type": "vector", "urls": {"geojson": "vectors/parks.geojson"}},
            {"id": "lake", "type": "timeseries-point", "urls": {"series": "series/lake.json"}},
        ]
    }
    f = tmp_path / "layers.json"
    f.write_text(json.dumps(layers), encoding="utf-8")
    assert script("inventory").main(["--layers", str(f), "--code", "SEN-FK", *ws_args(cat, work)]) == 0
    got = {
        item["id"]: (item["module"], item["click"])
        for item in json.loads((work / "SEN-FK" / "inventory.json").read_text())["layers"]
    }
    assert got["terrain"][0].startswith("map.sources")
    assert got["landcover"] == ("year-tiles", "class-at-point (band_per_year)")
    assert got["precip"][0] == "climate-grid" and got["spi3"][0] == "index-grid"
    assert got["canopy"] == ("raster-tiles", "value-at-point")
    assert got["parks"][1] == "feature-attributes"
    assert got["lake"][0].startswith("panels")
    assert (work / "SEN-FK" / "inventory.md").exists()


# --- check_data --------------------------------------------------------------------------------


class _Files(BaseHTTPRequestHandler):
    cors = True
    ranges = True
    present: ClassVar[set[str]] = set()

    def do_GET(self) -> None:
        path = self.path.lstrip("/")
        if path not in self.present:
            self.send_response(404)
            self.end_headers()
            return
        body = b"0123456789abcdef" * 4
        ranged = self.ranges and self.headers.get("Range")
        self.send_response(206 if ranged else 200)
        if self.cors:
            self.send_header("Access-Control-Allow-Origin", "*")
        if ranged:
            self.send_header("Content-Range", f"bytes 0-15/{len(body)}")
            body = body[:16]
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: Any) -> None:
        pass


@pytest.fixture
def server() -> Iterator[tuple[str, type[_Files]]]:
    handler = type("Files", (_Files,), {"present": set()})
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}/", handler
    httpd.shutdown()


def local_profile(cat: Path, work: Path, root: str) -> Path:
    new(cat, work, "--code", "COL-CUM", "--template", "explorer")
    path = cat / "landscapes" / "COL-CUM" / "explorer.yaml"
    ex = load(path)
    ex["data"]["roots"]["main"] = root
    ex["overlays"][0]["asset"] = "tiles/layer.pmtiles"
    ex["map"]["sources"] = {"area": {"type": "geojson", "data": {"asset": "vectors/area.geojson"}}}
    path.write_text(yaml.safe_dump(ex, sort_keys=False), encoding="utf-8")
    return path


def test_check_data_ok(blank: tuple[Path, Path], server: tuple[str, type[_Files]]) -> None:
    cat, work = blank
    root, handler = server
    local_profile(cat, work, root)
    handler.present = {"tiles/layer.pmtiles", "vectors/area.geojson"}
    assert script("check_data").main(["--code", "COL-CUM", *ws_args(cat, work)]) == 0
    files = {f["path"]: f for f in json.loads((work / "COL-CUM" / "data-check.json").read_text())["files"]}
    assert set(files) == {"tiles/layer.pmtiles", "vectors/area.geojson"}
    assert all(f["ok"] for f in files.values()) and files["tiles/layer.pmtiles"]["size"] == 64


def test_check_data_reports_cors_ranges_and_missing(blank: tuple[Path, Path], server: tuple[str, type[_Files]]) -> None:
    cat, work = blank
    root, handler = server
    local_profile(cat, work, root)
    handler.present = {"tiles/layer.pmtiles"}
    handler.cors = False
    handler.ranges = False
    assert script("check_data").main(["--code", "COL-CUM", *ws_args(cat, work)]) == 1
    files = {f["path"]: f for f in json.loads((work / "COL-CUM" / "data-check.json").read_text())["files"]}
    assert (
        "CORS" in files["tiles/layer.pmtiles"]["problem"] and "byte ranges" in files["tiles/layer.pmtiles"]["problem"]
    )
    assert "404" in files["vectors/area.geojson"]["problem"]


def test_check_data_todo_root(blank: tuple[Path, Path]) -> None:
    cat, work = blank
    new(cat, work, "--code", "COL-CUM", "--template", "explorer")
    assert script("check_data").main(["--code", "COL-CUM", *ws_args(cat, work)]) == 1
    files = json.loads((work / "COL-CUM" / "data-check.json").read_text())["files"]
    assert files and all(f["problem"] == "data root still TODO" for f in files)


# --- preview and pull request ------------------------------------------------------------------


def test_preview_and_pr(real: tuple[Path, Path], capsys: pytest.CaptureFixture[str]) -> None:
    cat, work = real
    assert script("preview").main(["--code", "KEN-LVB", *ws_args(cat, work)]) == 0
    page = (work / "KEN-LVB" / "preview.html").read_text(encoding="utf-8")
    assert "<title>KEN-LVB profile review</title>" in page
    assert "Years flooded" in page and "flood-query" in page and "Study cards" in page
    new(cat, work, "--code", "SEN-FK", "--like", "PER-PCL", "--only", "landcover")
    assert script("preview").main(["--code", "SEN-FK", *ws_args(cat, work)]) == 0
    assert "Still to fill in" in (work / "SEN-FK" / "preview.html").read_text(encoding="utf-8")
    capsys.readouterr()
    assert script("prepare_pr").main(["--code", "SEN-FK", *ws_args(cat, work)]) == 0
    out = capsys.readouterr().out
    assert (work / "SEN-FK" / "pr-title.txt").read_text().strip() == "Add the SEN-FK landscape profile"
    body = (work / "SEN-FK" / "pr-body.md").read_text(encoding="utf-8")
    assert "### Map explorer layers" in body and "Checklist for the reviewer" in body
    assert "gh pr create --base" in out and "git add landscapes/SEN-FK" in out


# --- the skill's own files ---------------------------------------------------------------------


def test_errors_reference_matches_validate() -> None:
    patterns = [p for p, _, _ in script("validate").EXPLAIN]
    doc = (SKILL / "references" / "errors.md").read_text(encoding="utf-8")
    missing = [p for p in patterns if f"`{p.replace('|', chr(92) + '|')}`" not in doc]
    assert not missing, f"references/errors.md lacks: {missing}"


def test_skill_md_names_existing_scripts_and_references() -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\nname: mosaic-landscape-profile\ndescription: ")
    for name in re.findall(r"scripts/(\w+\.py)", text):
        assert (SCRIPTS / name).exists(), name
    for name in re.findall(r"references/([\w-]+\.md)", text):
        assert (SKILL / "references" / name).exists(), name


def test_templates_are_english_yaml() -> None:
    for f in (SKILL / "templates").glob("*.yaml"):
        text = f.read_text(encoding="utf-8")
        yaml.safe_load(text.replace("__CENTER__", "[0, 0]").replace("__MAX_BOUNDS__", "[[0, 0], [1, 1]]"))
        assert not re.search(r"[áéíóúñ¿¡]", text), f"{f.name} is not in English"
