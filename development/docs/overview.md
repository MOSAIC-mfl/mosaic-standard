# Overview — MOSAIC after the v0.2 rebuild

## The four repositories

| Repository | Holds | Published as |
|---|---|---|
| [MOSAIC-mfl/mosaic-standard](https://github.com/MOSAIC-mfl/mosaic-standard) | The metadata standard v0.2 (schemas, vocabularies, crosswalks), the tool `mosaic_catalog` (validate, build), boundaries, the first pipeline's legacy, docs, this folder | Used by the catalogue's and the API's workflows (cloned, `pip install -e`) |
| [MOSAIC-mfl/catalog](https://github.com/MOSAIC-mfl/catalog) | Data only: `records/<ID>/record.yaml` (108 MOSAIC records) and `landscapes/<CODE>/` (landscape profiles; KEN-LVB and PER-PCL have map explorers) | `https://mosaic-mfl.github.io/catalog/`: `catalog.json`, `manifest.json`, `landscapes/`, the standard's `schema/`, `vocab/`, `crosswalks/`; the frozen STAC of the first pipeline at `/catalog/stac/` |
| [MOSAIC-mfl/mosaic-api](https://github.com/MOSAIC-mfl/mosaic-api) | The API: harvests MOSAIC and the CGIAR Climate Data Hub (CDH) into one model, serves it | Static JSON on `https://mosaic-mfl.github.io/mosaic-api/` (today); the same FastAPI app can run live on a server |
| [MOSAIC-mfl/website](https://github.com/MOSAIC-mfl/website) | The website (Astro + React), Lizeth's design | `https://mosaic-mfl.github.io/website/` |

## Data flow

```
catalog (records/, landscapes/)  ──build with mosaic-standard──▶  dist/ (catalog.json, landscapes/, vocab/, schema/)
                                                                        │
CDH (cdh-catalog, YAML)  ─────────────────────────────────────────┐    │
                                                                   ▼    ▼
                                     mosaic-api  harvest  ──▶  snapshot (one JSON, no database)
                                                   │
                         ┌─────────────────────────┴─────────────────────────┐
                    export (static JSON)                               serve (FastAPI, live)
           v1/records.json, v1/_index/… (hashed shards),         /v1/sources, /v1/records?…,
           v1/records/<src>/<id>.json, v1/landscapes…            /v1/records/{src}/{id}, /v1/landscapes…
                         └─────────────────────────┬─────────────────────────┘
                                                   ▼
                       website (browser) — one port, two adapters: StaticCatalogRepository | LiveCatalogRepository
                       PUBLIC_MOSAIC_API_MODE=static|live, PUBLIC_MOSAIC_API_URL=<any address>
```

The website has no catalogue data inside: every page reads the API when it opens, so a new record or
profile needs no website rebuild. The map explorers read their layers from where their author
publishes them (GitHub Pages of anaguilarar/mosaic-lake-victoria and mosaic-ucayali, and a Hugging
Face dataset); moving those layers is a separate decision.

## What changed, per repository

**mosaic-standard (new repository).**
- Standard v0.2, built on the CDH core: `record.schema.json`, levels (minimum, recommended),
  vocabularies (16 themes = 13 MFL + 3 CDH climate themes, 11 landscapes, geography from UN M49,
  access, data kinds, …), crosswalks (CDH, schema 1), landscape profile schemas.
- `processing_status` (optional): raw / processed / validated, declared by whoever registers the
  record, never inferred. Recovered for 102 of 108 records from the schema-1 records
  (`scripts/recover_processing_status.py`); CDH has no such field, so its records have none.
- The tool (`python -m mosaic_catalog --catalog <checkout> validate | validate-landscapes | build`).
- `boundaries/` and `legacy/` (the first pipeline: schema 1, the Excel registry, the frozen STAC),
  including the last two commits of the old catalogue `main` (KEN-LVB five-county boundary, landscape
  names).

**catalog.** Only data: records in v0.2 (`records/<ID>/record.yaml`) and landscape profiles
(`landscapes/<CODE>/profile.yaml`, `explorer.yaml`, `story.yaml`, `studies.yaml`, `sources.yaml`).
Workflows: `Validate` (every pull request) and `Publish` (Pages). The first pipeline
(`build_catalog.py`, `records/*.yaml`, `datasets.json`, `stac/`) is in the git history and in
mosaic-standard `legacy/`.

**mosaic-api (new repository).** Five endpoints (ADR-0007): `/v1/sources`, `/v1/records`,
`/v1/records/{source}/{id}`, `/v1/landscapes`, `/v1/landscapes/{code}`. `/v1/records` filters by
`source`, `theme`, `landscape`, `geography`, `data_kind`, `access`, `license`, `processing_status`
(OR inside a filter, AND across, ids or labels, accent- and case-insensitive) and counts every value
(`include_facets=true`). A record's landscapes are stated or derived from its bbox (CDH). Quality:
complete / incomplete against the standard's minimum. The static export is the same responses as
files; its search index is sharded and content-hashed.

**website.** Lizeth's redesign (Astro 7, Home, About, Landscapes explorer, catalogue, dataset page)
on top of the API-based data layer:
- catalogue: her filters (four first, four more), tiles / list, readiness legend with "Not stated";
- dataset page `/catalogue/dataset/?id=<source>:<id>`: her header, four tabs, quick facts, with
  more of v0.2 (access points, processing steps, contacts, funding, publications, completeness);
- Landscapes: her explorer; counts, coverage of the 16 themes and open access from the API;
  "Map visualization" shows the landscape's map profile (map, story, studies) for KEN-LVB and
  PER-PCL — embedded and full screen (`/landscapes/<code>/map/`) while the team chooses;
- old addresses (`/catalogue/MFL-…/`, `/landscapes/<code>/`) are redirected by the 404 page.

## Decisions (2026-11)

1. Everything visual is Lizeth's; everything that depends on the catalogue is read from the API at
   runtime.
2. The website talks to the API through one port; static and live are two adapters chosen by two
   environment variables. Today: static on GitHub Pages; later: live on a server, no code change.
3. Readiness is declared, never inferred; "Not stated" when missing.
4. Themes: the standard's 16.
5. Landscape texts and photos stay in the website (`frontend/data/`).
6. The map layers stay where their author hosts them for now.
