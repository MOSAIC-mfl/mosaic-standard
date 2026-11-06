# How to register a dataset in the MOSAIC catalog

*A guide for MFL focal points and contributors — updated 2026-09-28.*

MOSAIC keeps one small, validated **record** per dataset. You don't upload the
data itself — MOSAIC is a coordination network, not a repository: the record
describes your dataset and points to where it lives. Once a record is merged,
the catalog republishes itself automatically: your dataset appears on the
[MOSAIC website](https://mosaic-mfl.github.io/website/catalogue/)
and gets a citable metadata URL in the [STAC endpoint](https://mosaic-mfl.github.io/catalog/stac/catalog.json)
within a few minutes.

## Before you start — have these facts ready

**Required:**
- Dataset title (short and descriptive)
- Living Landscape it covers — one of the 11 canonical landscapes, or
  *country-wide (NATIONAL)*, or *global (GLOBAL)*
- Country
- Contact person (name + CGIAR email)

**Strongly recommended** (these are the gaps that most reduce reusability today):
- A working **download or source URL** — "it's on our server" is not findable
- **Spatial resolution with units** ("30 m", "0.05°", "admin level 2")
- **Coordinate reference system** ("EPSG:4326")
- Temporal coverage ("2017–2025"), license ("CC BY 4.0"), file format(s)
- A description covering method, caveats and related datasets

## Way 1 — the submission form (recommended, no Git skills or commands needed)

1. Open the **[Register a new dataset](https://github.com/MOSAIC-mfl/catalog/issues/new?template=new_dataset.yml)**
   form (needs a free GitHub account — if you'd rather not create one, see Way 2).
2. Fill in what you know — only four fields are required; everything else can
   be completed later.
3. Submit. The MOSAIC team converts your submission into a validated record and
   tags you on the pull request to confirm the details.
4. On merge, the catalog republishes automatically — you'll receive the link.

## Way 2 — plain email (no GitHub account needed)

Send the facts from the checklist above — at minimum the four required ones
(title, living landscape, country, contact person) — to the MOSAIC coordinator
(**Lizeth Llanos, l.llanos@cgiar.org**), subject "MOSAIC dataset registration".
We create the record for you, confirm the details with you by email, and send
back the published link.

## Way 3 — edit the record yourself (if you're comfortable with GitHub)

Records live in [`records/`](../records/) — one YAML file per dataset, e.g.
`records/MFL-2026-001.yaml`. To add one: copy an existing record, name it with
the next free ID (`MFL-YYYY-NNN`), edit the fields, and open a pull request.
The field-by-field reference is [`spec/record_schema.md`](../spec/record_schema.md),
and [`records/README.md`](../records/README.md) has the rules. Every pull
request is validated automatically — the build fails with a precise message if
a value is out of vocabulary, so you can't break the catalog.

To **update or correct** an existing dataset, edit its file the same way (or
just open an issue describing the change and we'll do it).

## Way 4 — bulk import (many datasets at once)

If your centre has an inventory of datasets (a spreadsheet, an internal
catalog), don't type them one by one — send it to the MOSAIC coordinator
(**Lizeth Llanos, l.llanos@cgiar.org**) and we'll run a scripted import and
send the draft records back for your review.

## What happens after you submit

| Step | Who | What |
|---|---|---|
| 1. Submission | You | Form, pull request, or bulk file |
| 2. Record + review | MOSAIC team + you | We draft/validate the record; you confirm |
| 3. Merge | MOSAIC team | Record joins `records/` with a permanent ID |
| 4. Publication | Automatic (~2 min) | Website + STAC endpoint republish; your dataset gets a stable, citable metadata URL |

Records are never silently changed: every edit is a reviewed pull request, and
each dataset's full history is visible in Git.

## FAQ

**Do I upload the data files?** Not for now. Today the record points to where
the data lives (your repository, Dataverse, a drive link, a server); making the
*pointer* public is what matters, and the data's own access level (Open /
Internal / Restricted) is recorded honestly. In a later phase, the plan is to
make the open datasets themselves directly available through MOSAIC — datasets
that already have a home will keep being linked at their source.

**Access level rule — what does "Open" mean?** Open means anyone can obtain the
data without asking permission. So a record marked Open needs a public
`download_url`, and its licence must not say "contact data owner". The build
checks this for every record and stops with `ACCESS RULE FAILED` (exit code 3)
when an Open record breaks it. The message names the record and the fix:
add a public download_url or set access_level to Restricted or Internal.
Licences that limit use but let anyone download the data, such as
non-commercial terms, are fine with Open. When the owner later shares a public
link, the record goes back to Open with a normal edit.

**What if I don't know a field?** Leave it empty. An incomplete-but-honest
record is far more useful than nothing — the catalog flags gaps rather than
hiding them.

**Which landscape do I pick for a national dataset?** Pick
`NATIONAL — Country-wide coverage` and the country; the catalog automatically
files it under your country's landscape collection with a "national coverage"
label.

**Can a dataset be removed?** Yes — records can be retired via pull request;
their ID stays reserved so citations never break.
