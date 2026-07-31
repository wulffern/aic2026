
JEKYLL_VERSION=3.8
SITE=${shell pwd}/docs
TAG=1
YEAR=2026

#-
PYTHON=python3
ifneq ($(wildcard /pyenv/bin/.*),)
	PYTHON=/pyenv/bin/python3
endif

.PHONY:  plots plots-one plots-data slides slides-one slides-parallel version tikz tikz-one tikz-check tikz-preview preview print-tikz figures prepare-docs standalone-one standalone-list book-pdf book-epub print-files examples check

#	lr0_logic \

FILES = l00_jayn \
	l01_intro \
	lr0_excellence \
	l00_refresher \
	l00_diode \
	lr0_mosfet \
	lr0_circuits \
	lr0_ota \
	lr0_passives \
	lr0_noise \
	lr0_tools \
	lr0_tut1 \
	l01_project \
	l02_esd \
	l03_refbias \
	l04_afe \
	l04_dac \
	l05_sc \
	l06_adc \
	l07_vreg \
	l08_pll \
	l09_osc \
	l10_lpradio \
	lx_energysrc \
	l11_aver \
	lp_project_report \
	lr0_layout \
	l13_thoughts \
	l00_spice \
	l00_sv \
	l00_ades \
	lr0_logic \
	l00_questions \
	l14_equations
	#s_mac\





all: version posts-parallel texfiles-parallel examples standalone-parallel latex-nobuild book-nobuild

latex-nobuild:
	cd pdf; make one
	cp pdf/aic.pdf docs/assets/

book-nobuild:
	cd pdf; make ebook
	cp pdf/aic.epub docs/assets/

version:
	echo "aic${YEAR}" > version

prepare-docs: clean-prepared version figures posts-parallel texfiles-parallel slides-parallel examples
	cd pdf; [ -d kaobook ] || git clone https://github.com/fmarotta/kaobook.git

# ---------------------------------------------------------------------------
# Interactive examples
#
# examples/ holds one self-contained HTML page per script in ex/. docs/assets/
# is gitignored, so examples/ is the source and gets copied in, the same way
# media/ is the source for docs/assets/media/. Nothing is generated, so this is
# a copy rather than a build.
# ---------------------------------------------------------------------------

EXAMPLEDIR = docs/assets/examples

