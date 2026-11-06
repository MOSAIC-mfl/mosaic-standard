# Records changelog — 2026-09-28

Batch: **Louis Kouadio's answers** (AfricaRice; inline reply to Lizeth's email of 2026-09-23, forwarded by
Lizeth on 2026-09-28) on his records MFL-2026-044, 046, 048, 066 and 067, plus the registration he opened as
GitHub issue #1 on 2026-09-22. Only what his answers settle was edited. Open points are listed at the end.

## Answers → edits

| ID | Field | From → To | His answer, verbatim or summarised |
|---|---|---|---|
| 044 | `download_url` | `GADM maps and data (gadm.org)` → `https://gadm.org/download_country.html` | "OK. Agree." to keeping the files internal and linking the record to gadm.org |
| 044 | `description` | "Administrative boundaries" → GADM 4.1, levels 0 to 4, country-wide, unmodified, internal copy only | Same answer. The facts come from the delivered files: 1, 14, 33, 113 and 191 features (12 districts + 2 autonomous districts; 31 regions + the same 2) |
| 044 | `source` | `National government (external)` → `AfricaRice` | **Convention edit, not an owner answer.** GADM is not a national government; `source` names the contributing centre, as in the other GADM records (018, 019, 021, 026). Alternative: `GADM (external)` |
| 044 | `spatial_resolution`, `temporal_coverage`, `last_updated` | admin levels 1-3, `NA`, null → levels 0-4, `2022`, `2022` | GADM 4.1 files dated 2022-07-19 |
| 046 | `description` | "…three major cities in the watershed…; climate data from M'Be research station" → the three historical series, Korhogo's fewer variables and estimated dew point, M'Bé moved to 084 | "Yes, this is correct" (046 = the three historical series only); dew point estimated from Tmin: "Yes" |
| 046 | `temporal_coverage` | `since 2014` → `1980-2010` | Korhogo's 1994-2001 is stated in the description, because R4 reads the first and last year of the string |
| 046 | `update_frequency` | `Monthly` → `Static` | "with no further updates": "Yes, this is correct" |
| 046 | `download_url` | `NHMS for the synoptic climate stations` → `https://arcweather.africarice.org/en/downloads` | "We can use the ARCweather download page" |
| 046 | `license` | `Other (specify in notes)` → `ARCWeather usage terms: non-commercial, educational, research or personal use only, with citation. The portal states that Côte d'Ivoire climate data is distributed by Sodexam; no licence stated by the rights holder` | **Provisional.** "For the license, I am a bit confused because the data are publicly accessible under terms similar to the CC BY-NC 4.0 license." The text describes the portal's terms without naming AfricaRice as the licensor, since the portal says Sodexam distributes Côte d'Ivoire data. Worded without "CC", so the pipeline does not turn it into a licence that was never granted |
| 048 | `title` | `DSSAT soil profiles (global .SOL files)` → `DSSAT soil profiles for Côte d'Ivoire (CI.SOL)` | "Good to limit it to Côte d'Ivoire" |
| 048 | `country`, `living_landscape` | `Global`, `GLOBAL` → `Côte d'Ivoire`, `NATIONAL` | Same answer; the file covers the whole country, 425 of its 3,823 profiles inside CIV-NZ. NATIONAL follows the other country-wide records |
| 048 | `description`, `data_type`, `file_names` | global database, null, null → the Côte d'Ivoire file, unmodified; `Tabular`; `CI.SOL` | "Yes, that's correct" (unmodified file of the IFPRI deposit). `file_names` makes the format read DSSAT-SOL instead of the CSV fallback |
| 048 | `download_url`, `citation`, `doi` | the full citation in `download_url` → `https://doi.org/10.7910/DVN/1PEEY0`; the citation moved to `citation`; `doi: 10.7910/DVN/1PEEY0` | "We can link the record directly to IFPRI Dataverse database DOI." The link is unchanged, because R8 already extracted the same URL. The site's suggested citation becomes the IRI/MSU/IFPRI citation |
| 066 | `title`, `description` | SoilGrids → iSDAsoil for the N'Zi watershed, 15 properties at 0-20 and 20-50 cm | "The dataset I am providing now is from iSDA (https://www.isda-africa.com/isdasoil/). Data were extracted for the N'Zi watershed." The SoilGrids registration is replaced; ask Louis only if AfricaRice also uses SoilGrids |
| 066 | `country`, `living_landscape` | `Global`, `GLOBAL` → `Côte d'Ivoire`, `CIV-NZ` | Same answer; the delivered rasters are masked to CIV-NZ |
| 066 | `data_type`, `spatial_resolution`, `download_url` | null, `250 m`, soilgrids.org → `Raster`, `30 m`, `https://www.isda-africa.com/isdasoil/` | The link is the one he gave. iSDAsoil is CC BY 4.0 (AWS Open Data registry), so the licence stays `CC BY 4.0` |
| 067 | — | no change | "No N'Zi-specific extracts… We can link the record to the original CHIRPS and AgERA5." Only half met today: R8 keeps one URL, so only the CHIRPS DOI is published and the AgERA5 DOI (https://doi.org/10.24381/f9c1f09d) is not linked. See Still open |

## New record

**MFL-2026-084 — Climate data AfricaRice M'Bé Research Station**, from GitHub issue #1 (LouisAK, 2026-09-22),
confirmed in his email ("two climate stations maintained by AfricaRice… from 2014 onwards").

- Values from the form: CIV-NZ, Côte d'Ivoire, Water / hydrology, point level, 2014 onward (written "2014 - present"
  so R4 keeps the interval open), AfricaRice and Open.
