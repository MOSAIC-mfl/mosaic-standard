# ADR-0005: Access is explicit; public data needs a URL, non-public data needs a way to ask

- Status: proposed (2026-10-30)
- Amended by [ADR-0009](0009-v02-on-the-cdh-core.md) (2026-11-05): `internal` is now `non-public` (CDH / DCAT value); a public resource needs a location in `data[].locations`.

## Decision

- `access` (`public` | `restricted` | `internal`) is part of the minimum. An absent value never
  means public.
- `public`: at least one access point has a `url`.
- `restricted` / `internal`: an `access_note` saying how to obtain the data is required; a URL is
  optional.
- Each access point may carry its own `access` when it differs from the record. Example: public
  data with an internal Earth Engine copy.
