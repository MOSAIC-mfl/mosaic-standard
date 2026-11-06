# ADR-0006: An access point states its data kind and its access method separately

- Status: proposed (2026-10-30)
- Amended by [ADR-0009](0009-v02-on-the-cdh-core.md) (2026-11-05): `method` is `data[].access_method`, `url` is `data[].locations[].url`; detail blocks become `structures[]`.

## Context

The first draft had one `kind` list that mixed data types (raster, vector…) with ways of access
(service, landing_page). Migrating schema 1 showed the problem: most records link to a page at the
source, so `kind: landing_page` would lose the fact that the data is vector or raster. That is the
"data type" facet users filter on.

## Decision

Each access point has two fields, both part of the minimum:

- `kind`: the data behind the point. One of raster, vector, tabular, document, mixed, other.
- `method`: how the point is used. One of download, landing_page, service, request.

A detail block must match the point: `raster`/`vector`/`tabular`/`document` need the same `kind`,
and `service` needs `method: service`. An Earth Engine asset is, for example,
`kind: raster, method: service`.
