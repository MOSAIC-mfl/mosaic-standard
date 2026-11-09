# Modules: what a profile can configure

Everything here is configuration the website already draws. The examples are taken from the two
curated profiles in the catalogue (`landscapes/KEN-LVB/`, `landscapes/PER-PCL/`); open those files
for the complete versions. The schemas (`schema/landscape/*.schema.json` in mosaic-standard) are
the source of truth.

Paths of data files are always **relative to a data root** (`tiles/landcover_2020.pmtiles`), never
full URLs and never with `..`.

## 1. The page: `profile.yaml`

```yaml
profile: mosaic-landscape-profile@0.1
landscape: KEN-LVB            # = the folder name, a code of vocab/landscapes.json
title: Lake Victoria Basin
summary: >-
  Terrain, flood hazard, rainfall, ... across the Lake Victoria Basin, 1981–2026, ...
status: draft                 # draft | review | published (draft and review show a notice)
sections:
- id: explorer                # anchor in the page (#explorer)
  kind: map-explorer
  title: Basin Explorer
  source: explorer.yaml
- id: datasets
  kind: catalogue-datasets
  title: Datasets in the catalogue
- id: data-status
  kind: data-status
  title: Data status
credits:
- name: Andrés Aguilar
  role: 'Lake Victoria Basin Explorer: data pipeline, analysis, design'
  url: https://github.com/anaguilarar/mosaic-lake-victoria
origin:                       # where the content came from (optional)
  repository: https://github.com/anaguilarar/mosaic-lake-victoria
  commit: 0d22fe2
  note: Converted by scripts/migrate_lake_victoria.py; the original explorer is unchanged.
```

| Section `kind` | Shows | Needs |
|---|---|---|
| `overview` | datasets, completeness, countries, code | nothing |
| `map-explorer` | the map explorer | `source: explorer.yaml` |
| `catalogue-datasets` | the catalogue's datasets for the landscape | nothing |
| `data-status` | what the catalogue holds and what records still lack | nothing |

Each section may have `title` and `intro`. Without `profile.yaml` a landscape gets the default page
(overview, datasets, data status).

## 2. The map explorer: `explorer.yaml`

Top level: `title`, `tagline`, `data`, `map`, `groups`, `toggles`, `panels`, `overlays`, `click`,
`story`, `studies`, `about`. Required: `title`, `data`, `map`, `groups`, `overlays`.

### `data`: where the files are served

```yaml
data:
  roots:                                  # name -> https address ending with '/'
    site: https://anaguilarar.github.io/mosaic-lake-victoria/data/
    hf: https://huggingface.co/datasets/aaguilar90/mosaic-lake-victoria/resolve/main/
  default_root: hf                        # files with no route come from here
  routes:                                 # exceptions, by folder (prefix) or by file (path)
  - prefix: vectors/
    root: site
  - path: tiles/terrain.pmtiles
    root: site
  withheld:                               # never requested (licence not cleared)
  - vectors/basin.geojson
  withheld_reason: 'ICPAC basin boundary: licence not specified, never published'
  tiles_version: '13'                     # change it after rebuilding tiles (defeats old caches)
  report: https://github.com/anaguilarar/mosaic-lake-victoria/blob/main/DATA_REPORT.md
```

### `map`: camera, limits and base map

`center` [lng, lat], `zoom`, `pitch`, `bearing`, `min_zoom`, `max_zoom`, `max_pitch`, `max_bounds`
[[w, s], [e, n]], `sky`, `glyphs` (fonts), `terrain`, `attribution`, and the base map as MapLibre
`sources` and `layers`. Files are written `{asset: path}` (GeoJSON, images) or `{pmtiles: path}`.

```yaml
  sources:
    lake:
      type: geojson
      data: {asset: vectors/lake.geojson}
    s2:
      type: raster
      url: {pmtiles: tiles/s2_rgb.pmtiles}
```

Base layer ids matter: overlays are drawn **under** the layer named in their `before`. KEN-LVB's
base layers, bottom to top: `bg, s2, hillshade, lake-fill, dim, rivers, basin-line, lake-hit,
labels-start, adm2-hit, …, osm-city, osm-country`. `labels-start` is an empty marker layer: draw
something "before: labels-start" to keep it under the place names. `new_profile.py --like` keeps the
base map of the copied profile: its boundary, mask and imagery files must be replaced.

### `groups`, `toggles`, `panels`: the side list (rail)

