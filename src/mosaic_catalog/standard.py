"""The MOSAIC metadata standard: load the schemas and check a record against them.

A record is checked in layers:

* structure (``record.schema.json`` + declared extensions): a failure makes the
  record **invalid** - it is malformed and the build stops;
* minimum (level 0): a failure makes it **incomplete** - it is listed for review;
* recommended (level 1) and the MOSAIC profile: failures are **warnings**, unless
  the profile is enforced in ``mosaic.config.yaml``, then they count as minimum.

Nothing here fills in or changes a value; it only reports.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schema"


class Status(str, Enum):  # StrEnum needs 3.11; this keeps 3.10 support
    INVALID = "invalid"
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


@dataclass(frozen=True)
class Issue:
    level: str  # structure | minimum | recommended | profile:<name> | extension:<name>
    field: str  # top-level field the issue is about ("" = whole record)
    message: str
    path: str = ""

    def as_dict(self) -> dict[str, str]:
        return {"level": self.level, "field": self.field, "path": self.path, "message": self.message}


@dataclass
class Report:
    record_id: str
    source: str = ""
    issues: list[Issue] = field(default_factory=list)
    completeness: dict[str, float] = field(default_factory=dict)

    def by_level(self, level: str) -> list[Issue]:
        return [i for i in self.issues if i.level == level]

    @property
    def status(self) -> Status:
        if any(i.level == "structure" or i.level.startswith("extension:") for i in self.issues):
            return Status.INVALID
        if self.by_level("minimum"):
            return Status.INCOMPLETE
        return Status.COMPLETE

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.record_id,
            "status": self.status.value,
            "completeness": self.completeness,
            "issues": [i.as_dict() for i in self.issues],
        }


def _load_json(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


class Standard:
    """The schemas of one standard version, ready to check records."""

    LEVELS = ("minimum", "recommended")

    def __init__(self, schema_dir: Path = SCHEMA_DIR, enforced_profiles: Iterable[str] = ()) -> None:
        self.schema_dir = schema_dir
        files = sorted(schema_dir.rglob("*.json"))
        docs = {p: _load_json(p) for p in files}
        self.registry: Registry = Registry().with_resources(
            (d["$id"], Resource.from_contents(d)) for d in docs.values() if "$id" in d
        )
        by_rel = {p.relative_to(schema_dir).as_posix(): d for p, d in docs.items()}
        self.record_schema = by_rel["record.schema.json"]
        self.known_fields = frozenset(self.record_schema["properties"])
        self.levels = {lv: by_rel[f"levels/{lv}.schema.json"] for lv in self.LEVELS}
        self.profiles = {
            p.split("/")[1].removesuffix(".schema.json"): d for p, d in by_rel.items() if p.startswith("profiles/")
        }
        self.extensions = {
            self._extension_key(p): d
            for p, d in by_rel.items()
            if p.startswith("extensions/") and not p.startswith("extensions/_template/")
        }
        unknown = set(enforced_profiles) - set(self.profiles)
        if unknown:
            raise ValueError(f"unknown profile(s) in configuration: {sorted(unknown)}")
        self.enforced_profiles = frozenset(enforced_profiles)
        self.version = self.record_schema["$id"].rsplit("/v", 1)[1].split("/")[0]

    @staticmethod
    def _extension_key(rel: str) -> str:
        # extensions/<name>/<version>/schema.json -> name@version
        _, name, version, _ = rel.split("/")
        return f"{name}@{version}"

    def _validator(self, schema: Mapping[str, Any]) -> Draft202012Validator:
        # Formats are asserted (date, email...), as in the CDH validator: "2020-13" is not a date.
        return Draft202012Validator(schema, registry=self.registry, format_checker=Draft202012Validator.FORMAT_CHECKER)

    # -- checking ---------------------------------------------------------------------
    def check(self, record: Mapping[str, Any], record_id: str | None = None) -> Report:
        rid = str(record_id or record.get("id") or "?")
        report = Report(rid)
        declared = self._declared_extensions(record, report)
        core = {k: v for k, v in record.items() if k not in declared}
        report.issues += self._run("structure", self.record_schema, core)
        for name, key in declared.items():
            if key in self.extensions:
                report.issues += self._run(f"extension:{name}", self.extensions[key], {name: record[name]})
        for level in self.LEVELS:
            issues = self._run(level, self.levels[level], core)
            report.issues += issues
            report.completeness[level] = self._completeness(self.levels[level], core, issues)
        for name, schema in self.profiles.items():
            level = "minimum" if name in self.enforced_profiles else f"profile:{name}"
            report.issues += self._run(level, schema, core)
        return report

    def _declared_extensions(self, record: Mapping[str, Any], report: Report) -> dict[str, str]:
        declared: dict[str, str] = {}
        raw = record.get("extensions") or []
        for key in raw if isinstance(raw, list) else []:
            if not isinstance(key, str) or "@" not in key:
                continue  # malformed entries are reported by the structure schema
            name = key.split("@", 1)[0]
            if key not in self.extensions:
                report.issues.append(Issue(f"extension:{name}", "extensions", f"unknown extension {key}"))
            elif name not in record:
                report.issues.append(Issue(f"extension:{name}", name, f"declares {key} but has no '{name}' block"))
            declared[name] = key
        for k in record:
            if k not in self.known_fields and k not in declared:
                msg = f"unknown field '{k}' (not in the standard and not a declared extension)"
                report.issues.append(Issue("structure", k, msg))
        return {n: k for n, k in declared.items() if n in record}

    def _run(self, level: str, schema: Mapping[str, Any], data: Mapping[str, Any]) -> list[Issue]:
        if level == "structure":
            # Unknown top-level keys are reported by _declared_extensions with a clearer message.
            schema = {**schema, "additionalProperties": True}
        out: list[Issue] = []
        for err in sorted(self._validator(schema).iter_errors(data), key=lambda e: list(e.absolute_path)):
            out.extend(self._to_issues(level, schema, err))
        # jsonschema reports `required` once per missing key with the full list; keep each issue once.
        return list(dict.fromkeys(out))

    def _to_issues(self, level: str, schema: Mapping[str, Any], err: ValidationError) -> list[Issue]:
        path = [str(p) for p in err.absolute_path]
        hint = self._hint(schema, err)
        if isinstance(err.schema, Mapping) and "x-message" in err.schema:
            hint = {**hint, "message": str(err.schema["x-message"])}
        if hint.get("message"):
            fieldname = hint.get("field") or (path[0] if path else "")
            return [Issue(level, fieldname, hint["message"], "/".join(path))]
        if err.validator == "required" and level != "structure":
            instance = err.instance if isinstance(err.instance, Mapping) else {}
            required = err.validator_value if isinstance(err.validator_value, list) else []
            missing = [str(m) for m in required if m not in instance]
            where = ".".join(path)
            return [
                Issue(level, path[0] if path else m, f"missing: {where + '.' if where else ''}{m}", where)
                for m in missing
            ]
        message = err.message
        if err.validator == "enum" and isinstance(err.validator_value, list) and len(err.validator_value) > 8:
            message = f"{err.instance!r} is not in the controlled vocabulary (see vocab/)"
        elif err.validator == "const":
            message = f"must be {err.validator_value!r} (a detail block must match the access point kind)"
        return [Issue(level, path[0] if path else "", message, "/".join(path))]

    @staticmethod
    def _hint(schema: Mapping[str, Any], err: ValidationError) -> dict[str, str]:
        """Nearest x-field / x-message on the schema path of the failing keyword."""
        node: Any = schema
        found: dict[str, str] = {}
        for step in err.absolute_schema_path:
            if isinstance(node, Mapping):
                for k in ("field", "message"):
                    if f"x-{k}" in node:
                        found[k] = node[f"x-{k}"]
                node = node.get(step) if isinstance(step, str) else None
            elif isinstance(node, list) and isinstance(step, int) and step < len(node):
                node = node[step]
            else:
                break
        return found

    @staticmethod
    def _completeness(schema: Mapping[str, Any], data: Mapping[str, Any], issues: list[Issue]) -> float:
        """Share of the level's fields that pass (fields = required + fields named by rules)."""
        fields = set(schema.get("required", [])) | set(schema.get("properties", {}))
        fields |= {r["x-field"] for r in schema.get("allOf", []) if "x-field" in r}
        if "access_note" in fields and data.get("access") not in ("restricted", "non-public"):
            fields.discard("access_note")
        failing = {i.field if i.field in fields else i.path.split("/")[0] for i in issues} & fields
        return round(1 - len(failing) / len(fields), 3) if fields else 1.0
