# MOSAIC dataset record schema — `records/<ID>.yaml`

**Status:** source of truth since 2026-07-24. One YAML file per dataset under `records/`,
validated and consumed by `mosaic_pipeline/records.py`. The Excel registry
(`catalog/MFL_Dataset_Registry.xlsx`) is now a frozen snapshot / fallback, used only when
PyYAML is unavailable (today's CI) or when `build_catalog.py --from-excel` is forced.

Machine-readable twin: [`record_schema.json`](record_schema.json) — jsonschema-*shaped*,
but consumed by our own pure-python validator (jsonschema is **not** installed here; npm
is blocked). The JSON file is the single source for enums and canonical key order; this
page explains intent. If the two disagree, the JSON wins — and please fix this page.

## Ground rules

1. **Filename = `id`.** `records/MFL-2026-048.yaml` must contain `id: MFL-2026-048`.
2. **Unknown top-level keys are a hard validation error** (build fails). If you need a new
   field, propose it via the metadata-standards-specialist first; don't invent keys.
3. **Never fabricate spatial facts.** `bbox`/`crs` stay `null` unless you actually know them.
4. **Strings that look like numbers or dates must be quoted** (`'2024'`, `'2026-07-15'`),
   otherwise YAML turns them into ints/dates and validation rejects them.
5. English only.
6. The build **fails (nonzero exit)** on any validation error, listing every error.

## Core fields (canonical key order)

| # | Key | Required | Type / enum | Notes |
|---|-----|----------|-------------|-------|
| 1 | `id` | yes | string, `^MFL-\d{4}-\d{3}$` | Must match filename stem. |
| 2 | `title` | yes | non-empty string | |
| 3 | `description` | | string \| null | Free text. Don't bury searchable facts here. |
| 4 | `country` | yes (since 2026-09-04) | enum | Cambodia, Colombia, Côte d'Ivoire, Ethiopia, Global, India, Kenya, Laos, Peru, Senegal, Tanzania, Tunisia, Vietnam, Zimbabwe — plus the regions **Africa**, **Asia**, **Latin America and the Caribbean** (added 2026-08-03, for datasets spanning many countries within one region; use `Global` only for worldwide scope). |
| 5 | `living_landscape` | yes | enum | **Bare code**: CIV-NZ, COL-CUM, ETH-OG, IND-CH, KEN-LVB, KEN-LEI, MEK-3S, PER-PCL, SEN-FK, TUN-NW, ZWE-MB, NATIONAL, GLOBAL. *Not* the Excel `CODE — Name` string. |
| 6 | `theme` | | enum \| null | The 13 MFL themes (see JSON). |
| 7 | `data_type` | | enum \| null | Raster, Vector, Tabular, Mixed, Netcdf. |
| 8 | `spatial_resolution` | | string \| null | Verbatim, messy by design ("30m", "5000", "Village level"). Pipeline flags non-numeric. |
| 9 | `temporal_coverage` | | string \| null | Verbatim; pipeline parses years (R4). |
| 10 | `source` | | string \| null | Source / Centre. |
| 11 | `contact` | yes (since 2026-09-04) | non-empty string | **Single "Name, email" cell** — keep as one string so the R1 extractors work unchanged. Required because a record nobody can be asked about cannot be maintained: two such records (016, 043) were moved to `records/_pending/` when this rule landed. |
| 12 | `access_level` | | enum \| null | Open, Internal, Restricted. ("CGIAR-internal" was normalized to Internal at migration.) **Open** = anyone can obtain the data without asking permission: since 2026-10-22 the build stops (exit 3, `ACCESS RULE FAILED`) when an Open record has no usable `download_url` after R8 cleaning, or when its `license` contains "contact data owner" (any letter case) — `mosaic_pipeline/rules.py`. |
| 13 | `license` | | string \| null | Original wording; SPDX mapping is a pipeline rule (R3). |
| 14 | `processing_status` | | enum \| null | Raw, Processed, Validated. Null → readiness "Raw" + flag. |
| 15 | `file_names` | | string \| null | Extensions drive `formats` (R2). |
| 16 | `current_location` | | string \| null | Operational pointer → STAC access note. |
| 17 | `migration_status` | | string \| null | Free string. |
| 18 | `server_path` | | string \| null | Internal path → STAC access note, never an asset href. |
| 19 | `date_registered` | | string \| null | Quote it. |
| 20 | `last_updated` | | string \| null | Quote it (registry cells are often bare years → `'2024'`). |
| 21 | `update_frequency` | | enum \| null | Annual, Seasonal, Monthly, On-demand, Static, Unknown. Null → "Unknown". |
| 22 | `download_url` | | string \| null | Raw value; pipeline extracts a real URL or nulls it (R8). |
| 23 | `file_size` | | string \| number \| null | Raw scalar; ints stay ints ("220 MB" stays a string). |
| 24 | `gee_asset_id` | | string \| null, `^projects/<cloud-project>/assets/<path>$` | Google Earth Engine asset ID of MOSAIC's copy (since 2026-09-23), e.g. `projects/mosaic-mfl/assets/mvp/MFL-2026-064`. **YAML-only** (the Excel path has no column). Published as STAC property `mosaic:gee_asset_id` and `gee_asset_id` in `datasets.json`. An ID, not a URL: `download_url` stays the canonical location, and no link is emitted while assets are private. Once an asset is public, the item also gets an `earth-engine` STAC asset whose href is the Earth Engine REST URL `https://earthengine.googleapis.com/v1/<gee_asset_id>` — the form the CDH uses (CDH issue #34, 2026-09-28). That URL needs a Google sign-in. |

## Forward-looking fields (assessment §4, Phase 1 — all default null)

Optional; omitted from the migrated files. **Validated but not yet consumed** by the
pipeline (a later phase will wire them into the STAC items — until then, filling them in
changes nothing in the outputs; this is documented so nobody is surprised).

| Key | Type | Notes |
|-----|------|-------|
| `encoding` | `stac` \| `ogc-records` \| null | Target encoding for the record. |
| `bbox` | `{xmin, ymin, xmax, ymax}` (numbers) \| null | The dataset's **own** extent, EPSG:4326. Never fabricated. |
| `crs` | string \| null | e.g. `EPSG:4326`. |
| `citation` | string \| null | Preferred citation. **Consumed:** passed to `datasets.json` and shown on the site as the "Suggested citation" (since 2026-08-03); not yet in STAC. |
| `doi` | string \| null | |
| `keywords` | list of strings \| null | |
| `media_type` | string \| null | IANA media type of the primary asset. |

## How a record becomes catalog output

`records/*.yaml` → `mosaic_pipeline/records.py` (`read_records`) → the **same**
`normalize_fields()` in `mosaic_pipeline/registry.py` that the Excel path uses (R1–R9
extractors in `transform.py`, landscape/bbox resolution in `vocab.py`) → `datasets.json`
+ `stac/`. Records are processed in ascending-`id` order (canonical build order for both
sources). The Excel path and the records path are required to produce **byte-identical**
artifacts as of the 2026-07-24 migration.

## Validation performed (pure python, `records.py`)

- YAML parses to a mapping; `.yaml` extension; filename stem = `id`.
- `id` pattern; ids unique across the directory.
- `title` present and non-blank; `living_landscape` present and in enum.
- Every enum/type/pattern rule in `record_schema.json` (unknown keys rejected).
- `bbox` shape (`xmin/ymin/xmax/ymax`, all numbers, no extra keys) when present.

## Adding a new dataset

1. Copy an existing record, rename to the next free `MFL-2026-###.yaml`, set `id` to match.
2. Fill what you know; leave the rest `null`. Quote year/date strings.
3. Run `python3 build_catalog.py` — it validates and rebuilds, and fails loudly on errors.