```yaml
groups: [Base, Water, Flood hazard, Climate, Exposure, Land, Fire]   # in this order
toggles:                         # switch base layers on/off
- id: rivers
  group: Water
  title: Rivers
  swatch: '#117A8D'
  default: true
  layers: [rivers]               # ids of map.layers
  source_ref: rivers             # its entry in sources.yaml
panels:                          # a side panel with KPIs and a chart of a series
- id: lake
  group: Water
  title: Lake level
  kind: series-summary
  open_on_click: lake-hit        # a click on this base layer opens it
  series: series/lake_level.json
  points: data                   # where the points are in the JSON
  date: date
  value: wse
  unit: m
  summary:
  - {stat: latest, label: 'Latest level · {date}'}
  - {stat: vs_median, label: vs median}
  - {stat: max, label: 'Record · {month}'}
  chart: {title: 'Water surface elevation, monthly mean (m)', reference: median}
```

Every overlay, toggle and panel needs a `group` listed in `groups`, and ids unique across the rail.

### `overlays`: the layers people choose (one at a time)

Common fields: `id`, `group`, `title`, `kind`, `swatch` (colour in the rail), `source_ref` (entry
in `sources.yaml`), `before`, `attribution`, `legend`, `inspect` (the click).

**Legend** (`legend`): `kind` `steps` (colours + first/last label), `classes` (one entry per class:
`name` and `color` or `rgb`, optionally `value`) or `gradient`; `title` (`{year}` becomes the
selected year), `notes`, `source`.

#### Overlay kinds (renderers)

| `kind` | For | Key fields |
|---|---|---|
| `raster-tiles` | one raster (PMTiles) | `asset`, `paint`; or `variants` switched in the legend |
| `year-tiles` | one raster per year (+ optional points per year) | `years: {'2020': path}`, `time_label`, `time_caption`, `points` |
| `climate-grid` | yearly/seasonal climate stacks with anomalies and a cell panel | `grid` (folder), `variables`, `aggregate`, `units`, `ramp`, `anomaly` |
| `index-grid` | a monthly index such as SPI-3 | `grid`, `stack`, `cells`, `qc`, `scale`, `range`, `ramp`, `classes` |
| `style-layers` | the overlay's own MapLibre `sources` + `layers` (vector polygons/points, raster grid with points) | `sources`, `layers` |

`raster-tiles` (KEN-LVB `population`):

```yaml
- id: population
  group: Exposure
  title: Population
  kind: raster-tiles
  swatch: '#d7301f'
  source_ref: population
  asset: tiles/population.pmtiles
  before: rivers
  paint: {raster-resampling: nearest, raster-opacity: 0.85}
  legend:
    kind: steps
    title: Population — persons per ~100 m cell (log scale)
    colors: ['#fff3e5', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#b30000', '#7f0000']
    labels: ['1', ≥3000]
  inspect: {kind: cell-sum, ...}          # see clicks
```

`raster-tiles` with `variants` (KEN-LVB `flood_freq`): a list of `{id, label, asset, legend}`; the
legend shows buttons (All / MAM / OND).

`year-tiles` (KEN-LVB `landcover`, abbreviated):

```yaml
  kind: year-tiles
  years:
    '2017': tiles/lulc_2017.pmtiles
    '2023': tiles/lulc_2023.pmtiles
  time_caption: land cover
  legend:
    kind: classes
    title: Land cover {year} (Esri/Impact Observatory)
    classes:
    - {value: 1, name: Water, rgb: [65, 155, 223]}
    - {value: 2, name: Trees, rgb: [57, 125, 73]}
```

With points per year (KEN-LVB `fire`): `points: {assets: {'2012': fire/points_2012.geojson, …},
min_zoom: 10, before: labels-start, paint: {circle-color: '#e55064', …}}`.

`climate-grid` (KEN-LVB `precip`): reads a climate folder produced by the MOSAIC climate pipeline
(`app_meta.json`, `landmask.tif`, `normals.tif`, `<var>_cells.bin`):

```yaml
- id: precip
  kind: climate-grid
  grid: climate/app/
  variables:
  - {id: precip, label: Precip, title: Precipitation, cells: precip_cells.bin}
  aggregate: total            # total (rain) or mean (temperature)
  units: mm
  ramp: ['#fde737', '#dec957', …, '#00224d']
  anomaly: {kind: ratio, units: '% of normal', centre: 100, ramp: [...], normals: precip}
  water_note: satellite rainfall over the lake is less reliable
```

