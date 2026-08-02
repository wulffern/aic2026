
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
	-makeindex -q aic.idx
	${PDFLATEX} aic
	# Recompress: /ebook downsamples the embedded rasters to 150 dpi,
	# which takes the book from ~50 MB to ~17 MB with no visible change
	# (checked page by page, including the board photos); all 3560 link
	# annotations and the outline survive. Skipped quietly if gs is absent.
	@if command -v gs >/dev/null 2>&1; then \
		${MAKE} compress && mv aic_compress.pdf aic.pdf; \
	else \
		echo "gs not found, keeping the uncompressed aic.pdf"; \
	fi

# The honest-colour edition: same book, but the chapters Claude wrote
# are set in blue. Same three-pass build under a different jobname, so
# it never disturbs aic.pdf's aux files.
book-ai: kaobook
	chmod -R 755  media
	${PDFLATEX} -draftmode -jobname aic_ai "\def\AIHIGHLIGHT{}\input{aic.tex}"
	${PDFLATEX} -draftmode -jobname aic_ai "\def\AIHIGHLIGHT{}\input{aic.tex}"
	-makeindex -q aic_ai.idx
	${PDFLATEX} -jobname aic_ai "\def\AIHIGHLIGHT{}\input{aic.tex}"

clean-main-aux:
	-rm -f ${MAIN_AUX}

compress:
	gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.5 -dPDFSETTINGS=/ebook \
	-dNOPAUSE -dQUIET -dBATCH -sOutputFile=aic_compress.pdf aic.pdf

# The figures are generated at print resolution, which the PDF wants and
# the ebook does not: epubshrink.py downsamples them and drops pointless
# alpha channels afterwards, which is worth about a third of the file.
ebook:
	cat aic.tex |perl -pe "s/chapters/chapters_epub/ig" > aic_epub.latex
	cat chapters.tex |perl -pe "s/fiximg/fiximg_png/ig" > chapters_epub.tex
	pandoc aic_epub.latex -t native | pandoc -f native -t epub3 -o aic.epub --mathml --metadata title="Advanced Integrated Circuits"
	${PYTHON} ../py/epubshrink.py aic.epub
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
