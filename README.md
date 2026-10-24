# FanBB2333.github.io

L1ght's open-source shelf at https://fanbb2333.github.io/: a static, hand-drawn page that lists the projects that have shipped. Research code, forks, coursework and work in progress stay off it.

The style follows the course notebook (`~/repos/poly-cources/home`): paper / chalkboard colors, Kalam + Caveat + Newsreader, and pen outlines drawn by `assets/site.js`.

## Files

| File | What it is |
| --- | --- |
| `projects.json` | The list. Sections (shelves) and, per project, the pitch, install command, platform and extra links. Only what is here appears on the page. |
| `stats.json` | Numbers from GitHub / PyPI: stars, language, last push, latest version. Written by `build.py --fetch`; the committed copy is what the CI build falls back to when GitHub cannot be reached. |
| `template.html` | Page skeleton with `{{PLACEHOLDERS}}`. |
| `build.py` | Renders `index.html` (Python standard library only). |
| `assets/` | `style.css`, `site.js`, `favicon.svg`, `og.png` (social preview), fonts. |
| `.github/workflows/pages.yml` | Builds the page and publishes it to GitHub Pages. |

## Edit the list

1. Change `projects.json`. A project needs `repo` and `pitch`; optional: `install` (`{"cmd": "..."}` for a copyable command, or `{"label": "...", "url": "..."}` for a store / download link), `platform`, `links`, `pypi` (version comes from PyPI instead of GitHub releases), `releases: false` (no version stamp), `featured` (pencil shading under the card), `name`, `language`, `stamp`.
2. `python3 build.py --fetch` and open `index.html` through a local server: `python3 -m http.server 8080`, then http://localhost:8080/. `index.html` is build output and stays out of git.
3. Commit and push to `main`.

## Deploy

Pushing to `main` runs `.github/workflows/pages.yml`: it copies `assets/` into `_site/`, runs `build.py --fetch --out _site` with the workflow's `GITHUB_TOKEN`, and publishes `_site/` with `actions/deploy-pages` (Settings → Pages → Source: GitHub Actions). If GitHub or PyPI cannot be reached, the page is built with the numbers in `stats.json`.

- The same workflow runs once a day on a schedule, so versions, "updated" dates and the fallback star counts stay current without a push. It can also be started by hand from the Actions tab. GitHub pauses scheduled workflows after 60 days without activity in the repository; re-enable it from the Actions tab if that happens.
- Star counts are live: on each visit `assets/site.js` reads https://api.github.com/users/FanBB2333/repos (one public request, no token) and updates every card and the total. If that fails or the visitor hits GitHub's limit of 60 requests an hour, the numbers baked into the page stay.

## Fonts

Self-hosted Latin subsets, SIL OFL 1.1; see `assets/fonts/LICENSE.md`.
