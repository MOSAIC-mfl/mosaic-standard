# Records changelog — 2026-09-22

Batch: **Beatriz Rodríguez's answers** (email reply received 2026-09-22, forwarded by Lizeth as a
screenshot) to the follow-up on her 11 Ucayali records **MFL-2026-072 … 082**. Her values were
applied as given; nothing else in the records was touched. The follow-up she answered was the v1
email of 2026-09-16 (questions 1 and 2 plus the two "already changed" notes).

## Answers → edits

| ID(s) | Field | From → To | Her answer (verbatim, Spanish) |
|---|---|---|---|
| 081, 082 | `license` | `Other (specify in notes)` → **`CC BY 4.0`** | "la fuente es Mapbiomas, según el sitio web la licencia es CC BY 4.0" |
| 075 | `license` | `Other (specify in notes)` → **`Free download from RAISG; no formal license stated`** | "son de descarga gratuita de RAISG" |
| 072, 073, 074, 076, 077, 078, 079, 080 | `license` | `Other (specify in notes)` → **`Free download from the Peruvian government source (MINAM/GEOBOSQUES, SERNANP, INEI); no formal license stated`** | "los demás datos de descarga gratuita de Geobosques, Geovisor MINAM de Perú" — 072 actually comes from INEI (datos abiertos) and 073/074 from SERNANP; same nature (free government downloads, terms not stated), and each record's `download_url` names the exact source, so one string serves the eight. |
| 080 | `description` | "Annual forest loss from **2001-2025** …" → "… **2001-2024** … . **The 2025 update published at source is not yet included in this layer.**" | "La correcta es 2001-2024, ya están disponibles para 2025, pero aún no las hemos actualizado en la plataforma." |
| 082 | `title` | `Annual Burned Area` → **`Accumulated Burned Area 2013-2024`** | "En este caso el área acumulada para el periodo 2013-2024. Creo que sería mejor 'Accumulated Burned Area 2013-2024'" — her wording kept (it is also how MapBiomas Fire names the product); the description still says "Cumulative Burned Area", a synonym, left verbatim. |

## Confirmed by her — no change

- **081** `temporal_coverage: 2000, 2005, 2010, 2015, 2020, 2024` (the 2026-09-16 fix) — "Está bien el cambio".

## Pipeline effect (rule R3, `map_license`) — and a gotcha

- `CC BY 4.0` → SPDX **`CC-BY-4.0`** (081, 082): the same string the 27 other CC BY records use.
- The nine "Free download …" statements are non-SPDX → kept **verbatim** (`non_spdx_license` flag), so
  they appear in the STAC items as `mosaic:license_original` and as `license` in `datasets.json` —
  exactly like "CGIAR Open Access". The meaningless "Other (specify in notes)" is gone for all 11.
- **Gotcha — why the wording matters:** a first attempt used "Open data — free download …". Any
  string that *starts with* "open" or contains "open data" hits the mapper's *vague-license* branch →
  `license: other`, and because `stac_build.py` writes `mosaic:license_original` only for non-SPDX
  values other than `other`, the text is **dropped from every output** (the public catalog would show
  just "other"). That branch had never been exercised before. Logged as a pipeline TODO in
  `MOSAIC_development/CLAUDE.md`; data-side rule until it is fixed: never start a license statement
  with "Open".

## Still open with Beatriz

- **PER-PCL confirmation** (question 3 — name and extent of the Peru Living Landscape): not in her
  reply (the sent version showed only questions 1–2). Still `mosaic:pending_confirmation` on PER-PCL.
- File-based fields (`file_names`, `server_path`, `file_size`, `crs`, measured `bbox`) wait for the
  next record batch. The storage layout they depend on was approved on 2026-09-22, and the batch itself
  awaits Lizeth's go.
