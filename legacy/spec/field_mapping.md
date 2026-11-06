# MOSAIC field_mapping.md — Excel registry → frontend datasets.json AND → STAC

**Scope:** v1, functional. Two outputs from one registry row:
1. **Frontend** `frontend/data/datasets.json` (flat record, the live data contract).
2. **STAC** Collection JSON skeleton (`encoding: stac`), per the §3 crosswalk of `MOSAIC_CDH_Interoperability_STAC_Assessment_202606.md`.

**Source:** `MFL_Dataset_Registry.xlsx`, sheet `' Registry'` (LEADING SPACE in name). 23 columns. **Skip the first data row** (placeholder/instructions: values like "Auto-filled by formula", "Select from dropdown"). A row is a placeholder if Record ID is blank or any cell equals one of: `Auto-filled by formula`, `Select from dropdown`, or the instruction sentences.

**Checked (2026-06-22):** CDH `vocab/geography.json` (UN M49 confirmed) and `spec/mapping-stac.md` (contact roles = STAC provider roles; `file:size` required for primary asset; `cgiar-cdh:geography` array; SPDX preferred for license). **Re-checked 2026-09-28 against CDH v0.3.0** (repo now `cdh-metadata-standard`): extension id = `…/v0.3.0/encodings/stac/schema.json`; `cgiar-cdh:geography` unchanged (array, at least 1); `cgiar-cdh:spatial_resolution` is now structured.

---

## 1. Excel column → frontend datasets.json key

| datasets.json key | Excel column | Rule |
|---|---|---|
| `id` | 1 Record ID | Keep `MFL-…` as-is (trim). If blank → generate `MFL-2026-<3-digit row index>` (see R6). Must be unique. |
| `title` | 2 Dataset title | Trim. If blank → `"Untitled dataset (<id>)"` and FLAG. |
| `country` | 3 Country | Map to canonical country enum (see vocab_reconciliation.md). Malformed `"Soil dataset"` → `null` + FLAG. |
| `living_landscape` | 5 Living landscape | Replace free text with CODE via `living_landscape_crosswalk.json` (trim+lowercase match). Unmatched → `GLB-UNSPEC` + FLAG. |
| `mfl_theme` | 4 MFL theme | Map to mfl_theme enum. `"Soil dataset"` → `null` + FLAG. |
| `data_type` | 6 Data type | Map to data_type enum {Raster,Vector,Tabular,Mixed}. `"Soil dataset"` → `null` + FLAG. |
| `spatial_resolution` | 7 Spatial resolution | Keep raw string for frontend display. See R5 (flag non-numeric). |
| `temporal_coverage` | 8 Temporal coverage | Keep raw string for frontend. (STAC splits it — R4.) |
| `source` | 9 Source / Centre | Trim. Map to centre enum where it matches (vocab_reconciliation.md). |
| `contact` | 10 Contact person | Extract **email** only (R1). If no email → `null`. |
| `access_level` | 11 Access level | Map to access_level enum {Open, Internal, Restricted}. Source `CGIAR-internal`/`CGIAR internal` → `Internal`. |
| `license` | 12 License | Map toward SPDX id; keep original as alias if non-SPDX (R3). |
| `readiness_status` | 13 Processing status | Map Raw/Processed/Validated → v1 readiness vocab (R7). |
| `formats` | 6 Data type + 14 File name(s) | Array; derive from file extensions, fallback to data_type (R2). |
| `description` | 18 Description / Notes | Trim. Empty string if blank. |
| `download_url` | 22 Primary source / Download URL | Clean (R8). Non-URL/"Internal"/"One drive" → `null`. |
| `metadata_url` | (generated) | Relative path to this dataset's STAC Item/Collection JSON (R9). |

Frontend keys NOT sourced from one column: `formats`, `metadata_url` (derived). `living_landscape` is the CODE, never the free text.

---

## 2. Excel column → STAC placement (`encoding: stac`, Collection-level)

Per §3 of the assessment. Use `cgiar-cdh:*` where the CDH defines it, `mosaic:*` for MOSAIC-only fields.

