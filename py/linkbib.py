#!/usr/bin/env python3
"""Turn the paper links in lectures/ into pdf/aic.bib entries.

See bib_conversion_plan.md. Neither command edits a lecture.

    python3 py/linkbib.py scan                  # summary to stdout
    python3 py/linkbib.py scan --tsv out.tsv    # one row per occurrence
    python3 py/linkbib.py fetch --out pdf/incoming.bib

`fetch` resolves each candidate to a DOI through Crossref, pulls the BibTeX
from doi.org, and writes entries in the house style for review. It needs
outbound network; `scan` does not.
"""

import re
import os
import sys
import glob
import json
import time
import difflib
import urllib.error
import urllib.request
import click
from urllib.parse import urlparse, parse_qs, urlencode

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

# A Crossref hit below this title similarity is not trusted. A wrong but
# plausible entry is worse than a missing one, so those go to the unresolved
# list for hand-fetching from Xplore instead.
TITLE_THRESHOLD = 0.90

# Order fields the way the existing entries do.
FIELD_ORDER = ("author", "title", "journal", "booktitle", "publisher", "school",
               "volume", "number", "year", "pages", "doi", "url")

CONTACT = os.environ.get("CROSSREF_MAILTO", "")
USER_AGENT = "aic2026-linkbib (https://github.com/wulffern/aic2026)"

# Crossref is happy with the honest agent string above. Xplore answers 418 to
# it, and to any client that does not present browser headers, so its two
# endpoints get this one instead.
BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/126.0.0.0 Safari/537.36")


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


def read_bib_keys(filename):
    """Existing keys and DOIs, so fetch never mints a duplicate."""
    keys = set()
    dois = set()
    with open(filename) as fi:
        for line in fi:
            m = BIB_KEY.match(line)
            if m:
                keys.add(m.group(1))
                continue
            m = BIB_FIELD.match(line)
            if m and m.group(1).lower() == "doi":
                dois.add(m.group(2).strip().lower())
    return keys, dois


def doi_from_url(url):
    """A DOI the URL states outright, without asking anyone."""
    m = re.search(r"(10\.\d{4,9}/[^\s?#]+)", url)
    if m:
        return m.group(1).rstrip(".").rstrip("/")
    return None


def looks_like_a_title(text):
    """Enough of a title to search Crossref with, rather than guess from."""
    if re.match(r"^\s*https?://", text):
        return False
    return len(squash(text)) >= 20


def similarity(a, b):
    return difflib.SequenceMatcher(None, squash(a), squash(b)).ratio()


def initials(given):
    """'Chun-Cheng' -> 'C.-C.', matching how aic.bib writes authors."""
    parts = [p for p in re.split(r"[\s-]+", given.strip()) if p]
    joiner = "-" if "-" in given else " "
    return joiner.join(p[0].upper() + "." for p in parts)


def format_author(authors):
    """Crossref author records -> 'C.-C. Liu and S.-J. Chang'."""
    out = list()
    for a in authors:
        family = a.get("family", "").strip()
        given = a.get("given", "").strip()
        if not family:
            if a.get("name"):
                out.append(a["name"].strip())
            continue
        out.append(f"{initials(given)} {family}".strip())
    return " and ".join(out)


def make_key(author, year, taken):
    """<firstauthorlastname><yy>, suffixed a/b/... on collision."""
    first = author.split(" and ")[0] if author else "anon"
    last = re.sub(r"[^A-Za-z]", "", first.split()[-1] if first.split() else "anon")
    stem = (last.lower() or "anon") + str(year)[-2:]
    if stem not in taken:
        return stem
    for suffix in "abcdefghijklmnopqrstuvwxyz":
        if stem + suffix not in taken:
            return stem + suffix
    raise RuntimeError(f"cannot find a free key for {stem}")


def entry_type(work):
    kind = work.get("type", "")
    if "proceedings" in kind:
        return "inproceedings"
    # Order matters: a book-chapter is a chapter, not a book.
    if "chapter" in kind or "book-part" in kind or "book-section" in kind:
        return "incollection"
    # Crossref calls a whole book "monograph" as often as "book", and the
    # 'book' test alone left Razavi's PLL book typed as an article.
    if "book" in kind or "monograph" in kind:
        return "book"
    if "dissertation" in kind:
        return "phdthesis"
    return "article"


