# Records changelog — 2026-09-29

Mechanical fix (Lizeth Llanos, 2026-09-29): text typed into `date_registered`, which must be a date.
In each case the text is a copy of another field of the same record, so nothing is lost. The real
registration date is unknown; all four records predate the canonical registry snapshot of
2026-07-21, which the STAC uses as their stand-in date.

| Record | Field | Before | After | The text is also in |
|---|---|---|---|---|
| MFL-2026-040 | `date_registered` | `Drive` | null | `current_location` |
| MFL-2026-041 | `date_registered` | `Drive` | null | `current_location` |
| MFL-2026-050 | `date_registered` | `MRC produced the data` | null | `description` |
| MFL-2026-051 | `date_registered` | `MRC produced the data` | null | `description` |
