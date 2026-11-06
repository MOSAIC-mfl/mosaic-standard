# Records changelog — 2026-10-15 (record batch A)

Batch: **record batch A**, the file-derived record fields that have been waiting in the root
`SESSION_STATUS.md` open items (intake item, point 4) since the intake review of 2026-09-22
(`MFL SP docs/project docs/MOSAIC internal/intake/intake_review_2026-09-22.md` §3.4 / §4, with the
046 and 048 rows added by `intake_review_2026-09-23.md` §3).

Second changelog of 2026-10-15; `RECORDS_CHANGELOG_2026-10-15.md` is the unrelated MEL Kef-Siliana
registration (MFL-2026-093…097), hence the suffixed file name.

**Where the values come from.** Every value below was measured during the intake facts pass
(`MOSAIC internal/intake/intake_place.py --facts`, 2026-09-22 and 2026-09-28) and is recorded in the
curated store's manifests, `Geospatial-data-repository/MOSAIC/datasets/<ID>/MANIFEST.md`. Nothing was
re-derived or estimated here. Only `crs` was read from a second measured source, the delivered `.prj`
files, to turn the shapefiles' PRJ datum name into an EPSG code.

**Scope.** Only what the files themselves settle. Everything that needs a data owner's judgement was
left untouched — see **Deliberately not applied** at the end.

## Edits

### Library location — all 20 records

`server_path: null` → `MOSAIC/datasets/<ID>/raw/`, the record's folder in the curated store.
It is a path inside the SharePoint library, never a link, and the pipeline publishes it in the STAC
item's `mosaic:access_note` ("Server path: …"), as it does for every other operational pointer.

### Measured file facts

| ID | `file_names` | `file_size` | `crs` | `bbox` (xmin, ymin, xmax, ymax) |
|---|---|---|---|---|
| 030 | `Tunisia_Governorate.shp` (8 files) | 571 KB | EPSG:4326 | 8.2529, 35.4774, 9.7697, 36.4639 |
| 031 | `Tunisia_Sector.shp` (8 files) | 692 KB | EPSG:4326 | 8.7670, 35.6887, 9.5377, 36.4634 |
| 032 | `Tunisia_ALL.shp` (8 files) | 723 KB | EPSG:4326 | 8.9235, 35.7384, 9.4466, 36.4324 |
| 044 | `gadm41_CIV_0…4.shp` (25 files) | 3.5 MB | EPSG:4326 | -8.5993, 4.3618, -2.4949, 10.7366 |
| 046 | `synoptic_stations_daily.xlsx` | 3.5 MB | — | — |
| 048 | unchanged (`CI.SOL`, set 2026-09-28) | 9.3 MB | — | — |
| 064 | 4 scenario `.tif` | unchanged (see below) | EPSG:4326 | 33.9083, -4.7083, 41.9250, 5.0583 |
| 068 | 4 scenario `.tif` | unchanged | EPSG:4326 | 100.0832, 13.9082, 107.6332, 22.4999 |
| 069 | 4 scenario `.tif` | unchanged | EPSG:4326 | 102.1499, 8.4165, 109.4582, 23.3915 |
| 072 | `Ucayali_Provinces_and_Districts.shp` (8 files) | 1.0 MB | EPSG:4326 | -75.9479, -11.4483, -70.4944, -7.2620 |
| 073 | `Ucayali_National_Protected_Natural_Areas.shp` (8 files) | 658 KB | EPSG:4326 | -76.6337, -11.6732, -70.5991, -6.1518 |
| 074 | `Ucayali_Regional_Conservation_Areas.shp` (8 files) | 125 KB | EPSG:4326 | -75.7270, -9.1703, -73.4370, -8.2754 |
| 075 | `Ucayali_Indigenous_Territories.shp` (8 files) | 5.3 MB | **EPSG:4674** | -75.9023, -12.1781, -70.5177, -6.7279 |
| 076 | `Ucayali_Ecosystems_map.shp` (8 files) | 109.7 MB | EPSG:4326 | -75.9479, -11.4483, -70.4944, -7.2620 |
| 077 | `Ucayali_Human_Footprint_map.shp` (8 files) | 125.6 MB | EPSG:4326 | -75.8586, -11.4394, -70.4949, -7.3333 |
| 078 | `Ucayali_Physical_Vulnerability_map.shp` (8 files) | 7.8 MB | EPSG:4326 | -75.9479, -11.4483, -70.4944, -7.2620 |
| 079 | `Ucayali_Forest_NonForest2000_ForestLoss2001_2024.shp` (8 files) | 175.2 MB | EPSG:4326 | -75.9479, -11.4476, -70.4953, -7.2620 |
| 080 | `Ucayali_Annual_Deforestation_2001_2024.shp` (8 files) | 143.3 MB | EPSG:4326 | -75.9419, -11.4473, -70.4954, -7.2716 |
| 081 | `Ucayali_Land_cover_Land_use.shp` (8 files) | 520.2 MB | EPSG:4326 | -75.9479, -11.4483, -70.4944, -7.2621 |
| 082 | `Ucayali_Cumulative_Burned_2013_2024.shp` (8 files) | 13.8 MB | EPSG:4326 | -75.8389, -11.4398, -70.4952, -7.7217 |

