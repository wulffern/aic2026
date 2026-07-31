# Archived media

Files that no lecture, script, Makefile target or docs page referenced as
of 2026-07-31. Moved here rather than deleted so they can be reviewed
before anything is lost.

Two groups, 446 files and 56 MB in total:

- **362 originals superseded by a TikZ redraw.** For each of these there
  is a `<name>_tikz.pdf` in `media/` that the lectures now use. Keeping
  the originals is still worth something: `tikz/STYLE.md` says to compare
  a redraw against the original point by point, and that is only possible
  while the original exists.
- **84 others**: old PNG versions of figures that later became PDFs,
  figures drawn but never referenced by a lecture, and per-lecture copies
  that were superseded by a top-level one (`media/l14/dff_setup_8.pdf`
  became `media/dff_setup_8_tikz.pdf`).

Nothing here is reachable from a build. Recovering one is `git mv` back.

The reference scan covered `lectures/*.md`, `docs/*.md`, `tikz/`, `py/`,
`ex/`, `jupyter/`, the Makefile and `pdf/*.py`, and treated a `.pdf` and
its `.svg` sibling as jointly referenced, because `py/lecture.py` copies
both whenever either is named.
