# Records changelog — 2026-10-22 (access levels)

Batch: **25 records that were marked `Open` but cannot be obtained without asking** now carry
`Restricted` (23 records) or `Internal` (2 records). Only the `access_level:` line of each file
changed. No download link was invented and no other field was touched.

## The rule (approved by Lizeth Llanos, 2026-10-22)

**Open means anyone can obtain the data without asking permission.** A record marked `Open`
therefore needs:

1. a usable `download_url` — something that is still a URL after the R8 cleaning in
   `mosaic_pipeline/transform.py` (`clean_download_url`); and
2. a `license` that does not say "contact data owner" (checked in any letter case).

Licences that limit *use* but let anyone download the data, such as non-commercial terms (GADM's,
for example), stay compatible with `Open`.

The rule is `check_access_consistency` in `mosaic_pipeline/rules.py`. Once it is wired into
`build_catalog.py`, a record that breaks it stops the build with `ACCESS RULE FAILED` and exit code
3, before any file is written, whichever source the build reads (records/ or the Excel snapshot).

## The 25 records

`000` and `002` say only "Internal" in `download_url`, so they became `Internal`. The other 23
became `Restricted`. The reason column quotes the record's own values verbatim; titles are quoted as
recorded, including the misspelling in 039.

| ID | Title | access_level | Reason (verbatim from the record) |
|---|---|---|---|
| MFL-2026-000 | Central India Landscape - Boundary | Open → Internal | `download_url`: "Internal" |
| MFL-2026-002 | Central India Landscape - Rainfall (Remote sensing data) | Open → Internal | `download_url`: "Internal" |
| MFL-2026-020 | Localities | Open → Restricted | `download_url`: none recorded (null) |
| MFL-2026-022 | Land Degradation - Senegal | Open → Restricted | `download_url`: "Plugin Trends earth" |
| MFL-2026-023 | Tree mapping | Open → Restricted | `download_url`: none recorded (null) |
| MFL-2026-025 | Crop damage mapping | Open → Restricted | `download_url`: "Internal Available on request" |
| MFL-2026-027 | LULC classification | Open → Restricted | `download_url`: "Internal Available on request" |
| MFL-2026-028 | LULC classification training points | Open → Restricted | `download_url`: "Internal Available on request" |
| MFL-2026-029 | Ecosystem services mapping | Open → Restricted | `download_url`: "Internal Available on request" |
| MFL-2026-030 | Tunisia LLs Governorate boundary for Le Kef and Siliana. | Open → Restricted | `download_url`: "www.geoboundaries.org" |
| MFL-2026-031 | Tunisia LLs Sector boundary containing Es Sers, Gaafour, El Krib, Makthar, and Kesra. | Open → Restricted | `download_url`: "www.geoboundaries.org" |
| MFL-2026-032 | Tunisia LLs boundary for the six communities containing Sers, Elles, El Ahouez Sud, Hammam Biadha Sud, Chouarnia, and Kesra. | Open → Restricted | `download_url`: "www.geoboundaries.org" |
| MFL-2026-033 | Tunisia Land use land cover for Le Kef and Siliana. | Open → Restricted | `download_url`: "Internal Available on request" |
| MFL-2026-034 | Tunisia Agricultural soil for Le Kef and Siliana. | Open → Restricted | `download_url`: "Internal Available on request" |
| MFL-2026-036 | Agricultural production system | Open → Restricted | `download_url`: "Internal Available on request"; `license`: "Restricted — contact data owner" |
| MFL-2026-038 | Soil resource | Open → Restricted | `download_url`: "Internal Available on request"; `license`: "Restricted — contact data owner" |
| MFL-2026-039 | District level crop area, prodcution and yield data - India | Open → Restricted | `download_url`: "Internal Available on request" |
| MFL-2026-040 | Agroecological zones | Open → Restricted | `download_url`: "Internal Available on request" |
| MFL-2026-041 | Experimental CSA practices | Open → Restricted | `download_url`: "Internal Available on request" |
| MFL-2026-042 | Erosion map | Open → Restricted | `download_url`: "Internal Available on request" |
| MFL-2026-063 | India's open natural ecosystem | Open → Restricted | `download_url`: "open-natural-ecosystems" |
| MFL-2026-065 | Soil health status and texture | Open → Restricted | `download_url`: "Internal Available on request" |
| MFL-2026-068 | Tree conservation and restoration priority areas (Laos) | Open → Restricted | `download_url`: none recorded (null) |
| MFL-2026-069 | Tree conservation and restoration priority areas (Vietnam) | Open → Restricted | `download_url`: none recorded (null) |
| MFL-2026-083 | Crop type map | Open → Restricted | `download_url`: none recorded (null) |

## Going back to Open

When an owner shares a public link to the data, edit the record as usual: put the link in
`download_url` and set `access_level: Open`. The build accepts the record as soon as the link
survives the R8 cleaning and the licence does not say "contact data owner". Then run
`python3 build_catalog.py` and `python3 scripts/records_to_excel.py`, and add a changelog entry.

## Output effect (built locally, not published)

- Still 102 records; only `access_level` changed.
- `datasets.json`: `access_level` changes on these 25 entries only.
- STAC: `mosaic:access_level` changes on these 25 items, and a collection's access-level summary
  changes where its set of levels changed. STAC validation reports 0 failed.
- `catalog/MFL_Dataset_Registry.xlsx` regenerated from records/ with
  `python3 scripts/records_to_excel.py` (self-verified).
- Committed on the branch `lizeth/pipeline-tests-access-rule`; **not pushed and not published**. The
  website's copy of `datasets.json` is synced after the merge
  (`python3 build_catalog.py --sync-frontend`).

## Follow-up

Lizeth asks the owners of these 25 records whether a public link exists; each record whose owner
supplies one goes back to Open with the edit above. Several of these records were already flagged
by the 2026-09-04 records audit (`docs/RECORDS_CHANGELOG_2026-09-04.md`).
