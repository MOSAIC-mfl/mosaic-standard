# ADR-001 — Repository architecture for the MOSAIC catalog

- **Status:** Proposed (awaiting Lizeth's confirmation)
- **Date:** 2026-06-22
- **Owner:** Lizeth Llanos (MOSAIC geospatial coordinator, MFL AoW2)
- **Decision driver:** A new empty repo `AoW2-MFL-CGIAR-Science-Program/MOSAIC_catalog` was created to receive the catalog backend. We must decide how to organize the work before populating it.
- **Update 2026-09-28:** the organization was renamed `MOSAIC-mfl` and the repos `catalog` (was `MOSAIC_catalog`), `website` (was `mfl-living-landscapes-frontend`) and `vision-foundations` (was `MOSAIC_vision_foundation`). The canonical STAC endpoint is now `https://mosaic-mfl.github.io/catalog/stac/catalog.json`. The two-repo decision stands; the names and URLs below are as of 2026-06-22.

---

## Context

MOSAIC is a coordination network and metadata system for the CGIAR MFL Science Programme — not a repository, platform, or database. It produces machine-readable metadata so each hub stays an addressable source of truth ("connect, don't duplicate").

The catalog system has two parts:

- **Backend (the pipeline).** Pure-Python, lives locally at `MOSAIC_development/MOSAIC_catalog/`, run with `python3 build_catalog.py`. It reads the **Excel registry** (single source of truth, ~60 records, filled by centre focal points) and emits two artifacts every run:
  - **A — STAC catalog tree** (`stac/`): 74 JSON files (1 catalog + 13 collections + 60 items). Internal hrefs are **relative**, so the tree is portable and serves from any static-host root.
  - **B — `datasets.json`**: the flat data file the website consumes.
- **Frontend (the website).** `AoW2-MFL-CGIAR-Science-Program/mfl-living-landscapes-frontend` — Astro 4 static site, live, auto-deploys to GitHub Pages on push to `main`. It **imports `datasets.json` at build time** (`loadDatasets.ts: import rawDatasets from '../../data/datasets.json'`) — there is no runtime fetch. So `datasets.json` must be a committed file in the frontend repo when Astro builds.

**Three problems to resolve:**

1. **Repo topology** — one repo (monorepo) or two (separate)?
2. **The STAC 404.** The `stac/` tree is published nowhere. The website's "View STAC metadata (JSON)" links (field `metadata_url`, e.g. `stac/collections/CIV-NZ/items/MFL-2026-044.json`) therefore 404.
3. **The `datasets.json` hand-off.** Today the pipeline writes it via a hardcoded sibling path directly into the frontend working copy (`build_catalog.py` lines 33–40). That path breaks once the backend is its own repo.

**Constraints.** npm is blocked in Lizeth's local environment (the backend is pure Python, so unaffected; GitHub Actions runners have npm, so the frontend's CI is fine). Public CGIAR org repos — CI must be realistic and low-maintenance. Lizeth coordinates at ~40–50% time and is not the sole producer; the bar is "functional, not perfect."

---

## Options considered

### Option A — Separate repos (RECOMMENDED)
Backend pipeline + STAC in `MOSAIC_catalog`; frontend stays in its own repo. Each repo has its own GitHub Pages and its own deploy cadence.

- **+** Clean ownership: a future data engineer or focal point can own the backend without touching the live website; concerns stay legible.
- **+** Reinforces MOSAIC's "network of addressable hubs" framing — the data endpoint (STAC) is a separate, citable service from the human UI.
- **+** Matches Lizeth's existing folder rules (`MOSAIC_catalog` and `MOSAIC_frontend` are already separate). Zero conceptual migration.
- **−** `datasets.json` must travel from backend to frontend (one hand-off to wire — addressed below).

### Option B — Monorepo
Move everything into the existing frontend repo; leave `MOSAIC_catalog` empty.

- **+** No cross-repo hand-off; one place.
- **−** Collapses two skill domains (Python pipeline, JS site) and two release cadences into one bucket; a backend edit can break the public deploy.
- **−** Contradicts the folder rules and the "addressable hubs" framing; harder to hand the backend to someone else.
- **−** Wastes the already-created `MOSAIC_catalog` repo.