| Excel column | STAC placement | Namespace |
|---|---|---|
| 1 Record ID | `id` | core |
| 2 Dataset title | `title` | core |
| 3 Country | `cgiar-cdh:geography` (array of UN M49 ids) + drives `extent.spatial.bbox` | cgiar-cdh + core |
| 4 MFL theme | `themes[]` (Themes ext) + `mosaic:theme` | mosaic |
| 5 Living landscape | `mosaic:living_landscape` (CODE) | mosaic |
| 6 Data type | object type + asset `media_type`; selects Datacube vs Table ext | core |
| 7 Spatial resolution | `mosaic:spatial_resolution` (verbatim string; omitted when blank). CDH v0.3.0 `cgiar-cdh:spatial_resolution` takes only structured point/polygon objects and grid spacing goes to `cube:dimensions[].step`, so MOSAIC's free text stays in its own namespace | mosaic |
| 8 Temporal coverage | Item `start_datetime`/`end_datetime` + collection `extent.temporal.interval` (R4). No period → item `datetime` = the date the record was catalogued (`date_registered`, else 2026-07-21, the canonical snapshot); an open end ("present") closes on that date; both flagged in `mosaic:datetime_note` (since 2026-09-28) | core + mosaic |
| 9 Source / Centre | `providers[]` (role producer/host) | core |
| 10 Contact person | `providers[]` + Contacts ext `contacts[]`; roles per R10 | core + Contacts ext |
| 11 Access level | `mosaic:access_level` | mosaic |
| 12 License | `license` on items (since 2026-09-28) and collections: the SPDX id (R3); a verbatim or vague string → `other`, with the text in `mosaic:license_original`. Item: omitted when blank. Collection: the members' shared SPDX id, else `other` | core |
| 13 Processing status | `mosaic:processing_status` | mosaic |
| 14 File name(s) | `assets{}` keys / `data[].name` | core |
| 15 Current location | `mosaic:access_note` (item property, with 17 and the source note); never an asset — STAC asset `href`s must resolve | mosaic |
| 16 Migration status | `mosaic:migration_status` | mosaic |
| 17 Server path | `mosaic:access_note` (see 15) | mosaic |
| 18 Description / Notes | `description` (+ `cgiar-cdh:note` for structured leftovers) | core + cgiar-cdh |
| 19 Date registered | `created` (RFC 3339, midnight UTC), only when it is a full date; otherwise omitted | core |
| 20 Last updated | `mosaic:last_updated` (verbatim: mostly a bare year, and it describes the data; STAC `updated` is the metadata's own timestamp) | mosaic |
| 21 Update frequency | `mosaic:update_frequency` | mosaic |
| 22 Download URL | primary asset `href` / `links[rel=via]` | core |
| 23 File Size | `file:size` (File ext) | File ext |

**YAML-only record fields (no Excel column):** `citation` → `datasets.json` `citation`; `gee_asset_id` (since 2026-09-23) → STAC item property `mosaic:gee_asset_id` (only when set) + `datasets.json` `gee_asset_id`. MOSAIC-local: the CDH has no Earth Engine field and plans none (CDH issue #34, 2026-09-28). It puts the Earth Engine REST URL (`https://earthengine.googleapis.com/v1/<gee_asset_id>`) in a data location, and MOSAIC adds that same URL as an `earth-engine` asset once an asset is public.

**Boundary asset fields (no registry source; since 2026-09-29):** each delineated landscape's collection carries a `boundary` asset with `license`, `mosaic:license_url`, `mosaic:source` and `mosaic:attribution`, and the same four facts ride in the boundary GeoJSON's feature properties. They come from `spec/boundary_provenance.json`, one entry per landscape code, not from a registry row — see R11.

**Not in registry, set by exporter:** `encoding: "stac"` (all spatial rows; a non-spatial document row → `"ogc-records"`), `mosaic_schema_version`, `extent.spatial.bbox` (from `bbox_lookup.json` until real geometries exist), `proj:code`/`proj:epsg` (CRS — absent in registry, leave null + FLAG). **Official STAC 1.0.0 schema conformance** since 2026-09-28 (MOSAIC STAC extension 0.3.0: `mosaic:access_note`, `mosaic:last_updated`, `mosaic:datetime_note`); `validate.py` enforces RFC 3339 dates and non-empty asset hrefs.

**SKIP (CDH owns):** the climate block (`climate.*`) and CDH climate vocabularies (hazard, commodity). For climate layers, MOSAIC links to the CDH via `links[rel=related|via]` — do not redefine.

---

## 3. Transformation RULES (code these exactly)

### R1 — Contact email extraction (col 10 → `contact`)
Input is messy "Name - email" / "Name, email" / "Name (email)" / just a name / just an email.
1. Regex-find first email: `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`.
2. If found → `contact = <that email, lowercased, trimmed>`.
3. If none → `contact = null` and FLAG `missing_contact_email`.
4. (STAC only) the name portion = text before the first of ` - `, `,`, `(`; use for `contacts[].name`. Email → `contacts[].email`. Roles per R10.

### R2 — formats[] derivation (cols 6 + 14 → `formats`)
1. From col 14 File name(s): extract all file extensions (regex `\.([A-Za-z0-9]{1,5})(?=[\s,;]|$)`), uppercase, dedupe. Map common ones: `tif/tiff→GeoTIFF`, `shp→Shapefile`, `gpkg→GeoPackage`, `csv→CSV`, `xlsx→XLSX`, `nc→NetCDF`, `geojson→GeoJSON`, `json→JSON`, `zarr→Zarr`, `parquet→Parquet`.
2. If no extensions found, fall back to col 6 Data type: `Raster→["GeoTIFF"]`, `Vector→["Shapefile"]`, `Tabular→["CSV"]`, `Mixed→["Mixed"]`.
3. Result is always a non-empty array; if everything fails → `["Unknown"]` + FLAG.

### R3 — License → SPDX (col 12 → `license`)
Map known values to SPDX ids; keep unknown CGIAR-specific strings verbatim and FLAG `non_spdx_license`.
Rules apply top to bottom (revised 2026-09-23; the emitted ids are `SPDX_LICENSE_IDS` in `transform.py`).
| Registry value (case-insensitive) | `license` |
|---|---|
| starts with "Restricted" (project rule: GADM, WDPA, IUCN, OSM/ODbL) | keep verbatim + FLAG `non_spdx_license`, even if it names a license |
| ODbL / Open Database License | `ODbL-1.0` |
| ODC-BY / Open Data Commons Attribution | `ODC-By-1.0` |
| PDDL / Public Domain Dedication and License | `PDDL-1.0` |
| any other "Open Data Commons" / ODC | keep verbatim + FLAG `non_spdx_license` |
| CC BY family, abbreviated ("CC BY-NC-SA 4.0") or long ("Creative Commons Attribution-NonCommercial-…") | `CC-BY[-NC][-SA\|-ND]-<version>[-IGO]`, e.g. `CC-BY-NC-SA-4.0`, `CC-BY-3.0-IGO`. No version → 4.0; IGO → 3.0 (its only version) |
| CC combination SPDX does not list (e.g. CC BY-ND 3.0 IGO, CC BY 4.0 IGO) | keep verbatim + FLAG `non_spdx_license` |
| CC0 / public domain | `CC0-1.0` |
| Open / open data (no specific license) | `other` + FLAG `vague_license` |
| (blank) | `null` + FLAG `missing_license` |
| anything else (e.g. "CGIAR internal use") | keep verbatim + FLAG `non_spdx_license` |

The original string travels as the alias whenever the value is verbatim or `other`, and is published as STAC `mosaic:license_original` (verbatim values are also `license` in `datasets.json`).

### R4 — Temporal coverage split (col 8 → STAC `extent.temporal.interval`)
Frontend keeps the raw string. For STAC only:
1. Find years/dates. Two found → `[["<start>-01-01T00:00:00Z","<end>-12-31T23:59:59Z"]]`.
2. One year found → `[["<y>-01-01T00:00:00Z","<y>-12-31T23:59:59Z"]]`.
3. None parseable (e.g. "Static", text) → `[[null, null]]` + FLAG `unparsed_temporal`.

### R5 — Spatial resolution (col 7 → `spatial_resolution`)
Keep the raw string for frontend. FLAG `non_numeric_resolution` when the value is not of form `<number><unit?>` (e.g. "Village level", "Admin - MFLLs Boundary", "5000", "25000" with no unit). These need `{value,unit}` normalization before STAC data-cube export — defer to Phase 2; do NOT block v1.

### R6 — id generation / normalization (col 1 → `id`)
1. Present → trim, keep verbatim (preserve `MFL-2026-000` style).
2. Blank → generate `MFL-2026-<NNN>` where NNN = zero-padded sequential index among real (non-placeholder) rows, starting after the highest existing `MFL-2026-NNN` to avoid collision.
3. Enforce uniqueness across the run; on duplicate append `-2`, `-3` and FLAG `duplicate_id`.

### R7 — readiness_status map (col 13 → `readiness_status`)  ** DECISION **
**v1 readiness_status vocab = the registry's own three values: `["Raw","Processed","Validated"]`.**
Rationale: the registry IS the single source of truth; remapping onto the 5-value frontend enum (`Registered only / Under review / Accepted / Validated / Analytics-ready`) invents distinctions the data does not carry and risks misclassification. Simplest correct answer wins. **Update the frontend `metadata_schema.json` readiness_status enum to `["Raw","Processed","Validated"]`** (see vocab_reconciliation.md).
Map:
| col 13 value | `readiness_status` |
|---|---|
| Raw | `Raw` |
| Processed | `Processed` |
| Validated | `Validated` |
| (blank / other) | `Raw` + FLAG `missing_readiness` |

### R8 — download_url cleaning (col 22 → `download_url`)
1. Trim. Take first line if multi-line.
2. Valid only if it starts with `http://` or `https://` (or `ftp://`).
3. Reject (→ `null`) free text: `Internal`, `One drive`, `OneDrive`, `On request`, `N/A`, `-`, `TBD`, server paths, anything without a scheme. FLAG `non_url_download` so it can later become an access note rather than an `href`.

### R9 — metadata_url generation (→ `metadata_url`)
Relative path convention pointing to this dataset's STAC JSON:
```
metadata_url = "stac/collections/" + <id> + "/collection.json"
```
- `<id>` is the cleaned/normalized id from R6, URL-safe (replace any char outside `[A-Za-z0-9._-]` with `-`).
- This file need not exist yet in v1 (STAC export is Phase 2); the path is the stable contract the exporter will honor. Frontend may treat a 404 gracefully.
- One Collection per dataset (registry is collection-level per §3.4). Item-level deferred.

---

### R10 — Contact roles (col 10 → STAC `contacts[].roles`)  ** DECISION **
Replaces the original rule, which hardcoded `["producer","licensor"]` on every item and
forced a `licensor` where none existed (Lizeth, 2026-10-15). In STAC/OGC `licensor` names
the party that **granted** the licence, so:

1. If the record's data belongs to a third party → `["point-of-contact"]`.
   The set of such records is `stac_build.py:THIRD_PARTY_RIGHTS`, grouped by rights holder.
2. Else if `license` is an SPDX id → `["producer", "licensor"]`.
3. Else → `["producer"]`.

An SPDX id alone is **not** sufficient for `licensor`: MFL-2026-066 is iSDAsoil under
CC BY 4.0, but iSDA is the licensor, not the AfricaRice contact. The judgement is who holds
the rights, which the registry does not record — so it lives in the pipeline, not the record
schema (decided 2026-10-15, no schema change). Add an id to `THIRD_PARTY_RIGHTS` when a new
record turns out to re-describe someone else's data.

Result on the 89 published records: 52 `point-of-contact`, 30 `producer`, 7 `producer`+`licensor`.
Sweep behind the list: `MFL SP docs/project docs/MOSAIC internal/stac_contact_roles_sweep_2026-10-15.md`.
The flag `no_licensor_assigned` is retired — having no licensor is now a valid outcome.

### R11 — Landscape boundary provenance (`spec/boundary_provenance.json` → boundary GeoJSON + STAC `boundary` asset)
Not a registry rule: provenance belongs to a landscape (11 canonical codes), not to a dataset record. The one source is `spec/boundary_provenance.json` (keyed by code; `_meta` is skipped), read by two writers — `scripts/build_boundaries.py` (GeoJSON) and `mosaic_pipeline/stac_build.py:_boundary_asset()` (STAC). Added 2026-09-29 (`a90d4f4`, `806850d`).

| provenance key | GeoJSON property (`boundaries/<CODE>.geojson`, `landscapes.geojson`) | STAC `boundary` asset field | Rule |
|---|---|---|---|
| `source` | `source` | `mosaic:source` | Verbatim: what the geometry was derived from. Filled for all 11; the code does not enforce it. |
| `license` | `license` | `license` | Verbatim: an SPDX id when the licence has one, else `other`. **Not passed through R3.** Today: 9 `other`, `CC-BY-4.0` (ETH-OG), `CC-BY-3.0-IGO` (TUN-NW). |
| `license_url` | `license_url` — always present, `null` when none | `mosaic:license_url` — **omitted** when none | Where the terms are stated. None for COL-CUM and PER-PCL. |
| `attribution` | `attribution` | `mosaic:attribution` | Verbatim: the credit line to reproduce. Filled for all 11; the code does not enforce it. |
| `source_url` | not written | not written on a `boundary` asset; becomes the `href` of a `boundary-source` asset (rule 3) | Link to the source's own page. |
| `publish` | `true` → `<CODE>.geojson` is written; `false` → the file is deleted and the geometry withheld | **not read** — see rule 3 | All 11 are `true` since 2026-09-29 (Lizeth). |

1. **Verbatim copy.** The four fields are copied as written in the provenance file: no trimming, no mapping, no validation. The GeoJSON gets them in `scripts/build_boundaries.py`, which stops with an error if a canonical code has no entry; `landscapes.geojson` is the combined collection of the published features.
2. **The asset.** `stac_build.py` adds it to the **collection**, never to an item, and only for a delineated landscape (not `GLB`). Key `boundary`; `href` = `{STAC_BASE_URL}/boundaries/<CODE>.geojson`; `type` `application/geo+json`; `roles` `["data"]`; `title` "Landscape boundary (canonical delineation, simplified, EPSG:4326)"; plus the four fields above. `license` is a STAC common-metadata field on the asset; the other three are `mosaic:*`.
3. **Published is decided by the file, not by `publish`.** `stac_build.py` calls the boundary published when `boundaries/<CODE>.geojson` exists. If it does not and the provenance entry has a `source_url`, the asset is keyed `boundary-source` instead: `href` = `source_url`, `type` `text/html`, `roles` `["metadata"]`, title "Source of the landscape boundary (geometry not redistributed by MOSAIC)", same four fields, and the collection description says the geometry is not redistributed. If there is no file and no `source_url`, there is no asset. This path is currently unused.
4. **No provenance entry → no fields.** If a code has no entry, or `spec/boundary_provenance.json` is missing, `stac_build.py` still writes the asset, with no `license`, `mosaic:source` or `mosaic:attribution`, and raises no error.
5. **The asset licence is its own.** The collection's `license` still follows row 12 (the members' shared SPDX id, else `other`) and does not look at the boundary: ETH-OG's collection is `other` while its `boundary` asset is `CC-BY-4.0`.
6. **Catalog link.** `catalog.json` links `boundaries/landscapes.geojson` as `rel: related`, titled "…(simplified; licence per feature)".
7. **Not checked by `validate.py`.** It requires only a non-empty `href` on each asset; it does not require the four fields.
8. **Extension version.** The three `mosaic:*` asset fields were added without a version bump; the MOSAIC extension is still 0.3.0.

Result on the 11 published landscapes: every GeoJSON feature and every `boundary` asset carries all four fields, equal to the provenance file; 9 have `license_url`, COL-CUM and PER-PCL do not.

## 4. Data-quality FLAGS the engineer must emit (for a side report, not to block v1)
`missing_contact_email`, `non_spdx_license`, `vague_license`, `missing_license`, `unparsed_temporal`, `non_numeric_resolution`, `duplicate_id`, `missing_readiness`, `non_url_download`, `malformed_row` (the "Soil dataset" record), `unmatched_living_landscape`, `missing_crs`.

Emit as `flags: []` per record in an export log. v1 ships even with flags present.
