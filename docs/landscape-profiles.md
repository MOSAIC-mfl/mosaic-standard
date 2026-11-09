# Landscape profiles

Every living landscape has a page on the MOSAIC website: `/landscapes/<code>/` (for example
`/landscapes/ken-lvb/`). What the page shows is written in the catalogue repository
([MOSAIC-mfl/catalog](https://github.com/MOSAIC-mfl/catalog), `landscapes/<CODE>/`), next to the records,
and validated like them with the tool of this repository (schemas: `schema/landscape/`).

- **No folder for a landscape:** its page has the default sections (`mosaic.config.yaml`,
  `landscapes.default_sections`: overview, datasets in the catalogue, data status). All 11
  landscapes have a page this way, with nothing written.
- **`landscapes/<CODE>/profile.yaml`:** the landscape's own page, curated. It lists its sections in
  order. A section can be a core module or a module of its own.

```
landscapes/KEN-LVB/
  profile.yaml     the page: title, summary, status, sections, credits
  explorer.yaml    a map explorer section: data locations, base map, layers, panels, click, about
  story.yaml       its story (chapters that move the map), optional
  studies.yaml     its study cards (verified findings, explore questions), optional
  sources.yaml     source, licence, citation and caveats of each layer, optional
```

The heavy data (map tiles, GeoTIFFs, series) **is not copied here**. It stays where its author serves
it (GitHub Pages, Hugging Face…). `explorer.yaml` only says where each file lives; the visitor's
browser reads them from there.

## Check and publish

```sh
python -m mosaic_catalog --catalog ../catalog validate-landscapes   # every landscape: OK / ERR, and why
python -m mosaic_catalog --catalog ../catalog validate-landscapes KEN-LVB -v
python -m mosaic_catalog --catalog ../catalog build  # also writes dist/landscapes/index.json + <CODE>.json
```

The checks go beyond the schemas (`schema/landscape/*.schema.json`):

- the folder name is the landscape code, and the code exists in `vocab/landscapes.json`;
- every overlay, toggle and panel belongs to a group of the rail, and its `before` layer exists;
- every layer a toggle switches exists in the base map;
- every overlay a story chapter or a study card names exists;
- every catalogue record named (`record: mosaic:MFL-…`) exists;
- the data routes point to declared roots, and no path leaves its folder;
- a published study card has its finding, citation and the verified claims.

A kind of section or overlay the website does not know is a **warning**, not an error: the website
must register it first (see mosaic-web, `docs/landscape-profiles.md`).

## Sections

| `kind` | What it shows | Configuration |
|---|---|---|
| `overview` | datasets, completeness, countries, code | none |
| `map-explorer` | a map explorer (layers, time, panels, story, studies) | `source: explorer.yaml` |
| `catalogue-datasets` | the catalogue's datasets for the landscape | none |
| `data-status` | what the catalogue holds and what the records still lack | none |

## Map explorer (explorer.yaml)

| Block | Content |
|---|---|
| `data` | `roots` (name → base URL), `default_root`, `routes` (prefix or path → root), `withheld` (never requested), `tiles_version`, `report` |
| `map` | camera and limits, `terrain`, `sky`, `glyphs`, and the base map as MapLibre `sources` and `layers` (files as `{asset: path}` or `{pmtiles: path}`) |
| `groups` | the rail groups, in order |
| `toggles` | switch base layers on and off (place names, admin boundaries, rivers) |
| `panels` | side panels opened from the rail (`kind: series-summary`: KPIs and the monthly chart of a series) |
| `overlays` | the layers people choose, one at a time; `kind` picks the renderer, `inspect` what a click shows |
| `click` | what a click shows with no overlay (place, administrative unit) |
| `story`, `studies`, `about` | the files above |

Overlay kinds: `raster-tiles` (one PMTiles raster, or `variants` switched in the legend),
`year-tiles` (one raster per year, optionally points per year), `climate-grid` (yearly and seasonal
climate stacks with anomalies and a cell panel), `index-grid` (a monthly index such as SPI-3),
`style-layers` (the overlay's own MapLibre `sources` and `layers`: vector data coloured by a
property, points from a zoom level, or a raster grid with points on top).
Click kinds: `cell-sum`, `class-at-point`, `annual-series`, `region-series`, `feature-attributes`
(the clicked polygon or nearest point, its fields as templates `{field|filter}`), `value-at-point`
(raster bands at the click, with scale and nodata), `series-values` (named values from a JSON file),
`combined` (several of these on one click), and the ones a profile plugin adds (KEN-LVB:
`flood-query`). Story charts: `seasonal-total`, `monthly-mean`, `monthly`, `annual-bars`,
`class-bars` (one horizontal bar per class). Story chapters can carry `steps` (chips that switch the
layer and its time, highlight a feature with `focus`, and move the camera, also to a `bounds` box);
`story.map.focus` names the layers and the field of that highlight.

## A new profile

**Without programming:** the Claude Code skill
[`skills/mosaic-landscape-profile/`](../skills/mosaic-landscape-profile/README.md) guides the whole
process in any language (a profile like KEN-LVB or PER-PCL, with fewer or changed layers, or a new
one; data hosting checks; validation with explanations; a preview; the pull request), and writes
everything in English. By hand:

1. In the catalogue repository, create `landscapes/<CODE>/profile.yaml` with the sections you want. Without a map explorer,
   that is all.
2. For a map explorer, start from `landscapes/KEN-LVB/explorer.yaml`: change `data`, the camera, the
   base map and the overlays. The same renderers draw any data of the same kind.
3. `python -m mosaic_catalog --catalog ../catalog validate-landscapes <CODE>` (here, or the catalogue's
   Validate check on the pull request).
4. Only when the profile needs something no module does yet (a new kind of layer, a click on a data
   format of its own), the website adds a module or a profile plugin. The rest is configuration.

## Lake Victoria (KEN-LVB)

The profile was converted from the Lake Victoria Basin Explorer by Andrés Aguilar
(https://github.com/anaguilarar/mosaic-lake-victoria, commit 0d22fe2) with
`scripts/migrate_lake_victoria.py`. The explorer's repository is only read. Its own JSON files
(`layers.json`, `story_chapters.json`, `studies.json`) are converted as they are; what it kept in
JavaScript (layers, legends, map style, colours) is transcribed in the script, so the profile shows
exactly what the explorer shows.

Its layers are not catalogue records yet: `review/landscape_KEN-LVB_sources.md` lists them for the
team to register. Licences to confirm before publishing: the ICPAC basin boundary (not specified:
withheld), DAHITI lake levels (non-commercial), HydroSHEDS rivers (display only).

## Pucallpa – Ucayali (PER-PCL)

Converted the same way from the MOSAIC Ucayali Explorer by Andrés Aguilar
(https://github.com/anaguilarar/mosaic-ucayali, commit 24fbe3a) with `scripts/migrate_ucayali.py`:

```
python scripts/migrate_ucayali.py --source D:/Code/Mosaic/mosaic-ucayali --catalog ../catalog
```

The explorer was scaffolded from the Lake Victoria one, so land cover, forest loss, fire, burned area
and the climate layers use the same modules. Its vegetation classes, protected areas and GEDI
footprints are `style-layers` overlays with `feature-attributes` clicks (GEDI: `combined` with the
1 km cell's `value-at-point`); canopy height uses `value-at-point`; the story's class charts use
`class-bars`. It needs no profile plugin. Its climate files are the newer format of the pipeline
(per-variable `scales`, `seasons` and real-unit normals in `app_meta.json`), which the climate
modules read as well as the older one.

Its layers are not catalogue records yet: `review/landscape_PER-PCL_sources.md` lists them, with the
records MOSAIC already has on the same sources (derived products, not the same files). Licences to
confirm before publishing: terrain (DEM provenance open), GEOBOSQUES forest loss (no licence stated),
SERNANP protected areas (derived maps authorised, no commercial use). RAISG Indigenous territories
are deliberately not hosted.