def fields_from_work(work):
    """Crossref work JSON -> the bib fields aic.bib uses."""
    fields = dict()
    fields["author"] = format_author(work.get("author", list()))

    title = work.get("title") or list()
    if title:
        fields["title"] = re.sub(r"\s+", " ", title[0]).strip()

    kind = entry_type(work)
    container = work.get("container-title") or list()
    if container and kind != "book":
        # A chapter's container is the book it sits in, not a journal.
        fields["booktitle" if kind in ("inproceedings", "incollection")
               else "journal"] = container[0]

    # A book has no journal to name it, so without this it lands in aic.bib
    # with nothing but a title and a year.
    if kind in ("book", "incollection") and work.get("publisher"):
        fields["publisher"] = work["publisher"]

    issued = work.get("issued", dict()).get("date-parts") or [[None]]
    if issued[0] and issued[0][0]:
        fields["year"] = str(issued[0][0])

    for src, dst in (("volume", "volume"), ("issue", "number"), ("page", "pages")):
        if work.get(src):
            fields[dst] = str(work[src])

    if work.get("DOI"):
        fields["doi"] = work["DOI"]

    return fields


def to_bibtex(key, kind, fields):
    """House style: one field per line, closed with '}' and no stray semicolon."""
    lines = [f"@{kind}{{{key},"]
    ordered = [f for f in FIELD_ORDER if fields.get(f)]
    ordered += [f for f in fields if f not in FIELD_ORDER and fields.get(f)]
    for i, name in enumerate(ordered):
        value = str(fields[name]).replace('"', "'").strip()
        comma = "," if i < len(ordered) - 1 else ""
        lines.append(f'{name}= "{value}"{comma}')
    lines.append("}")
    return "\n".join(lines) + "\n"


def swap_name(name):
    """'Ker, Ming-Dou' -> 'M.-D. Ker'. IEEE writes family-first."""
    if "," in name:
        family, given = name.split(",", 1)
        return f"{initials(given.strip())} {family.strip()}".strip()
    parts = name.split()
    if len(parts) < 2:
        return name.strip()
    return f"{initials(' '.join(parts[:-1]))} {parts[-1]}"


def parse_bibtex_entry(text):
    """One BibTeX entry -> (kind, fields). Handles IEEE's brace style."""
    m = re.search(r"@(\w+)\s*{\s*([^,]+),", text)
    if not m:
        return None, dict()
    kind = m.group(1).lower()

    fields = dict()
    body = text[m.end():]
    for fm in re.finditer(r"(\w+)\s*=\s*", body):
        rest = body[fm.end():].lstrip()
        if not rest or rest[0] not in "{\"":
            continue
        close = "}" if rest[0] == "{" else "\""
        depth = 0
        value = list()
        for c in rest:
            if c == "{":
                depth += 1
                if depth == 1:
                    continue
            elif c == "}":
                depth -= 1
                if depth == 0:
                    break
            elif c == "\"" and close == "\"":
                if value:
                    break
                continue
            value.append(c)
        fields[fm.group(1).lower()] = re.sub(r"\s+", " ", "".join(value)).strip()
    return kind, fields


def fields_from_ieee(raw):
    """IEEE's own BibTeX -> the fields and author style aic.bib uses."""
    fields = dict()

    if raw.get("author"):
        fields["author"] = " and ".join(
            swap_name(a) for a in re.split(r"\s+and\s+", raw["author"]))

    for name in ("title", "journal", "booktitle", "volume", "number",
                 "year", "pages", "doi"):
        if raw.get(name):
            fields[name] = raw[name]

    # IEEE emits empty volume/number on conference papers.
    return {k: v for k, v in fields.items() if v}


def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def get_json(url):
    return json.loads(get(url))


def xplore_headers(number):
    """Xplore answers 418 to anything that does not look like a browser."""
    return {
        "User-Agent": BROWSER_UA,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"https://ieeexplore.ieee.org/document/{number}",
    }


def fields_from_metadata(meta):
    """xplGlobal.document.metadata -> the fields aic.bib uses."""
    fields = dict()

    authors = meta.get("authors") or list()
    names = [a.get("name", "") for a in authors if a.get("name")]
    if names:
        fields["author"] = " and ".join(swap_name(n) for n in names)

    if meta.get("title"):
        fields["title"] = re.sub(r"<[^>]+>", "", meta["title"]).strip()

    container = meta.get("publicationTitle", "")
    if container:
        conference = "conference" in (meta.get("contentType", "") or "").lower()
        fields["booktitle" if conference else "journal"] = container

    for src, dst in (("volume", "volume"), ("issue", "number")):
        if meta.get(src):
            fields[dst] = str(meta[src])

    start, end = meta.get("startPage"), meta.get("endPage")
    if start and end:
        fields["pages"] = f"{start}-{end}"
    elif start:
        fields["pages"] = str(start)

    year = meta.get("publicationYear") or ""
    m = re.search(r"(\d{4})", str(meta.get("publicationDate", "")))
    fields["year"] = str(year) or (m.group(1) if m else "")

    if meta.get("doi"):
        fields["doi"] = meta["doi"]

    return {k: v for k, v in fields.items() if v}


