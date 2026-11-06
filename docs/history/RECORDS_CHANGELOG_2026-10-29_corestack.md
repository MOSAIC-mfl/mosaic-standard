# Records changelog — 2026-10-29 (CoRE Stack layers)

Six Central India records from the **CoRE Stack GEE Layers Links** sheet (Lizeth Llanos,
2026-10-29). The sheet is the same one that `RECORDS_CHANGELOG_2026-10-29.md` used for 013–015.
It lists about 130 layers. 013–015 already covered land cover, trees and waterbodies, so the
remaining layer groups were checked against the IND-CH records. Five of them fill MFL themes
that IND-CH had no record for, and one completes the pending record 016.

Sheet: https://docs.google.com/spreadsheets/d/1xS5d7vgyjyoqqnmmajKDZBx9qS6GqyAdSbNDR62ot2Y/edit?gid=0
(read 2026-10-29; public, no sign-in).

| Record | Title | Sheet group(s) | Theme | Licence, from the sheet's licence column |
|---|---|---|---|---|
| 016 (restored from `records/_pending/`) | Groundwater data - India | Groundwater Layers | Water / hydrology | "Published by CGWB; Re-published here" |
| 106 (new) | Microwatershed boundaries and drainage network - India | Hydrological boundaries (microwatershed rows only), Drainage layers | Water / hydrology | CC BY 4.0 on every row |
| 107 (new) | Climate hazard and drought indices - India | Hazard Index | Scenarios / future risks | none stated |
| 108 (new) | Restoration opportunities and plantation site suitability - India | WRI restoration opportunities atlas, Plantation Site Suitability | Hotspots / leverage points | WRI India: "Re-published here"; plantation: CC BY 4.0 |
| 109 (new) | Land-use pressures: mining, industry, energy and land conflicts - India | Industry | Pressures / drivers | each row names its publisher; no licence |
| 110 (new) | Soil type, nutrients and organic carbon - India | Soil | Degradation / land health | none stated |

**Shared values.** Every record follows 013–015:
- `download_url` is the sheet URL, and `current_location` names the sheet group plus the map
  viewer.
- The contact is the same as 013–015 (Sudharsan, IWMI, who shared the sheet).
- `access_level` is Open, because every layer is a public Earth Engine asset, and most also have
  a public Drive download.
- `living_landscape` is IND-CH. The layers are pan-India; the descriptions say so.

**Licence wording.**
- Where the sheet states no licence (107, 110), the record says so instead of assuming CC BY 4.0.
- 108 mixes two licences. The pipeline (R3) turns any licence that mentions "CC BY" into
  `CC-BY-4.0`, so the licence field describes the mix in words. The description carries the
  plantation layer's CC BY 4.0.

**Pipeline.** `stac_build.py:THIRD_PARTY_RIGHTS` gains 016 and 106–110, so their STAC contact
role is `point-of-contact`, as for 013–015. `records/_pending/README.md` drops 016 from its table.

**Left out on purpose:**
- **SRTM and FABDEM terrain.** These are global datasets; MOSAIC connects to the original source.
- **WRIS river basin, sub-basin and watershed.** These are re-published WRIS layers; 106 keeps
  only CoRE Stack's own hydrology.
- **Historical WRIS land cover (2005–2018).** Low value next to 015.
- **The training-data tabs.** The ground-truth sites are mostly outside Central India.

**Lower priority, not added:**
- Village, panchayat and tehsil boundaries (SHRUG).
- Agro-ecological, agro-climatic and biogeographic zones.
- Distance to facilities.
- Tree degradation in forest fringes and the tree-in-grassland change matrix.
- Antyodaya 2020: 004 and 005 already point to the original source.

**Noticed, not changed:**
- 063 (Open Natural Ecosystems, Restricted). The sheet lists "ONE Map" 2018–2024 as public Earth
  Engine assets under `projects/ext-datasets/assets/datasets/ONES/`. This looks like the same
  ATREE dataset. If Smitha Krishnan confirms, 063 could become Open with a real link; its
  `download_url` is currently the bare string `open-natural-ecosystems`.
- 015. The sheet now also lists IndiaSAT v4 (2017–2024, 13 classes, adding orchards and
  plantations), without a licence or Drive downloads yet.
