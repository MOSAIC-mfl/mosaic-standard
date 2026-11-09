# Recipes

All commands are run as `python SKILL_DIR/scripts/<script>.py …` after `setup.py`. After every
recipe: `validate.py`, `preview.py`, then the pull request (SKILL.md, step 8).

## A. The same as an existing profile, for another landscape

"I want for Senegal what Ucayali has."

1. `new_profile.py --code SEN-FK --like PER-PCL`
2. Read `work/SEN-FK/checklist.md` with the person. The structure (layers, legends, clicks) is the
   copy; **everything that describes data is TODO**: summary, explorer title and tagline, section
   title, data roots, each sources.yaml entry, credits.
3. The data for the new landscape must exist with the same structure (same file names, or change
   the paths). Ask who produces it. If it comes from the same pipeline (e.g. the MOSAIC climate
   pipeline), the files will have the same names.
4. Replace the base map files (boundary, mask, imagery, terrain) listed in the checklist.
5. Check each layer: legend classes and colours of the new source, texts that name the other
   landscape, `click.admin.units` for the new country (administrative level names), story and
   studies are not copied (they are about the other landscape).
6. Hosting (`set-root`, `check_data.py`), then fill in the TODOs with the person's texts.

## B. Like an existing profile, with changes

"Like Lake Victoria, but only rainfall, drought and land cover."

1. `edit_profile.py list --code KEN-LVB` to see the layer ids.
2. `new_profile.py --code KEN-LEI --like KEN-LVB --only precip,spi3,landcover`
3. As in A. To add a layer later: copy the overlay block of the most similar layer
   (`references/modules.md`), change id, title, files, legend; add its group to `groups` and its
   entry to `sources.yaml`.

## C. A new page

Without a map (only the catalogue's sections, with the landscape's own title and summary):

1. `new_profile.py --code TUN-NW --template default --title "…" --summary "…"`
2. Validate, preview, pull request. Done.

With a map explorer:

1. `new_profile.py --code COL-CUM --template explorer [--with-story] [--with-studies]`
2. The template has one placeholder layer and a minimal base map. For each layer of the person's
   data, choose the module (modules.md) and write the overlay; delete the placeholder.
3. If the person has an explorer repository, `inventory.py --source <repo> --code COL-CUM` first:
   it suggests module and click for each layer.

## D. Change an existing profile

- Remove a layer: `edit_profile.py remove-overlay --code KEN-LVB --id fire` (also its story
  references, study cards, sources entry, an empty group).
- Move the data: `edit_profile.py set-root …`, then `check_data.py`.
- Texts, colours, legends, add a layer: edit the YAML directly, then `validate.py`.
- Publish a draft: set `status: review` or `published` only when the MOSAIC team agrees.
- Pull request: `prepare_pr.py --code KEN-LVB --change "remove the fire layer"`.

Changes to KEN-LVB and PER-PCL alter pages converted from Andrés Aguilar's explorers: mention it in
the pull request.

## E. A landscape that is not in the standard yet

`new_profile.py` stops with exit code 3. The landscape codes, names, countries and bounding boxes are
in mosaic-standard (`vocab/landscapes.json`, boundaries in `boundaries/`); adding one is a decision
of the MOSAIC team. Open an issue in `MOSAIC-mfl/mosaic-standard` with:

- the proposed code (`ISO3-XXX`, e.g. `GHA-NR`), name, countries;
- the bounding box (west, south, east, north) or a boundary file and its licence;
- why it is a MOSAIC landscape (programme, partners).

When it is merged, run `setup.py` again (it updates the standard) and continue with A, B or C.

## Converting an existing explorer (like Lake Victoria or Ucayali)

1. `inventory.py --source <explorer repo> --code <CODE>` (reads only).
2. Start with B from the profile most like it (both existing explorers share most modules), or C.
3. Keep the author's texts as they are (story, studies, sources). Record `origin` (repository and
   commit) and `credits` in profile.yaml.
4. The explorer's data roots are its GitHub Pages and Hugging Face addresses.