`index-grid` (KEN-LVB `spi3`): `grid: climate/app/`, `stack: spi3.tif`, `cells: spi3_cells.bin`,
`qc: spi3_qc.tif`, `scale: 0.01`, `range: [-3, 3]`, `ramp`, `classes` (`{max|below, label}`),
`provisional_months`, `basin_series: series/spi3_basin.json`, `calibration: 1991–2020`.
(`cells`, `stack`, `qc` are file names inside `grid`.)

`style-layers` (PER-PCL `veg_classes`): polygons coloured by a property:

```yaml
- id: veg_classes
  kind: style-layers
  sources:
    veg: {type: geojson, data: {asset: vectors/veg_classes.geojson}}
  layers:
  - {id: veg-fill, type: fill, source: veg, paint: {fill-color: [get, color], fill-opacity: 0.72}}
  - {id: veg-line, type: line, source: veg, paint: {line-color: [get, color], line-width: 1.2}}
  legend: {kind: classes, title: Vegetation classes, classes: [{name: Palm swamps, color: '#5e9ea0'}, …]}
  inspect: {kind: feature-attributes, layers: [veg-fill], ...}
```

PER-PCL `gedi` combines a raster grid (`{pmtiles: tiles/gedi_grid.pmtiles}`) faded out by zoom with
vector points (`source-layer: footprints`, `minzoom: 9`) coloured by `rh95`.

#### Clicks (`inspect`)

| `kind` | A click shows | Key fields |
|---|---|---|
| `cell-sum` | the value of the cell and of the 3×3 block | `asset` (GeoTIFF), `title`, `cell_label`, `block_label`, `nodata_text`, `note` |
| `class-at-point` | the class at the point (per year with `band_per_year`) | `asset`, `classes`, `band_per_year`, `title` (`{place}`), `hint`, `year`, `facts`, `area_series` (`key: value`) |
| `annual-series` | a yearly series of the area, as chart | `series`, `path`, `title`, `unit`, `chart_title`, `note_field`, `area_name` |
| `region-series` | a series for the region clicked (polygons) | `series`, `regions_path`, `default_region`, `polygons`, `title` (`{region}`), `unit`, `kpi_*`, `chart_title` |
| `feature-attributes` | fields of the clicked polygon or nearest point | `layers`, `place`, `title`, `fields: [{label, value: '{FIELD|filter}'}]`, `notes` |
| `value-at-point` | raster band values at the point | `asset`, `bands: [{band, label, unit, nodata, scale}]`, `title`, `hint`, `facts`, `note` |
| `series-values` | named values from a JSON file | `series`, `path`, `labels_path`, `unit`, `title`, `note` |
| `combined` | several of the above on one click | `target: panel`, parts |
| `flood-query` | KEN-LVB plugin: flood statistics at the point | `asset`, `crs`, `source` (only for KEN-LVB) |

`climate-grid` and `index-grid` have their click built in (the cell panel).

Templates in texts: `{place}`, `{year}`, `{region}`, and in `feature-attributes` field values
`{FIELD}` with filters, e.g. `{area_ha|num}`, `{COBERTURA|spaces}`.

`value-at-point` (PER-PCL `canopy`):

```yaml
  inspect:
    kind: value-at-point
    asset: query/canopy_height_10m.tif
    title: Canopy height at {place}
    bands:
    - {band: 0, label: Canopy top height · 2020, unit: m, nodata: [255]}
    facts:
    - {label: Licence, value: CC BY 4.0}
```

`region-series` (KEN-LVB `forest_loss`):

```yaml
  inspect:
    kind: region-series
    series: series/forest_loss.json
    regions_path: [regions]
    default_region: Lake Victoria Basin
    polygons: vectors/subbasins.geojson
    title: Tree-cover loss · {region}
    unit: km²
    kpi_upto: Loss 2001–{year}
    kpi_total: Full record
    chart_title: Annual tree-cover loss, {region} (km²)
```

`annual-series` (KEN-LVB `fire`): `series: series/fire.json`, `path: [snpp_detections_basin]`,
`unit: detections`, `chart_title: …`, `note_field: caveats`.

### `click`: a click with no overlay

