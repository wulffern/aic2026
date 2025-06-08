
JEKYLL_VERSION=3.8
SITE=${shell pwd}/docs
TAG=1
YEAR=2025

#-
PYTHON=python3
ifneq ($(wildcard /pyenv/bin/.*),)
	PYTHON=/pyenv/bin/python3
endif

.PHONY:  slides

#	lr0_logic \

FILES = l01_intro \
		l00_refresher \
	l00_diode \
	lr0_noise \
	lr0_tools \
	l00_ades \
	l02_esd \
	l03_refbias \
	l04_afe \
	l05_sc \
	l06_adc \
	l07_vreg \
	l08_pll \
	l09_osc \
	l10_lpradio \
	lx_energysrc \
	l11_aver \
	lp_project_report \
	l04_mac \
	lr0_passives \
	lr0_mosfet \
	lr0_layout \
	lr0_circuits \
	l00_spice \
	lr0_logic \
	l00_sv




	#l00_need_to_know


all: posts texfiles latex standalone book

posts:
	-rm images.txt
	cp syllabus.md docs/syllabus.md
	cp plan.md docs/plan.md
	${foreach f, ${FILES}, ${PYTHON} py/lecture.py post lectures/${f}.md || exit; }
	cd lectures; cat ../images.txt |xargs git add -f


jstart:
	docker run --rm --name aic_docs --volume="${SITE}:/srv/jekyll" -p 3002:4000 -it jekyll/jekyll:${JEKYLL_VERSION} jekyll serve --watch --drafts

texfiles:
	-mkdir pdf/media
	-rm pdf/chapters.tex
	-rm docs/downloads.md
	cd pdf; make hash_short
	cat downloads.md > docs/downloads.md
	${PYTHON} py/lecture.py latex lectures/tex_intro.md
	${foreach f, ${FILES}, ${PYTHON} py/lecture.py latex lectures/${f}.md || exit ; }
	cd pdf; make fix hash pandoc.tex

images:
	${foreach f, ${FILES}, echo ${f} && egrep "^!.*\(https://" lectures/${f}.md;}

standalone: texfiles
	${foreach f, ${FILES}, cd pdf; make standalone FNAME=${f}.tex;}
	${foreach f, ${FILES}, cp pdf/${f}.pdf docs/assets/;}

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
	docker run --rm  -it -v `pwd`:/workspace/ -i wulffern/aic:${YEAR}_latest bash --login
