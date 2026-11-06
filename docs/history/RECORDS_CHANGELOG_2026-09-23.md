# Records changelog — 2026-09-23

## New record field `gee_asset_id` (approved by Lizeth Llanos, 2026-09-23)

Records the Google Earth Engine asset ID of MOSAIC's copy of a dataset, after the Earth Engine
hosting pilot on the programme project `mosaic-mfl`.

- **Schema:** `gee_asset_id` (string | null) added to `spec/record_schema.json` after `file_size`,
  pattern `^projects/[a-z][a-z0-9-]{4,28}[a-z0-9]/assets/[A-Za-z0-9_-]+(/[A-Za-z0-9_-]+)*$`
  (Cloud-project asset IDs only). YAML-only, like `citation`.
- **Output:** STAC item property `mosaic:gee_asset_id` (only when set); `datasets.json` key
  `gee_asset_id` (null when unset). No STAC link or asset: an Earth Engine asset ID is not a URL,
  and a link to a private asset is a dead end. Add a `rel: related` Code Editor link once an asset
  is public. *Update 2026-09-29:* no Code Editor link. Once an asset is public it gets an
  `earth-engine` STAC asset with the Earth Engine REST URL (`https://earthengine.googleapis.com/v1/<gee_asset_id>`), the form the CDH uses
  (CDH issue #34); Lizeth's choice.
- **MOSAIC STAC extension version:** 0.1.0 → 0.2.0 (first new `mosaic:*` item property), so every
  STAC file changes its `mosaic:schema_version` / extension URL. 0.2.0 also covers
  `mosaic:spatial_resolution` (catalog commit `30d42c6`, CDH v0.3.0 alignment, 2026-09-28); both
  were published in the same push.
- Naming and placement reviewed by the metadata-standards specialist the same day
  (`gee_asset_id` rather than `gee_asset`, because "asset" means a file object in STAC).

## Record edits

| Record | Field | Before | After |
|---|---|---|---|
| MFL-2026-064 | `gee_asset_id` | (absent) | `projects/mosaic-mfl/assets/mvp/MFL-2026-064` |
| MFL-2026-072 | `gee_asset_id` | (absent) | `projects/mosaic-mfl/assets/mvp/MFL-2026-072` |

Both assets are **private** (not shared) as of this date. Committed and pushed 2026-09-28 at
Lizeth's request; the assets stay private (only the IDs are public).
