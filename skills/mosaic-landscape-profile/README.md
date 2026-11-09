# mosaic-landscape-profile (Claude Code skill)

A skill for [Claude Code](https://claude.com/claude-code) that lets anyone, with no programming,
create or change a MOSAIC landscape profile and open the pull request to the catalogue. The person
talks with Claude in any language; everything written to the repositories is in English.

What it covers: a profile like an existing one (KEN-LVB, PER-PCL), the same with fewer or changed
layers, a new page with or without a map explorer, changes to an existing profile, converting an
explorer repository, data hosting checks, validation with explanations, an HTML preview and the
pull request text.

## Install

Requirements: git, Python 3.11+, Claude Code, and the GitHub CLI (`gh auth login`) for pull requests.

```sh
git clone https://github.com/MOSAIC-mfl/mosaic-standard.git ~/mosaic/mosaic-standard
# make the skill available to Claude Code in every project (macOS/Linux):
mkdir -p ~/.claude/skills && ln -s ~/mosaic/mosaic-standard/skills/mosaic-landscape-profile ~/.claude/skills/
# Windows (PowerShell): copy the folder instead
#   Copy-Item -Recurse $HOME\mosaic\mosaic-standard\skills\mosaic-landscape-profile $HOME\.claude\skills\
```

Then open Claude Code anywhere and ask, for example: *"I want a landscape page for Fatick, Senegal,
like the Ucayali one"* or *"Quita la capa de incendios del perfil de Lake Victoria"*. Claude runs
`scripts/setup.py` first (it clones the catalogue next to the standard and installs the validator).

## Contents

```
SKILL.md                 the workflow Claude follows
scripts/
  setup.py               workspace: clones/updates the standard and the catalogue, installs the validator
  new_profile.py         a new profile from a template or like an existing one (TODO placeholders + checklist)
  inventory.py           reads an explorer repository (read only) and suggests modules
  check_data.py          HTTPS, CORS and byte ranges of every data file
  edit_profile.py        list, remove-overlay (with every reference), set-root
  validate.py            the standard's validator, each problem explained
  preview.py             one-page HTML review
  prepare_pr.py          pull request title, body and commands
templates/               the files new_profile.py starts from
references/              modules, data hosting, recipes, errors, glossary
```

The scripts run on their own too (`python scripts/<name>.py --help`). Tests:
`tests/test_skill_landscape_profile.py` in this repository.