---

## Decision

**Adopt Option A — two separate repos.** Populate `MOSAIC_catalog` with the backend (pipeline + spec + STAC), and have that repo **publish its own GitHub Pages serving the `stac/` tree (and `datasets.json`) as a stable, addressable static endpoint.** The frontend repo stays as-is.

The whole team (product, geospatial-engineering, metadata-standards, frontend) converged on this independently.

### Resolutions to the three problems

1. **Topology:** separate repos (above).

2. **STAC 404 — fix it by publishing STAC on the catalog's own Pages and making `metadata_url` absolute.**
   Canonical endpoint:
   `https://aow2-mfl-cgiar-science-program.github.io/MOSAIC_catalog/stac/catalog.json`
   The pipeline emits `metadata_url` as an **absolute URL** to that endpoint, e.g.
   `https://aow2-mfl-cgiar-science-program.github.io/MOSAIC_catalog/stac/collections/CIV-NZ/items/MFL-2026-044.json`
   This (a) makes the link resolve and (b) makes every item globally citable so the CDH and others can dereference MOSAIC collections directly. Keep the STAC tree's **internal** links relative (portable); publish an absolute `self` link on each object that matches its `metadata_url`.

3. **`datasets.json` flow — keep it a file, not a live dependency. Manual copy now; automatable later.**
   - Chosen: the catalog pipeline writes `datasets.json` into `MOSAIC_catalog`; Lizeth copies that file into the frontend repo and commits it (status quo boundary, minus the broken hardcoded path).
   - Rejected: a cross-repo PR bot (needs a PAT/GitHub-App secret that can rot — token expiry, org SSO, scope creep — net new standing machinery for a part-time owner). Rejected: build-time `fetch` of `datasets.json` (forces rewriting `loadDatasets.ts` from static import to async fetch, makes every frontend build depend on the catalog Pages being live, and breaks offline builds). Rejected: git submodule (confusing for a part-time owner).
   - Because CI **also publishes `datasets.json` on the catalog's Pages**, upgrading to a PR bot or fetch later is non-breaking — the data is already addressable.

### Reconciled tension
The product view favored automating the hand-off so it "never becomes a chore"; the engineering and frontend views favored the manual copy because the PR-bot/fetch paths *add* maintenance (secret rotation, coupled deploys, lost offline builds) for a low regeneration cadence. They share the goal — minimize ongoing burden. On that shared criterion the manual copy wins **for now** (zero secrets, one diffable command, infrequent), with CI-published `datasets.json` keeping the automated path open for when a dedicated data engineer owns the backend.

---

## Consequences

**Positive**
- Backend and frontend evolve and deploy independently; the live site is unaffected by backend work.
- MOSAIC gains a stable, citable STAC endpoint — the first concrete "addressable hub" surface for CDH cross-linking.
- The STAC 404 is fixed.
- Backend can be handed off without website access.

**Costs / risks**
- **Manual `datasets.json` copy** on each regeneration. Cheap because regen cadence is low; revisit if it ever becomes frequent.
- **URL stability depends on the exact repo name `MOSAIC_catalog`** (case-sensitive in the Pages path). A rename or case change silently breaks every absolute `metadata_url`, `self` link, and future CDH link. Mitigation: freeze the repo name as an API contract; optionally front it later with a custom domain (e.g. `catalog.mosaic.cgiar.org`) so the citable URL never depends on the `github.io` path.
- **One small pipeline change and one small frontend change** are required (below).

