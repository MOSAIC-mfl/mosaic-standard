# Records changelog — 2026-09-16

Batch: 11 new Peru (Ucayali) records from Beatriz Rodríguez, consolidation of
the registry Excel into a single up-to-date workbook, and (same day, second
batch) one new Kenya record from an external copy of the old registry.

## Second batch — MFL-2026-083 (Crop type map, Kenya)

Source: an old external copy of the original registry
(`MFL_Dataset_RegistryCG.xlsx`, received via Downloads) with one row added at
the bottom: **Crop type map** — major crop type maps in Nandi county, Kenya;
IFPRI; contact Zhe Guo; Raster, 10 m, 2023; Open, CGIAR Open Access, Validated;
on OneDrive, no download URL. The other 69 rows of that copy were all already
registered (four looked new but were the renamed AfricaRice pairs 046/067 and
048/066).

- **ID:** the copy's formula had labelled the row `MFL-2026-066` — already
  taken by SoilGrids. Registered as **MFL-2026-083** (next free ID, verified
  against `records/` AND `records/_pending/`).
- **`living_landscape: KEN-LVB` is provisional** — the source row left it
  empty; Nandi county sits in the Lake Victoria Basin area. Confirm with Zhe
  Guo (also ask for the files or a URL). KEN-LVB goes from 1 to 2 datasets.
- Mechanical: contact email lowercased (`Z.GUO@CGIAR.ORG` → `z.guo@cgiar.org`).
- First IFPRI-owned dataset with a named owner (Zhang Wei is the focal point).

## New records — MFL-2026-072 … MFL-2026-082

Source: 11 rows added (by 2026-09-15) to the original registry workbook
`MFL_Dataset_Registry 21jul.xlsx`, all contributed by **Beatriz Rodríguez
(b.rodriguez@cgiar.org), Alliance Bioversity-CIAT**, all Peru / Ucayali
department → `living_landscape: PER-PCL` (landscape coverage). PER-PCL goes
from 1 to 12 datasets.

| ID | Title | Theme |
|---|---|---|
| MFL-2026-072 | Provinces and Districts | Boundaries / admin units |
| MFL-2026-073 | National Protected Natural Areas | Boundaries / admin units |
| MFL-2026-074 | Regional Conservation Areas | Boundaries / admin units |
| MFL-2026-075 | Indigenous Territories | Boundaries / admin units |
| MFL-2026-076 | National Ecosystem Map | Biodiversity / ecosystems |
| MFL-2026-077 | Human Footprint map | Pressures / drivers |
| MFL-2026-078 | Physical Vulnerability map | Pressures / drivers |
| MFL-2026-079 | Forest/Non-forest 2000/Forest loss 2001-2024 | Pressures / drivers |
| MFL-2026-080 | Annual deforestation | Pressures / drivers |
| MFL-2026-081 | Land Cover and Land Use | Land cover / land use |
| MFL-2026-082 | Annual Burned Area | Pressures / drivers |

`date_registered: '2026-09-15'` (the day the rows entered the workbook).

### ID re-assignment (collision with existing records)

The workbook's positional ID formulas had labelled five of the new rows
**MFL-2026-070 … 074** — but 070 and 071 were already taken by the Burkart
records registered by email on 2026-08-03 (the workbook never knew about them),
and six of the eleven rows had no ID at all. All eleven were therefore assigned
the next free IDs **072–082**, in sheet-row order. Do not quote the workbook's
old 070–074 labels back to the depositor.

### Mechanical fixes applied (verbatim otherwise)

| ID | Field | From → To | Why |
|---|---|---|---|
| 072 | title | `Provinces and districtis` → `Provinces and Districts` | typo |
| 072 | download_url | …`?utm_source=chatgpt.com` stripped | tracking parameter |
| 076 | title | `Nacional Ecosystem map` → `National Ecosystem Map` | Spanish "Nacional" |
| 081 | temporal_coverage | `2000, 2005, 2010, 2025, 2020, 2024` → `…2015…` | its own description lists 2015, not 2025 |
| 082 | title | `Annual Burned` → `Annual Burned Area` | truncated title (description: "Cumulative Burned Area") |

**Left as-is (question for the depositor):** MFL-2026-080's description says
forest loss "2001-2025" while title/temporal coverage say 2001-2024 — kept
verbatim; ask Beatriz which is right. All 11 records have
`license: Other (specify in notes)` with no license actually specified in the
notes, and `current_location: One Drive` with no server path — both flagged by
the pipeline; follow up with Beatriz alongside the phase-2 replies.

## Excel consolidation — one workbook, regenerated from records

- `catalog/MFL_Dataset_Registry.xlsx` (the tracked workbook `build_catalog.py
  --from-excel` reads) was **regenerated from `records/` (79 records)** with the
  new `scripts/records_to_excel.py`. It had been frozen at the 2026-07-21
  migration content (68 rows, no audit fixes, no 070/071).
- The original `catalog/MFL_Dataset_Registry 21jul.xlsx` (gitignored) was
  **deleted** after extracting the 11 new rows — its remaining content was the
  pre-canonicalization July state, fully superseded by `records/`.
- Two ghost rows (stray `mailto:` hyperlink cells below the data, rows 104–105)
  were purged — they made the Excel-fallback build invent two phantom GLB
  records (083/084).
- Acceptance check (both build paths): `stac/` byte-identical; `datasets.json`
  differs only in `citation` for 070/071 (a YAML-only field the workbook cannot
  carry — known, documented in `catalog/SNAPSHOT_NOTE.md`).
