# ADR-0008: One page per living landscape, written as a profile and validated like the records

- Status: proposed by Santiago Calderón (2026-11-03); to review with Lizeth Llanos

## Context

The deliverables ask for an automated profile page for every living landscape, and for the Lake
Victoria Basin Explorer (Andrés Aguilar) to become MOSAIC's first rich profile. More profiles will
follow: some like Lake Victoria with other themes, some with sections of their own. The explorer was
written as one JavaScript application with its configuration, content and code mixed, so a second
profile would have meant copying and editing it.

## Decision

- A profile is **content**, kept in this repository next to the records:
  `landscapes/<CODE>/profile.yaml` plus the configuration files its sections name. It is validated
  (`validate-landscapes`, schemas in `schema/landscape/`) and published by `build`
  (`dist/landscapes/`).
- Every landscape of the vocabulary gets a page. Without a profile, the default sections apply.
- A page is an ordered list of **sections**, each drawn by a website module named by its `kind`.
  A map explorer is one kind of section. Its layers are drawn by **renderers**, also by `kind`.
- What differs between profiles is configuration. Code is added only for a new kind of section,
  layer or click, as a module or a profile plugin on the website.
- Heavy data is never copied into MOSAIC: the profile says where each file is served.
- Each layer should become a catalogue record (`record:`); until the team assigns ids, the layer's
  source, licence and citation stay in `sources.yaml`.

## Consequences

- A new landscape page with standard sections needs no code. A new explorer like Lake Victoria needs
  an `explorer.yaml`.
- The profile can be reviewed in a pull request like a record, and broken references fail the
  check instead of the page.
- The website must know every `kind` a profile uses; unknown kinds are warnings here and skipped
  there, so an older website still opens a newer profile.
