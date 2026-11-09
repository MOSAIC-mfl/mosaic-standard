"""Tests that read the real catalogue (records/, landscapes/) need a checkout of MOSAIC-mfl/catalog:
set MOSAIC_CATALOG (the CI clones it). Without it they are skipped; the rest use this repository."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

from mosaic_catalog.config import set_catalog


@pytest.fixture
def catalog() -> Iterator[Path]:
    path = os.environ.get("MOSAIC_CATALOG")
    if not path or not (Path(path) / "records").is_dir() or not (Path(path) / "landscapes").is_dir():
        pytest.skip("needs a catalogue checkout (records/ and landscapes/): set MOSAIC_CATALOG")
    set_catalog(path)
    yield Path(path)
    set_catalog(None)


@pytest.fixture
def empty_catalog(tmp_path: Path) -> Iterator[Path]:
    """A catalogue with no records and no curated landscape profiles."""
    (tmp_path / "catalog" / "records").mkdir(parents=True)
    set_catalog(tmp_path / "catalog")
    yield tmp_path / "catalog"
    set_catalog(None)