def describe_page(html):
    """One line saying what Xplore actually served, for the unresolved list."""
    title = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    return (f"page was {len(html)} bytes"
            f", title {title.group(1).strip()[:60]!r}" if title
            else f"page was {len(html)} bytes, no <title>") + (
        ", has metadata blob" if "xplGlobal.document.metadata" in html
        else ", no metadata blob")


def scrape_metadata(html):
    """Pull the metadata blob Xplore inlines into every document page."""
    m = re.search(r"xplGlobal\.document\.metadata\s*=\s*(\{.*?\});\s*\n",
                  html, re.S)
    if not m:
        return dict()
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return dict()


def ieee_by_arnumber(number):
    """What the 'Cite This' button downloads, keyed by article number.

    This cannot return a different paper the way a title search can -- the
    article number is the one the lecture links to. Xplore sits behind bot
    protection and answers 418 to a plain client, so try the citation
    endpoint the button uses, then the metadata the document page inlines.
    Both are allowed to fail; Crossref is the fallback.
    """
    url = ("https://ieeexplore.ieee.org/rest/search/citation/format"
           f"?recordIds={number}&download-format=download-bibtex"
           "&citations-format=citation-only")
    try:
        payload = json.loads(get(url, headers=xplore_headers(number)))
        text = payload.get("data", "")
        if text.strip():
            # The endpoint escapes newlines inside the JSON string.
            kind, raw = parse_bibtex_entry(text.replace("\\n", "\n"))
            fields = fields_from_ieee(raw)
            if fields.get("title"):
                return kind, fields
    except (urllib.error.HTTPError, json.JSONDecodeError):
        pass

    page = get(f"https://ieeexplore.ieee.org/document/{number}",
               headers=dict(xplore_headers(number), Accept="text/html"))
    fields = fields_from_metadata(scrape_metadata(page))
    if not fields.get("title"):
        # Distinguish "Xplore served an interstitial" from "the page was fine
        # and the parse missed", which need completely different fixes.
        raise LookupError(describe_page(page))
    kind = "inproceedings" if fields.get("booktitle") else "article"
    return kind, fields


def crossref_by_title(title):
    """Best Crossref match for a title, or None if nothing is close enough."""
    query = {"query.bibliographic": title, "rows": "3"}
    if CONTACT:
        query["mailto"] = CONTACT
    data = get_json("https://api.crossref.org/works?" + urlencode(query))

    best = None
    best_score = 0.0
    for item in data.get("message", dict()).get("items", list()):
        candidate = (item.get("title") or [""])[0]
        score = similarity(title, candidate)
        if score > best_score:
            best, best_score = item, score
    if best is not None and best_score >= TITLE_THRESHOLD:
        return best, best_score
    return None, best_score


def crossref_by_doi(doi):
    if CONTACT:
        url = f"https://api.crossref.org/works/{doi}?" + urlencode({"mailto": CONTACT})
    else:
        url = f"https://api.crossref.org/works/{doi}"
    return get_json(url).get("message")


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


@cli.command()
@click.option("--lectures", default="lectures/*.md", help="Glob of lectures to scan")
@click.option("--bib", default="pdf/aic.bib", help="Bibliography to dedupe against")
@click.option("--out", default="pdf/incoming.bib", help="Staged entries go here")
@click.option("--unresolved", default="pdf/link_unresolved.tsv",
              help="Candidates needing a hand-fetch from Xplore")
@click.option("--limit", default=0, help="Stop after N papers (0 = all)")
@click.option("--delay", default=1.0, help="Seconds between API calls")
@click.option("--source", default="both",
              type=click.Choice(["both", "ieee", "crossref"]),
              help="Where to resolve from. 'both' tries Xplore first.")
