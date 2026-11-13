# The `mosaic-landscape-profile` skill

A Claude Code skill (repository `mosaic-skills`, folder `skills/mosaic-landscape-profile/`) that lets someone with no programming create or change a landscape profile — the page a living
landscape gets under "Map visualization" — and open the pull request to the catalogue. The person
talks with Claude in any language; everything written to the repositories is in English.

## What it does

| Step | Script | Result |
|---|---|---|
| Prepare | `setup.py` | uses (or clones) mosaic-standard and the catalogue next to the skills checkout, installs the validator, saves the paths in `~/.mosaic/workspace.json`; `--web` also the website and the API |
| Start a profile | `new_profile.py --code <CODE> [--from KEN-LVB]` | `landscapes/<CODE>/` from the templates (default page, or a map explorer like an existing one) |
| Understand the data | `inventory.py`, `check_data.py` | what files the person has, whether they are reachable and in a format the explorer reads |
| Change a profile | `edit_profile.py` | add / remove layers, chapters, studies without hand-editing YAML |
| Check | `validate.py` | the standard's validator on the profile, explained in plain words |
| Look at it | `preview.py`; with a website change `web_preview.py` | a local preview of the page |
| Website change (rare) | `web_check.py`, `web_preview.py` | only when the profile needs a module the website does not have (`references/web-modules.md`) |
| Send | `prepare_pr.py [--depends <PR URL>]` | title, body and the exact git / gh commands for the pull request to `main` |

The rules Claude follows are in `SKILL.md`; the modules a profile can use in `references/modules.md`;
worked cases (a new explorer, a change to an existing one, a new landscape, …) in
`references/recipes.md`; errors in `references/errors.md`.

## Install

Clone `mosaic-skills` next to the other repositories (e.g. `D:\Code\Mosaic\mosaic-skills`) and link the
skill once into Claude Code's personal skills, from that checkout:

```sh
ln -s "$PWD/skills/mosaic-landscape-profile" ~/.claude/skills/        # macOS / Linux
```
```powershell
New-Item -ItemType Junction -Path $HOME\.claude\skills\mosaic-landscape-profile -Target skills\mosaic-landscape-profile   # Windows
```

Needs git, Python 3.10+, the GitHub CLI (`gh auth login`); Node.js 22.23.4+ only for a website change.

## Demo (10 minutes)

1. Open Claude Code in any folder and ask: *"Quiero ver qué perfiles de paisaje hay y crear uno
   para Fatick (Senegal) como el de Ucayali, solo con el mapa base y los límites."*
2. Claude runs `setup.py` (first time), then `new_profile.py --code SEN-FK --from PER-PCL`, explains
   what it kept and what it left as TODO, and runs `validate.py`.
3. Ask for a change in plain words (*"quita la capa de incendios"*, *"añade un capítulo a la
   historia sobre el agua"*); Claude edits with `edit_profile.py` and validates again.
4. `preview.py` shows the page; nothing has been pushed.
5. `prepare_pr.py` writes the pull request; show the text and stop before pushing.

## Tests

In the `mosaic-skills` checkout (they find `../mosaic-standard`, or `MOSAIC_STANDARD`; `MOSAIC_CATALOG`
for the catalogue tests):

```sh
pytest -q skills/mosaic-landscape-profile/tests
```
