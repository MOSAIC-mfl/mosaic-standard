# Records changelog — 2026-10-29

Real access links for three Central India records (Lizeth Llanos, 2026-10-29). Their
`download_url` pointed to QGIS style files (`.qml`) on GitHub, not to data; the 2026-09-04
audit and the 2026-10-28 baseline check both flagged this. On 2026-10-23 Sudharsan Maliappan
(IWMI) shared the source in the Teams chat of the meeting "Baseline data for Ethiopia, India and
LVB + MOSAIC". The source is the **CoRE Stack GEE Layers Links** sheet, with one row per layer
giving its public Earth Engine asset, its Google Drive download and its licence. He named the
owner as CoRE Stack, "a coalition of various organisations in India". The map viewer is the
"GEE datasets directory" linked from core-stack.org.

Sheet: https://docs.google.com/spreadsheets/d/1xS5d7vgyjyoqqnmmajKDZBx9qS6GqyAdSbNDR62ot2Y/edit?gid=0
(read 2026-10-29; public, no sign-in).

| Record | Field | Before | After | Why |
|---|---|---|---|---|
| 013, 014, 015 | `download_url` | QGIS `.qml` style files on GitHub | the sheet URL | The sheet is the only page that gives each layer's download. The pipeline keeps one URL per record, and each record covers several layers. |
| 013, 014, 015 | `current_location` | `CoreStack: Github / Google rive` | CoRE Stack: public Earth Engine assets and Drive downloads, listed in the sheet, plus the map viewer URL | Says where the data is. The old value had a typo. |
| 013, 015 | `source` | `National government (external)` | `CoRE Stack (external)` | CoRE Stack produced these layers. It is a coalition, not a government. |
| 014 | `source` | `National government (external)` | `India-WRIS, via CoRE Stack (external)` | The sheet says the layers in its Waterbodies group (rivers, canals, waterbodies census, reservoirs, reservoir stations) are "Published by India WRIS; Re-published here". |
| 014 | `license` | `CC BY 4.0` | `India-WRIS layers re-published by CoRE Stack; no licence stated by the source` | CC BY 4.0 covers CoRE Stack's own layers, not the re-published ones. No India-WRIS licence text was found on 2026-10-29. |

**Licence check, from the sheet's licence column.** 013's layers (canopy density, canopy height
and tree cover change) and 015's layers (IndiaSAT LULC) are CoRE Stack's own and say CC BY 4.0.
Both keep their licence.

**Unchanged.** Access level stays Open on all three: anyone can download without asking. The
STAC contact role stays `point-of-contact`, because the three ids were already in
`stac_build.py:THIRD_PARTY_RIGHTS`; only that list's comment changed, regrouping them under
CoRE Stack. Titles, descriptions, temporal coverage and spatial resolution were not changed.

**Noticed, not changed:**
- 015 says 2018–2025 and 30 m. The sheet lists IndiaSAT v3 for 2017-18 to 2024-25 and gives no
  resolution.
- The contact line spells the name "Malaiappan". His Teams name and his email both read
  "Maliappan".
- MFL-2026-001's Drive link is the CoRE Stack file for IndiaSAT v3 LULC 2024-25 (same file id).
