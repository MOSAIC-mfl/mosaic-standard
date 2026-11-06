"""Landscape profiles: one page per living landscape (landscapes/<CODE>/).

A profile is a ``profile.yaml`` (the page: an ordered list of sections) plus the configuration files
its sections name (for a map explorer: explorer.yaml, story.yaml, studies.yaml, sources.yaml).
Landscapes without a folder get the default sections from ``mosaic.config.yaml``, so every landscape
of the vocabulary has a page.

``check`` validates each document against schema/landscape/ and then runs the checks a schema cannot do
(references between files: overlays named by the story, base layers named by overlays, catalogue
records, ...). ``bundle`` resolves every profile into one JSON document for mosaic-api.

Nothing here reads the data files the profiles point to: those stay where their authors serve them.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from .config import ROOT, landscapes_dir, records_dir
from .records import RECORD_FILE

SCHEMA_DIR = ROOT / "schema" / "landscape"
VOCAB_FILE = ROOT / "vocab" / "landscapes.json"
PROFILE_FILE = "profile.yaml"
CORE_SECTIONS = frozenset({"overview", "map-explorer", "catalogue-datasets", "data-status"})
CORE_OVERLAYS = frozenset({"raster-tiles", "year-tiles", "climate-grid", "index-grid", "style-layers"})
DOCS = {  # file key in a map-explorer config -> schema
    "explorer": "explorer.schema.json",
    "story": "story.schema.json",
    "studies": "studies.schema.json",
    "sources": "sources.schema.json",
}


@dataclass(frozen=True)
class Problem:
    level: str  # error | warning
    where: str  # file (and path inside it)
    message: str

    def __str__(self) -> str:
        return f"[{self.level}] {self.where}: {self.message}"


@dataclass
class Profile:
    code: str
    curated: bool
    data: dict[str, Any]
    sections: list[dict[str, Any]] = field(default_factory=list)  # resolved: section + its config
    problems: list[Problem] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(p.level == "error" for p in self.problems)


def _schema(name: str) -> Draft202012Validator:
    return Draft202012Validator(json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8")))


def _vocab() -> dict[str, dict[str, Any]]:
    data = json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
    return {c["id"]: c for c in data["concepts"]}


def _load_yaml(path: Path, problems: list[Problem]) -> dict[str, Any] | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        problems.append(Problem("error", path.name, f"cannot read: {exc}"))
        return None
    if not isinstance(data, dict):
        problems.append(Problem("error", path.name, "not a YAML mapping"))
        return None
    return data


def _validate(validator: Draft202012Validator, data: Any, where: str) -> list[Problem]:
    out = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        path = "/".join(str(p) for p in err.absolute_path)
        msg = err.schema.get("x-message", err.message) if isinstance(err.schema, Mapping) else err.message
        out.append(Problem("error", f"{where}:{path}" if path else where, str(msg)[:300]))
    return out


def default_profile(code: str, label: str, sections: Iterable[str]) -> dict[str, Any]:
    titles = {"overview": "Overview", "catalogue-datasets": "Datasets in the catalogue", "data-status": "Data status"}
    return {
        "profile": "mosaic-landscape-profile@0.1",
        "landscape": code,
        "title": label,
        "status": "published",
        "sections": [{"id": k.removeprefix("catalogue-"), "kind": k, "title": titles.get(k, k)} for k in sections],
    }


def _assets(node: Any) -> Iterator[str]:
    """Every {asset: path} / {pmtiles: path} inside a style fragment."""
    if isinstance(node, dict):
        for k in ("asset", "pmtiles"):
            if isinstance(node.get(k), str) and len(node) <= 2:
                yield node[k]
        for v in node.values():
            yield from _assets(v)
    elif isinstance(node, list):
        for v in node:
            yield from _assets(v)


def _explorer_checks(cfg: dict[str, Any], where: str, record_ids: set[str]) -> list[Problem]:
    """References a schema cannot check, inside one map-explorer configuration."""
    out: list[Problem] = []
    explorer, story, studies, sources = (cfg.get(k) or {} for k in ("explorer", "story", "studies", "sources"))

    def err(path: str, msg: str) -> None:
        out.append(Problem("error", f"{where}:{path}", msg))

    def warn(path: str, msg: str) -> None:
        out.append(Problem("warning", f"{where}:{path}", msg))

    data = explorer.get("data") or {}
    roots = set(data.get("roots") or {})
    if data.get("default_root") not in roots:
        err("data.default_root", f"'{data.get('default_root')}' is not one of the roots {sorted(roots)}")
    for i, r in enumerate(data.get("routes") or []):
        if r.get("root") not in roots:
            err(f"data.routes/{i}", f"unknown root '{r.get('root')}'")

    style = explorer.get("map") or {}
    base_ids = [lyr.get("id") for lyr in style.get("layers") or []]
    story_ids = [lyr.get("id") for lyr in (story.get("map") or {}).get("layers") or []]
    overlay_layer_ids = [lyr.get("id") for o in explorer.get("overlays") or [] for lyr in o.get("layers") or []]
    for dup, n in Counter(base_ids + story_ids + overlay_layer_ids).items():
        if n > 1:
            err("map.layers", f"layer id '{dup}' used {n} times")
    sources_ids = set(style.get("sources") or {}) | set((story.get("map") or {}).get("sources") or {})
    for lyr in (style.get("layers") or []) + ((story.get("map") or {}).get("layers") or []):
        if lyr.get("source") and lyr["source"] not in sources_ids:
            err(f"map.layers/{lyr.get('id')}", f"unknown source '{lyr['source']}'")
    terrain = style.get("terrain") or {}
    if terrain and terrain.get("source") not in sources_ids:
        err("map.terrain", f"unknown source '{terrain.get('source')}'")

    groups = set(explorer.get("groups") or [])
    source_refs = {s["id"] for s in sources.get("layers") or [] if isinstance(s, dict) and "id" in s}
    items = [*(explorer.get("toggles") or []), *(explorer.get("panels") or []), *(explorer.get("overlays") or [])]
    for dup, n in Counter(i.get("id") for i in items).items():
        if n > 1:
            err("overlays", f"rail id '{dup}' used {n} times")
    for item in items:
        iid = item.get("id")
        if item.get("group") not in groups:
            err(f"{iid}", f"group '{item.get('group')}' is not in groups")
        if item.get("source_ref") and sources and item["source_ref"] not in source_refs:
            err(f"{iid}.source_ref", f"'{item['source_ref']}' is not in sources.yaml")
        rec = item.get("record")
        if rec and rec.startswith("mosaic:") and rec.split(":", 1)[1] not in record_ids:
            err(f"{iid}.record", f"catalogue record {rec} does not exist")
    for t in explorer.get("toggles") or []:
        for lid in t.get("layers") or []:
            if lid not in base_ids:
                err(f"toggles/{t.get('id')}", f"layer '{lid}' is not in map.layers")
    for p in explorer.get("panels") or []:
        if p.get("open_on_click") and p["open_on_click"] not in base_ids:
            err(f"panels/{p.get('id')}", f"open_on_click '{p['open_on_click']}' is not in map.layers")
    overlay_ids = set()
    for o in explorer.get("overlays") or []:
        overlay_ids.add(o.get("id"))
        if o.get("before") and o["before"] not in base_ids:
            err(f"overlays/{o.get('id')}.before", f"'{o['before']}' is not in map.layers")
        own_sources = set(o.get("sources") or {}) | sources_ids
        for lyr in o.get("layers") or []:
            if lyr.get("source") and lyr["source"] not in own_sources:
                err(f"overlays/{o.get('id')}.layers/{lyr.get('id')}", f"unknown source '{lyr['source']}'")
        if o.get("kind") not in CORE_OVERLAYS:
            warn(
                f"overlays/{o.get('id')}",
                f"kind '{o.get('kind')}' is not a core renderer: the website must register it",
            )
    for s in sources.get("layers") or []:
        rec = s.get("record") if isinstance(s, dict) else None
        if rec and rec.startswith("mosaic:") and rec.split(":", 1)[1] not in record_ids:
            err(f"sources/{s.get('id')}.record", f"catalogue record {rec} does not exist")

    focus = (story.get("map") or {}).get("focus") or {}
    for lid in focus.get("layers") or []:
        if lid not in story_ids + base_ids:
            err("story.map.focus", f"layer '{lid}' is not in the story or base map layers")
    panel_ids = {p.get("id") for p in explorer.get("panels") or []}
    highlights = set((story.get("map") or {}).get("highlights") or {})
    for ch in story.get("chapters") or []:
        v = ch.get("visual") or {}
        for lid in v.get("layers") or []:
            if lid not in overlay_ids:
                err(f"story/{ch.get('id')}.visual.layers", f"'{lid}' is not an overlay")
        for name in v.get("show") or []:
            if name not in highlights:
                err(f"story/{ch.get('id')}.visual.show", f"'{name}' is not in story.map.highlights")
        for st in v.get("steps") or []:
            if st.get("layer") and st["layer"] not in overlay_ids:
                err(f"story/{ch.get('id')}.visual.steps", f"'{st['layer']}' is not an overlay")
        cmp_ = v.get("compare") or ch.get("compare_option") or {}
        if cmp_ and cmp_.get("overlay") not in overlay_ids:
            err(f"story/{ch.get('id')}.compare", f"'{cmp_.get('overlay')}' is not an overlay")
    for card in studies.get("cards") or []:
        if card.get("kind") == "published" and not card.get("verified"):
            warn(f"studies/{card.get('id')}", "no 'verified' list: check that the finding cites its pages")
        if card.get("kind") == "explore" and card.get("finding"):
            warn(f"studies/{card.get('id')}.finding", "an explore card states no claims: check the text only describes")
        for st in card.get("steps") or []:
            if st.get("layer") and st["layer"] not in overlay_ids:
                err(f"studies/{card.get('id')}.steps", f"'{st['layer']}' is not an overlay")
        for lid in card.get("layers") or []:
            if lid not in overlay_ids:
                warn(f"studies/{card.get('id')}.layers", f"'{lid}' is not an overlay (the card shows it as missing)")
        if card.get("open_panel") and card["open_panel"] not in panel_ids:
            err(f"studies/{card.get('id')}.open_panel", f"'{card['open_panel']}' is not a panel")

    for path in _assets([style, story.get("map")]):
        if ".." in path or path.startswith("/"):
            err("assets", f"asset path '{path}' must be relative, without '..'")
    return out


def load_profile(folder: Path, vocab: Mapping[str, Mapping[str, Any]], record_ids: set[str]) -> Profile:
    problems: list[Problem] = []
    data = _load_yaml(folder / PROFILE_FILE, problems) or {}
    code = folder.name
    prof = Profile(code, curated=True, data=data, problems=problems)
    if not data:
        return prof
    problems += _validate(_schema("profile.schema.json"), data, f"{code}/{PROFILE_FILE}")
    if data.get("landscape") != code:
        problems.append(
            Problem("error", f"{code}/{PROFILE_FILE}", f"landscape '{data.get('landscape')}' != folder '{code}'")
        )
    if code not in vocab:
        problems.append(Problem("error", f"{code}/", "not a landscape of vocab/landscapes.json"))
    for dup, n in Counter(s.get("id") for s in data.get("sections") or []).items():
        if n > 1:
            problems.append(Problem("error", f"{code}/{PROFILE_FILE}", f"section id '{dup}' used {n} times"))
    for sec in data.get("sections") or []:
        resolved = {k: v for k, v in sec.items() if k != "source"}
        if sec.get("kind") not in CORE_SECTIONS:
            problems.append(
                Problem(
                    "warning",
                    f"{code}/{PROFILE_FILE}",
                    f"section kind '{sec.get('kind')}' is not a core kind: the website must register it",
                )
            )
        if sec.get("kind") == "map-explorer" and sec.get("source"):
            resolved["config"] = _load_explorer(folder, sec["source"], problems, record_ids)
        prof.sections.append(resolved)
    return prof


def _load_explorer(folder: Path, source: str, problems: list[Problem], record_ids: set[str]) -> dict[str, Any]:
    code = folder.name
    explorer = _load_yaml(folder / source, problems) or {}
    problems += _validate(_schema(DOCS["explorer"]), explorer, f"{code}/{source}")
    cfg: dict[str, Any] = {"explorer": explorer}
    refs = {
        "story": (explorer.get("story") or {}).get("file"),
        "studies": (explorer.get("studies") or {}).get("file"),
        "sources": (explorer.get("about") or {}).get("sources"),
    }
    for key, name in refs.items():
        if not name:
            continue
        doc = _load_yaml(folder / name, problems)
        if doc is None:
            continue
        problems += _validate(_schema(DOCS[key]), doc, f"{code}/{name}")
        cfg[key] = doc
    problems += _explorer_checks(cfg, code, record_ids)
    # one self-contained document for the website: the explorer plus what it references
    out = dict(explorer)
    for key in ("story", "studies"):
        if key in cfg:
            out[key] = cfg[key]
    if "sources" in cfg:
        out["about"] = {**(explorer.get("about") or {}), "sources": cfg["sources"].get("layers") or []}
    return out


def record_ids(folder: Path | None = None) -> set[str]:
    return {p.parent.name for p in (folder or records_dir()).glob(f"*/{RECORD_FILE}")}


def load_all(default_sections: Iterable[str], folder: Path | None = None) -> list[Profile]:
    """Every landscape of the vocabulary: its curated profile, or the default one."""
    vocab = _vocab()
    ids = record_ids()
    root = folder or landscapes_dir()
    folders = {f.name: f for f in sorted(root.iterdir()) if f.is_dir()} if root.exists() else {}
    out: list[Profile] = []
    for f in folders.values():
        out.append(load_profile(f, vocab, ids))
    for code, concept in vocab.items():
        if code in folders:
            continue
        data = default_profile(code, str(concept.get("label", code)), default_sections)
        out.append(Profile(code, curated=False, data=data, sections=list(data["sections"])))
    return sorted(out, key=lambda p: p.code)


def bundle(p: Profile, vocab: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    concept = vocab.get(p.code, {})
    meta = {k: v for k, v in p.data.items() if k not in ("sections", "profile", "landscape")}
    return {
        "profile": p.data.get("profile"),
        "landscape": {
            "code": p.code,
            "label": concept.get("label", p.code),
            "countries": concept.get("countries", []),
            "bbox": concept.get("bbox"),
        },
        "curated": p.curated,
        **meta,
        "sections": p.sections,
    }


def summary(p: Profile, vocab: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    b = bundle(p, vocab)
    return {
        "code": p.code,
        "slug": p.code.lower(),
        "label": b["landscape"]["label"],
        "countries": b["landscape"]["countries"],
        "bbox": b["landscape"]["bbox"],
        "title": b.get("title"),
        "summary": b.get("summary"),
        "status": b.get("status", "draft"),
        "curated": p.curated,
        "sections": [{"id": s.get("id"), "kind": s.get("kind"), "title": s.get("title")} for s in p.sections],
    }


def vocab() -> dict[str, dict[str, Any]]:
    return _vocab()
