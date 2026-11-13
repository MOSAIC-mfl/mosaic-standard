# Changelog

## [0.2.0] - unreleased

### `development/` (2026-11-13)
- How the standard, the catalogue, the API and the website work together after the rebuild:
  overview, running locally (static and live API), publishing and moving the API to a server.
- How to install and demo the Claude Code skill `mosaic-landscape-profile` (it lives in its own
  repository, `mosaic-skills`).

### File formats recovered (2026-11-13)
- `scripts/recover_formats.py`: `data[].media_type` from the extensions of the schema-1
  `file_names` (31 records; the first website showed these formats). Formats the first pipeline
  guessed from the data type when there were no file names are not copied.

### Ported from the old catalogue `main` (2026-11-13)
- The two commits Lizeth made on MOSAIC-mfl/catalog `main` after the migration base `0dad25c`:
  #16 KEN-LVB five-county boundary (OCHA COD-AB / IEBC, CC BY-IGO 3.0, release
  `boundaries-2026-11-10`) and #17 one spelling per landscape (Cumbal (Nariño), Pucallpa – Ucayali,
  Mbire – Lower Zambezi Valley). In `boundaries/`, `legacy/spec/`, `legacy/scripts/`, `legacy/stac/`
  (now the last build of the old `main`, 9abbfc6) and `docs/history/`.
- `vocab/landscapes.json`: KEN-LVB bbox of the new outline (33.948, -0.6615, 35.675, 0.5631).
- Schema-1 crosswalk: "CC BY-IGO 3.0" -> SPDX `CC-BY-3.0-IGO`.

### Optional field `processing_status` (2026-11-12)
- New top-level field and vocabulary `processing_status`: raw, processed, validated - how far the data
  has been processed, as declared by whoever registers it. MOSAIC does not verify it, and it is never
  inferred: a record without it is shown as "not stated".
- Schema-1 crosswalk: `processing_status` is now mapped (lower-cased) instead of dropped.
  `scripts/recover_processing_status.py` copies the values of the schema-1 records (catalog @ 0dad25c)
  into the migrated records: 102 of 108 had one; 6 had none and stay without it.
- Other catalogues: the Climate Data Hub has no equivalent field, so its records have none.

### New repository: mosaic-standard (2026-11-06)
- Everything that is not data moved here from MOSAIC-mfl/catalog (branch metadata-standard-v0.1 @
  92ccf1e): schemas, vocabularies, crosswalks, `mosaic.config.yaml`, the tool (`src/mosaic_catalog`),
  scripts, tests, examples, docs, ADRs, review lists, boundaries and legacy. The catalogue keeps only
  `records/` and `landscapes/`.
- The tool reads the catalogue from a checkout: `--catalog PATH` or `MOSAIC_CATALOG`. The build takes
  `created` / `updated` from the catalogue's git history and records both commits in the manifest
  (`commit`: catalogue, `standard_commit`: this repository).
- CI `Check`: lint, types, generated files, tests, and the catalogue's records and profiles validated
  against the standard (the catalogue is cloned). Publishing moved to the catalogue's own workflow.

### Landscape profile PER-PCL (Pucallpa – Ucayali)
- `landscapes/PER-PCL/`: the MOSAIC Ucayali Explorer (Andrés Aguilar, anaguilarar/mosaic-ucayali @
  24fbe3a) converted by `scripts/migrate_ucayali.py` (the explorer is only read): vegetation classes,
  canopy height, GEDI lidar, land cover, forest loss, fire, burned area, protected areas, climate and
  SPI-3, a 10-chapter story and 5 study cards. Layers to register and licences to confirm:
  `review/landscape_PER-PCL_sources.md`.
- Explorer schema: overlay kind `style-layers` (own `sources` and `layers`); the rail item rule now
  applies to overlays (a duplicated `allOf` key hid it). Studies schema: `steps`, `map_note`,
  `data_note`; a missing `verified` list and a finding on an explore card are warnings.
  `validate-landscapes` checks layer ids of style-layers overlays, step layers and `story.map.focus`.

### Standard on the Climate Data Hub core (ADR-0009, review of 2026-11-05)
- `schema/record.schema.json` is the CDH core v0.5.0 (MIT) with MOSAIC's fields in the same core:
  `themes`, `language`, `spatial.landscapes`, `spatial.resolution`, `temporal.text`,
  `license_text`, `citation.text`, `data[].access_method / kind / access / geometry_type /
  feature_count / service / spatial.crs`, `derived`, `source_updated`; `commodities` and `usage`
  (CDH extensions) move into the core. Formats are checked (dates, e-mails).
