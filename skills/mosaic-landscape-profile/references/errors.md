# Validator messages

`validate.py` prints each message of the standard's validator with what it means and how to fix it.
This table is the same list (`EXPLAIN` in `scripts/validate.py`; a test keeps them in step).
The message pattern is a regular expression matched against the validator's text.

| Message contains | Means | Fix |
|---|---|---|
| `is not one of the roots` | data.default_root names a root that data.roots does not define. | Use one of the names under data.roots, or add that root. |
| `unknown root` | A data route sends files to a root that does not exist. | Fix the route's 'root' to a name under data.roots. |
| `layer id '.*' used \d+ times` | Two map layers have the same id. | Rename one of them (ids must be unique across the base map, the story and the overlays). |
| `unknown source '` | A map layer uses a source that is not declared. | Add the source under map.sources (or the overlay's sources), or fix the layer's 'source'. |
| `rail id '.*' used \d+ times` | Two layers, toggles or panels in the side list share an id. | Give each one its own id. |
| `group '.*' is not in groups` | A layer belongs to a group that is not in the list of groups. | Add the group to 'groups' (in the order of the side list) or fix the layer's group. |
| `is not in sources.yaml` | A layer points to a source entry (source_ref) that sources.yaml does not have. | Add an entry with that id to sources.yaml (source, licence, citation), or fix source_ref. |
| `catalogue record .* does not exist` | A layer links a catalogue record that does not exist. | Check the id (mosaic:MFL-YYYY-NNN) or set record: null until the dataset is registered. |
| `is not in map.layers` | Something names a base map layer that does not exist. | Use the id of a layer under map.layers (e.g. 'labels-start' to draw an overlay under the labels). |
| `is not an overlay` | The story or a study card names a layer that is not in the overlays. | Use the id of one of the overlays, or remove the reference. |
| `is not in story.map.highlights` | A chapter asks to show a highlight the story does not define. | Add it under story.map.highlights or remove it from the chapter's 'show'. |
| `is not a panel` | A study card opens a panel that does not exist. | Use the id of a panel or remove open_panel. |
| `is not in the story or base map layers` | story.map.focus names layers that do not exist. | Add those layers to story.map.layers or fix the ids. |
| `must be relative, without '\.\.'` | A data path is absolute or leaves the data folder. | Write paths relative to the data root, e.g. tiles/landcover_2020.pmtiles. |
| `!= folder` | profile.yaml says a different landscape than its folder. | Set 'landscape' to the folder name (the landscape code). |
| `not a landscape of vocab/landscapes.json` | The folder is not a landscape code of the standard. | Use an existing code; a new landscape is added to mosaic-standard first (case E). |
| `section id '.*' used` | Two sections of the page share an id. | Give each section its own id. |
| `cannot read\|not a YAML mapping` | A file is not valid YAML (indentation, a missing quote or colon). | Open the file at the line given and fix the syntax; quote texts that contain ': ' or start with special characters. |
| `is not a core renderer` | The layer uses a kind the website does not have yet. | Use a core kind (references/modules.md) or ask the developers for a new module. |
| `is a required property` | A required field is missing. | Add the field named in the message (references/modules.md lists what each block needs). |
| `Additional properties are not allowed` | A field name is not known (often a typo). | Fix the spelling or remove the field. |
| `does not match '\^https://` | A data root is not an https:// address ending with '/'. | Write the root as https://…/ (with the final slash). |
| `no 'verified' list` | A published study card has no 'verified' list. | Allowed when the finding cites its pages; otherwise add verified: [{claim, where}]. |
| `explore card states no claims` | An explore card has a finding. | Keep it a question; the text may only describe, not claim results. |

## Other situations

| Situation | Fix |
|---|---|
| `No workspace yet: run scripts/setup.py first` | run `setup.py` |
| `The validator did not run` | `setup.py` again (it installs the tool); check Python 3.11+ |
| `is not a catalogue checkout (no records/ folder)` | `--catalog` points to the wrong folder |
| `new_profile.py` exit code 3 | the code is not a landscape of the standard: recipes.md, case E |
| `new_profile.py` exit code 4 | the profile exists: edit it (case D), or `--force` to start again |
| A warning `unknown kind` / `is not a core renderer` | the website does not draw it yet: use a core kind or request a module |
| TODO placeholders left | fill them with the person's texts; `--allow-todo` only for drafts |
| The pull request's Validate check fails but `validate.py` passed | run `setup.py` (your standard may be older than the one CI uses) and validate again |
