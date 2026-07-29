
VERSION_DATE=Built on $(shell date)
VERSION_HASH=${shell git log -1 --pretty=format:"%H"}
FILE= aic

TEXS = ${shell ls -1 *.latex}
STANDALONE = ${shell cat standalone.files}

PYTHON=python3
ifneq ($(wildcard /pyenv/bin/.*),)
	PYTHON=/pyenv/bin/python3
endif

kaobook:
	git clone https://github.com/fmarotta/kaobook.git

fix:
	${foreach f, ${TEXS}, ${PYTHON} fix_svg.py ${f};}

hash:
	echo '{\\noindent ${VERSION_DATE}} \\\\ \n {\\noindent from ${VERSION_HASH}}'  > version.tex

hash_short:
	echo ' ${VERSION_DATE} from ${VERSION_HASH}'  > version_short.tex

#- Choose right pandoc file based on pandoc version.
#  A copy, not a symlink: pandoc.tex travels between CI jobs in the
#  prepared-sources artifact, and upload/download-artifact does not
#  round-trip symlinks.
#  Exact version match when a support file exists for it; otherwise the
#  newest one available. pandoc_3.6.tex already defines \pandocbounded and
#  \tightlist, which is what newer pandoc output actually needs.
PANDOC_VER=pandoc_$(shell pandoc --version|head -n 1|cut -d " " -f 2|cut -d "." -f "1,2").tex
PANDOC=$(shell [ -f ${PANDOC_VER} ] && echo ${PANDOC_VER} || ls -1 pandoc_*.tex | sort -V | tail -n 1)
pandoc.tex:
	@[ -f ${PANDOC_VER} ] || echo "pandoc.tex: no ${PANDOC_VER}, falling back to ${PANDOC}"
	cp -f ${PANDOC} pandoc.tex

MAIN_AUX = aic.aux aic.blg aic.log aic.toc aic.lof aic.lot aic.out aic.mw aic.nlo aic.nls aic.ilg aic.ind aic.idx aic.fff aic.ttt aic.loi aic.lol
PDFLATEX = ulimit -n 4096; TEXINPUTS=".:kaobook:" pdflatex

one: kaobook clean-main-aux
	chmod -R 755  media
	${PDFLATEX} -draftmode aic
	#TEXINPUTS=".:kaobook:" makeindex aic.nlo
	${PDFLATEX} -draftmode aic
	${PDFLATEX} aic
	#TEXINPUTS=".:kaobook:" pdflatex aic.tex
	#-pdflatex -interaction nonstopmode --shell-escape aic.latex
	#${MAKE} compress

clean-main-aux:
	-rm -f ${MAIN_AUX}

compress:
	gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
	-dNOPAUSE -dQUIET -dBATCH -sOutputFile=aic_compress.pdf aic.pdf

ebook:
	cat aic.tex |perl -pe "s/chapters/chapters_epub/ig" > aic_epub.latex
	cat chapters.tex |perl -pe "s/fiximg/fiximg_png/ig" > chapters_epub.tex
	pandoc aic_epub.latex -t native | pandoc -f native -t epub3 -o aic.epub --mathml
#pandoc --gladtex -o aic.epub aic_epub.latex

# Two passes, not three: the standalone chapters have no index or bibtex
# run, so references settle after one draft pass (verified: pass three
# changes nothing).
standalone:
	pdflatex -draftmode ${FNAME}
	pdflatex  ${FNAME}
	#dvipdf ${FNAME}

clean:
	-rm *.latex
	-rm *_fiximg.tex
	-rm *.md
	-rm l*.tex
	-rm *.epub
	-rm -rf media
	-rm *.bbl
	-rm *.aux
	-rm *.toc
	-rm *.log
	-rm *.blg
	-rm *.dvi
	-rm *.fff
	-rm *.lof
	-rm *.lot
	-rm *.ttt
	-rm *.xml
	-rm *.pdf
	-rm *.bcf
	-rm *fiximg*.tex
	-rm *.mw
