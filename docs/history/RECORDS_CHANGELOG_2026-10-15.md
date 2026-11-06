# Records changelog — 2026-10-15

Batch: **five ICARDA Kef-Siliana datasets already published on the MEL data portal**, registered as
TUN-NW records **link-at-source**. New records **MFL-2026-093 to 097**. Nothing was copied into this
repository and nothing was downloaded: each record's `download_url` is the dataset's own persistent
handle on `data.mel.cgiar.org`, and the MOSAIC item carries that handle as its `data` asset.

This closes the "register the 4–5 MEL Kef-Siliana datasets as TUN-NW records (link-at-source)" item
carried in the root `SESSION_STATUS.md` since 2026-09-22.

## Where the datasets came from

The five handles were recorded on 2026-09-22 (`MFL SP docs/project docs/MOSAIC internal/intake/intake_review_2026-09-22.md`,
§1a, "Bonus, connect-don't-duplicate") while checking where ICARDA deposits its data. Every field below
was then read on 2026-10-15 from the live Dataverse API of the MEL portal
(`/api/datasets/:persistentId/?persistentId=hdl:20.500.11766.1/FK2/<handle>`), not from those notes:
all five deposits resolve, are **Open access** with no restricted files and no access request, and
carry the Dataverse licence **CC BY-SA 4.0**.

They are one coherent study by the same five authors (Zahra Shiri, Aymen Frija, Hichem Rejeb,
Hassen Ouerghemmi, Quang Bao Le — ICARDA, with ISA-CM), deposited in the MEL collection
*Sustainable use and management of scarce water and land resources*, first published 2024-04-05.

| ID | Title (verbatim from MEL) | Handle | Type | Theme |
|---|---|---|---|---|
| 093 | Land cover Kef-Siliana region (2017) | `FK2/HNCLNU` | Raster, 10 m | Land cover / land use |
| 094 | Land cover Kef-Siliana region (2022) | `FK2/H4QIFS` | Raster, 10 m | Land cover / land use |
| 095 | Land Cover change in Kef-Siliana region (2017-2022) | `FK2/YUXPQY` | Raster, 10 m | Land cover / land use |
| 096 | Data on landscape metrics … (2017-2022) | `FK2/UN7DKQ` | Tabular (2 CSV) | Ecosystem condition |
| 097 | Data on the dynamics of Land Cover … (2017-2022) | `FK2/U4JHNU` | Tabular (2 CSV) | Degradation / land health |

Titles 096 and 097 are shortened in this table only; the records carry the full MEL titles, with the
colon replaced by a comma (a leading-colon construction reads badly in a catalogue card) and
"sub spatial units" hyphenated to "sub-spatial units".

## Values common to all five

| Field | Value | Where it comes from |
|---|---|---|
| `country` / `living_landscape` | `Tunisia` / `TUN-NW` | MEL geographic coverage is Tunisia, Le Kef and Siliana — the canonical "Northwestern Tunisia" landscape |
| `source` | `ICARDA` | MEL distributor; author affiliations |
| `access_level` | `Open` | Dataverse `availabilityStatus: Open access`, every file unrestricted, `fileAccessRequest: false` |
| `license` | `CC BY-SA 4.0` | Dataverse licence field (`CC-BY-SA-4.0`). R3 maps it to SPDX `CC-BY-SA-4.0` — verified in the build |
| `current_location` | `MEL data portal (data.mel.cgiar.org)` | The data lives there; MOSAIC holds no copy |
| `download_url` | `https://hdl.handle.net/20.500.11766.1/FK2/<handle>` | The deposit's persistent identifier |
| `citation` | Dataverse-style, authors + year + title + handle + `MELDATA` + version | Built from the MEL metadata, as for 070/071/048 |
| `date_registered` | `'2026-10-15'` | Date added to the catalogue |
| `last_updated` | release date of the current MEL version | Dataverse `releaseTime` (094: 2025-10-30; the other four: 2026-04-09) |
| `file_names` | the deposit's data files | Drives `formats` (R2) → GeoTIFF + CSV for 093–095, CSV for 096/097. The three `DataDictionary_*.csv` documentation files are deliberately left out |
| `file_size` | size of the primary data file | Dataverse file sizes (093/094: 143 MB; 095: 14 MB; 096: 9.5 KB; 097: 18 KB) |

