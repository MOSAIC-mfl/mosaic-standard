# MOSAIC standard

> **Status: standard v0.2.0, new repository (2026-11-06).** It holds what used to live next to the
> records in [MOSAIC-mfl/catalog](https://github.com/MOSAIC-mfl/catalog) and is not data: the
> standard, its tooling, examples, docs and review lists. The catalogue repository keeps only the
> records and the landscape profiles. The API lives in
> [MOSAIC-mfl/mosaic-api](https://github.com/MOSAIC-mfl/mosaic-api).

MOSAIC is a network of metadata. It describes geospatial and related resources wherever they live
and links to them; it does not copy them. Three repositories:

| Repository | Holds |
|---|---|
| **mosaic-standard** (this one) | the metadata standard (JSON Schemas, vocabularies, crosswalks), the validator and build (`mosaic_catalog`), examples, docs, ADRs, review lists |
| [catalog](https://github.com/MOSAIC-mfl/catalog) | only data: `records/<id>/record.yaml` and `landscapes/<CODE>/` (landscape profiles). Its workflows use this repository to validate pull requests and to publish `dist/` |
| [mosaic-api](https://github.com/MOSAIC-mfl/mosaic-api) | harvests the catalogue (and the CGIAR Climate Data Hub) and serves it |

What this repository provides:

1. **The MOSAIC metadata standard.** JSON Schemas, controlled vocabularies and crosswalks to other
   catalogues. Since v0.2 the record uses the field names and shapes of the CGIAR Climate Data Hub
   (CDH) core v0.5.0, plus what MOSAIC needs, in the same core.
2. **The tool** (`python -m mosaic_catalog`). It validates the records and the landscape profiles
   of a catalogue checkout and builds what the API reads (`dist/catalog.json`,
   `dist/manifest.json`, `dist/landscapes/`, plus `schema/`, `vocab/`, `crosswalks/`).
3. **Docs and review.** Field reference, design notes, ADRs, the guide to landscape profiles, and
   the review lists of the records (`review/`).

## The standard in one minute

| Level | What | If it is missing |
|---|---|---|
| **Structure** | Every field has the right shape and uses the vocabularies | **Invalid:** the check fails and must be fixed |
| **Minimum** | Enough to find, understand, use legally and reach the resource | **Incomplete:** listed in `review/minimum_gaps.csv` and published flagged (configurable) |
| **Recommended** | Keywords, coverage (geography, bbox, period), citation or DOI, how each data entry is reached and what it holds… | Warning |
| **Profile MOSAIC** | MFL id and living landscapes (`spatial.landscapes`) | Warning (can be enforced in `mosaic.config.yaml`) |
| **Extensions** | Only for very particular cases: `climate@0.2.0` (projection provenance, as in CDH) | Invalid if malformed or undeclared |

**The minimum** (`schema/levels/minimum.schema.json`):

- `id`, `title`, `description`, `resource_type`, `themes`
- `license`: SPDX (`CC-BY-4.0`), or `LicenseRef-…` with its text (`license_text`) or link
- `contact`: each with `organization` and `roles`; at least one **licensor** (who grants the licence)
- `access` (always explicit: `public`, `restricted`, `non-public`); `access_note` when not public
- `data`: at least one entry with a `name`; a **public** resource needs a location (`locations[].url`)

`keywords` are required by CDH and recommended in MOSAIC for now. Design and FAIR notes:
[`docs/standard.md`](docs/standard.md).

Further reading:

- All fields with their level, type, values and equivalents (CDH v0.5.0, MOSAIC v0.1):
  [`docs/fields.xlsx`](docs/fields.xlsx), [`docs/fields.md`](docs/fields.md), and a record with every
  field commented: [`docs/record-reference.yaml`](docs/record-reference.yaml). All three are
  generated from the schemas.
- Why each decision was taken: [`docs/standard.md`](docs/standard.md) and [`docs/adr/`](docs/adr/).

## Layout

```
schema/
  record.schema.json             structure of a record: the CDH core v0.5.0 + MOSAIC fields (types, vocabularies)
  levels/minimum.schema.json     level 0
  levels/recommended.schema.json level 1
  profiles/mosaic.schema.json    MOSAIC profile (not enforced)
  extensions/climate/0.2.0/      climate extension (same fields as the CDH one)
  extensions/_template/          how to add an extension (only for very particular cases)
  vocab.schema.json              generated from vocab/
vocab/                           themes, landscapes, geography (ISO 3166 / UN M49), access, data kinds, access methods, service types, roles…
crosswalks/cdh.yaml              the few differences between a Climate Data Hub record and a MOSAIC record
crosswalks/mosaic-schema1.yaml   how the old schema-1 records were migrated
schema/landscape/                schemas of the landscape profile files (the profiles are in the catalogue)
review/                          minimum_gaps, classification_gaps, migration_notes, migration_v02, inference_report
examples/                        real records converted by hand (999 a rich one, with an example id; 079 and 090)
tests/fixtures/                  valid / invalid / incomplete cases the suite checks
src/mosaic_catalog/              validator, build, inference, CLI; v02.py converts v0.1 records
scripts/                         build_vocab.py, build_docs.py, build_reference.py, migrate_schema1.py, migrate_v02.py,
                                 migrate_lake_victoria.py, migrate_ucayali.py (explorers -> landscape profiles)
mosaic.config.yaml               standard version, enforced profiles, publish incomplete records or not
boundaries/                      landscape delineations (GeoJSON), kept from the first pipeline
docs/history/                    decisions, guides and record changelogs of the first pipeline
legacy/                          Excel registry, schema 1, pending submission, frozen STAC (legacy/README.md);
                                 the catalogue's Publish workflow serves legacy/stac at its old URL
development/                     how the standard, catalogue, API and website work together (run, publish,
                                 the landscape-profile skill of mosaic-skills): development/README.md
```

## Use

The commands that read records or profiles need a checkout of the catalogue: `--catalog PATH`
(before the command) or the environment variable `MOSAIC_CATALOG`.

```sh
pip install -e ".[dev]"                     # Python 3.10+
git clone https://github.com/MOSAIC-mfl/catalog.git ../catalog   # (branch metadata-standard-v0.1 until merged)
export MOSAIC_CATALOG=../catalog            # Windows: set MOSAIC_CATALOG=..\catalog

python -m mosaic_catalog validate examples  # check records (text report)
python -m mosaic_catalog validate examples -v --format json
python -m mosaic_catalog validate --gaps review/minimum_gaps   # the catalogue's records; writes the review list
python -m mosaic_catalog infer              # read public downloadable files, fill geometry type, counts, data dictionary (needs pyshp)
python -m mosaic_catalog validate-landscapes # the landscape profiles
python -m mosaic_catalog build              # dist/catalog.json + dist/manifest.json + dist/landscapes/ for the API
python -m mosaic_catalog --catalog ../catalog build --out ../catalog/dist   # same, explicit
pytest -q                                   # tests (those on the real records and profiles need MOSAIC_CATALOG)
python scripts/build_vocab.py               # after editing a vocabulary in the script
python scripts/build_docs.py                # after editing a schema
python scripts/build_reference.py           # docs/fields.xlsx + docs/record-reference.yaml
```

Exit code 1 means at least one record is **invalid**. Incomplete records do not fail the check:
they go to the review list.

Editors with the YAML language server can validate while typing (once the schemas are published):

```yaml
# yaml-language-server: $schema=https://mosaic-mfl.github.io/catalog/schema/v0.2.0/record.schema.json
```

## Rules for changes

- A branch per topic, pull request, green checks (`Check` runs on every pull request, against the
  catalogue). Lizeth reviews any change to the standard or the build; record and profile changes
  go to the catalogue repository.
- `vocab/*.json`, `schema/vocab.schema.json` and `docs/fields.md` are generated. Change the script
  or the schema, then regenerate.
- Nothing is invented: what the source does not state stays empty and is reported.

## Migration from the old catalogue (phase 2)

The 108 records were converted from the schema-1 records of this repository's first pipeline
(main @ `0dad25c`, see [`legacy/README.md`](legacy/README.md)) by `scripts/migrate_schema1.py`,
which reads them with `git show 0dad25c:records/...` (`--ref`). Mapping: [`crosswalks/mosaic-schema1.yaml`](crosswalks/mosaic-schema1.yaml).

```sh
python scripts/migrate_schema1.py --source ../catalog --ref 0dad25c --out ../catalog/records   # reads the first pipeline
python scripts/migrate_v02.py --catalog ../catalog             # v0.1 -> v0.2 (already applied; leaves v0.2 records as they are)
python -m mosaic_catalog --catalog ../catalog validate --gaps review/minimum_gaps
```

**Results:**

- **108 records migrated** (catalog main @ 0dad25c), converted to v0.2 (`review/migration_v02.md`).
  None is invalid, and none is complete yet: no record says who grants its licence (licensor), and
  in 107 a contact has no organization. Recommended gaps: no keywords, 92 without citation, 65
  licences without an SPDX code.
- **`review/minimum_gaps.csv`** lists what is missing for the minimum, with the person to ask. Its
  `decision` column is for the outcome: complete, publish incomplete, or withdraw.
- **`review/migration_notes.csv`** lists conversions a person should check: licence texts that
  describe access, `NATIONAL`/`GLOBAL` landscapes, periods without a year, and so on.
