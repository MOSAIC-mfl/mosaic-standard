# ADR-0007: Data classification is explicit in the record and inferred when the file can be read

- Status: accepted by Santiago Calderón (2026-10-30); to review with Lizeth Llanos
- Amended by [ADR-0009](0009-v02-on-the-cdh-core.md) (2026-11-05): geometry type is `data[].geometry_type`; "spatial or not" is no longer a field or a filter.

## Context

The website must filter by data type, geometry type (points, lines, polygons) and "spatial or
not". Only 11 of the 102 migrated records have a downloadable file. 50 link to a page at the
source, 40 are restricted or internal, and 1 has no access point. Inference alone would leave
about 90 records without values.

## Decision

- The classification lives in explicit fields: `data[].vector.geometry_type`,
  `data[].tabular.spatial` with `coordinate_columns` or `geometry_column`. They are recommended, not
  part of the minimum.
- `python -m mosaic_catalog infer` fills them from public downloadable files (Shapefile, GeoJSON,
  GeoPackage, CSV; raster later). It lists what it filled in `derived`, never overwrites a person's
  value, and reports conflicts.
- What cannot be inferred goes to `review/classification_gaps.csv`, with the person to ask.
- An absent value is shown as "not specified" by the API. No "unknown" values are written.