Conventions used, so the next batch matches:

- **`file_names`** lists the dataset's own files under the names they were delivered with; the copies
  in the library carry the intake prefix `<ID>__`, which is not part of the data. For a shapefile only
  the `.shp` is named, with the file count of the complete set in brackets, so rule R2 derives one
  format (`Shapefile`) rather than one per sidecar extension.
- **`file_size`** is the size of the dataset's files, **excluding the container `.zip`** it arrived in
  where the unpacked members sit beside it (030, 031, 032, 044, 048) — counting both would double it.
  Decimal units, matching the manifests.
- **`crs`** is the EPSG code of the delivered files' own CRS, read from the `.prj`:
  `GCS_WGS_1984` → EPSG:4326, and for 075 `GCS_SIRGAS_2000` → **EPSG:4674** (its `bbox` is therefore
  in SIRGAS 2000 degrees; the difference from WGS 84 is sub-metre).
- **`bbox`** is the extent of the delivered files, not of the landscape. Where one record holds several
  files they share one extent (044's five admin levels, the four scenario rasters of 064/068/069).

`file_size` on **064, 068 and 069** was **left as the owner's figure** (220 MB, 250 MB, 250 MB). What
arrived is four scenario rasters per record (432 KB, 302 KB, 431 KB) — a subset of the full C4R output
the record points to, so overwriting the field would understate the dataset. The measured sizes stay in
the manifests. See the questions at the end.

### Distinct titles — 064, 068, 069

Three records shared the title *Tree conservation and restoration priority areas*. Disambiguated by
country, following the 2026-09-04 audit rule for look-alike titles:

| ID | Country | Title |
|---|---|---|
| 064 | Kenya | Tree conservation and restoration priority areas (Kenya) |
| 068 | Laos | Tree conservation and restoration priority areas (Laos) |
| 069 | Vietnam | Tree conservation and restoration priority areas (Vietnam) |

## Output effect

- 94 records, 12 collections, 94 items; STAC validation **107/107**. No record was added or removed.
- **`datasets.json`: 4 values change** — the three titles above, and 046's `formats` `CSV` → `XLSX`
  (R2 now reads a real file name instead of falling back on `data_type: Tabular`). The frontend repo
  therefore needs its own commit.
- **STAC: 23 files change.** 20 items gain `Server path: …` in `mosaic:access_note`; 064/068/069 carry
  the new title (and so do the item links in the KEN-LVB and MEK-3S collections); 046's asset type
  becomes the XLSX media type.
- **`crs` and `bbox` change no output.** Both are forward-looking record fields (`spec/record_schema.json`):
  validated, not yet consumed — the pipeline still draws item bboxes from the landscape/country locator
  lookup, and still writes `mosaic:crs_note: "CRS not recorded in registry"`. The measured extents are
  now in the records for when the pipeline does use them.

## Deliberately not applied — waiting on a data owner

Per the working agreement of 2026-09-23, intake corrections wait for the owner's reply even when they
look certain. Three points of batch A were left untouched:

1. **030, 031, 032 — provenance (Layal Atassi, ICARDA).** The records name geoBoundaries
   (`source: ICARDA`, `download_url: www.geoboundaries.org`); the files' embedded ArcGIS metadata says
   OCHA/HDX **COD-AB Tunisia, source INS, 2022-11-15** (layers `tun_admbnda_adm2/3/4_ins_20221115`),
   exported from a `Tunisia_HOLPA.gdb`. The prepared fix is `source` → "ICARDA (clipped from OCHA/HDX
   COD-AB Tunisia, INS 2022)" and `download_url` → `https://data.humdata.org/dataset/cod-ab-tun`.
   **Question for Layal:** are these three layers subsets of the COD-AB Tunisia boundaries rather than
   geoBoundaries? (And, still open from 2026-09-22: may the HOLPA female/male and education shares in
   032 be published, or boundaries only?) This is also what holds their provisional STAC contact role.
2. **046 — title and description (Louis Kouadio, AfricaRice).** Everything else on 046 was settled on
   2026-09-28; the title still says *Climate station data (NHMS synoptic stations)*. Whether that is
   right depends on the unresolved source question: Louis says the Bouaké and Ferkessédougou 1980–2010
   series are station observations, while ARCWeather's own station metadata lists them under project
   AgMERRA (CIV5002, CIV5004), with no altitude and flag 9 on every value. **Question for Louis:** are
   those two series AgMERRA reanalysis values or station observations? The title follows the answer.
3. **064, 068, 069 — `file_size`,** as described above. **Question for Hannes Gaisberger:** should the
   field keep describing the full C4R output (220/250 MB), or the four scenario rasters MOSAIC holds?
   The older open question on these records is unchanged: are the four rasters part of the published
   Harvard Dataverse deposit (doi:10.7910/DVN/2ZQTB2), and what is the legend of the uint16 values?

**Not part of batch A: MFL-2026-066.** It arrived on 2026-09-28, after the batch was defined, and its
manifest holds the same measured facts (32 files, 1.60 GB, EPSG:4326, bbox -5.3794, 5.9499, -3.8581,
9.4334). The same five fields can be filled for it whenever Lizeth says so.