def fetch(lectures, bib, out, unresolved, limit, delay, source):
    """Resolve candidate links to bib entries. Needs network."""

    papers = group(scan_lectures(lectures))
    known_titles = read_bib_titles(bib)
    taken, known_dois = read_bib_keys(bib)

    staged = list()
    missed = list()
    skipped = 0
    errors = 0

    # Candidates whose link text is a real title first. Scan order is lecture
    # order, and the early lectures are exactly the ones that link from prose
    # ("[diffusion](...)"), so a --limit run down the raw list tests only the
    # candidates that cannot resolve and tells you nothing.
    def resolvable_first(item):
        hits = item[1]
        best = max(hits, key=lambda h: len(h.text))
        return (0 if doi_from_url(best.url) or looks_like_a_title(best.text)
                else 1, best.lecture, best.line)

    todo = sorted(papers.items(), key=resolvable_first)
    if limit:
        todo = todo[:limit]

    for ident, hits in todo:
        # The best link text is the longest: some occurrences are a bare URL
        # or a single word of prose, others are the full paper title.
        hit = max(hits, key=lambda h: len(h.text))
        title = hit.text.strip()

        if squash(title) in known_titles:
            skipped += 1
            continue

        reason = ""
        kind = None
        fields = dict()
        origin = ""
        ieee_note = ""

        # IEEE first when the link names an article number. That lookup is by
        # identity rather than by title, so it cannot come back with a
        # different paper -- which is the one failure mode a title search has.
        ar = arnumber(hit.url)
        if ar and source in ("ieee", "both"):
            try:
                kind, fields = ieee_by_arnumber(ar)
                origin = "ieee"
                if not fields:
                    reason = f"Xplore returned nothing for {ar}"
                    ieee_note = reason
            except (urllib.error.URLError, TimeoutError, LookupError,
                    json.JSONDecodeError, UnicodeDecodeError) as e:
                reason = f"Xplore lookup failed: {e}"
                ieee_note = reason
                # Xplore is behind bot protection and is allowed to fail when
                # Crossref can still pick it up. With --source ieee there is
                # no fallback, so the run really did fail.
                if source == "ieee":
                    errors += 1

        if not fields and source in ("crossref", "both"):
            try:
                doi = doi_from_url(hit.url)
                if doi:
                    work = crossref_by_doi(doi)
                    reason = "" if work else f"DOI {doi} unknown to Crossref"
                elif not looks_like_a_title(title):
                    # Prose links like "[diffusion](...)", and the handful
                    # whose text is just the URL, carry nothing to match on.
                    work, reason = None, "link text is not a title"
                else:
                    work, score = crossref_by_title(title)
                    if work is None:
                        reason = f"best Crossref match scored {score:.2f}"
                if work is not None:
                    kind, fields = entry_type(work), fields_from_work(work)
                    origin = "crossref"
                    reason = ""
            except (urllib.error.URLError, TimeoutError,
                    json.JSONDecodeError) as e:
                reason = f"lookup failed: {e}"
                errors += 1

        if not fields:
            missed.append((hit, reason))
            click.echo(f"  miss  {hit.lecture:22s} {reason}", err=True)
        elif fields.get("doi", "").lower() in known_dois:
            skipped += 1
        else:
            key = make_key(fields.get("author", ""), fields.get("year", ""), taken)
            taken.add(key)
            if fields.get("doi"):
                known_dois.add(fields["doi"].lower())
            # A lookup by article number is trusted on identity, so it does
            # not need the title to match. A title search does.
            exact = (origin == "ieee"
                     or squash(fields.get("title", "")) == squash(title))
            staged.append((key, kind or "article", fields, hits, exact, title,
                           origin, ieee_note))
            mark = "ok   " if exact else "check"
            click.echo(f"  {mark} {key:14s} [{origin}] {fields.get('title','')[:52]}")

        time.sleep(delay)

    with open(out, "w") as fo:
        fo.write("% Staged by py/linkbib.py fetch -- review before merging into aic.bib.\n")
        fo.write("% The comment above each entry lists the lectures that link to it.\n")
        fo.write("% CHECK marks an entry whose Crossref title is not identical to the\n")
        fo.write("% link text. Crossref will happily return a different paper whose title\n")
        fo.write("% merely contains the one you asked for, and no similarity threshold\n")
        fo.write("% separates those from a genuine punctuation difference. Read both\n")
        fo.write("% titles before merging a CHECK entry.\n\n")
        for key, kind, fields, hits, exact, asked, origin, note in staged:
            where = ", ".join(sorted({f"{h.lecture}:{h.line}" for h in hits}))
            fo.write(f"% {where}\n")
            fo.write(f"% source: {origin}" + (f" -- {note}\n" if note else "\n"))
            if not exact:
                fo.write(f"% CHECK  lecture says: {asked}\n")
                fo.write(f"% CHECK  Crossref says: {fields.get('title', '')}\n")
            fo.write(to_bibtex(key, kind, fields))
            fo.write("\n")

    with open(unresolved, "w") as fo:
        fo.write("lecture\tline\ttext\turl\treason\n")
        for hit, reason in missed:
            fo.write(f"{hit.lecture}\t{hit.line}\t{hit.text}\t{hit.url}\t{reason}\n")

    tocheck = len([s for s in staged if not s[4]])

    click.echo("")
    click.echo(f"staged     : {len(staged)} -> {out}")
    click.echo(f"  of those, needing a title check: {tocheck}")
    click.echo(f"unresolved : {len(missed)} -> {unresolved}")
    click.echo(f"already in {bib}: {skipped}")

    # A link whose text is not a title, or a Crossref hit that scored too low,
    # is an expected outcome that needs a human -- not a broken run. Only a
    # lookup that actually failed means the job could not do its job.
    if errors:
        click.echo(f"lookups failed  : {errors}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
