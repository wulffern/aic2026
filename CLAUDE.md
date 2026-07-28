# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is **aic2026** — course materials for *TFE4188 Advanced Integrated Circuits 2026* by Carsten Wulff. The repo generates:
- A **Jekyll website** (`docs/`) deployed to GitHub Pages at `wulffern.github.io/aic2026`
- **Standalone PDFs** (one per lecture) and a combined **PDF book** (`pdf/aic.pdf`) and **ebook** (`pdf/aic.epub`)

Source lectures are Markdown files in `lectures/` that are processed by `py/lecture.py` into both Jekyll posts and LaTeX.

## Key Commands

### Full build
```sh
make all   # version + posts-parallel + texfiles-parallel + standalone-parallel + latex-nobuild + book-nobuild
```

### Partial builds (most common)
```sh
make posts-parallel       # Convert lectures/*.md → docs/_posts/*.markdown (parallel, 4 workers)
make texfiles-parallel    # Convert lectures/*.md → pdf/*.tex (parallel, 4 workers)
make standalone-parallel  # Compile individual PDFs in pdf/ (parallel, 4 workers)
make latex-nobuild        # Compile combined PDF (pdf/aic.pdf) without regenerating .tex files
make book-nobuild         # Compile EPUB without regenerating .tex files
```

### Single lecture processing
```sh
# Jekyll post
python3 py/lecture.py post lectures/l01_intro.md

# LaTeX file
python3 py/lecture.py latex lectures/l01_intro.md

# With --no-append flag (skips writing to shared chapters.tex/downloads.md, used in parallel builds)
python3 py/lecture.py latex --no-append lectures/l01_intro.md
```

### Jekyll development server
```sh
make jstart   # Runs Jekyll in Docker on port 3002 (http://localhost:3002)
```

### Slide decks
```sh
make slides              # Render every lecture to docs/assets/html/<name>.html
make slides-parallel     # Same, 4 workers
make slides-one FNAME=l05_sc
```
The lectures in `lectures/` are Deckset source. `py/slides.py` renders the same
files to standalone HTML decks: `pan_doc`/`pan_latex` bodies are dropped, the
`pan_skip` title slides are kept, and the Deckset directives (`---`, `#[fit]`,
`![left fit]`, `[.column]`, `[.background-color:]`) become CSS. Open the HTML
in a browser; arrow keys or space to navigate, `f` for fullscreen, Cmd-P to
print to PDF. Maths is typeset by a vendored MathJax (`slides/vendor/`), not a
CDN, so a deck works with no network. Needs `markdown` (in
`requirements-ci.txt`) and `pdftocairo` from poppler to turn PDF figures into
SVG for the browser.

### TikZ figures
```sh
make tikz   # Builds tikz/*.tex files → media/*_tikz.{pdf,svg}
```

### Docker image
```sh
make ci           # Build Docker image wulffern/aic:2026_latest
make cish         # Shell into the Docker image with repo mounted
make tagpush      # Tag and push to Docker Hub
```

## Architecture

### Lecture source format (`lectures/*.md`)
Markdown with special front-matter and pandoc-style comment blocks:
- `<!--pan_title: Title -->` — sets the lecture title
- `<!--pan_skip: -->` — content skipped in web output (slide deck headers)
- `<!--pan_doc: ... -->` — content included only in web/doc output (not slides)
- `<!--pan_latex: ... -->` — LaTeX-only content

Files prefixed `l` are main lectures; `lr` are reference/refresher lectures; `lx` are extra topics; `lp` are project-related; `g` are guest lectures.

### Python processor (`py/lecture.py`)
Two CLI commands via Click:
- `post` → `Lecture` class: produces Jekyll markdown for `docs/_posts/`
- `latex` → `Latex` class: produces `.tex` and `pdf/*_chapter.inc` / `pdf/*_download.inc` files

Key classes: `Bibtex`, `Image`, `Lecture`, `Latex`.

The `FILES` list in the root `Makefile` controls which lectures are processed and their order in the book.

### PDF pipeline (`pdf/Makefile`)
- Individual lecture `.tex` files are compiled with `pdflatex` via `make standalone FNAME=<file>.tex`
- The book (`aic.pdf`) is compiled with `kaobook` (auto-cloned from GitHub) using `TEXINPUTS=".:kaobook:"`
- `pdf/chapters.tex` is assembled from `*_chapter.inc` files; `docs/downloads.md` from `*_download.inc` files
- `pdf/fix_svg.py` post-processes generated `.latex` files before compilation

### Jekyll site (`docs/`)
- Uses `jekyll/jekyll:3.8` Docker image
- Remote theme: `wulffern/minima`
- Posts land in `docs/_posts/` as `YYYY-MM-DD-<title>.markdown`
- Media assets copy to `docs/assets/media/`

### Dependencies
The build requires: `pandoc`, `pdflatex` + kaobook, `python3` with `click`, `svglib`, `numpy`, `pandas`, `matplotlib`. The Docker image (`docker/Dockerfile`) has all dependencies pre-installed.