**Required code changes (small; implemented as a follow-up, not in this ADR)**
- `build_catalog.py` (~lines 33–40): stop writing `datasets.json` into the frontend sibling path; write it **inside `MOSAIC_catalog`** (next to `stac/`). `frontend_build.py` already takes `out_path` as a parameter — no change there.
- Pipeline: emit `metadata_url` (and each STAC object's `self` link) as the **absolute** catalog-Pages URL.
- Frontend `frontend/src/pages/catalogue/[id].astro` (line 78): the link is currently `href={`${base}/${dataset.metadata_url}`}`. With an absolute `metadata_url` this double-prefixes. Change to `href={dataset.metadata_url}` directly, keeping `target="_blank" rel="noopener noreferrer"` (off-site JSON endpoint). No other frontend change; the deploy workflow is untouched and offline builds are preserved.

---

## Migration plan (PLAN ONLY — do not execute)

> Run from `MOSAIC_development/MOSAIC_catalog/`. Replace `<ORG>` with `AoW2-MFL-CGIAR-Science-Program`. None of this is run as part of this ADR.

**Step 0 — Make the small code changes first** (so the first commit is already correct):
- Repoint `FRONTEND_DATASETS` in `build_catalog.py` to write `datasets.json` inside `MOSAIC_catalog` (e.g. `HERE / "datasets.json"`).
- Emit absolute `metadata_url` / `self` links from the pipeline.
- Re-run `python3 build_catalog.py` locally; confirm `stac/` + `datasets.json` regenerate and validation passes.

**Step 1 — Initialize the backend repo and push.**
```bash
git init -b main
# .gitignore: __pycache__/, *.pyc, .DS_Store
git add build_catalog.py mosaic_pipeline/ spec/ stac/ datasets.json README.md docs/ \
        catalog/MFL_Dataset_Registry.xlsx MOSAIC_CDH_Interoperability_STAC_Assessment_202606.md
git commit -m "MOSAIC catalog pipeline: registry -> STAC + datasets.json"
git remote add origin https://github.com/<ORG>/MOSAIC_catalog.git
git push -u origin main
```
*(Commit the Excel registry into the repo at `catalog/MFL_Dataset_Registry.xlsx` so the build is self-contained and CI can run it. At ~60 rows a binary file in git is fine.)*

**Step 2 — Add the catalog's Pages workflow** `.github/workflows/build-and-pages.yml` (pure Python, no npm):
```yaml
name: Build and publish STAC catalog
on:
  push: { branches: [main] }
  workflow_dispatch:
permissions: { contents: read, pages: write, id-token: write }
concurrency: { group: pages, cancel-in-progress: false }
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install openpyxl
      - run: python3 build_catalog.py        # regenerates stac/ + datasets.json from the committed registry
      - run: cp datasets.json stac/datasets.json   # publish datasets.json alongside the STAC tree
      - uses: actions/upload-pages-artifact@v3
        with: { path: stac }
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: { name: github-pages }
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

**Step 3 — Enable Pages** on `MOSAIC_catalog` (Settings → Pages → Source: GitHub Actions). After the first run, verify:
- `https://aow2-mfl-cgiar-science-program.github.io/MOSAIC_catalog/stac/catalog.json` resolves.
- A sample item URL (matching the new `metadata_url`) resolves.

**Step 4 — Fix the frontend link.** In the frontend repo, edit `frontend/src/pages/catalogue/[id].astro` line 78: `href={dataset.metadata_url}` (drop `${base}/`). Commit; the existing deploy workflow ships it.

**Step 5 — Sync `datasets.json` into the frontend (the routine hand-off).** After each regeneration:
```bash
cp MOSAIC_catalog/datasets.json \
   MOSAIC_frontend/frontend/data/datasets.json
# in the frontend repo:
git add frontend/data/datasets.json
git commit -m "Update datasets.json from MOSAIC catalog regeneration"
git push          # triggers the frontend Pages deploy
```

**Step 6 — Verify end to end.** Open a dataset detail page on the live site; confirm "View STAC metadata (JSON)" opens the catalog Pages item (no 404, no double-prefix).

---

## Open decisions for Lizeth
1. **Excel home:** commit the registry into `MOSAIC_catalog` (recommended — self-contained, CI-buildable, diffable), or keep it on OneDrive and run the pipeline locally only? Affects whether Step 2's CI can rebuild on its own.
2. **`datasets.json` hand-off:** confirm manual copy (Step 5) for now, accepting the PR-bot/fetch upgrade is available later. Confirm you (not a bot) own this step in 2026.
3. **URL durability:** accept the `github.io/MOSAIC_catalog/...` path as the canonical endpoint now, or reserve a custom domain (e.g. `catalog.mosaic.cgiar.org`) before the CDH hardcodes any MOSAIC URLs?
4. **Repo name is frozen** as an API contract — confirm `MOSAIC_catalog` (exact case) is final.
