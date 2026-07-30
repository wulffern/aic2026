# Book-style site prototype

A prototype of the course site as a *book*: chapter list in a sidebar,
built-in search, previous/next navigation, responsive on phone and
desktop. Built on [just-the-docs](https://just-the-docs.com), which is
plain Jekyll and works on GitHub Pages.

**This directory is a local prototype - nothing here is deployed.**

## Preview locally

```sh
make jbook        # generates chapters + serves http://localhost:3003
```

`py/mkbooksite.py` converts the generated posts in `docs/_posts/` into
ordered pages under `chapters/` (order = the FILES list in the root
Makefile) and copies `docs/assets` so figures, PDFs and slide links
work unchanged. `chapters/` and `assets/` are generated - only
`_config.yml`, `Gemfile`, `index.md` and `_includes/` are source.

## How launch would work (after approval)

The Docs workflow already builds the site with
`actions/jekyll-build-pages` (the GitHub Pages builder), which allows
any theme via `remote_theme`. Launch is:

1. In `_config.yml`: replace `theme: just-the-docs` with
   `remote_theme: just-the-docs/just-the-docs` and add
   `plugins: [jekyll-remote-theme, jekyll-seo-tag]` (both whitelisted).
2. Run `py/mkbooksite.py` in the `prepare` job after posts are
   generated (one extra line in the workflow).
3. Point the jekyll build step's `source` at `docs-book/` instead of
   `docs/`.

Old URLs keep working: chapters keep the same permalinks
(`/aic2026/mosfets` etc.) as the current posts, and assets stay at
`/aic2026/assets/...`.

## Open questions for review

- Keep the current landing page content, or the book cover style?
- just-the-docs' accent colors are configurable (`color_scheme`) - the
  default is a neutral light scheme with a dark toggle available.
- The old minima site stays in `docs/` until the switch is approved.
