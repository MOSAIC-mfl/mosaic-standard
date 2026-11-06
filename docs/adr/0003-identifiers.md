# ADR-0003: Keep MFL-YYYY-NNN ids, add an optional slug, namespace ids in the API

- Status: proposed (2026-10-30)
- Amended by [ADR-0009](0009-v02-on-the-cdh-core.md) (2026-11-05): ids stay MFL-YYYY-NNN; the optional slug is dropped (unused).

## Options

| | MFL-YYYY-NNN | Readable slug |
|---|---|---|
| Stable when the title or content changes | yes | no: the slug goes stale or has to change |
| Already cited and linked (pages, STAC, e-mails, Excel) | yes | 102 redirects needed |
| Readable | no | yes |
| Collisions across federated catalogues | unlikely | likely |

## Decision

- `id` stays `MFL-YYYY-NNN`: permanent, never reused, never changed.
- `slug` is optional and only used for readable URLs; it may change.
- The API addresses every record as `<catalogue>:<id>` (`mosaic:MFL-2026-079`,
  `cdh:esa-worldcover-2021`), so ids from different catalogues never clash and MOSAIC never renames
  another catalogue's ids.