- `download_url`: the ARCWeather downloads page. The form gave the home page; Louis agreed to the downloads page for 046.
- Added from ARCWeather: the two stations, MBE_LOWLAND (273 m) and MBE_UPLAND (303 m).
- `data_type: Tabular`. The form left it empty.
- `update_frequency: Unknown`. The form has no such field, and the portal's data ended on 2026-04-01 when checked, so
  the cadence is a question for Louis.
- `processing_status: null`. The agreement of 2026-08-03 keeps it null for email-in registrations until real QC;
  applying it to a GitHub-form registration needs Lizeth's confirmation. The form said "Processed".
- **`license`: provisional.** It quotes the AfricaRice Terms of Use, the usage policy ARCWeather links to
  (https://www.africarice.org/privacy-policy): attribution, non-commercial use, reuse under the same conditions.
  The form said CC BY-NC-SA 4.0, but Louis wrote that "no formal license statement is issued for the climate
  data" and asked for advice. To be replaced once AfricaRice chooses a licence and states it at the source.

## Output effect

- 81 records, 12 collections, 81 items; STAC validation 94/94.
- 048 and 066 move from the GLB collection to CIV-NZ, and 084 joins CIV-NZ. The CIV-NZ and GLB collection files
  change accordingly. No other item changes.
- Formats on the site: 048 becomes DSSAT-SOL and 066 becomes GeoTIFF; both read Unknown before.
- `datasets.json` synced to the frontend; registry Excel regenerated (81 rows).
- `spec/record_schema.md`: the `citation` row now says the field is consumed by `datasets.json` and the site.

## Still open

**For Lizeth to decide or answer:**

- **046 source.** Louis says the Bouaké and Ferkessédougou series "are station observations". ARCWeather's station
  metadata lists them under the AgMERRA project (codes CIV5002 and CIV5004), without altitude, and every value has
  flag 9. The record follows the owner's statement. He also asked: "Do you think the AgMERRA data should be
  uploaded too?" Under link-at-source, the answer is no, because AgMERRA is a public global product.
- **046 Korhogo.** Louis suggested "Perhaps we use AgMERRA data instead". Not applied. The choice depends on the
  source question above: if Bouaké and Ferkessédougou are observations, switching Korhogo would mix observed and
  gridded series in one record.
- **Licences of 046 and 084, both provisional.** AfricaRice can only license its own M'Bé stations (084). ARCWeather
  says Sodexam distributes Côte d'Ivoire climate data, so 046 keeps the portal's terms.
- **084 attachment and issue #1.** The M'Bé Excel attached to public issue #1 is still downloadable from MOSAIC's
  repository, under a licence that was never granted. Ask Louis to agree to removing it, then edit the issue and
  close it with a pointer to MFL-2026-084. That is a public post, so it needs Lizeth's OK.
- **084 update cadence.** How often ARCWeather is updated for the two stations.
- **067 links.** How to link AgERA5 as well: split the record, or keep CHIRPS as the primary link and cite AgERA5.
  Also whether `data_type: Tabular` and `current_location` still fit, now that there is no AfricaRice extract.
- **044 scope.** The layer is country-wide but stays CIV-NZ, as registered. NATIONAL would match 048.
- **046 badge.** The record keeps `processing_status: Validated`. Louis says the files have known bugs and his QC
  is not finished.

**Waiting for AfricaRice:**

- **046 revised files.** AfricaRice will check the 30 December end date, possibly caused by the server migration,
  and fix Korhogo's radiation units, then send revised files. The current raw copy moves to `superseded/` when they
  arrive.
- **N'Zi watershed boundary.** Louis attached AfricaRice's watershed layer to his email and asked whether to
  upload it. It is not yet in the library.
