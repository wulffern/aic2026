#!/usr/bin/env python3
"""Inventory the paper links in lectures/ that are candidates for aic.bib.

Phase 1 of the link-to-bibliography conversion (see bib_conversion_plan.md).
This command only reads; it never edits a lecture.

    python3 py/linkbib.py scan                  # summary to stdout
    python3 py/linkbib.py scan --tsv out.tsv    # one row per occurrence
"""

import re
import os
import glob
import click
from urllib.parse import urlparse, parse_qs

# Hosts that publish citable literature. Everything else (wikipedia, github,
# youtube, vendor pages, patents, datasheets) stays a plain link.
PAPER_HOSTS = (
    "ieeexplore.ieee.org",
    "ntnuopen.ntnu.no",
    "link.springer.com",
    "doi.org",
    "arxiv.org",
    "dl.acm.org",
    "www.researchgate.net",
)

# IEEE URLs that are not a single article: search results, media assets, books.
IEEE_NOT_AN_ARTICLE = ("/search/", "/mediastore_new/", "/book/", "/xpl/")

# A link straight to a figure is artwork, not a reference.
ASSETS = (".jpg", ".jpeg", ".png", ".gif", ".svg", ".pdf")

MD_LINK = re.compile(r"\[([^\]\[]*)\]\((https?://[^)\s]+)\)")
BIB_KEY = re.compile(r"^\s*@[a-zA-Z]+\s*{\s*([^,\s]+)\s*,")
BIB_FIELD = re.compile(r'^\s*([a-zA-Z]+)\s*=\s*"?(.*?)"?\s*,?\s*$')


def arnumber(url):
    """IEEE article number, however the URL happens to spell it."""
    m = re.search(r"/document/(\d+)", url)
    if m:
        return m.group(1)
    q = parse_qs(urlparse(url).query)
    if "arnumber" in q:
        return q["arnumber"][0]
    return None


def normalize(url):
    """Collapse the spellings of one paper to a single identity."""
    ar = arnumber(url)
    if ar:
        return f"ieee:{ar}"
    return url.split("#")[0].rstrip("/")


def citable(url):
    """True if this URL points at something that belongs in aic.bib."""
    host = urlparse(url).netloc
    if not any(host == h or host.endswith("." + h) for h in PAPER_HOSTS):
        return False
    if urlparse(url).path.lower().endswith(ASSETS):
        return False
    if "ieeexplore" in host:
        if any(p in url for p in IEEE_NOT_AN_ARTICLE):
            return False
        if arnumber(url) is None:
            return False
    return True


def read_bib_titles(filename):
    """Map of normalized title -> key, for the entries already in the bib."""
    titles = dict()
    key = None
    with open(filename) as fi:
        for line in fi:
            m = BIB_KEY.match(line)
            if m:
                key = m.group(1)
                continue
            m = BIB_FIELD.match(line)
            if m and key and m.group(1).lower() == "title":
                titles[squash(m.group(2))] = key
    return titles


def squash(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


class Link:
    def __init__(self, lecture, line, section, text, url):
        self.lecture = lecture
        self.line = line
        self.section = section
        self.text = text
        self.url = url
        self.ident = normalize(url)


def scan_lectures(pattern="lectures/*.md"):
    links = list()
    for fname in sorted(glob.glob(pattern)):
        section = ""
        with open(fname) as fi:
            for nr, line in enumerate(fi, 1):
                if line.startswith("#"):
                    section = re.sub(r"^#+\s*(\[fit\])?\s*", "", line).strip()
                for m in MD_LINK.finditer(line):
                    text, url = m.group(1), m.group(2)
                    if citable(url):
                        links.append(Link(os.path.basename(fname), nr,
                                          section, text, url))
    return links


def group(links):
    """Occurrences keyed by paper identity, in first-seen order."""
    papers = dict()
    for link in links:
        papers.setdefault(link.ident, list()).append(link)
    return papers


@click.group()
def cli():
    pass


@cli.command()
@click.option("--lectures", default="lectures/*.md", help="Glob of lectures to scan")
@click.option("--bib", default="pdf/aic.bib", help="Bibliography to check against")
@click.option("--tsv", default=None, help="Write one row per occurrence here")
def scan(lectures, bib, tsv):
    """List the lecture links that should become bib entries."""

    links = scan_lectures(lectures)
    papers = group(links)
    known = read_bib_titles(bib)

    matched = dict()
    for ident, hits in papers.items():
        for hit in hits:
            key = known.get(squash(hit.text))
            if key:
                matched[ident] = key
                break

    per_lecture = dict()
    for link in links:
        per_lecture.setdefault(link.lecture, list()).append(link)

    for lecture in sorted(per_lecture):
        hits = per_lecture[lecture]
        print(f"{lecture:24s} {len(hits):3d} links")

    print()
    print(f"occurrences        : {len(links)}")
    print(f"distinct papers    : {len(papers)}")
    print(f"cited more than one: {len([p for p in papers.values() if len(p) > 1])}")
    print(f"already in {bib}: {len(matched)}")
    print(f"new entries needed : {len(papers) - len(matched)}")

    if tsv:
        with open(tsv, "w") as fo:
            fo.write("paper\tlecture\tline\tsection\ttext\turl\texisting_key\n")
            for ident in sorted(papers, key=lambda i: papers[i][0].lecture):
                for hit in papers[ident]:
                    fo.write("\t".join([ident, hit.lecture, str(hit.line),
                                        hit.section, hit.text, hit.url,
                                        matched.get(ident, "")]) + "\n")
        print(f"\nwrote {tsv}")


if __name__ == "__main__":
    cli()
