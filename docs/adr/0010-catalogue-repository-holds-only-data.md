# ADR-0010: The catalogue repository holds only data; the standard has its own repository

- Status: accepted (2026-11-06, review of the catalogue; final approval by Lizeth pending)

## Context

MOSAIC-mfl/catalog held the records, the landscape profiles and everything around them: the
standard (schemas, vocabularies, crosswalks), the validator and build, scripts, tests, examples,
docs, ADRs, review lists, boundaries and the legacy of the first pipeline. The reviewers asked for
a catalogue that is only a catalogue of datasets, so that it does not fill up with things that are
not data.

## Decision

- **MOSAIC-mfl/catalog** keeps `records/<id>/record.yaml` and `landscapes/<CODE>/`, a short README,
  the dataset request template and two workflows that use this repository: `Validate` (pull
  requests) and `Publish` (builds `dist/` and publishes it on the catalogue's Pages, with the frozen
  STAC of `legacy/stac` at its old URL).
- **MOSAIC-mfl/mosaic-standard** (this repository) holds the rest. The tool keeps its name
  (`python -m mosaic_catalog`: it validates and builds the catalogue) and reads the catalogue from a
  checkout (`--catalog PATH` / `MOSAIC_CATALOG`).
- The schema `$id`s stay under `https://mosaic-mfl.github.io/catalog/schema/…`: the catalogue's
  Publish workflow keeps serving `schema/` and `vocab/` there.

## Consequences

- A change to the standard is a pull request here; a new or corrected record or profile is a pull
  request to the catalogue. Both are checked against each other (this repository's CI clones the
  catalogue; the catalogue's CI installs this repository).
- mosaic-api clones both to build what it harvests.
