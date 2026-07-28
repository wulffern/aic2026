
JEKYLL_VERSION=3.8
SITE=${shell pwd}/docs
TAG=1
YEAR=2026

#-
PYTHON=python3
ifneq ($(wildcard /pyenv/bin/.*),)
	PYTHON=/pyenv/bin/python3
endif

.PHONY:  slides version tikz tikz-one tikz-check tikz-preview preview print-tikz figures prepare-docs standalone-one standalone-list book-pdf book-epub print-files

#	lr0_logic \

FILES = l00_jayn \
	l01_intro \
	lr0_excellence \
	l00_refresher \
	l00_diode \
	lr0_mosfet \
	lr0_circuits \
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
	l00_questions
	#l04_mac\





all: version posts-parallel texfiles-parallel standalone-parallel latex-nobuild book-nobuild

latex-nobuild:
	cd pdf; make one
	cp pdf/aic.pdf docs/assets/

book-nobuild:
	cd pdf; make ebook
	cp pdf/aic.epub docs/assets/

version:
	echo "aic${YEAR}" > version

prepare-docs: clean-prepared version figures posts-parallel texfiles-parallel
	cd pdf; [ -d kaobook ] || git clone https://github.com/fmarotta/kaobook.git

figures: media/antenna_diode_leak.pdf

media/antenna_diode_leak.pdf: ex/antenna_diode_leakage.py
	${PYTHON} ex/antenna_diode_leakage.py

clean-prepared:
	-rm -f docs/downloads.md images.txt *_images.inc
	-rm -f docs/assets/*.pdf docs/assets/*.epub
	-rm -f pdf/*.aux pdf/*.log pdf/*.pdf pdf/*.epub pdf/*.bbl pdf/*.blg pdf/*.toc pdf/*.bcf pdf/*.xml pdf/*.mw

print-files:
	@printf '%s\n' ${FILES}


posts:
	-rm images.txt
	cp syllabus.md docs/syllabus.md
	cp plan.md docs/plan.md
	${foreach f, ${FILES}, ${PYTHON} py/lecture.py post lectures/${f}.md || exit; }
	cd lectures; cat ../images.txt |xargs git add -f

posts-parallel:
	-rm -f images.txt *_images.inc
	-mkdir -p docs/assets/media docs/_posts
	cp syllabus.md docs/syllabus.md
	cp plan.md docs/plan.md
	printf '%s\n' ${FILES} | xargs -P 4 -I{} ${PYTHON} py/lecture.py post lectures/{}.md --images-file {}_images.inc
	cat ${addsuffix _images.inc,${FILES}} > images.txt 2>/dev/null; true
	@if [ -z "$$CI" ] && [ -s images.txt ]; then cd lectures && cat ../images.txt | xargs git add -f; fi
	-rm -f *_images.inc


jstart:
	docker run --rm --name aic_docs --volume="${SITE}:/srv/jekyll" -p 3002:4000 -it jekyll/jekyll:${JEKYLL_VERSION} jekyll serve --watch --drafts

texfiles:
	-mkdir pdf/media
	-rm pdf/chapters.tex
	cd pdf; make hash_short
	${PYTHON} py/lecture.py latex lectures/tex_intro.md
	-rm docs/downloads.md

	cat downloads.md > docs/downloads.md
	${foreach f, ${FILES}, ${PYTHON} py/lecture.py latex lectures/${f}.md || exit ; }
	cd pdf; make fix hash pandoc.tex

texfiles-parallel:
	-mkdir pdf/media
	-rm -f pdf/chapters.tex
	cd pdf; make hash_short
	${PYTHON} py/lecture.py latex --no-append lectures/tex_intro.md
	-rm docs/downloads.md
	cat downloads.md > docs/downloads.md
	printf '%s\n' ${FILES} | xargs -P 4 -I{} ${PYTHON} py/lecture.py latex --no-append lectures/{}.md
	cat pdf/tex_intro_chapter.inc > pdf/chapters.tex
	${foreach f, ${FILES}, cat pdf/${f}_chapter.inc >> pdf/chapters.tex;}
	${foreach f, ${FILES}, cat pdf/${f}_download.inc >> docs/downloads.md;}
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
	cp "pdf/$$f.pdf" "docs/assets/"

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
TIKZ_INCLUDES = fig_header.tex ckt_lib.tex

# pdfTeX stamps /CreationDate into every PDF, so an unchanged figure would
# still produce a different file on each run — and CI commits what it builds.
# Pinning the epoch keeps rebuilds byte-identical, locally and in CI alike.
TIKZ_REPRODUCIBLE = SOURCE_DATE_EPOCH=1700000000 FORCE_SOURCE_DATE=1

# Every figure source under tikz/, at any depth, minus the shared includes.
TIKZ_SOURCES = $(shell find tikz -name '*.tex' -not -path 'tikz/build/*' \
	$(foreach i,${TIKZ_INCLUDES},-not -name '${i}') | sort)

print-tikz:
	${foreach f,${TIKZ_SOURCES},echo ${f};}

tikz:
	@set -e; \
	for f in ${TIKZ_SOURCES}; do \
		${MAKE} --no-print-directory tikz-one FNAME="$$f"; \
	done

# Rasterise the figures left in tikz/build/ by tikz-check, so they can be
# reviewed without a PDF viewer. CI uploads the result as an artifact.
tikz-preview:
	-mkdir -p preview
	@set -e; \
	for f in ${TIKZ_SOURCES}; do \
		rel=$${f#tikz/}; rel=$${rel%.tex}; \
		b=$$(basename "$$rel"); \
		pdf="tikz/build/$$rel.pdf"; \
		if [ ! -f "$$pdf" ]; then \
			echo "$$pdf missing — run 'make tikz-check' first"; exit 1; \
		fi; \
		echo "Rendering $$rel"; \
		pdftoppm -png -r 150 -singlefile "$$pdf" "preview/$${b}_tikz"; \
	done

# Compare one figure's original artwork against its TikZ redraw, as PNG.
# Needs requirements-preview.txt.
preview:
	@test -n "${FNAME}" || (echo "Usage: make preview FNAME=l03_ptat"; exit 1)
	${PYTHON} py/preview.py --compare ${FNAME} -o preview

# Compile every figure without touching media/ — for CI, where the only
# question is whether the sources still build.
tikz-check:
	-mkdir -p tikz/build
	@set -e; \
	for f in ${TIKZ_SOURCES}; do \
		rel=$${f#tikz/}; \
		echo "Checking $${rel%.tex}"; \
		mkdir -p "tikz/build/$$(dirname "$${rel}")"; \
		${TIKZ_REPRODUCIBLE} pdflatex -interaction=nonstopmode -halt-on-error \
			-output-directory "tikz/build/$$(dirname "$${rel}")" "$$f"; \
	done

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
