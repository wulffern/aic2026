# Build & Workflow Plan

Measured baseline (run 30484788053, 2026-07-29):

| | |
|---|---|
| **Docs** workflow total | 6m50s wall, ~22 runner-minutes |
| `prepare` | 2m51 = 57s apt + 91s `make prepare-docs` + 10s artifact upload |
| each of 6 TeX-container jobs | **78s container init + ~22s apt** for 11–53s of real work |
| `jekyll_preview` + `deploy` | 57s |
| **TikZ** workflow total | 2m46 = 78s init + 11s apt + 61s serial build of 76 figures |
| local `make texfiles-parallel` | 43s, always rebuilds all 30 lectures |

The dominant CI cost is not the build — it is pulling
`texlive/texlive:TL2022-historic` seven times per push and re-running
`apt-get install` inside each container: ~11 of the 22 runner-minutes.

## 1. Workflow speed

- **A. Use our own image from GHCR.** `docker/Dockerfile` already installs
  exactly what every job apt-gets, but no active workflow uses it. Publish to
  `ghcr.io/wulffern/aic` (co-located with the runners, so it pulls faster than
  docker.io) via a workflow triggered on changes to `docker/Dockerfile` /
  `requirements-ci.txt`, and set it as `container:` in `matrix_build.yaml` and
  `tikz.yaml`. Deletes all seven apt steps.
- **B. Slim the TeX base** (later). The 78s init is full TeX Live (~5.6 GB).
  A `scheme-medium` image plus the explicit package list kaobook and the
  chapters need should pull in ~15–20s. Needs a one-time package audit; do
  after A is stable.
- **C. Merge `epub` into `book_pdf`.** The epub job pays ~100s overhead for
  11s of work.
- **D. Parallelize `make tikz` / `tikz-check` / `tikz-preview`** — serial
  loops over 76 figures; `xargs -P 4` takes the build from 61s to ~20s.
- **E. Narrow the Docs path filter.** `'**.md'` fires the whole 7-minute
  pipeline when a plan file changes. Scope to what the build reads.
  (TikZ's lack of a filter is deliberate and documented — keep.)
- **F. Bump deprecated actions** (Node 20 warnings on checkout/setup-python/
  cache/upload-artifact).

## 2. Build optimization

- **G. Real Makefile dependencies.** All targets are phony;
  `texfiles-parallel` re-runs 30 pandoc invocations (43s) for a one-lecture
  edit. Stamp-based pattern rules (`.build/%.post.stamp` etc., since the post
  filename embeds the frontmatter date) make it ~1.5s.
- **H. Cache standalone PDFs in CI**, keyed on lecture + referenced media +
  templates, once G exists. A typical push rebuilds 1 of 30 chapters.
- **I. Fewer pdflatex passes.** `standalone` always runs 3; `latexmk`
  converges in 1–2 for index-free chapters.
- **J. Cache the `Bibtex` parse** — 612 entries re-parsed per `Lecture`
  object, 60× per full build.
- **K. Trim the `prepared-sources` artifact** — `pdf/media` ships to six
  downloaders; only the TeX jobs need it.
- **L. Sweep unreferenced media** — 442 of 807 files in `media/` (152 MB) are
  referenced by no lecture; `.git` is 199 MB. One cleanup commit cuts
  checkout cost everywhere. (Check for references from docs/, examples/,
  jupyter/ before deleting.)

## 3. Lecture note correctness

Automated checks are clean today: 0 broken image refs, 0 citations missing
from `aic.bib`, 0 unbalanced `$$`, 0 duplicate/undefined footnotes.

- **N. Deckset table directives publish verbatim.** The filter regex
  `\[\.table  *\]` never matches the real syntax `[.table: margin(8)]` /
  `[.table-separator: ...]`; 12 occurrences from `lr0_logic.md` render as
  literal text on the site and in the book (`pdf/cmos_logic.latex:97`). Fix
  with a line-anchored directive filter; dedupe the thrice-copied filter dict
  while there.
- **O. Five verified TikZ redraws not yet referenced:** `l00_diode.md:888`
  (`vd.pdf`), `l00_diode.md:934` (`l3_ptat.pdf`), `l03_refbias.md:258`
  (`vd.svg`), `l03_refbias.md:481` (`l3_bgsim.pdf`), `l03_refbias.md:502`
  (`l3_bgsimtfs.pdf`). Switch only after the point-by-point verification in
  `tikz_translation_plan.md`.
- **P. The three source/figure disagreements in
  `interactive_examples_plan.md` §1** (e.g. `ex/iir.py` pole at z=1 vs the
  z=0.25 the prose discusses) are real technical errors in figures the text
  reads. They need the author's call on intent.
- **Q. Eleven lectures are never built** (`l12_chinf`, `l00_need_to_know`,
  `lr0_tut2`, `l04_mac`, `g0*`, `lp_radio_guest`, `exam`, `maxwell`,
  `project_scratch`) so they rot invisibly. Each should join `FILES` or move
  aside. Author's call.
- **R. `make check` + fast CI job** running the mechanical checks above in
  <2s with no TeX, so N-class bugs fail the push instead of shipping.
- **S. Physics/maths review** can't be automated; track per-lecture the way
  `tikz_translation_plan.md` does, starting with the derivation-heavy
  `lr0_mosfet`, `l03_refbias`, `l05_sc`, `l06_adc`, `l08_pll`.

## Execution order

1. **N + R** — cheap, stops a visible bug class.
2. **A + C + D + E + F** — roughly halves CI time, no build-logic risk.
3. **G + J (+ I, K)** — incremental local builds.
4. **H** — CI-side incrementality, once G is proven.
5. **B** — after the rest is stable.
6. **O, P, Q, S** — content items, author-gated.