`bbox` is set on **093, 094 and 095** from the deposits' own `geographicBoundingBox`
(8.256625, 35.475588, 9.772774, 36.462446 — rounded to 6 decimal places), which is wider than the
canonical TUN-NW delineation. 096 and 097 state no bounding box at source, so theirs stays unset.
The field is validated but not yet consumed by the pipeline, so today all five items still take the
landscape bbox as their locator — recording it now means nothing has to be re-derived when the
pipeline wires it in. `crs` stays unset: MEL says "UTM WGS84" without a zone, and no file was opened.

## Fields that were inferred, not read

Four judgement calls. Each is defensible but none is stated at source.

1. **`contact` = `Layal Atassi (l.atassi@cgiar.org)`.** MEL's own dataset contact is
   *Shiri, Zahra — shiri.zahra994@gmail.com*, a personal address that should not go into a public
   catalogue. Layal Atassi is ICARDA's contact for the Tunisia landscape and is already the contact on
   MFL-2026-030/031/032. **To confirm with her** — she may prefer to name Zahra Shiri with an
   institutional address, or Aymen Frija (`a.frija@cgiar.org` per MEL's author affiliation).
2. **`processing_status` = `Processed`.** These are derived products (classified imagery, a change
   map, computed metrics) published at source; MOSAIC has not validated them, so `Validated` would
   overstate it.
3. **`update_frequency` = `Static`.** A finished 2017–2022 study with no update schedule announced.
   The deposits have high version numbers (V10–V17), but those are metadata edits, not new data.
4. **`theme` for 096 and 097.** 093–095 are plainly *Land cover / land use*. Landscape metrics
   (fragmentation and configuration) were put under *Ecosystem condition*; the land cover dynamics
   table, which assesses degradation and improvement with the UNCCD Good Practice Guidance, under
   *Degradation / land health*. Both could reasonably sit under *Land cover / land use* instead.

## One decision left to Lizeth: the STAC contact role

The five items came out of the build with `contacts: [producer, licensor]`, because R10 gives that to
any record with an SPDX licence that is not listed in `stac_build.py:THIRD_PARTY_RIGHTS`. For 096 and
097 (ICARDA's own computed statistics) that is right. For **093, 094 and 095 it probably is not**: the
land cover maps are classified from ESRI's Sentinel-2 Land Cover Explorer rasters, and the roles sweep
of 2026-10-15 put exactly that case — MFL-2026-017, Esri Living Atlas — under `point-of-contact`, on
the same reasoning as MFL-2026-066 (iSDAsoil under CC BY 4.0, licensor iSDA, not the contact).

Nothing was changed: that is a pipeline edit (three ids into `THIRD_PARTY_RIGHTS`, rights holder
"Esri Living Atlas"), and the status file reserves those moves for Lizeth. Question 4 below is the
same issue seen from the licence side.

## Discrepancy found at source, not carried into the records

All five deposits declare `timePeriodCovered` **2022-01-01 to 2024-01-01**, which contradicts their own
titles and descriptions (2017; 2022; 2017–2022) and is identical across five datasets covering
different periods — a deposit-form artefact. `temporal_coverage` follows the titles and descriptions
instead (`'2017'`, `'2022'`, `2017-2022`). Worth mentioning to Layal so MEL can be corrected.

## Output effect (built locally, not published)

- 94 records, 12 collections, 94 items; STAC validation **107/107**.
- **TUN-NW goes from 6 to 11 records.** The collection's temporal extent now starts 2017-01-01
  (was 2021-01-01) and gains the theme *Ecosystem condition*.
- Changed files: `datasets.json`, `stac/collections/TUN-NW/collection.json`, five new
  `stac/collections/TUN-NW/items/MFL-2026-09[3-7].json`. The diff is additive.
- The five items each carry a working `data` asset pointing at the MEL handle, `license`
  `CC-BY-SA-4.0`, and `mosaic:access_note` naming the MEL portal.
- **Not committed, not pushed, not published**, and the registry Excel has not been regenerated
  (`scripts/records_to_excel.py` is due before any commit). The frontend `datasets.json` has not been
  synced either — rebuild with `--sync-frontend` when Lizeth approves.

## Questions for Layal Atassi, when Lizeth decides to raise them

1. Who should be the public contact for these five records (see point 1 above)?
2. The MEL time period (2022–2024) does not match the datasets' own years — can it be corrected at source?
3. Are these five the complete Kef-Siliana set on MEL, or are there further deposits MOSAIC should link?
4. The 2017 and 2022 land cover maps derive from ESRI's Sentinel-2 Land Cover Explorer. Does ICARDA's
   CC BY-SA 4.0 licence on the derived maps clear the source imagery's own terms?
