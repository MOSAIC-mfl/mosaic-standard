"""Schema-1 -> v0.2 migration: conversions keep what the old record says and invent nothing."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

from mosaic_catalog.records import load_record
from mosaic_catalog.standard import Standard, Status

ROOT = Path(__file__).resolve().parents[1]


def _load_migration() -> ModuleType:
    spec = importlib.util.spec_from_file_location("migrate_schema1", ROOT / "scripts" / "migrate_schema1.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mig = _load_migration()


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            "Beatriz Rodríguez (b.rodriguez@cgiar.org)",
            [{"name": "Beatriz Rodríguez", "email": "b.rodriguez@cgiar.org"}],
        ),
        ("Ayman Frija -  a.frija@cgiar.org", [{"name": "Ayman Frija", "email": "a.frija@cgiar.org"}]),
        (
            "Hannes Gaisberger, h.gaisberger@cgiar.org",
            [{"name": "Hannes Gaisberger", "email": "h.gaisberger@cgiar.org"}],
        ),
        ("Degefie Tibebe- d.tibebe@cgiar.org", [{"name": "Degefie Tibebe", "email": "d.tibebe@cgiar.org"}]),
        ("z.guo@cgiar.org", [{"email": "z.guo@cgiar.org"}]),
        (
            "Core Stack (Open access)\nSudharsan Malaiappan - s.maliappan@cgiar.org",
            [
                {"organization": "Core Stack (Open access)"},
                {"name": "Sudharsan Malaiappan", "email": "s.maliappan@cgiar.org"},
            ],
        ),
    ],
)
def test_contact_strings(raw: str, expected: list[dict[str, str]]) -> None:
    got = mig.to_contacts(raw, None)
    assert [{k: v for k, v in c.items() if k != "roles"} for c in got] == expected
    assert all(c["roles"] == ["point-of-contact"] for c in got)


def test_source_becomes_producer() -> None:
    assert mig.to_contacts(None, "ICARDA") == [{"organization": "ICARDA", "roles": ["producer"]}]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2001 to 2025", {"start": "2001", "end": "2025"}),
        ("1981 – présent", {"start": "1981", "end": None}),
        ("2000, 2005, 2010", {"start": "2000", "end": "2010"}),
        ("Till 2019", {"end": "2019"}),
        ("2015", {"start": "2015", "end": "2015"}),
        ("Current boundaries", {}),
    ],
)
def test_temporal_keeps_the_text(raw: str, expected: dict[str, str | None]) -> None:
    assert mig.to_temporal(raw) == {**expected, "text": raw}


def test_temporal_placeholder_is_dropped() -> None:
    assert mig.to_temporal("NA") is None


def test_license() -> None:
    notes = mig.Notes()
    assert mig.to_license("CC BY 4.0", "x", notes) == {
        "spdx": "CC-BY-4.0",
        "url": "https://spdx.org/licenses/CC-BY-4.0.html",
        "text": None,
    }
    gadm = mig.to_license("Source terms (https://gadm.org/license.html)", "x", notes)
    assert gadm == {
        "spdx": None,
        "url": "https://gadm.org/license.html",
        "text": "Source terms (https://gadm.org/license.html)",
    }
    assert mig.to_license("Other (specify in notes)", "x", notes) == {"spdx": None, "url": None, "text": None}
    mig.to_license("Restricted — contact data owner", "x", notes)
    assert [n[1] for n in notes.rows] == ["license", "license"]


def test_restricted_text_becomes_access_note_and_request_point() -> None:
    old = {"download_url": "Internal Available on Request", "data_type": "Vector"}
    points, note = mig.to_data(old, "restricted", "x", mig.Notes())
    assert note == "Internal Available on Request"
    assert points == [
        {"name": "Data held by the owner (on request)", "kind": "vector", "method": "request", "access": "restricted"}
    ]


def test_url_kind_and_method() -> None:
    old = {
        "download_url": "https://a.org/x.zip https://b.org/page",
        "data_type": "Raster",
        "spatial_resolution": "30 m",
    }
    points, note = mig.to_data(old, "public", "x", mig.Notes())
    assert note is None
    assert [(p["kind"], p["method"]) for p in points] == [("raster", "download"), ("raster", "landing_page")]
    assert points[0]["raster"] == {"resolution": {"value": 30, "unit": "m"}}


def test_gee_asset_has_no_public_url() -> None:
    old = {"gee_asset_id": "projects/p/assets/a", "data_type": "Raster", "download_url": "https://a.org/x.tif"}
    points, _ = mig.to_data(old, "public", "x", mig.Notes())
    ee = points[-1]
    assert ee["method"] == "service" and ee["access"] == "internal" and "url" not in ee


def test_migrated_records_are_never_invalid(catalog: Path) -> None:
    """The catalogue's records/ must load and be at worst incomplete."""
    std = Standard()
    files = sorted((catalog / "records").glob("*/record.yaml"))
    if not files:
        pytest.skip("records/ not migrated yet")
    for f in files:
        rec = load_record(f)
        assert rec.data is not None, rec.error
        assert std.check(rec.data).status is not Status.INVALID, f


