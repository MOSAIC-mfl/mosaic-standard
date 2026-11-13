# development/ — how the MOSAIC v0.2 pieces work together

Notes for whoever develops or maintains MOSAIC after the v0.2 rebuild (2026-10/11): how the
standard, the catalogue, the API and the website fit together, how to run them on your machine,
how they are published, and how to use the Claude Code skill that writes landscape profiles (the
skill itself lives in its own repository, `mosaic-skills`).

| | |
|---|---|
| [docs/overview.md](docs/overview.md) | The four repositories, the data flow, what changed in each and the decisions behind it |
| [docs/run-locally.md](docs/run-locally.md) | Run everything on your machine: the API static or live, the website against either |
| [docs/publish.md](docs/publish.md) | How each piece reaches GitHub Pages, the order of merges, checks after a release, how to roll back, moving the API to a server |
| [docs/landscape-profile-skill.md](docs/landscape-profile-skill.md) | The `mosaic-landscape-profile` skill (repository `mosaic-skills`): what it does, how to install it, how to demo it |

Nothing here is read by the validator or the build: this folder is documentation only.