```yaml
click:
  title: Ucayali                       # PER-PCL
  source: Sentinel-2 mosaic · 30 m
  admin:
    layers: [districts-hit, provinces-hit]
    visible_layer: provinces-hit
    name_fields: [district, province]
    iso: PER
    units: {PER: [Province, District]}   # KEN-LVB lists one entry per country
```

### `about`

```yaml
about:
  intro: Part of MOSAIC — the CGIAR Multifunctional Landscapes Science Programme.
  licence: Content licensed under CC BY 4.0 unless otherwise stated. ...
  sources: sources.yaml
```

`story: {file: story.yaml}` and `studies: {file: studies.yaml}` link the two optional files.

## 3. The story: `story.yaml`

Chapters that set the map as the reader scrolls. Required: `title`, `chapters` (each `id`, `title`,
`text`). Optional per chapter: `status` (`ready`, `pending`, `provisional`), `visual`, `numbers`,
`sources`.

```yaml
- id: rains
  title: The short rains of 2019
  text: Late 2019 brought exceptional rain. ...      # the author's text, with its citations
  status: ready
  visual:
    type: map
    layers: [precip]                                 # overlay ids
    time: {var: precip, season: ond, mode: anomaly, year: 2019}
    camera: {lng: 32.6, lat: -1.15, zoom: 6.65, pitch: 0}
    charts:
    - builder: seasonal-total
      title: Short-rains (OND) basin rainfall, mm
      series: series/precip_basin.json
      path: [monthly]
      months: [10, 11, 12]
      normal: [1991, 2020]
      unit: mm
  numbers:
  - value: 658 mm
    label: OND 2019 basin rainfall, vs a 381 mm OND normal (1991-2020)
    source: {kind: app, method: CHIRPS v3.0 basin mean, land cells only}   # or {kind: study, citation: ...}
  sources:
  - 'SON 2019 rains dominant: Khaki & Awange (2021), Sensors 21, 4304 · abstract p.1'
```

- Chart builders: `seasonal-total`, `monthly-mean`, `monthly`, `annual-bars`, `class-bars` (one
  horizontal bar per class; PER-PCL uses it for its tables).
- `steps`: chips in the chapter that switch layer, time and camera:
  `[{label: 'Active fires, 2024', layer: fire, time: {year: 2024}, camera: {...}}]`; a camera can be
  a `bounds` box; `focus` highlights one feature.
- `story.map`: extra layers for the story (`sources`, `layers`, `while_open`, `highlights`), and
  `focus: {layers: [...], field: PLOTID}` for the feature a step highlights (PER-PCL).
- A number always says where it comes from: `kind: study` with the `citation` (page), or `kind: app`
  with the `method`.

## 4. Study cards: `studies.yaml`

```yaml
cards:
- id: rise_2020
  question: How unusual was the 2020 lake-level rise?
  kind: published                       # a verified finding from a paper
  finding: Lake Victoria rose by 1.21 m in the six months to 17 May 2020, ...
  citation: Pietroiusti et al. (2024), Earth System Dynamics 15, 225-264
  doi: 10.5194/esd-15-225-2024
  verified:                             # each claim and where it is in the paper
  - {claim: return period 63.2 years (CI 27-395), where: abstract p.225; sect. 3.5 p.237}
  layers: []
  open_panel: lake
  camera: {lng: 33.0, lat: -1.0, zoom: 7, pitch: 0}
  caveat: The confidence interval includes 1, ...
```

`kind: explore` is a question for further work: its text describes, it does not claim results.
Optional: `layers`, `time`, `steps`, `map_note` (what the map shows for this card), `data_note`
(why no layer).

## 5. Sources: `sources.yaml`

One entry per `source_ref`, written as the data's author states it:

```yaml
layers:
- id: basin
  title: Lake Victoria Basin boundary
  group: Base
  source: ICPAC geoportal (geonode:lv_basin), 2019; ...
  licence: 'ICPAC: not specified (confirm before public release); ...'
  caveats: Lake shoreline from the Copernicus GLO-30 water-body mask (2011-2015); ...
  citation: ICPAC Geoportal; Copernicus DEM GLO-30 (ESA/Airbus)
  record: null              # mosaic:MFL-YYYY-NNN once the dataset is in the catalogue
```

## What needs the developers

A new overlay `kind`, a click on a data format no inspector reads, a new chart builder or a new
section kind. The validator reports an unknown kind as a warning; the website must register it
before it shows. Describe the need in the pull request ("Request to the developers").