def test_build_outputs(tmp_path: Path, empty_catalog: Path) -> None:
    from mosaic_catalog.build import build

    res = build(ROOT / "examples", tmp_path)  # examples/ is flat: build reads <id>/record.yaml
    assert res.published == 0
    rec_dir = tmp_path / "records"
    for f in (ROOT / "examples").glob("*.yaml"):
        (rec_dir / f.stem).mkdir(parents=True)
        (rec_dir / f.stem / "record.yaml").write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    out = tmp_path / "dist"
    res = build(rec_dir, out)
    assert res.published == 3 and not res.invalid
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    # v0.2: no example says who grants the licence (licensor), so none is complete
    assert manifest["counts"]["complete"] == 0 and manifest["counts"]["incomplete"] == 3
    catalog = json.loads((out / "catalog.json").read_text(encoding="utf-8"))
    rec = {r["id"]: r for r in catalog["records"]}["MFL-2026-999"]
    assert rec["meta"]["missing_minimum"] == ["contact"] and rec["schema_version"] == "0.2.0"
    assert (out / "schema" / "record.schema.json").exists()


def test_v01_to_v02_moves_and_renames_only() -> None:
    from mosaic_catalog.v02 import convert

    old = {
        "id": "MFL-2099-002", "geography": ["PER"], "update_frequency": "annual",
        "license": {"spdx": None, "url": "https://x.org/terms", "text": "Source terms"},
        "contacts": [{"organization": "X", "roles": ["producer"]}], "access": "internal",
        "citation": "Someone (2020). Data.",
        "temporal": {"start": "2001", "end": "2001", "text": "2001"},
        "data": [{"name": "Shapefile", "kind": "vector", "method": "download", "url": "https://x.org/a.zip",
                  "size": "1.2 MB", "vector": {"geometry_type": "polygon", "feature_count": 3, "crs": "EPSG:4326",
                                               "attributes": [{"name": "code", "type": "string"}]},
                  "derived": ["vector.geometry_type"]}],
        "mosaic": {"landscapes": ["PER-PCL"], "intake": {"status": "published"}},
    }  # fmt: skip
    new, notes = convert(old)
    assert new["spatial"] == {"geography": ["PER"], "landscapes": ["PER-PCL"]}
    assert new["temporal"] == {"date": "2001", "text": "2001", "update_frequency": "annual"}
    assert new["license"] == "LicenseRef-source-terms" and new["license_text"] == "Source terms"
    assert new["additional_links"] == [{"rel": "license", "url": "https://x.org/terms"}]
    assert new["access"] == "non-public" and new["contact"] == old["contacts"]
    assert new["citation"] == {"text": "Someone (2020). Data."}
    d = new["data"][0]
    assert d["locations"] == [{"url": "https://x.org/a.zip"}] and d["access_method"] == "download"
    assert (d["geometry_type"], d["feature_count"], d["spatial"], d["file_size"]) == (
        "polygon",
        3,
        {"crs": "EPSG:4326"},
        "1.2 MB",
    )
    assert new["structures"] == [{"name": "Shapefile", "variables": [{"name": "code", "data_type": "string"}]}]
    assert new["derived"] == ["data[].geometry_type"] and "mosaic" not in new
    assert [f for f, _ in notes] == ["license"]
    assert convert(new) == (new, [])  # already v0.2: unchanged
    assert Standard().check(new).status is not Status.INVALID
