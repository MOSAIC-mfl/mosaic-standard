"""Inference reads files and fills only what is absent; a person's value always wins."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from mosaic_catalog.infer import Findings, apply, inspect_file, read_csv, read_geojson
from mosaic_catalog.standard import Standard, Status

shapefile = pytest.importorskip("shapefile")

WGS84 = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]]]'


def _points_shp(folder: Path) -> Path:
    base = folder / "sites"
    with shapefile.Writer(str(base), shapeType=shapefile.POINT) as w:
        w.field("name", "C")
        w.field("count", "N", decimal=0)
        w.point(-74.5, -8.4)
        w.record("a", 1)
        w.point(-74.0, -8.0)
        w.record("b", 2)
    (folder / "sites.prj").write_text(WGS84, encoding="utf-8")
    return base.with_suffix(".shp")


def test_zipped_point_shapefile(tmp_path: Path) -> None:
    shp = _points_shp(tmp_path)
    z = tmp_path / "sites.zip"
    with zipfile.ZipFile(z, "w") as zf:
        for ext in (".shp", ".shx", ".dbf", ".prj"):
            zf.write(shp.with_suffix(ext), f"sites{ext}")
    f = inspect_file(z)
    assert f.kind == "vector" and f.point["geometry_type"] == "point" and f.point["feature_count"] == 2
    assert f.structure["variables"] == [
        {"name": "name", "data_type": "string"},
        {"name": "count", "data_type": "integer"},
    ]
    assert f.record == {"spatial.crs": "EPSG:4326", "spatial.bbox": [-74.5, -8.4, -74.0, -8.0]}


def test_csv_with_coordinates_is_spatial_point_table(tmp_path: Path) -> None:
    p = tmp_path / "plots.csv"
    p.write_text("plot;Latitude;Longitude;yield\n1;-8.4;-74.5;3.2\n", encoding="utf-8")
    f = read_csv(p)
    assert [(d["name"], d["type"], d["unit"]) for d in f.structure["dimensions"]] == [
        ("Longitude", "x", "degree"),
        ("Latitude", "y", "degree"),
    ]
    assert f.structure["variables"] == [{"name": "plot"}, {"name": "yield"}]
    assert f.point["feature_count"] == 1


def test_csv_without_coordinates_is_not_spatial(tmp_path: Path) -> None:
    p = tmp_path / "stats.csv"
    p.write_text("district,population\nA,10\n", encoding="utf-8")
    f = read_csv(p)
    assert "dimensions" not in f.structure and "geometry_column" not in f.structure


def test_geojson_mixed_geometries(tmp_path: Path) -> None:
    p = tmp_path / "x.geojson"
    p.write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [1, 2]}, "properties": {}},
        {"type": "Feature", "geometry": {"type": "LineString", "coordinates": [[0, 0], [3, 4]]}, "properties": {}},
    ]}), encoding="utf-8")  # fmt: skip
    f = read_geojson(p)
    assert f.point["geometry_type"] == "mixed"
    assert f.record["spatial.bbox"] == [0.0, 0.0, 3.0, 4.0]


def test_raster_is_reported_not_guessed(tmp_path: Path) -> None:
    p = tmp_path / "x.tif"
    p.write_bytes(b"II*\x00")
    f = inspect_file(p)
    assert f.point == {} and f.problems


def _record() -> dict:
    return {
        "data": [
            {"name": "x", "kind": "vector", "access_method": "download", "locations": [{"url": "https://x.org/a.zip"}]}
        ]
    }


def test_apply_fills_and_marks_derived() -> None:
    rec = _record()
    found = Findings(kind="vector", point={"geometry_type": "point"}, structure={"variables": [{"name": "a"}]},
                     record={"spatial.crs": "EPSG:4326"})  # fmt: skip
    out = apply(rec, 0, found)
    assert rec["data"][0]["geometry_type"] == "point" and rec["data"][0]["structures"] == ["x"]
    assert rec["structures"] == [{"name": "x", "variables": [{"name": "a"}]}]
    assert rec["derived"] == ["data[].geometry_type", "spatial.crs", "structures"]
    assert out.filled == ["data[0].geometry_type", "structures[x].variables", "spatial.crs"] and not out.conflicts


def test_authored_value_wins_and_conflict_is_reported() -> None:
    rec = _record()
    rec["data"][0]["geometry_type"] = "polygon"
    out = apply(rec, 0, Findings(kind="vector", point={"geometry_type": "point"}))
    assert rec["data"][0]["geometry_type"] == "polygon" and "derived" not in rec
    assert out.conflicts == ["data[0].geometry_type: record says 'polygon', the file says 'point'"]


def test_derived_value_is_refreshed() -> None:
    rec = _record()
    apply(rec, 0, Findings(kind="vector", point={"feature_count": 2}))
    apply(rec, 0, Findings(kind="vector", point={"feature_count": 3}))
    assert rec["data"][0]["feature_count"] == 3


def test_kind_mismatch_is_not_applied() -> None:
    rec = _record()
    rec["data"][0]["kind"] = "raster"
    out = apply(rec, 0, Findings(kind="tabular", point={"feature_count": 3}))
    assert "feature_count" not in rec["data"][0] and out.conflicts


def test_inferred_values_are_valid_in_the_standard(tmp_path: Path) -> None:
    p = tmp_path / "plots.csv"
    p.write_text("plot,lat,lon\n1,-8.4,-74.5\n", encoding="utf-8")
    rec = {"id": "MFL-2099-003", "data": [{"name": "t", "kind": "tabular", "access_method": "download",
                                           "locations": [{"url": "https://x.org/t.csv"}]}]}  # fmt: skip
    apply(rec, 0, read_csv(p))
    assert Standard().check(rec).status is not Status.INVALID
