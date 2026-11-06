# Records changelog — 2026-10-21 (landscape boundaries as records)

Lizeth asked for the living-landscape boundaries to appear in the catalogue as dataset records, so that
every landscape shows its boundary under the theme *Boundaries / admin units*. Until now each boundary was
published only as an asset of its landscape's STAC collection and in the release `boundaries-2026-10-14`.

## Added — 8 records, MFL-2026-098 to 105

| Record | Landscape | Delineation source | Licence (record wording) |
|---|---|---|---|
| 098 | CIV-NZ | HydroBASINS v1c (HydroSHEDS v1, WWF) | Source terms |
| 099 | COL-CUM | Nine veredas of the Cumbal indigenous reserve; origin not attributed | No licence stated |
| 100 | ETH-OG | World Bank, Ethiopia River Basins | CC BY 4.0 |
| 101 | KEN-LEI | GADM 4.1 counties | Source terms |
| 102 | KEN-LVB | GADM 4.1 counties | Source terms |
| 103 | PER-PCL | INEI census district limits | No licence stated |
| 104 | SEN-FK | GADM department | Source terms |
| 105 | ZWE-MB | GADM 4.1 wards | Source terms |

Every record: source *Alliance Bioversity-CIAT (MOSAIC)*, contact Lizeth Llanos, access Open, data type
Vector, `download_url` = the landscape's zip in release `boundaries-2026-10-14`, bbox from
`boundaries/<CODE>.geojson`, citation = the release's credit line (`spec/boundary_provenance.json`).

## Pipeline

`stac_build.py:THIRD_PARTY_RIGHTS` gains 098–105, so their STAC contact is `point-of-contact`, not
`licensor`: the rights stay with GADM, WWF, the World Bank and INEI.

## Not added — already registered, pending Lizeth's confirmation

- **IND-CH** — MFL-2026-000 (IWMI) is the Central India landscape boundary.
- **MEK-3S** — MFL-2026-050 (IWMI, "watershed boundary") appears to be the same MRC sub-catchment layer.
- **TUN-NW** — MFL-2026-032 (ICARDA, the six communities) appears to be the same COD-AB level-4 layer.

## Effect

102 records, STAC 115/115 valid. Lake Victoria reaches 10 records of its own and LEILA gets its first
record, through boundary records in both cases.
