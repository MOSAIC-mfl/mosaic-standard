# Registry Excel — import/working view only (demoted 2026-07-24)

**The source of truth is `records/<ID>.yaml`** — one validated YAML file per
dataset, reviewed via pull requests (see `records/README.md`). This workbook is
kept as an import/working view for people who prefer a spreadsheet, and as the
emergency fallback for a build environment without PyYAML (`build_catalog.py`
prints a loud banner when that fallback triggers; CI normally builds from
records).

- **Since 2026-09-16 this is the ONLY registry Excel**, regenerated from
  `records/` (79 records) by `scripts/records_to_excel.py`. The original
  `MFL_Dataset_Registry 21jul.xlsx` was retired after its last 11 new rows were
  migrated into `records/` (see `docs/RECORDS_CHANGELOG_2026-09-16.md`).
- **After any edit under `records/`, keep this workbook in step:**
  `python3 scripts/records_to_excel.py` (it verifies itself cell-by-cell).
- `scripts/excel_to_records.py` converts workbook → `records/` (bulk imports
  from focal points); `records_to_excel.py` is its inverse.
- Known, accepted gap: the workbook has no columns for the YAML-only forward
  fields (`citation`, `doi`, `bbox`, …), so an `--from-excel` build matches the
  records build byte-for-byte in `stac/` but drops `citation` in
  `datasets.json` (070/071 today). Never treat an Excel-fallback publish as
  canonical.
- `PER-PCL` (Pucallpa – Ucayali) is pending confirmation with the Peru team —
  note that the 11 records added 2026-09-16 are all explicitly Ucayali.
