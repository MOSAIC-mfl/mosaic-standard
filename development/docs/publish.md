# Publishing

Everything is on GitHub Pages for now; each repository publishes itself with GitHub Actions
(Settings → Pages → Source: GitHub Actions).

| Repository | Workflow | Runs on | Publishes |
|---|---|---|---|
| mosaic-standard | `Check` | pull requests, pushes | nothing (lint, tests, generated files, the catalogue validated against the standard) |
| catalog | `Validate`, `Publish` | pull requests; push to `main` | `catalog/`: the built catalogue + the frozen STAC at `/catalog/stac/` |
| mosaic-api | `Check and publish` | push to `main`, daily 05:17 UTC, by hand, `repository_dispatch: catalog-updated` | `mosaic-api/`: clones the catalogue (`main`) and the standard (`main`), builds, harvests MOSAIC + CDH, exports the static API |
| website | `Deploy to GitHub Pages`, `Lint frontend` | push to `main` (deploy); pull requests (lint) | `website/`, built with `PUBLIC_MOSAIC_API_MODE=static` and the Pages address of the API |

A change to the catalogue reaches the website through the API: the API's daily run (or a run by
hand) picks it up; the website needs no rebuild.

## Order of a release that touches several repositories

1. **mosaic-standard** (`main`): the catalogue and the API build with it.
2. **catalog** (pull request to `main`, reviewed by Lizeth): records and profiles valid against the
   new standard.
3. **mosaic-api** (`main`): run "Check and publish" by hand if nothing else triggers it.
4. **website** (pull request to `main`): deploys by itself.

Before merging the website, check the new API on Pages: `v1/sources.json` (harvest date),
`v1/records.json` (fields the website uses), `v1/landscapes.json`.

## After a release

The pages listed in [run-locally.md](run-locally.md#pages-to-look-at-after-a-change), on
`https://mosaic-mfl.github.io/website/`, in light and dark mode and on a phone.

## Rolling back

- website: revert the merge on `main` (a pull request) or run the deploy workflow on the previous
  commit; the API keeps working with either.
- catalog: revert the merge; `Publish` republishes. Tag `main` before a large merge
  (`git tag pre-<topic>-<date>`).
- mosaic-api: revert and run the workflow; the previous export is replaced.

## Moving the API to a server

The live API is the same code (`python -m mosaic_api serve`). On the server: the configuration
with https locations (`config/mosaic-api.published.yaml`), a scheduled harvest, and
`http.cors_origins` with `https://mosaic-mfl.github.io`. Then in the website's
`.github/workflows/deploy-pages.yml`:

```yaml
PUBLIC_MOSAIC_API_MODE: live
PUBLIC_MOSAIC_API_URL: https://<the server>
```

No website code changes. The static export can stay published as a fallback.
