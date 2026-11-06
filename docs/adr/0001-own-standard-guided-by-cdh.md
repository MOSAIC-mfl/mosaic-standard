# ADR-0001: MOSAIC has its own metadata standard, guided by CDH

- Status: proposed (2026-10-30)
- Superseded in part by [ADR-0009](0009-v02-on-the-cdh-core.md) (2026-11-05): v0.2 uses the CDH core structure itself.
- Deciders: Lizeth Llanos, Steven Sotelo, Santiago Calderón

## Context

MOSAIC will list its own records and records read from other catalogues (CGIAR Climate Data Hub
first, then others). The CDH standard is mature and well designed, but it is built for a climate
hub. MOSAIC is global, covers more than climate, and has to federate catalogues with different
formats.

## Decision

- MOSAIC defines its own standard: JSON Schemas in `schema/` and vocabularies in `vocab/`.
- The CDH "bare minimum" is the starting point of the MOSAIC minimum, with MOSAIC's own names and
  choices (see `docs/standard.md` §4 and §6).
- Other catalogues are read through crosswalks (`crosswalks/`). MOSAIC does not adopt their
  formats, and does not write records in them.

## Consequences

- MOSAIC can change its standard without waiting for another project.
- Each external catalogue needs a crosswalk and a translator in the API, and both have to be
  maintained when that catalogue changes its format.
