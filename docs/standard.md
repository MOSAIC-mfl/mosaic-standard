# MOSAIC metadata standard v0.2 — design notes

Field by field: [`fields.md`](fields.md) and [`fields.xlsx`](fields.xlsx) (generated from the
schemas). Decisions: [`adr/`](adr/), in particular [ADR-0009](adr/0009-v02-on-the-cdh-core.md).

## 1. Purpose

MOSAIC is a network of metadata for the CGIAR Multifunctional Landscapes programme. It describes
geospatial and related resources wherever they live and links to them; it does not copy them. The
standard says what a record must contain so that a person or a program can find a resource,
understand it, use it legally and reach it, without opening its files.

## 2. Principles

1. **One structure, built on the CGIAR Climate Data Hub (CDH) core v0.5.0.** Same field names and
   shapes where they coincide (`contact`, `license`, `keywords`, `spatial`, `temporal`, `data`,
   `structures`, `citation`…). A CDH record is a MOSAIC record almost as it is; there are not two
   structures to maintain (review of 2026-11-05).
2. **A complete core.** It covers everything MOSAIC has or can be expected to have: themes,
   landscapes, the way data is reached (download, service, page, request), kinds of data,
   resolution, licence text, a data dictionary for rasters, vectors and tables. What CDH keeps in
   extensions but is general (commodities, usage guidance) is in the core.
3. **Extensions only for very particular cases** of one domain. Today: `climate` (projection
   provenance: models, scenarios, downscaling), the same fields as the CDH climate extension.
4. **Profiles are policy.** The MOSAIC profile asks for an `MFL-YYYY-NNN` id and the living
   landscapes. It is a warning until enforced in `mosaic.config.yaml`.
5. **Nothing is invented.** What the source does not state stays empty and is listed for review
   (`review/`). Values a tool reads from the data are marked in `derived`.
6. **FAIR** (section 6).

## 3. Levels

| Level | Schema | If it fails |
|---|---|---|
| Structure | `schema/record.schema.json` (+ declared extensions) | **Invalid**: the build stops |
| Minimum | `schema/levels/minimum.schema.json` | **Incomplete**: published flagged, listed in `review/minimum_gaps` |
| Recommended | `schema/levels/recommended.schema.json` | Warning |
| Profile MOSAIC | `schema/profiles/mosaic.schema.json` | Warning (minimum when enforced) |

## 4. The minimum

Aligned with the fields CDH requires, plus what MOSAIC needs to be usable:

| Field | Why |
|---|---|
| `id`, `title`, `description`, `resource_type` | Identify and understand the resource (F1, F2). |
| `themes` | Browse the catalogue by MFL theme (F2). CDH's `cdh.domain` maps to them. |
| `license` | Know whether it can be reused (R1.1): SPDX, or `LicenseRef-…` with its text or link. |
| `contact` | Who answers for the resource, each with its organization and roles; **one must be the licensor** (who grants the licence, R1.2). |
| `access` (+ `access_note` when not public) | Always explicit in MOSAIC (CDH assumes public when it is absent): 45 records are not public. |
| `data` | At least one entry with its name; a public resource needs a location (A1, F3). |

`keywords` are required by CDH; in MOSAIC they are recommended for now (decision of 2026-11-05):
no migrated record has them.

## 5. Data entries and the data dictionary

Each `data[]` entry is one way to reach the data:

- `locations[]`: URLs. CDH accepts only machine-actionable URLs (a file, a store, a service);
  MOSAIC also accepts a landing page or the page where data is requested, because most MFL data is
  reached that way (62 + 40 records). `access_method` says which (`download`, `service`,
  `landing_page`, `request`).
- `kind` (raster, vector, tabular, document, mixed, other), `media_type`, `file_size`,
  `geometry_type` and `feature_count` for vectors, `spatial.crs` of the entry, `service` (type and
  layers), `access` when it differs from the record.
- `structures[]` (CDH): one data dictionary for every kind of data. Variables are raster bands,
  vector attributes or table columns (name, description, unit, data type, nodata, categories);
  dimensions are time, x / y (coordinate columns or a regular grid), z or other axes.

## 6. FAIR

| Principle | How |
|---|---|
| F1 persistent identifier | `id` never reused; with its catalogue it is a global id (`mosaic:MFL-2026-079`) resolvable in the API; `doi` when there is one. |
| F2 rich metadata | Description, themes, keywords, spatial and temporal coverage, data dictionary, usage. |
| F3 identifier of the data | `data[].locations[].url`, `doi`. |
| F4 indexed | Catalogue on Pages, API with search, website. Pending: schema.org JSON-LD in each dataset page for dataset search engines. |
| A1 open protocol | HTTPS; the metadata needs no authentication. |
| A1.2 authorisation | `access`, `access_note`, `data[].access`. |
| A2 metadata persists | Records are not deleted; `deprecated` and `previous_version` mark replacements. |
| I1 formal language | JSON Schema 2020-12; the CDH names, which CDH maps to schema.org and STAC. |
| I2 FAIR vocabularies | Controlled vocabularies with ids (themes, resource types, ISO 3166 / UN M49, DCAT access rights, roles), SPDX, IANA media types, UDUNITS, ORCID, ROR; keywords with scheme and URI (AGROVOC). |
| I3 qualified references | `additional_links[].rel`, `related_publications`, `processing[].derived_from`, `structures[].foreign_keys`, `parent`. |
| R1.1 licence | `license` in the minimum. |
| R1.2 provenance | Contact roles, `processing`, `derived`, `created`, `updated`, `source_updated`. |
| R1.3 community standard | Aligned with the CDH core (CGIAR). |

## 7. From v0.1 to v0.2

`src/mosaic_catalog/v02.py` (run by `scripts/migrate_v02.py`) moves and renames only:

| v0.1 | v0.2 |
|---|---|
| `geography`, `mosaic.landscapes`, `update_frequency` | `spatial.geography`, `spatial.landscapes`, `temporal.update_frequency` |
| `temporal.start` / `end` | `temporal.start_date` / `end_date` (`date` when they are equal) |
| `license {spdx, url, text}` | `license` (SPDX or `LicenseRef-source-terms`), `license_text`, `additional_links` (rel: license) |
| `contacts` | `contact` |
| `citation` as text | `citation.text` |
| `access: internal` | `access: non-public` |
| `data[].method`, `url`, `size` | `access_method`, `locations[].url`, `file_size` |
| `data[].raster / vector / tabular` | `geometry_type`, `feature_count`, `spatial.crs` of the entry, and `structures[]` |
| `data[].service.service_type` | `data[].service.type` |
| `related[]` | `related_publications[]` / `additional_links[]` |
| `data[].derived` | `derived` (one list per record) |
| `slug`, `mosaic.intake`, `document.pages`, `tabular.spatial`, `service.auth_required`, `citation.version` | dropped (unused, deduced, or workflow state kept in git) |

Notes per record: `review/migration_v02.md`.

## 8. Reading other catalogues

A catalogue that follows the CDH core is read field for field (`crosswalks/cdh.yaml` lists the
few differences: `cdh.domain` → `themes`, `cdh.usage` → `usage`, `cdh_schema_version` →
`schema_version`). A catalogue in another format needs a crosswalk and a translator in mosaic-api;
its values that have no place are reported, never dropped silently.

## 9. Open questions

- Who grants the licence (`licensor`) for each of the 108 records.
- SPDX codes for the 65 records that only have licence text.
- Keywords: when they become part of the minimum again.
- schema.org JSON-LD in the website's dataset pages (FAIR F4).
