"""Write records as YAML the same way everywhere (migration, inference), keeping the header comment."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class _Dumper(yaml.SafeDumper):
    pass


def _str_presenter(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
    style = ">" if len(value) > 90 and "\n" not in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


_Dumper.add_representer(str, _str_presenter)


def dump(rec: dict[str, Any]) -> str:
    return yaml.dump(rec, Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=100)


def header_of(path: Path) -> str:
    """Leading comment lines of a YAML file (kept when the file is rewritten)."""
    if not path.exists():
        return ""
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("#"):
            break
        out.append(line + "\n")
    return "".join(out)


def write_record(path: Path, rec: dict[str, Any], header: str | None = None) -> None:
    head = header_of(path) if header is None else header
    path.write_text(head + dump(rec), encoding="utf-8")
