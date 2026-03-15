
JEKYLL_VERSION=3.8
SITE=${shell pwd}/docs
TAG=1
YEAR=2026

#-
PYTHON=python3
ifneq ($(wildcard /pyenv/bin/.*),)
	PYTHON=/pyenv/bin/python3
endif

.PHONY:  slides version tikz

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
	cd lectures; cat ../images.txt |xargs git add -f
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

latex: texfiles
	cd pdf; make one
	cp pdf/aic.pdf docs/assets/

book:
	cd pdf; make ebook
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

tikz:
	-mkdir -p tikz/build
	-mkdir -p pdf/media
	@set -e; \
	for f in tikz/l3_vi.tex ; do \
		[ -f "$$f" ] || continue; \
		b=$$(basename "$$f" .tex); \
		[ "$$b" = "ckt_lib" ] && continue; \
		echo "Building $$b"; \
		pdflatex -interaction=nonstopmode -halt-on-error -output-directory tikz/build "$$f"; \
		cp "tikz/build/$$b.pdf" "media/$${b}_tikz.pdf"; \
		cp "tikz/build/$$b.pdf" "pdf/media/$${b}_tikz.pdf"; \
		if command -v pdf2svg >/dev/null 2>&1; then \
			pdf2svg "tikz/build/$$b.pdf" "media/$${b}_tikz.svg" || true; \
			if [ -f "media/$${b}_tikz.svg" ]; then cp "media/$${b}_tikz.svg" "pdf/media/$${b}_tikz.svg"; fi; \
		elif command -v dvisvgm >/dev/null 2>&1; then \
			dvisvgm --pdf "tikz/build/$$b.pdf" -n -o "media/$${b}_tikz.svg" >/dev/null 2>&1 || true; \
			if [ -f "media/$${b}_tikz.svg" ]; then cp "media/$${b}_tikz.svg" "pdf/media/$${b}_tikz.svg"; fi; \
		fi; \
	done
