FROM texlive/texlive:TL2022-historic
    MAINTAINER Carsten Wulff <carsten@wulff.no>

# Everything the Docs and TikZ workflows previously apt-got in every job,
# plus cairo headers so the pip packages build.
RUN apt-get update && \
    apt-get -y install ghostscript python3-pip poppler-utils pandoc wget imagemagick python3-svglib \
    python3-venv build-essential pkg-config libcairo2-dev python3-dev librsvg2-bin && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Pin pandoc: the texlive base ships pandoc 3.10, whose longtable output
# breaks the kaobook book build ("No counter 'none' defined"). 3.6 matches
# pandoc_3.6.tex and the author's local build. The symlink outranks the
# base image's copy in /usr/local/bin.
RUN wget -q https://github.com/jgm/pandoc/releases/download/3.6.4/pandoc-3.6.4-1-amd64.deb -O /tmp/pandoc.deb && \
    dpkg -i /tmp/pandoc.deb && rm /tmp/pandoc.deb && \
    ln -sf /usr/bin/pandoc /usr/local/bin/pandoc && \
    pandoc --version | head -n 1

# The same package set CI installs, so py/lecture.py, py/slides.py and the
# figure scripts run identically here and there. Makefiles pick this
# interpreter up automatically (see the /pyenv check in Makefile).
COPY requirements-ci.txt /tmp/requirements-ci.txt
RUN  python -m venv /pyenv && /pyenv/bin/python3 -m pip install -r /tmp/requirements-ci.txt
