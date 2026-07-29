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

# The same package set CI installs, so py/lecture.py, py/slides.py and the
# figure scripts run identically here and there. Makefiles pick this
# interpreter up automatically (see the /pyenv check in Makefile).
COPY requirements-ci.txt /tmp/requirements-ci.txt
RUN  python -m venv /pyenv && /pyenv/bin/python3 -m pip install -r /tmp/requirements-ci.txt
