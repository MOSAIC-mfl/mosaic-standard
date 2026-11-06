"""Read records from disk and run the checks that need the whole catalogue."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

RECORD_FILE = "record.yaml"


class _UniqueKeyLoader(yaml.SafeLoader):
    """safe_load that rejects duplicate keys instead of silently keeping the last one."""


def _construct_mapping(loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
    seen: set[Any] = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(None, None, f"duplicate key {key!r}", key_node.start_mark)
        seen.add(key)
    mapping: dict[Any, Any] = loader.construct_mapping(node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


@dataclass(frozen=True)
class LoadedRecord:
    path: Path
    data: dict[str, Any] | None
    error: str | None = None


def load_record(path: Path) -> LoadedRecord:
    try:
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)  # noqa: S506 - safe loader subclass
    except (OSError, yaml.YAMLError) as exc:
        return LoadedRecord(path, None, f"cannot read YAML: {exc}")
    if not isinstance(data, dict):
        return LoadedRecord(path, None, "the file is not a YAML mapping")
    return LoadedRecord(path, data)


def iter_record_files(paths: list[Path]) -> Iterator[Path]:
    for p in paths:
        if p.is_dir():
            yield from sorted(f for f in p.rglob("*") if f.suffix in (".yaml", ".yml"))
        elif p.suffix in (".yaml", ".yml"):
            yield p


def catalogue_issues(records: list[LoadedRecord], records_root: Path | None) -> list[tuple[str, str]]:
    """Checks a single record cannot do: unique ids, folder name = id."""
    out: list[tuple[str, str]] = []
    ids = Counter(str(r.data.get("id")) for r in records if r.data and r.data.get("id"))
    out += [(i, f"id used by {n} records") for i, n in ids.items() if n > 1]
    if records_root is not None:
        for r in records:
            in_records = r.data and r.path.name == RECORD_FILE and r.path.is_relative_to(records_root)
            if in_records and r.data and r.data.get("id") and r.path.parent.name != r.data["id"]:
                out.append((str(r.data["id"]), f"folder '{r.path.parent.name}' does not match the id"))
    return out
