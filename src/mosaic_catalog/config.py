"""Configuration: where the standard is (this repository) and where the catalogue is.

The standard (schemas, vocabularies, crosswalks, mosaic.config.yaml) lives in this repository,
MOSAIC-mfl/mosaic-standard. The catalogue - only the records and the landscape profiles - lives in
MOSAIC-mfl/catalog. Every command that reads records or profiles needs the catalogue checkout:
``--catalog PATH`` on the command line, or the environment variable MOSAIC_CATALOG.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = ROOT / "mosaic.config.yaml"

_catalog: Path | None = None


class CatalogNotSet(RuntimeError):
    def __init__(self) -> None:
        super().__init__(
            "where is the catalogue? pass --catalog PATH (a checkout of MOSAIC-mfl/catalog, with records/ and "
            "landscapes/) or set MOSAIC_CATALOG"
        )


def set_catalog(path: Path | str | None) -> None:
    """The catalogue checkout for this process (the CLI's --catalog)."""
    global _catalog
    _catalog = Path(path).resolve() if path else None


def catalog_root() -> Path:
    """The catalogue checkout: --catalog, else MOSAIC_CATALOG."""
    if _catalog:
        return _catalog
    env = os.environ.get("MOSAIC_CATALOG")
    if env:
        return Path(env).resolve()
    raise CatalogNotSet()


def records_dir() -> Path:
    return catalog_root() / "records"


def landscapes_dir() -> Path:
    return catalog_root() / "landscapes"


@dataclass(frozen=True)
class Config:
    standard_version: str
    enforced_profiles: frozenset[str]
    include_incomplete: bool
    landscape_sections: tuple[str, ...] = ("overview", "catalogue-datasets", "data-status")

    @classmethod
    def load(cls, path: Path = CONFIG_FILE) -> Config:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        profiles = raw.get("profiles") or {}
        return cls(
            standard_version=str(raw["standard_version"]),
            enforced_profiles=frozenset(n for n, p in profiles.items() if (p or {}).get("enforce")),
            include_incomplete=bool((raw.get("publication") or {}).get("include_incomplete", True)),
            landscape_sections=tuple((raw.get("landscapes") or {}).get("default_sections") or cls.landscape_sections),
        )
