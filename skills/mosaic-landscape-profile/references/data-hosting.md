# Data hosting

The catalogue holds only the profile (YAML). The data files stay where their author serves them,
and the visitor's browser reads them directly from there. So every file must be:

1. **On HTTPS**, at a stable address. The address of a folder is a *data root* (`data.roots`),
   ending with `/`.
2. **Readable from the MOSAIC website (CORS):** the server answers
   `Access-Control-Allow-Origin: *` (or `https://mosaic-mfl.github.io`).
3. **Readable in parts (byte ranges)** for `.pmtiles`, `.tif` and `.bin` files: a request with
   `Range: bytes=0-15` gets status `206`. The map then downloads only the tiles it shows instead of
   a whole file of hundreds of MB.
4. **Licensed for display.** A file whose licence is not cleared is listed under `data.withheld`
   (with `withheld_reason`) and is never requested.

`scripts/check_data.py` tests 1–3 for every file the profile names.

## Where to serve the files

| Option | Good for | CORS | Ranges | Limits |
|---|---|---|---|---|
| **GitHub Pages** of a repository (`https://<user>.github.io/<repo>/data/`) | small files: GeoJSON, JSON series, fonts, small PMTiles | yes | yes | files < 100 MB, site < 1 GB |
| **Hugging Face dataset** (`https://huggingface.co/datasets/<org>/<name>/resolve/main/`) | large PMTiles and GeoTIFFs | yes | yes | public datasets; large files with Git LFS / `huggingface_hub` upload |
| **Cloud storage** (S3, Google Cloud Storage, Azure, Cloudflare R2) with a public bucket | anything | configure a CORS rule | yes | costs; set the CORS rule yourself |
| An institutional server | anything | must be configured | must be supported | ask its administrator to allow CORS and ranges |

KEN-LVB and PER-PCL use both: GitHub Pages (`site`) for small files and Hugging Face (`hf`) for
the large ones, with `routes` sending each folder or file to its root:

```yaml
data:
  roots:
    site: https://anaguilarar.github.io/mosaic-lake-victoria/data/
    hf: https://huggingface.co/datasets/aaguilar90/mosaic-lake-victoria/resolve/main/
  default_root: hf
  routes:
  - {prefix: vectors/, root: site}
  - {path: tiles/terrain.pmtiles, root: site}
```

Change a root with `edit_profile.py set-root --code <CODE> --root <name> --url https://…/`.

## File formats the modules read

| Data | Format | Notes |
|---|---|---|
| Rasters for display | **PMTiles** (raster tiles, PNG/WebP) | e.g. `gdal_translate -of MBTILES in.tif out.mbtiles && gdaladdo -r nearest out.mbtiles && pmtiles convert out.mbtiles out.pmtiles` |
| Rasters read on click | **Cloud-optimized GeoTIFF** (COG) | `gdal_translate in.tif out.tif -of COG -co COMPRESS=DEFLATE`; keep the projection the `inspect` expects |
| Polygons, lines, points | GeoJSON (small) or **vector PMTiles** (large; `tippecanoe -o out.pmtiles -l <layer> in.geojson`) | for vector PMTiles the layer name is the `source-layer` |
| Series for charts and panels | JSON | the paths in the YAML (`path`, `regions_path`) point inside it |
| Climate (`climate-grid`, `index-grid`) | the MOSAIC climate pipeline folder: `app_meta.json`, `landmask.tif`, `normals.tif`, `*_cells.bin`, `spi3.tif` | produced by the pipeline, not by hand |
| Fonts for labels | glyph PBF ranges (`fonts/<Font name>/0-255.pbf`) | copy them from the profile you started from |

## Fixing what check_data.py reports

| Problem | Meaning | Fix |
|---|---|---|
| `data root still TODO` | the root is the placeholder | set the real root (`set-root`) |
| `not served over HTTPS` | `http://` address | use the https address of the same host |
| `HTTP 404 (file not found)` | no file at that address | check the file name and folder, the root, or the route that sends it elsewhere; upload the file |
| `HTTP 403` | private or blocked | make the repository/bucket public, or use another host |
| `no CORS for the website` | the server does not allow the website to read it | GitHub Pages and Hugging Face allow it; for a bucket add a CORS rule allowing `GET` and `HEAD`, header `Range`, from `*` |
| `no byte ranges` | the server sends the whole file | use a host that supports ranges (all above do); some CDNs/proxies need it enabled |
| `unreachable` | wrong host name, network, or the server is down | check the address in a browser |

A Hugging Face address must use `/resolve/main/` (the file), not `/blob/main/` (the web page).
