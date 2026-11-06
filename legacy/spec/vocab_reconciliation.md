# MOSAIC vocab_reconciliation.md — v1 controlled vocabularies

Final enum lists for `frontend/data/metadata_schema.json` v1, plus reconciliation notes.
Bar: functional, not perfect. Engineer applies these as the dropdown / validation enums.

**Identical-vs-mappable (from assessment §5):**
- **Identical to CDH (must match):** country → UN M49, license → SPDX, contact roles → STAC provider roles. Mirror the CDH `vocab/geography.json` (UN M49) and SPDX — do not invent our own ids.
- **Mappable (crosswalk is enough):** mfl_theme ↔ CDH `domain`, and all `mosaic:*` fields (living_landscape, access_level, readiness/processing, update_frequency, migration_status).

**[COORD]** items need confirmation with Brayden/CDH before being treated as byte-aligned.

---

## 1. country  (frontend display value; STAC uses UN M49 id behind it)

Enum (display strings — keep exactly, including diacritics):
```
["Colombia","Côte d'Ivoire","Ethiopia","India","Kenya","Laos","Peru","Senegal","Tanzania","Tunisia","Vietnam","Zimbabwe"]
```
- **Added** per brief: Senegal, Côte d'Ivoire, Tunisia, Zimbabwe, Peru, **Tanzania (0 records but enum-listed)**.
- `null` allowed for the malformed "Soil dataset" row (do NOT add "Soil dataset" as a country).
- STAC mapping table (frontend display → UN M49 id from CDH `geography.json`, ISO3 in parens):
  | display | M49 id (kebab) | ISO3 |
  |---|---|---|
  | Colombia | colombia | COL |
  | Côte d'Ivoire | cote-d-ivoire | CIV |
  | Ethiopia | ethiopia | ETH |
  | India | india | IND |
  | Kenya | kenya | KEN |
  | Laos | lao-people-s-democratic-republic | LAO |
  | Peru | peru | PER |
  | Senegal | senegal | SEN |
  | Tanzania | united-republic-of-tanzania | TZA |
  | Tunisia | tunisia | TUN |
  | Vietnam | viet-nam | VNM |
  | Zimbabwe | zimbabwe | ZWE |
- **Confirmed 2026-09-28** against CDH v0.3.0 `vocab/geography.json`: all 17 ids in `vocab.py:COUNTRY_M49` exist, including `lao-people-s-democratic-republic`, `united-republic-of-tanzania`, `viet-nam` and `cote-d-ivoire`. ISO3 stays in the table as a second key.
- **Added 2026-08-03 — region/continent tier**, for datasets whose scope spans many countries within one region (e.g. a Latin-America-wide adoption study): `Africa`, `Asia`, `Latin America and the Caribbean` (UN M49 macro-region names/kebab ids — `africa`, `asia`, `latin-america-and-the-caribbean`). No ISO3 exists at this granularity. `Global` stays reserved for worldwide scope; these three sit between a single country and `Global`. (Kebab ids confirmed 2026-09-28.) Add more regions (Europe, Oceania, Northern America) the same way if a submission ever needs one — it's a one-line addition to `COUNTRY_M49` in `vocab.py` + the schema enum.

## 2. living_landscape  (CODE enum — from living_landscape_crosswalk.json)
```
["MEK-3S","IND-CH","SEN-FK","KEN-NAT","ZWE-MB","CIV-NZ","TUN-NW","ETH-OG","COL-NAT","PER-NAT","GLB-UNSPEC"]
```
- PROVISIONAL. `COL-*` and `PER-*` to be finalized when engineer reads the full registry (may become a sub-national code). Add the confirmed code to BOTH the crosswalk and this enum.
- Existing demo codes in landscapes.json (KEN-LV, ETH-GT, IND-WG, COL-AM, MEK-LM, …) are NOT in the real data; either retire them or keep only as demo. Do not mix demo and real codes in the production enum.

## 3. mfl_theme  (identical to CLAUDE.md MFL theme labels; mappable to CDH `domain`)
```
["Boundaries / admin units","Land cover / land use","Ecosystem condition","Degradation / land health","Water / hydrology","Biodiversity / ecosystems","Pressures / drivers","Ecosystem services","Hotspots / leverage points","Scenarios / future risks","Decision-support outputs","Agrobiodiversity / crops","Socio-economic / livelihoods"]
```
- Registry uses 10 of these 13; keep all 13 in the enum (forward-compatible).
- `"Soil dataset"` is NOT a theme → `null` + flag.
- CDH mapping: MOSAIC theme ↔ CDH `domain` is a documented crosswalk only (climate maps to CDH `domain: climate`); do not merge. No theme is climate-exclusive here, so for v1 leave the CDH-domain column unset and let the CDH own it.

