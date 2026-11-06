# Records changelog — 2026-09-30

Batch: **eight ILRI datasets for the Lake Victoria Basin (Kenya)**, received as a filled MOSAIC registration
template (`MFL metadata.xlsx`, sheet "Metadata"). The file was created by Fredah Cherotich (ILRI) on 2026-09-15,
last saved by Ambica Paliwal (ILRI) on 2026-09-29, and shared by Lizeth on 2026-09-30. New records
**MFL-2026-085 to 092**, one per row, in the sheet's order. No earlier record covers them; the only other
KEN-LVB record from a centre is 083 (IFPRI crop type map).

| ID | Title (verbatim) | Theme as sent → recorded |
|---|---|---|
| 085 | Landscape Resources | Ecosystem services |
| 086 | Resource change | Ecosystem conditions → Ecosystem condition |
| 087 | Environmental challenges | Degradation/ Land Health → Degradation / land health |
| 088 | Climate risks | Ecosystem conditions → Ecosystem condition |
| 089 | Livelihood resources | Socio-economic/livelihoods → Socio-economic / livelihoods |
| 090 | Conflicts | Socio-economic/livelihoods → Socio-economic / livelihoods |
| 091 | Drivers of change | Pressures/drivers → Pressures / drivers |
| 092 | Restoration opportunities | Decision-support outputs |

## Values common to all eight

| Field | As sent | Recorded | Why |
|---|---|---|---|
| `living_landscape` | LVB Kenya | `KEN-LVB` | Canonical code; the crosswalk name is "Lake Victoria Basin (Kenya)" |
| `access_level` | CGIAR internal/Restricted | `Restricted` | The enum takes one value. Restricted matches the licence, which requires contacting the owner. **To confirm with Ambica** |
| `license` | Restricted-contact data owner | `Restricted — contact data owner` | The template's own dropdown value, as used by 14 other records; kept verbatim by R3 |
| `contact` | "Ambica Paliwal a.paliwal@cgiar.org " | `Ambica Paliwal (a.paliwal@cgiar.org)` | The format the other records use, trailing space removed |
| `processing_status` | Validated | `Raw` | Lizeth, 2026-09-30: the datasets are still in process. The enum has no "in process"; Raw is the site's "Metadata registered; dataset not yet reviewed" |
| `temporal_coverage`, `last_updated` | 2026 (number) | `'2026'` | Quoted, as the schema asks |
| `date_registered` | — | `'2026-09-30'` | Date added to the catalog |
| `data_type`, `spatial_resolution`, `source`, `country`, `current_location`, `update_frequency` | Vector, Basin level, ILRI, Kenya, One drive, On-demand | unchanged | Already valid |
| `download_url` | Internal Available on Request | unchanged | Verbatim, as in the other restricted records; R8 publishes no link |
| `description` | — | verbatim | |

## Output effect

- 89 records, 12 collections, 89 items; STAC validation 102/102.
- KEN-LVB goes from 2 to 10 records. Only the KEN-LVB collection file and its 8 new items change in `stac/`.
- The public pages show the eight as Restricted, with the licence as terms of use and no download link.
- `datasets.json` synced to the frontend; registry Excel regenerated (89 rows).

## Questions for Ambica, when Lizeth decides to raise them

1. **Access level:** Internal (CGIAR staff can obtain the data on request) or Restricted (only with the owner's
   permission)? The template allows one; Restricted was recorded.
2. **Climate risks (088):** the theme was sent as "Ecosystem conditions". Would "Scenarios / future risks" fit
   better?
3. **Method and scale:** the layers read like participatory or expert mapping at "basin level". A sentence on how
   they were produced, and when, would make the records usable for others.
4. **Conflicts (090):** please confirm it holds no personal or sensitive location data beyond what the
   Restricted access protects.

No files were received with the metadata. The data stays on ILRI's OneDrive until the owner shares it.
