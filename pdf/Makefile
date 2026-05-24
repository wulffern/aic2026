
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

#- Choose right pandoc file based on pandoc version
PANDOC=pandoc_$(shell pandoc --version|head -n 1|cut -d " " -f 2|cut -d "." -f "1,2").tex
pandoc.tex:
	ln -s ${PANDOC} pandoc.tex

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

standalone:
	pdflatex -draftmode ${FNAME}
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
