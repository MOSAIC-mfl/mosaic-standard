# Pending records (not built)

Records here are **not** part of the catalogue: `build_catalog.py` reads only the
top level of `records/`. They were set aside on 2026-09-04 because they have no
contact, source, license or access level, and `contact` became a required field
that day (see `spec/record_schema.md`). A record with no one to ask cannot be
published as a MOSAIC record.

| Record | Title | Scope | Who might know |
|---|---|---|---|
| MFL-2026-043 | Rainfall trends | NATIONAL · Kenya | unknown — no Kenya focal point contacted yet |

To restore one: fill in `contact` (and `source`, `license`, `access_level`), move the
file back to `records/`, and rebuild.

Restored: MFL-2026-016 (Groundwater data - India) on 2026-10-29, filled from the CGWB
groundwater layers re-published by CoRE Stack (`docs/RECORDS_CHANGELOG_2026-10-29_corestack.md`).
