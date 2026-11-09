# Glossary

Words used in this skill, explained for someone who does not program. Use them to explain to the
person, in their language.

| Word | Meaning |
|---|---|
| **Landscape** | One of MOSAIC's living landscapes, with a code such as `KEN-LVB` (country + place). The list is in mosaic-standard, `vocab/landscapes.json`. |
| **Profile** | The files that describe a landscape's page on the website: `landscapes/<CODE>/` in the catalogue. |
| **Catalogue** | The repository `MOSAIC-mfl/catalog`: dataset records (`records/`) and landscape profiles (`landscapes/`). |
| **Standard** | The repository `MOSAIC-mfl/mosaic-standard`: the rules (schemas, vocabularies), the validator and this skill. |
| **Section** | A block of the landscape page: the map explorer, the datasets list, the data status. |
| **Map explorer** | The interactive map of a profile: layers, time slider, clicks, story and study cards. |
| **Overlay / layer** | A map layer people choose in the side list (land cover, rainfall…). One is shown at a time. |
| **Base map** | What is always under the layers: imagery, terrain, boundary, place names. |
| **Toggle** | A switch in the side list that shows or hides part of the base map (place names, rivers). |
| **Panel** | A side panel with figures and a chart, opened from the side list or by a click. |
| **Group** | A heading of the side list (Climate, Land…). |
| **Legend** | The colours of a layer and what they mean. |
| **Click (inspect)** | What appears when someone clicks the map while a layer is shown. |
| **Module** | A piece of the website that draws one kind of thing (a kind of layer, of click, of chart). A profile chooses modules and configures them; it does not program them. |
| **Story** | Chapters of text that move the map as the reader scrolls. |
| **Study card** | A question with a finding from a published paper (verified against it), or an open question to explore. |
| **Data root** | The web address of a folder where data files are served. Paths in the profile are relative to it. |
| **PMTiles** | One file holding all the map tiles of a layer, read in small parts. |
| **COG (cloud-optimized GeoTIFF)** | A raster file the website can read in parts, used for the values of a click. |
| **CORS** | A server setting that lets the MOSAIC website read files from another site. |
| **Byte ranges** | The server can send part of a file. Large map files need it. |
| **Withheld** | A file the profile names but never requests, because its licence is not cleared. |
| **TODO** | A placeholder for a text or value still to be provided. The page would show it, so none can stay. |
| **Validator** | The program that checks a profile against the standard (`validate.py`). The pull request runs it too. |
| **Branch** | A separate line of changes in a repository. Work is done on a branch, never on `main`. |
| **Pull request (PR)** | The request to the MOSAIC team to review and add the changes of a branch. |
| **Fork** | Your own copy of a repository on GitHub, used to propose changes when you cannot write to the original. |
