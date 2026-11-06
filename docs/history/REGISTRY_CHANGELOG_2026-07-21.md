# Registry change log — 2026-07-21

Canonical `MFL_Dataset_Registry.xlsx` rebuilt from Lizeth's `MFL_Dataset_Registry 21jul.xlsx` (kept untouched, git-ignored). 68 records, all IDs unique and literal (ID formulas removed — the positional formulas were the root cause of the duplicate-ID bug). Living landscape column normalized to the canonical controlled list approved 2026-07-21 (11 delineated landscapes + NATIONAL + GLOBAL). Dropdown validations recreated; Reference sheet gained the canonical landscape table; stale 'CGIAR-internal' renamed to 'Internal'.

```
Column A: converted 63 formula IDs to literal values, cleared 35 empty-row formulas. Rationale: positional ID formulas caused the duplicate-ID bug and shift when rows are inserted; IDs are now stable literals. New rows: type the next free MFL-2026-### manually.
A2 (placeholder note): 'Auto-filled by formula — do not edit' -> manual-ID instruction
R10: fix typo in description (Dsitric) | was: 'Dsitric level solar Irrigation Suitability Map ' -> now: 'District-level solar irrigation suitability map.'
A28: duplicate ID MFL-2026-023 -> unique ID | was: 'MFL-2026-023' -> now: 'MFL-2026-064'
A29: duplicate ID MFL-2026-024 -> unique ID | was: 'MFL-2026-024' -> now: 'MFL-2026-065'
C53: Country was 'Soil dataset' (malformed); global soil-profile DB | was: 'Soil dataset' -> now: 'Global'
D53: MFL theme was 'Soil dataset' | was: 'Soil dataset' -> now: 'Degradation / land health'
C54: Country was 'Soil dataset' (malformed); SoilGrids is global | was: 'Soil dataset' -> now: 'Global'
D54: MFL theme was 'Soil dataset' | was: 'Soil dataset' -> now: 'Degradation / land health'
A54: Record ID was empty | was: 'None' -> now: 'MFL-2026-066'
E48: Living landscape was empty; Kenya country-scale record | was: 'None' -> now: 'NATIONAL — Country-wide coverage'
E3: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E4: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E5: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E6: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E7: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E8: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E9: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E10: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E11: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E12: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E13: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E14: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E15: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E16: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E17: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E18: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E19: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E20: normalized 'Department of Fatick' -> 'SEN-FK — Fatick Department'
E21: normalized 'Department of Fatick' -> 'SEN-FK — Fatick Department'
E22: normalized 'Department of Fatick' -> 'SEN-FK — Fatick Department'
E23: normalized 'Department of Fatick' -> 'SEN-FK — Fatick Department'
E24: normalized 'Department of Fatick' -> 'SEN-FK — Fatick Department'
R25 (desc): appended 'Original landscape entry: In the Senegal region, the resolution does not allow for data at the departmental level'
E25: normalized 'In the Senegal region, the resolution does no' -> 'SEN-FK — Fatick Department'
E26: normalized 'Department of Fatick' -> 'SEN-FK — Fatick Department'
E27: normalized 'Department of Fatick' -> 'SEN-FK — Fatick Department'
E28: normalized 'Entire Kenya' -> 'NATIONAL — Country-wide coverage'
R29 (desc): appended 'Original landscape entry: Mbire: Wards 2 and 3'
E29: normalized 'Mbire: Wards 2 and 3' -> 'ZWE-MB — Mbire – Lower Zambezi Valley'
R30 (desc): appended 'Original landscape entry: Mbire: Wards 2, 3, 9, 12 and 17'
E30: normalized 'Mbire: Wards 2, 3, 9, 12 and 17' -> 'ZWE-MB — Mbire – Lower Zambezi Valley'
E31: normalized 'Lower Zambezi Valley' -> 'ZWE-MB — Mbire – Lower Zambezi Valley'
R32 (desc): appended 'Original landscape entry: Mbire: Wards 2, 3, 9, 12 and 17'
E32: normalized 'Mbire: Wards 2, 3, 9, 12 and 17' -> 'ZWE-MB — Mbire – Lower Zambezi Valley'
R33 (desc): appended 'Original landscape entry: Mbire: Wards 2, 3, 9, 12 and 17'
E33: normalized 'Mbire: Wards 2, 3, 9, 12 and 17' -> 'ZWE-MB — Mbire – Lower Zambezi Valley'
R34 (desc): appended 'Original landscape entry: Mbire Ward 2'
E34: normalized 'Mbire Ward 2' -> 'ZWE-MB — Mbire – Lower Zambezi Valley'
E35: normalized 'Northwestern Tunisia' -> 'TUN-NW — Northwestern Tunisia'
E36: normalized 'Northwestern Tunisia' -> 'TUN-NW — Northwestern Tunisia'
E37: normalized 'Northwestern Tunisia' -> 'TUN-NW — Northwestern Tunisia'
E38: normalized 'Northwestern Tunisia' -> 'TUN-NW — Northwestern Tunisia'
E39: normalized 'Northwestern Tunisia' -> 'TUN-NW — Northwestern Tunisia'
E40: normalized 'Northwestern Tunisia' -> 'TUN-NW — Northwestern Tunisia'
E41: normalized 'Omo-Gibe Ethiopia' -> 'ETH-OG — Omo-Gibe Basin'
E42: normalized 'Omo-Gibe Ethiopia' -> 'ETH-OG — Omo-Gibe Basin'
E43: normalized 'Omo-Gibe Ethiopia' -> 'ETH-OG — Omo-Gibe Basin'
E44: normalized 'Omo-Gibe Ethiopia' -> 'ETH-OG — Omo-Gibe Basin'
E45: normalized 'Omo-Gibe Ethiopia' -> 'ETH-OG — Omo-Gibe Basin'
E46: normalized 'Omo-Gibe Ethiopia' -> 'ETH-OG — Omo-Gibe Basin'
E47: normalized 'Omo-Gibe Ethiopia' -> 'ETH-OG — Omo-Gibe Basin'
E49: normalized "N'Zi watershed" -> "CIV-NZ — N'Zi Watershed"
E50: normalized "N'Zi watershed" -> "CIV-NZ — N'Zi Watershed"
E51: normalized "N'Zi watershed" -> "CIV-NZ — N'Zi Watershed"
E52: normalized "N'Zi watershed" -> "CIV-NZ — N'Zi Watershed"
E53: normalized 'Soil dataset' -> 'GLOBAL — Global / cross-landscape'
E54: normalized 'Soil dataset' -> 'GLOBAL — Global / cross-landscape'
E55: normalized '3S basins-Sekong, Sesan, and Srepok' -> 'MEK-3S — 3S Basins (Sekong, Sesan, Srepok)'
E56: normalized '3S basins-Sekong, Sesan, and Srepok' -> 'MEK-3S — 3S Basins (Sekong, Sesan, Srepok)'
E57: normalized '3S basins-Sekong, Sesan, and Srepok' -> 'MEK-3S — 3S Basins (Sekong, Sesan, Srepok)'
E58: normalized 'Country and basin scale' -> 'NATIONAL — Country-wide coverage'
E59: normalized 'Country and basin scale' -> 'NATIONAL — Country-wide coverage'
E60: normalized 'Country and basin scale' -> 'NATIONAL — Country-wide coverage'
E61: normalized 'Country and basin scale' -> 'NATIONAL — Country-wide coverage'
E62: normalized 'Country and basin scale' -> 'NATIONAL — Country-wide coverage'
E63: normalized '3S basins-Sekong, Sesan, and Srepok' -> 'MEK-3S — 3S Basins (Sekong, Sesan, Srepok)'
E64: normalized '3S basins-Sekong, Sesan, and Srepok' -> 'MEK-3S — 3S Basins (Sekong, Sesan, Srepok)'
E65: normalized '3S basins-Sekong, Sesan, and Srepok' -> 'MEK-3S — 3S Basins (Sekong, Sesan, Srepok)'
E66: normalized '3S basins-Sekong, Sesan, and Srepok' -> 'MEK-3S — 3S Basins (Sekong, Sesan, Srepok)'
E67: normalized '3S basins-Sekong, Sesan, and Srepok' -> 'MEK-3S — 3S Basins (Sekong, Sesan, Srepok)'
E68: normalized 'Central India highlands: Hot sub-humid rainfe' -> 'IND-CH — Central India Highlands'
E104: normalized 'Entire Laos' -> 'NATIONAL — Country-wide coverage'
E105: normalized 'Entire Vietnam' -> 'NATIONAL — Country-wide coverage'
Reference!I3: 'CGIAR-internal' -> 'Internal'
Reference!A15: added 'Global' to Countries list
Reference!K1:M14: added canonical Living Landscape table
validation: C3:C200 -> ='Reference'!$A$2:$A$16
validation: D3:D200 -> ='Reference'!$C$2:$C$15
validation: E3:E200 -> ='Reference'!$K$2:$K$14
validation: F3:F200 -> ='Reference'!$E$2:$E$7
validation: I3:I200 -> ='Reference'!$G$2:$G$18
validation: K3:K200 -> ='Reference'!$I$2:$I$4
A52: Record ID was empty -> MFL-2026-067 (Climate data / Côte d'Ivoire)
A104: Record ID was empty -> MFL-2026-068 (Tree conservation and restoration priori / Laos)
A105: Record ID was empty -> MFL-2026-069 (Tree conservation and restoration priori / Vietnam)
Note: rows 104-105 sit after a block of empty rows (70-103) — harmless to the pipeline; consider moving them up next time the file is edited in Excel.
```
