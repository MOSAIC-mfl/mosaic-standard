"""Landscape profiles: every landscape gets a page, and references between profile files are checked."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml

from mosaic_catalog import landscapes as ls
from mosaic_catalog.config import Config, landscapes_dir

SECTIONS = Config.load().landscape_sections
pytestmark = pytest.mark.usefixtures("catalog")  # every test reads the real landscapes/ (conftest.py)


def test_every_landscape_of_the_vocabulary_has_a_valid_profile() -> None:
    profiles = ls.load_all(SECTIONS)
    assert {p.code for p in profiles} == set(ls.vocab())
    assert all(p.ok for p in profiles), [str(x) for p in profiles for x in p.problems if x.level == "error"]
    lvb = next(p for p in profiles if p.code == "KEN-LVB")
    assert lvb.curated and lvb.sections[0]["kind"] == "map-explorer"
    pcl = next(p for p in profiles if p.code == "PER-PCL")
    assert pcl.curated and pcl.sections[0]["kind"] == "map-explorer"
    default = next(p for p in profiles if p.code == "SEN-FK")
    assert not default.curated and [s["kind"] for s in default.sections] == list(SECTIONS)


def _copy(tmp: Path, code: str = "KEN-LVB") -> Path:
    dst = tmp / code
    shutil.copytree(landscapes_dir() / code, dst)
    return dst


def _edit(path: Path, change) -> None:  # type: ignore[no-untyped-def]
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _errors(folder: Path) -> list[str]:
    p = ls.load_profile(folder, ls.vocab(), ls.record_ids())
    return [f"{x.where} {x.message}" for x in p.problems if x.level == "error"]


@pytest.mark.parametrize(
    ("file", "change", "expected"),
    [
        ("explorer.yaml", lambda d: d["overlays"][0].update(before="nope"), "'nope' is not in map.layers"),
        ("explorer.yaml", lambda d: d["overlays"][0].update(group="Weather"), "group 'Weather' is not in groups"),
        ("explorer.yaml", lambda d: d["overlays"][0].update(record="mosaic:MFL-1999-001"), "does not exist"),
        ("explorer.yaml", lambda d: d["toggles"][0]["layers"].append("ghost"), "layer 'ghost' is not in map.layers"),
        ("explorer.yaml", lambda d: d["data"].update(default_root="s3"), "is not one of the roots"),
        ("story.yaml", lambda d: d["chapters"][1]["visual"].update(layers=["rain"]), "'rain' is not an overlay"),
        ("studies.yaml", lambda d: d["cards"][0].update(open_panel="dam"), "'dam' is not a panel"),
        ("studies.yaml", lambda d: d["cards"][0].pop("finding"), "'finding' is a required property"),
        (
            "studies.yaml",
            lambda d: d["cards"][0].update(steps=[{"label": "x", "layer": "rain"}]),
            "'rain' is not an overlay",
        ),
        (
            "story.yaml",
            lambda d: d["chapters"][1]["visual"].update(steps=[{"label": "x", "layer": "rain"}]),
            "'rain' is not an overlay",
        ),
        ("profile.yaml", lambda d: d.update(landscape="KEN-LEI"), "!= folder"),
    ],
)
def test_broken_references_are_errors(tmp_path: Path, file: str, change, expected: str) -> None:  # type: ignore[no-untyped-def]
    folder = _copy(tmp_path)
    assert _errors(folder) == []
    _edit(folder / file, change)
    assert any(expected in e for e in _errors(folder)), _errors(folder)


def test_unknown_section_kind_is_a_warning_not_an_error(tmp_path: Path) -> None:
    folder = _copy(tmp_path)
    _edit(folder / "profile.yaml", lambda d: d["sections"].append({"id": "hub", "kind": "action-hub"}))
    p = ls.load_profile(folder, ls.vocab(), ls.record_ids())
    assert p.ok and any("action-hub" in x.message for x in p.problems if x.level == "warning")


def test_bundle_inlines_the_explorer_files() -> None:
    p = next(p for p in ls.load_all(SECTIONS) if p.code == "KEN-LVB")
    doc = ls.bundle(p, ls.vocab())
    cfg = doc["sections"][0]["config"]
    assert doc["landscape"]["label"] == "Lake Victoria Basin (Kenya)"
    assert cfg["story"]["chapters"] and cfg["studies"]["cards"]
    assert isinstance(cfg["about"]["sources"], list)  # sources.yaml inlined
    json.dumps(doc)  # one JSON document
