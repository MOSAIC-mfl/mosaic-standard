# Run MOSAIC on your machine

Everything runs from checkouts side by side, for example `D:\Code\Mosaic\`:

```
mosaic-standard/   catalog/   mosaic-api/   website/   cdh/cdh-catalog/   _local/mosaic-api.local.yaml
```

Needs: git, Python 3.12, Node.js 22.23.4 or newer (Astro 7), and npm.

## 1. Build the catalogue

From `mosaic-standard`, install the tool once (`pip install -e .`; an older `mosaic_catalog`
installed from the old catalogue repo does not know `--catalog`), then:

```sh
python -m mosaic_catalog --catalog ../catalog validate               # records
python -m mosaic_catalog --catalog ../catalog validate-landscapes    # landscape profiles
python -m mosaic_catalog --catalog ../catalog build --out ../catalog/dist
```

Without installing: set `PYTHONPATH=src` (PowerShell: `$env:PYTHONPATH="src"`) for these commands.

## 2. The API

A configuration with local paths (`_local/mosaic-api.local.yaml`; same keys as
`mosaic-api/config/mosaic-api.yaml`):

```yaml
standard: ../catalog/dist                 # the standard as published with the catalogue build
state: ../mosaic-api/state/snapshot.json
export_dir: ../mosaic-api/site
sources:
  - {id: mosaic, name: MOSAIC, type: mosaic_catalog, translator: mosaic, format: mosaic-v0.2,
     location: ../catalog/dist, homepage: https://mosaic-mfl.github.io/website/,
     record_url_template: "https://github.com/MOSAIC-mfl/catalog/blob/main/records/{id}/record.yaml"}
  - {id: cdh, name: CGIAR Climate Data Hub, type: git_yaml, translator: cdh, format: cdh-yaml-v0.5,
     location: ../cdh/cdh-catalog, ref: main, pattern: "records/*/*.yaml",
     homepage: https://cgiar-climate-data-hub.github.io/,
     record_url_template: "https://github.com/CGIAR-Climate-Data-Hub/cdh-catalog/blob/{ref}/{path}"}
http:
  cors_origins: [http://localhost:4321, http://127.0.0.1:4321, https://mosaic-mfl.github.io]
```

From `mosaic-api` (`pip install -e .` once):

```sh
export MOSAIC_API_CONFIG=../_local/mosaic-api.local.yaml        # PowerShell: $env:MOSAIC_API_CONFIG="..\_local\mosaic-api.local.yaml"
python -m mosaic_api harvest      # "mosaic: 108 records …, cdh: 17 records …"
python -m mosaic_api serve        # live:   http://127.0.0.1:8000  (docs at /docs)
python -m mosaic_api export       # static: the files GitHub Pages serves, into site/
```

Harvest again after every catalogue build; the harvest is incremental (only changed records are
translated again).

## 3. The website

From `website/frontend` (`npm ci` once). Copy `.env.example` to `.env` and choose:

| API | `.env` | Start the API |
|---|---|---|
| live | `PUBLIC_MOSAIC_API_MODE=live`<br>`PUBLIC_MOSAIC_API_URL=http://127.0.0.1:8000` | `python -m mosaic_api serve` |
| static (local export) | `PUBLIC_MOSAIC_API_MODE=static`<br>`PUBLIC_MOSAIC_API_URL=http://127.0.0.1:8001` | `npm run api:static` (serves `../../mosaic-api/site` on :8001 with CORS) |
| static (published) | `PUBLIC_MOSAIC_API_MODE=static`<br>`PUBLIC_MOSAIC_API_URL=https://mosaic-mfl.github.io/mosaic-api` | nothing |

```sh
npm run dev            # http://localhost:4321/website/  (port 4321: the API allows only this origin locally)
npm run build && npm run preview     # the production build
```

The `.env` values are read when the site starts or builds: restart `npm run dev` after changing them.

Map explorer data without network: put a profile's files in `<folder>/<CODE>/` and set
`PUBLIC_MOSAIC_PROFILE_DATA=http://127.0.0.1:8002`, served with
`PORT=8002 node scripts/serve-static-api.mjs <folder>`.

## 4. Checks (what CI runs)

| Repository | Commands |
|---|---|
| mosaic-standard | `ruff check src scripts tests`, `mypy src`, `python scripts/build_vocab.py --check`, `python scripts/build_docs.py --check`, `pytest -q` |
| mosaic-skills | `ruff check skills`, `pytest -q skills/mosaic-landscape-profile/tests` |
| catalog | `python -m mosaic_catalog --catalog . validate` and `validate-landscapes` (from the standard) |
| mosaic-api | `ruff check src tests`, `ruff format --check src tests`, `mypy src`, `lint-imports`, `pytest -q` |
| website | `npm run lint`, `npm run typecheck`, `npm test`, `npm run check`, `npm run build` |

## Pages to look at after a change

- `/website/` — Home figures (datasets, landscapes, countries).
- `/website/landscapes#KEN-LVB` — counts, the coverage ring ("n of 16"), open access; `#KEN-LVB/map`
  and `/website/landscapes/ken-lvb/map/` — the map profile; `#COL-CUM` has no Map visualization.
- `/website/catalogue/?processing_status=validated` — filters, tiles / list, readiness.
- `/website/catalogue/dataset/?id=mosaic:MFL-2026-001` and `?id=cdh:africa-spei-drought` — the four tabs.
- `/website/catalogue/MFL-2026-001/` and `/website/landscapes/ken-lvb/` — redirected (old addresses).

## Troubleshooting

| Symptom | Cause |
|---|---|
| `mosaic_catalog: error: argument cmd: invalid choice` | An old `mosaic_catalog` is installed: `pip install -e .` in mosaic-standard, or `PYTHONPATH=src` |
| The website says it could not reach the catalogue | The API is not running, the URL in `.env` is wrong, or the site runs on a port the API's CORS list does not have |
| Every record shows "Not stated" | The API was harvested before the catalogue was rebuilt with `processing_status`: build, then harvest again |
| Astro refuses to start | Node.js older than 22.23.4 |
| The map panel is empty | The explorer's layers are online at their author's GitHub Pages: check the network, or use `PUBLIC_MOSAIC_PROFILE_DATA` |