- Levels: the minimum follows CDH's required fields plus `themes` and an explicit `access`; a
  contact with the licensor role and an organization in every contact are now minimum; keywords,
  citation or DOI, geography and the kind and access method of each data entry are recommended.
- Extension `climate@0.2.0` (same fields as CDH's). Vocabularies: access `internal` ->
  `non-public`; new `service_type`; `semiannual` frequency; `relation` removed (links use `rel`).
- The 108 records, the examples and the fixtures are converted by `src/mosaic_catalog/v02.py`
  (`scripts/migrate_v02.py`; moves and renames only; notes in `review/migration_v02.md`).
  `migrate_schema1.py` now writes v0.2 directly. `infer` fills `geometry_type`, `feature_count`
  and the data dictionary (`structures[]`).
- Docs: `docs/standard.md` (v0.2, FAIR), field reference regenerated with the CDH and v0.1
  equivalents of every field, `docs/record-template.yaml`.

## [0.1.0] - 2026-11-04 (branch metadata-standard-v0.1, first push)

### Catalogue main up to 0dad25c
- Migration re-run on the current `catalog` main: record 016 restored, 106-110 added (CoRE Stack,
  IND-CH), 013-015 point to the CoRE Stack layer sheet. 108 records, 0 invalid. The values inferred
  from the boundary files (098-105) are kept.
- The example record moves to the example id MFL-2026-999 (106 is now a real record).

### Landscape profiles (ADR-0008)
- One page per living landscape: `landscapes/<CODE>/profile.yaml` (sections), validated with
  `python -m mosaic_catalog validate-landscapes` against `schema/landscape/` plus cross-file checks,
  published by `build` in `dist/landscapes/` (index + one document per landscape).
- Landscapes without a profile get the default sections (`mosaic.config.yaml`).
- KEN-LVB: the Lake Victoria Basin Explorer (Andrés Aguilar) converted with
  `scripts/migrate_lake_victoria.py` (its repository only read): map explorer, story, studies and
  the sources of its layers. `review/landscape_KEN-LVB_sources.md` lists the layers to register.
- Guide: `docs/landscape-profiles.md`.

### Phase 2 (records and build)
- 102 records migrated from the old catalogue (read only, ref main) with
  `scripts/migrate_schema1.py`: 0 invalid, 102 incomplete. Review lists in `review/`.
- `python -m mosaic_catalog build`: `dist/catalog.json`, `dist/manifest.json` (SHA-256 per
  record), schemas and vocabularies.
- Standard changes:
  - access points now say `kind` (data type) **and** `method` (download, landing_page,
    service, request);
  - new fields `source_updated` and `spatial.resolution` (from schema 1);
  - new themes `climate`, `climate-adaptation`, `climate-mitigation` (following the CDH
    domains);
  - new update frequency `seasonal`;
  - a contact may be just an e-mail.
- Field reference generated from the schemas: `docs/fields.xlsx`, `docs/record-reference.yaml`.

### Data classification (ADR-0007)
- New fields: `tabular.spatial`, `tabular.coordinate_columns`, `derived` (record and access
  point).
- Recommended: `vector.geometry_type` for vector data, `tabular.spatial` for tables.
- `python -m mosaic_catalog infer` reads public downloadable files (Shapefile, GeoJSON,
  GeoPackage, CSV) and fills what is absent. Result on the 102 records: the 8 landscape boundaries
  were classified (polygon, EPSG:4326). The other records cannot be read automatically and are
  listed in `review/classification_gaps.csv`.
- Migration: GIS style files (`.qml`) are no longer taken as data. They become `related`
  (`IsSupplementedBy`); records 013–015 now say their data link is missing.

### Phase 1 (standard)

### Added
- MOSAIC metadata standard v0.1.0:
  - record structure;
  - minimum and recommended levels;
  - MOSAIC profile (not enforced);
  - data-type blocks (raster, vector, tabular, document, service);
  - extension mechanism and template.
- Vocabularies: themes (13 MFL), landscapes (11), geography (ISO 3166 + UN M49), resource type,
  access, data kind, contact role, relation, update frequency.
- Crosswalk for reading Climate Data Hub records (v0.5.0).
- Python validator and CLI (`python -m mosaic_catalog validate`), with the review list
  (`--gaps`).
- Examples: MFL-2026-999 (complete; an example id, 106 is a real record), MFL-2026-079 and MFL-2026-090 (incomplete).
- Tests: 31, including valid / invalid / incomplete fixtures.
- Docs: README, design notes, generated field reference, ADR-0001…0005.
