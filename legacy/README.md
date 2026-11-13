# legacy/ — the first catalogue pipeline (until 9abbfc6)

Until commit `0dad25c` (records) and `9abbfc6` (boundaries, last commit of the old `main`) this repository built the catalogue with `build_catalog.py`: records in
`records/<ID>.yaml` (schema 1), an Excel registry as a working view, a static STAC catalog and the
`datasets.json` read by the website. Branch `metadata-standard-v0.1` replaces that pipeline with the
MOSAIC metadata standard v0.1 (see the [README](../README.md)). All 108 records were migrated by
`scripts/migrate_schema1.py`; what the migration did per record is in
[`review/migration_notes.md`](../review/migration_notes.md).

What is kept here, unchanged, and why:

| Path | What | Why it stays |
|---|---|---|
| `registry/` | `MFL_Dataset_Registry.xlsx` and its `SNAPSHOT_NOTE.md` | The last Excel view of the registry, for people who used it. It is no longer regenerated. |
| `spec/` | Schema 1 (`record_schema.json/.md`), field mapping, vocabulary reconciliation, living-landscape crosswalk, bbox lookup, boundary provenance, registry workbook texts | The definitions the migration read; `boundary_provenance.json` and `bbox_lookup.json` document `../boundaries/`. |
| `pending/` | `MFL-2026-043` and its README | A submission that was waiting for information and was never a published record. It is not migrated. |
| `stac/` | The STAC catalog as last built on the old `main` (`9abbfc6`, 2026-11-12: KEN-LVB boundary of 2026-11-10 and the corrected landscape names) | Frozen. The Pages workflow still publishes it at `https://mosaic-mfl.github.io/catalog/stac/` so existing links keep working. It is not updated when records change: the current catalogue is `catalog.json` and the API (mosaic-api). |
| `scripts/build_boundaries.py` | Rebuilds `boundaries/` from the delineation shapefiles | Local only, needs geopandas. Its paths are those of the old layout (`spec/` is now `legacy/spec/`). |

The rest of the old pipeline (`build_catalog.py`, `mosaic_pipeline/`, its tests and scripts,
`datasets.json`) was removed from this branch and remains in the git history (`git show 9abbfc6:<path>`).

**Ported from the old `main` after the migration** (2026-11-13): the two commits made there after
`0dad25c` - #16 KEN-LVB five-county boundary (OCHA COD-AB, CC BY-IGO 3.0, release `boundaries-2026-11-10`)
and #17 one spelling per landscape - are in `../boundaries/`, `spec/`, `scripts/build_boundaries.py`,
`stac/`, the KEN-LVB bbox of `vocab/landscapes.json`, record MFL-2026-102 of the catalogue, and
[`docs/history/RECORDS_CHANGELOG_2026-11-10_lvb_boundary.md`](../docs/history/RECORDS_CHANGELOG_2026-11-10_lvb_boundary.md).