examples:
	-mkdir -p ${EXAMPLEDIR}/common
	cp -f examples/*.html ${EXAMPLEDIR}/
	cp -f examples/common/* ${EXAMPLEDIR}/common/

# Nothing to do. This used to regenerate one matplotlib figure into
# media/; every data figure now comes from a script in ex/ through
# py/tikzplot.py, and the generated tikz/*.tex and media/*_tikz.pdf are
# committed. Use `make plots` to regenerate them, which needs numpy and
# in a few cases cicsim, and is deliberately not part of the doc build.
figures:
	@:

clean-prepared:
	-rm -rf ${BUILDDIR}
	-rm -f docs/downloads.md images.txt *_images.inc
	-rm -f docs/assets/*.pdf docs/assets/*.epub
	-rm -rf docs/assets/html docs/assets/examples
	-rm -f pdf/*.aux pdf/*.log pdf/*.pdf pdf/*.epub pdf/*.bbl pdf/*.blg pdf/*.toc pdf/*.bcf pdf/*.xml pdf/*.mw

print-files:
	@printf '%s\n' ${FILES}

# Mechanical correctness checks (see py/check.py): image refs, citations,
# $$ balance, FILES coverage, and — when docs/_posts exists — leftover
# Deckset directives and footnote sanity in the generated posts.
check:
	${PYTHON} py/check.py


# ---------------------------------------------------------------------------
# Incremental lecture conversion
#
# Each lecture gets a stamp in .build/ recording when it was last converted,
# so editing one lecture reconverts one lecture instead of all of them.
# The stamps deliberately do NOT depend on version_short.tex: that file
# embeds the build date and git hash, so depending on it would invalidate
# every lecture on every commit. The header of an untouched standalone PDF
# keeps the date it was last actually built — which is what it says anyway.
#
# `make posts-parallel` / `make texfiles-parallel` keep their names and
# behavior (CI calls them), they just skip up-to-date lectures now.
# ---------------------------------------------------------------------------

BUILDDIR = .build

POST_STAMPS = ${addprefix ${BUILDDIR}/,${addsuffix .post,${FILES}}}

# `version` is order-only: the target is PHONY (it rewrites the same content
# every run), so a normal dependency would invalidate every stamp every time.
${BUILDDIR}/%.post: lectures/%.md py/lecture.py pdf/aic.bib | version
	@mkdir -p ${BUILDDIR} docs/assets/media docs/_posts
	${PYTHON} py/lecture.py post lectures/$*.md --images-file ${BUILDDIR}/$*_images.inc
	@touch $@

posts: posts-parallel
posts-parallel:
	cp syllabus.md docs/syllabus.md
	cp plan.md docs/plan.md
	@${MAKE} --no-print-directory -j 4 ${POST_STAMPS}
	cat ${addprefix ${BUILDDIR}/,${addsuffix _images.inc,${FILES}}} > images.txt
	@if [ -z "$$CI" ] && [ -s images.txt ]; then cd lectures && cat ../images.txt | xargs git add -f; fi


jstart:
	docker run --rm --name aic_docs --volume="${SITE}:/srv/jekyll" -p 3002:4000 -it jekyll/jekyll:${JEKYLL_VERSION} jekyll serve --watch --drafts

# Book-style site prototype (just-the-docs). Regenerates chapters from
# docs/_posts, then serves on http://localhost:3003
#
# ruby (multi-arch), not jekyll/jekyll: that image is amd64-only, and
# under emulation on Apple silicon sass-embedded's compiler subprocess
# dies with "Broken pipe". Gems cache in docs-book/vendor across runs.
jbook:
	${PYTHON} py/mkbooksite.py
	docker run --rm --name aic_book --volume="$(shell pwd)/docs-book:/srv/jekyll" -w /srv/jekyll -e BUNDLE_PATH=vendor/bundle -p 3003:4000 -it ruby:3.3 sh -c "bundle install --quiet && bundle exec jekyll serve --watch --host 0.0.0.0"

TEX_STAMPS = ${addprefix ${BUILDDIR}/,${addsuffix .tex,tex_intro ${FILES}}}

${BUILDDIR}/%.tex: lectures/%.md py/lecture.py pdf/aic.bib pdf/short_tmplt.tex pdf/ieee-with-url.csl | version
	@mkdir -p ${BUILDDIR} pdf/media
	${PYTHON} py/lecture.py latex --no-append lectures/$*.md
	@touch $@

texfiles: texfiles-parallel
texfiles-parallel:
	-mkdir -p pdf/media
	cd pdf; make hash_short
	@${MAKE} --no-print-directory -j 4 ${TEX_STAMPS}
	cat downloads.md > docs/downloads.md
	cat pdf/tex_intro_chapter.inc > pdf/chapters.tex
	${foreach f, ${FILES}, cat pdf/${f}_chapter.inc >> pdf/chapters.tex;}
	${foreach f, ${FILES}, cat pdf/${f}_download.inc >> docs/downloads.md;}
	${PYTHON} py/mkrefs.py
	cat pdf/references_chapter.inc >> pdf/chapters.tex
	cd pdf; make fix hash pandoc.tex

images:
	${foreach f, ${FILES}, echo ${f} && egrep "^!.*\(https://" lectures/${f}.md;}

standalone: texfiles standalone-nobuild
standalone-nobuild:
	${foreach f, ${FILES}, cd pdf; make standalone FNAME=${f}.tex;}
	${foreach f, ${FILES}, cp pdf/${f}.pdf docs/assets/;}

standalone-parallel:
	printf '%s\n' ${FILES} | xargs -P 4 -I{} sh -c 'cd pdf && make standalone FNAME={}.tex && cp {}.pdf ../docs/assets/'

standalone-one:
	@test -n "${FNAME}" || (echo "Usage: make standalone-one FNAME=l03_refbias"; exit 1)
	-mkdir -p docs/assets
	@set -e; \
	f="${FNAME}"; \
	f="$${f%.tex}"; \
	echo "Building $$f"; \
	cd pdf && $(MAKE) standalone FNAME="$$f.tex"; \
	cp "$$f.pdf" "../docs/assets/"

# Like standalone-list, but chapters whose content hash matches a cached PDF
# are copied instead of rebuilt. The version stamp is excluded from the hash
# on purpose (see py/pdfcache.py). CI restores/saves CACHEDIR around this.
CACHEDIR = ~/.cache/aic-standalone
standalone-cached:
	@test -n "${FILES}" || (echo "Usage: make standalone-cached FILES=\"l03_refbias l04_afe\""; exit 1)
	${PYTHON} py/pdfcache.py --cache ${CACHEDIR} ${FILES}

standalone-list:
	@test -n "${FILES}" || (echo "Usage: make standalone-list FILES=\"l03_refbias l04_afe\""; exit 1)
	-mkdir -p docs/assets
	@set -e; \
	for f in ${FILES}; do \
		name="$${f%.tex}"; \
		echo "Building $$name"; \
		cd pdf && $(MAKE) standalone FNAME="$$name.tex"; \
		cd ..; \
		cp "pdf/$$name.pdf" "docs/assets/"; \
	done

latex: texfiles
	cd pdf; make one
	cp pdf/aic.pdf docs/assets/

book:
	cd pdf; make ebook
	cp pdf/aic.epub docs/assets/

book-pdf:
	-mkdir -p docs/assets
	cd pdf; $(MAKE) one
	cp pdf/aic.pdf docs/assets/

book-epub:
	-mkdir -p docs/assets
	cd pdf; $(MAKE) ebook
	cp pdf/aic.epub docs/assets/


ci:
	docker build --platform linux/amd64,linux/arm64 -f docker/Dockerfile ${OPT} . -t wulffern/aic:${YEAR}_latest

tagpush:
	docker tag wulffern/aic:${YEAR}_latest wulffern/aic:${YEAR}.${TAG}
	docker push wulffern/aic:${YEAR}.${TAG}
	docker push wulffern/aic:${YEAR}_latest

cish:

	docker run --rm  -it -v $(shell pwd):/workdir/  wulffern/aic:${YEAR}_latest bash --login


equations:
	${foreach f,${FILES},cat lectures/${f}.md |perl -pe 's/\n//ig;'| perl -ne 'print "\n# ${f}\n\n";while(m/\$$\$$([^\$$]+)\$$\$$/ig){print "\n\$$\$$".$$1."\$$\$$\n"}';}

# Shared TikZ preamble/library files, included by the figures rather than built.
TIKZ_INCLUDES = fig_header.tex constellation_lib.tex esd_lib.tex ckt_lib.tex mos_lib.tex spec_lib.tex plane_lib.tex sc_lib.tex boot_lib.tex gmc_lib.tex sfg_lib.tex rdac_lib.tex dacsm_lib.tex

# pdfTeX stamps /CreationDate into every PDF, so an unchanged figure would
# still produce a different file on each run — and CI commits what it builds.
# Pinning the epoch keeps rebuilds byte-identical, locally and in CI alike.
TIKZ_REPRODUCIBLE = SOURCE_DATE_EPOCH=1700000000 FORCE_SOURCE_DATE=1

# Every figure source under tikz/, at any depth, minus the shared includes.
TIKZ_SOURCES = $(shell find tikz -name '*.tex' -not -path 'tikz/build/*' \
	$(foreach i,${TIKZ_INCLUDES},-not -name '${i}') | sort)

# ---------------------------------------------------------------------------
# Data plots
#
# The figures that plot numbers rather than draw circuits are generated by
# scripts in ex/ through py/tikzplot.py, which renders them with the same
# preamble as the schematics so the two match on a page. Each script writes
# one or more tikz/<name>.tex, which are committed, so building the book
# never runs any of this.
#
#   make plots                 regenerate every generated tikz/*.tex, then
#                              rebuild the figures those scripts produce
#   make plots-one FNAME=buck  the same for one script
#   make plots-data            re-vendor the simulation data into ex/data/
#                              (needs the aicex and dicex repos; only after
#                              a simulation has been re-run)
#
# Anything in ex/ that imports tikzplot is a plot script; that is the whole
# registration mechanism, so a new one needs no edit here.
PLOT_SOURCES = $(shell grep -l 'from tikzplot import' ex/*.py 2>/dev/null | sort)

print-plots:
	${foreach f,${PLOT_SOURCES},echo ${f};}

plots:
	printf '%s\n' ${PLOT_SOURCES} | xargs -P 4 -I{} ${MAKE} --no-print-directory plots-one FNAME={}

# Runs one script, then rebuilds exactly the figures it printed. Doing it
# per script rather than rebuilding all of tikz/ keeps the loop short when
# you are iterating on a single plot.
plots-one:
	@test -n "${FNAME}" || (echo "Usage: make plots-one FNAME=buck (also accepts ex/buck.py)"; exit 1)
	@set -e; \
	f="${FNAME}"; \
	[ -f "$$f" ] || f="ex/${FNAME}.py"; \
	[ -f "$$f" ] || { echo "No plot script for FNAME=${FNAME}"; exit 1; }; \
	out=$$(cd ex && ${PYTHON} "$$(basename $$f)" | sed -n 's/^tikzplot: wrote tikz\/\(.*\)\.tex$$/\1/p'); \
	test -n "$$out" || { echo "$$f produced no figures"; exit 1; }; \
	for n in $$out; do ${MAKE} --no-print-directory tikz-one FNAME="$$n"; done

plots-data:
	${PYTHON} ex/fetch_data.py

# ---------------------------------------------------------------------------
# Slide decks
#
# The lectures in lectures/ are Deckset source. These targets render the same
# files to standalone HTML decks, dropping the pan_doc prose that belongs to
# the book and keeping the pan_skip title slides that the web build hides.
#
# docs/assets/ is gitignored, so slides/vendor is the source for anything the
# decks need at runtime and gets copied in, the same way media/ is the source
# for docs/assets/media/. The decks land in docs/assets/html/ and are published
# with the site; prepare-docs builds them so CI picks them up.
# ---------------------------------------------------------------------------

SLIDEDIR = docs/assets/html

slides-vendor:
	-mkdir -p ${SLIDEDIR}/vendor docs/assets/media
	cp -f slides/vendor/* ${SLIDEDIR}/vendor/

# tex_intro is not in FILES, but it is a chapter and downloads.md links a deck
# for it, so it has to be rendered too or that link is dead.
# s_* are standalone decks: not in the lecture series or the book, but used
# as slides, so they render too (linked from the Downloads page).
STANDALONE_DECKS = s_chinf s_exam s_mac s_maxwell s_need_to_know s_project_scratch s_teach s_tut2
SLIDEFILES = ${FILES} tex_intro ${STANDALONE_DECKS}

slides: slides-vendor
	${foreach f, ${SLIDEFILES}, ${PYTHON} py/slides.py lectures/${f}.md || exit; }

slides-parallel: slides-vendor
	printf '%s\n' ${SLIDEFILES} | xargs -P 4 -I{} ${PYTHON} py/slides.py lectures/{}.md

slides-one: slides-vendor
	@test -n "${FNAME}" || (echo "Usage: make slides-one FNAME=l05_sc"; exit 1)
	${PYTHON} py/slides.py lectures/${FNAME}.md


print-tikz:
	${foreach f,${TIKZ_SOURCES},echo ${f};}

# Four figures at a time; each lands in its own tikz/build/<subdir>/<name>.*
# so the workers never touch the same file. xargs exits non-zero if any
# figure fails, so -halt-on-error still fails CI.
tikz:
	printf '%s\n' ${TIKZ_SOURCES} | xargs -P 4 -I{} ${MAKE} --no-print-directory tikz-one FNAME={}

# Rasterise the figures left in tikz/build/ by tikz-check, so they can be
# reviewed without a PDF viewer. CI uploads the result as an artifact.
tikz-preview:
	-mkdir -p preview
	printf '%s\n' ${TIKZ_SOURCES} | xargs -P 4 -n 1 sh -c ' \
		f="$$1"; rel=$${f#tikz/}; rel=$${rel%.tex}; \
		b=$$(basename "$$rel"); \
		pdf="tikz/build/$$rel.pdf"; \
		if [ ! -f "$$pdf" ]; then \
			echo "$$pdf missing — run '\''make tikz-check'\'' first"; exit 1; \
		fi; \
		echo "Rendering $$rel"; \
		pdftoppm -png -r 150 -singlefile "$$pdf" "preview/$${b}_tikz"' sh

# Compare one figure's original artwork against its TikZ redraw, as PNG.
# Needs requirements-preview.txt.
preview:
	@test -n "${FNAME}" || (echo "Usage: make preview FNAME=l03_ptat"; exit 1)
	${PYTHON} py/preview.py --compare ${FNAME} -o preview

# Compile every figure without touching media/ — for CI, where the only
# question is whether the sources still build.
tikz-check:
	-mkdir -p tikz/build
	printf '%s\n' ${TIKZ_SOURCES} | xargs -P 4 -n 1 sh -c ' \
		f="$$1"; rel=$${f#tikz/}; \
		echo "Checking $${rel%.tex}"; \
		mkdir -p "tikz/build/$$(dirname "$$rel")"; \
		${TIKZ_REPRODUCIBLE} pdflatex -interaction=nonstopmode -halt-on-error \
			-output-directory "tikz/build/$$(dirname "$$rel")" "$$f" >/dev/null || \
			{ echo "FAILED $$rel — see tikz/build/$${rel%.tex}.log"; exit 1; }' sh

tikz-one:
	@test -n "${FNAME}" || (echo "Usage: make tikz-one FNAME=l3_bjtonly (also accepts l13/pdpu or tikz/l3_bjtonly.tex)"; exit 1)
	@set -e; \
	if [ -f "${FNAME}" ]; then \
		f="${FNAME}"; \
	elif [ -f "tikz/${FNAME}.tex" ]; then \
		f="tikz/${FNAME}.tex"; \
	else \
		echo "Could not find TikZ source for FNAME=${FNAME}"; \
		exit 1; \
	fi; \
	rel=$${f#tikz/}; rel=$${rel%.tex}; \
	b=$$(basename "$$rel"); \
	sub=$$(dirname "$$rel"); \
	if [ "$$sub" = "." ]; then sub=""; else sub="/$$sub"; fi; \
	mkdir -p "tikz/build$$sub" "media$$sub"; \
	echo "Building $$rel"; \
	${TIKZ_REPRODUCIBLE} pdflatex -interaction=nonstopmode -halt-on-error -output-directory "tikz/build$$sub" "$$f"; \
	cp "tikz/build$$sub/$$b.pdf" "media$$sub/$${b}_tikz.pdf"; \
	if command -v pdf2svg >/dev/null 2>&1; then \
		pdf2svg "tikz/build$$sub/$$b.pdf" "media$$sub/$${b}_tikz.svg" || true; \
	elif command -v dvisvgm >/dev/null 2>&1; then \
		dvisvgm --pdf "tikz/build$$sub/$$b.pdf" -n -o "media$$sub/$${b}_tikz.svg" >/dev/null 2>&1 || true; \
	fi
