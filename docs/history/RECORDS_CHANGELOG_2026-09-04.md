# Records changelog — 2026-09-04 audit fixes

Applied locally on 2026-09-04 after a read-only audit of `records/*.yaml` against the published
catalogue (live STAC was byte-identical to the local build — every problem was in the records).
Lizeth's instruction: *"apply the three mechanical fixes and put the rest in the emails."*
Committed with the push that carries this file. `records/*.yaml` is the source of truth; the Excel in
`catalog/` is a frozen 68-row snapshot (missing 070/071) and was **not** edited.

## 1. GADM-derived records — license made restrictive

GADM's terms allow academic and non-commercial use only and forbid redistribution; the project rule
(data-strategy license audit) is that GADM, WDPA, IUCN Red List and OSM (ODbL) are always marked
restrictive. New value on all five: `Restricted — GADM terms (academic/non-commercial use only, no redistribution)`.

| Record | Title | Source | Before |
|---|---|---|---|
| MFL-2026-018 | Departments | ISRA-BAME | CC BY 4.0 |
| MFL-2026-019 | Municipalities | ISRA-BAME | CC BY 4.0 |
| MFL-2026-021 | Road | ISRA-BAME | CC BY 4.0 |
| MFL-2026-026 | District/ward boundaries | CIMMYT | CGIAR Open Access |
| MFL-2026-044 | District/Region boundaries | National government (external) | CC BY 4.0 |

Open question sent to the owner (Dieye email): GADM publishes no road data — the true source and
terms of **021 Road** are to be confirmed. Non-SPDX license strings publish as `mosaic:license_original`
in STAC and as `license` in `datasets.json` (same path as "Restricted — contact data owner").

## 2. Distinct titles for look-alike pairs

Each pair shared a title while describing different datasets. IDs, collections and URLs unchanged.

| Record | Before | After |
|---|---|---|
| MFL-2026-046 | Climate data | Climate station data (NHMS synoptic stations) |
| MFL-2026-067 | Climate data | Gridded climate data (CHIRPS and AgERA5) |
| MFL-2026-048 | Soil dataset | DSSAT soil profiles (global .SOL files) |
| MFL-2026-066 | Soil dataset | SoilGrids gridded soil information |

(048 was first retitled "…(global .SOL database)"; reworded the same day so no catalogue title carries
the word "database".)

## 3. `country` and `contact` are now required

`spec/record_schema.json` → `required`: `id, title, living_landscape` **+ `country`, `contact`**.
Docs updated: `spec/record_schema.md` (rows 4 and 11), `records/README.md` (template). Rationale: the
registration guide promised country and contact as required and the strategy names seven mandatory
fields; the schema enforced three, which is how two records entered with no contact, source, license
or access level.

**Consequence — two records parked in `records/_pending/`** (not built; the build reads only the top
level of `records/`): **MFL-2026-016** *Groundwater data – India* (IND-CH) and **MFL-2026-043** *Rainfall
trends* (NATIONAL · Kenya). To restore: fill `contact` (plus `source`, `license`, `access_level`), move
the file back to `records/`, rebuild. 016 was asked about in the IWMI email (Sudharsan Malaiappan);
043 has no owner yet (needs the Kenya focal point).

## Build result

`python3 build_catalog.py --sync-frontend` → 68 records, 12 collections, 81/81 STAC files valid;
`datasets.json` synced to `MOSAIC_frontend/mfl-living-landscapes-frontend/frontend/data/` (commit
both repos together).

## Not changed here — asked of the data owners instead

Everything that needs the owner's judgement went into the 12 emails in
`MFL SP docs/project docs/CoP/data_request_2026-09/` (outside this repo — they hold contact details):
16 Open records whose owners wrote "Internal / available on request" in `download_url`; 036/038 Open
with a restricted license; 7 licenses "Other (specify in notes)" left unspecified (003, 004, 005, 012,
045, 046, 058); ~13 external/derived sources to link at source (geoBoundaries 030–032, MRC 050–052,
MOAE 053/054, NHMS 046, Trends.Earth 022, ATREE/GEE 063, NASA/USGS 002/036, national government
039/040/042/044); 6 links unreachable from outside India (003–005, 008–010); 001's Google Drive asset;
013–015 `.qml` style files published as "downloads"; doubtful access levels on 006/007/011/055–057;
053 scoped NATIONAL though the Sekong is a 3S river. Answers come back as record edits, one
changelog per batch.