## 4. data_type
```
["Raster","Vector","Tabular","Mixed"]
```
- Registry has exactly these four (+ malformed "Soil dataset" → null). NetCDF (mentioned in §3) is treated as Raster/Mixed at frontend level; the precise STAC type is inferred from media_type at export.

## 5. access_level
```
["Open","Internal","Restricted"]
```
- MOSAIC-local (`mosaic:access_level`). Mappable, not identical to CDH.
- Source spellings `CGIAR-internal` / `CGIAR internal` in the registry are normalized to `Internal` on read (registry.py `ACCESS_ALIASES`).

## 6. readiness_status  ** DECISION (see field_mapping.md R7) **
```
["Raw","Processed","Validated"]
```
- **CHANGE to frontend metadata_schema.json:** replace the current 5-value enum `["Registered only","Under review","Accepted","Validated","Analytics-ready"]` with these 3. Rationale: align the frontend to the registry's actual `Processing status` values — the registry is the single source of truth and the 5-value scheme has no data behind it. Stored as `mosaic:processing_status` in STAC.

## 7. license  (SPDX — identical to CDH)
Enum is open to SPDX ids; the dropdown seed list (extend as data requires):
```
["CC-BY-4.0","CC-BY-SA-4.0","CC-BY-NC-4.0","CC0-1.0","other",null]
```
- 2026-09-23: R3 now also emits every CC BY variant (1.0–4.0, the 3.0 IGO ports), `ODC-By-1.0`, `ODbL-1.0` and `PDDL-1.0` — list in `transform.py:SPDX_LICENSE_IDS`.
- Non-SPDX CGIAR strings kept verbatim as documented aliases + flagged (field_mapping R3).
- **[COORD]** agree the SPDX subset + CGIAR-license aliases with Brayden so both hubs read the same values.

## 8. contact role  (STAC provider roles — identical to CDH)
```
["licensor","producer","processor","host"]
```
- Not a registry column today; assigned at export (default `producer`, ensure ≥1 `licensor` per record — field_mapping R1). Confirmed against CDH `mapping-stac.md`: "at least one contact must use role=licensor".

## 9. Source / Centre  (display, light reconciliation)
Canonicalize CGIAR centre names; keep external orgs verbatim. Known/expected values to normalize (engineer confirms full set from data):
```
["Alliance Bioversity-CIAT","CIMMYT","CIP","ICARDA","ICRISAT","IFPRI","IITA","ILRI","IWMI","WorldFish","AfricaRice","ISRA-BAME","Wageningen University & Research"]
```
- AfricaRice / ISRA-BAME / Wageningen flagged in the brief as likely present — engineer adds any others found verbatim; do not drop unknown sources, just keep the string.
- Free-text allowed (not a hard enum) for v1; this is a normalization aid, not a blocker.

## 10. update_frequency  (MOSAIC-local `mosaic:update_frequency`)
```
["Annual","Seasonal","Monthly","On-demand","Static","Unknown"]
```
- **"Static"** retained per brief (datasets that do not change). Blank → `"Unknown"`.

---

## Frontend metadata_schema.json — required changes summary (for engineer)
1. `readiness_status.enum` → `["Raw","Processed","Validated"]` (was 5 values).
2. `country.enum` → 12-country list above (adds Senegal, Côte d'Ivoire, Tunisia, Zimbabwe, Peru, Tanzania).
3. `living_landscape.enum` → new CODE list (replace demo codes).
4. `mfl_theme.enum` → 13-theme list above.
5. `data_type.enum` → `["Raster","Vector","Tabular","Mixed"]`.
6. Confirm `access_level`, `update_frequency`, `license` enums match §5/§7/§10.

## Items needing CDH coordination [COORD]
- ~~Exact UN M49 kebab ids for country~~ — confirmed 2026-09-28 (CDH v0.3.0).
- SPDX subset + CGIAR-license alias table (shared, byte-aligned).
- Shared-vocab version line (geography/license/contact roles move together) — assessment §5.5, open question #3 for Lizeth/Brayden.
