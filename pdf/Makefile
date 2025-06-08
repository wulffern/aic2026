
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


one: fix hash kaobook pandoc.tex
	export
	chmod -R 755  media
	TEXINPUTS=".:kaobook:" pdflatex aic
	#TEXINPUTS=".:kaobook:" makeindex aic.nlo
	#-pdflatex -interaction nonstopmode --shell-escape aic.latex
	-TEXINPUTS=".:kaobook:" bibtex aic
	TEXINPUTS=".:kaobook:" pdflatex aic
	TEXINPUTS=".:kaobook:" pdflatex aic
	#TEXINPUTS=".:kaobook:" pdflatex aic.tex
	#-pdflatex -interaction nonstopmode --shell-escape aic.latex
	#${MAKE} compress

compress:
	gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
	-dNOPAUSE -dQUIET -dBATCH -sOutputFile=aic_compress.pdf aic.pdf

ebook:
	cat aic.tex |perl -pe "s/chapters/chapters_epub/ig" > aic_epub.latex
	cat chapters.tex |perl -pe "s/fiximg/fiximg_png/ig" > chapters_epub.tex
	pandoc --gladtex -o aic.epub aic_epub.latex

standalone:
	pdflatex ${FNAME}
	-bibtex ${FNAME}
	pdflatex ${FNAME}
	pdflatex ${FNAME}

clean:
	-rm *.latex
	-rm *_fiximg.tex
	-rm *.md
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
