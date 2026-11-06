# ADR-0002: Licence as {spdx, url, text}; required, with text alone enough for the minimum

- Status: proposed (2026-10-30)
- Superseded by [ADR-0009](0009-v02-on-the-cdh-core.md) (2026-11-05): `license` is an SPDX expression (or `LicenseRef-…` with `license_text`), as in CDH.

## Context

Only 36 of the 102 schema-1 records hold a standard licence (CC BY 4.0, CC BY-SA 4.0, CC0). The
rest state source terms, a restriction, or "no licence stated". An SPDX-only field could not record
them without inventing a licence.

## Decision

`license` is required and is an object:

```yaml
license:
  spdx: null        # SPDX expression when it is a standard licence, e.g. CC-BY-4.0
  url: null         # link to the terms; recommended when spdx is null
  text: Dryad terms of use — licence to confirm with the authors
```

- **Minimum:** `spdx` or `text` is present.
- **Recommended:** a non-SPDX licence has a `url`, and one contact has the `licensor` role.

The SPDX URL can be derived from the id, so `url` is optional when `spdx` is set.

## Consequences

Every record states what is known about its licence. Records whose terms are unclear are complete
at the minimum, but they show a warning until someone adds the link to the terms.
