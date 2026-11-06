# ADR-0004: Records below the minimum are listed for review and published flagged

- Status: proposed (2026-10-30)

## Decision

- A record that fails the minimum is **incomplete**, not invalid. The build does not stop.
- The validator writes `review/minimum_gaps.csv` and `.md`: one row per record and missing field,
  with columns for a suggestion, the owner and the decision (complete / publish incomplete /
  withdraw).
- With `publication.include_incomplete: true` (the default), incomplete records are published with
  `status: incomplete` and their completeness score. With `false`, they are left out of the
  published catalogue but stay in `records/` and in the review list.
- A single record can be taken out with `mosaic.intake.status: withdrawn`.

## Why

Most current records lack keywords and a citation. Hiding them all would empty the catalogue, and
filling the gaps automatically would invent metadata.
