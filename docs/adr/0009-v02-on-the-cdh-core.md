# ADR-0009: Standard v0.2 on the Climate Data Hub core

- Status: accepted (2026-11-05, review with Steven Sotelo and Andrés Aguilar)
- Supersedes in part: ADR-0001 (own standard guided by CDH), ADR-0002 (licence object),
  ADR-0006 (kind and method on access points)

## Context

v0.1 was MOSAIC's own standard, guided by CDH but with its own names and shapes (122 fields). The
team wants a single structure: MOSAIC records should follow the CDH structure so that a CDH record
and a MOSAIC record are the same kind of thing, without maintaining two schemas. At the same time,
MOSAIC data has things CDH does not describe (living landscapes, landing pages and data on
request, licence texts without an SPDX code, resolution for discovery), and the standard must
cover everything MOSAIC has or can be expected to have. Extensions are only for very particular
cases.

## Decision

- The record schema is the **CDH core v0.5.0** (MIT): same field names and shapes.
- MOSAIC additions go **into the core**, each with a reason (`docs/fields.xlsx`, column v0.1 /
  CDH): `themes`, `language`, `spatial.landscapes`, `spatial.resolution`, `temporal.text`,
  `license_text`, `citation.text`, `data[].access_method`, `kind`, `access`, `geometry_type`,
  `feature_count`, `service`, `data[].spatial.crs`, `derived`, `source_updated`; and two CDH
  extension blocks that are general: `commodities`, `usage`.
- **Extensions**: only `climate` (same fields as the CDH climate extension).
- **Minimum** aligned with CDH's required fields plus `themes` and an explicit `access`;
  `keywords` recommended for now. Completeness rules that CDH puts in its structure (licensor,
  citation or DOI, access_note, LicenseRef link) move to the levels, so an incomplete record is
  never invalid.
- Ids stay `MFL-YYYY-NNN`; the id pattern also accepts CDH lowercase ids.
- The 108 records are converted by `src/mosaic_catalog/v02.py` (moves and renames only).

## Consequences

- A CDH record is valid in MOSAIC after renaming `cdh_schema_version` and translating
  `cdh.domain` to `themes`; mosaic-api reads both catalogues with the same model.
- No record is complete today: none says who grants its licence (`licensor`). This is the main
  review item (`review/minimum_gaps`).
- The website and the API follow the new field names (generated types).
