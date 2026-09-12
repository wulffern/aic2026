#!/usr/bin/env python3
"""Assemble the text edition of the book, for readers that are machines.

The site, the PDF and the EPUB are all built for people. This builds the
same content as Markdown a language model can fetch and reason over, in
the llms.txt shape:

  docs-book/llms.md         the index: every chapter, linked and described
  docs-book/llms-full.md    the whole book, one document
  docs-book/txt/<id>.md     one chapter, for a reader that wants only one

Each of the first two is written twice, once as .md and once as .txt:
the content is Markdown, but the llms.txt convention puts the .txt name
at the site root and that is where an agent will look for it. Everything
is wrapped to 80 columns by py/mdwrap.py.

Input is the per-lecture .build/<id>.llm.md written by
`python3 py/lecture.py text`, taken in the order of the FILES list in the
root Makefile — the same order as the printed book.

Usage: python3 py/mkllms.py
"""

import datetime
import os
import re
import statistics
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mdwrap  # noqa: E402
from lecture import Bibtex, aic_version  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, ".build")
BOOK = os.path.join(ROOT, "docs-book")
TXT = os.path.join(BOOK, "txt")

SITE = f"https://wulffern.github.io/{aic_version}"

TITLE = "Advanced Integrated Circuits"
SUMMARY = (
    "Lecture notes for TFE4188 Advanced Integrated Circuits at NTNU, on the "
    "design of analog and mixed-signal integrated circuits in CMOS: "
    "references and bias, data converters, switched capacitor circuits, "
    "voltage regulators, phase locked loops, oscillators and low power "
    "radio, with the device physics and circuit theory they rest on."
)

#- Chapters are listed in the order of the Makefile FILES list, which is
#  the order of the book. The site sidebar groups them into Lectures,
#  Refreshers and Background instead (py/mkbooksite.py), which suits a
#  reader browsing for a topic; a reader working through the book wants
#  the order the book is in.
def files_list():
    out = subprocess.check_output(
        ["make", "-s", "--no-print-directory", "print-files"], cwd=ROOT,
        text=True)
    return out.split()


def split_title(text):
    """The chapter title, and the body under it."""
    m = re.match(r"#\s+(.*?)\n+(.*)$", text, re.S)
    if not m:
        return None, text
    return m.group(1).strip(), m.group(2)


#- The line CLAUDE.md asks for on drafted chapters. True of the chapter,
#  but it says nothing about what the chapter is about.
ATTRIBUTION = re.compile(r"(written|pictures) by", re.I)


def blurb(body):
    """One line saying what the chapter is about, for the index."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", body)]

    #- The whole paragraph, not one line of it: the body is wrapped to 80
    #  columns, so a long keyword list runs over several lines and a
    #  line-anchored match would keep only the first few keywords.
    for para in paras:
        if para.startswith("**Keywords:**"):
            kw = re.sub(r"\s+", " ", para[len("**Keywords:**"):]).strip()
            if kw:
                return kw.rstrip(" ,.")
            break

    #- No keywords, so the opening sentence of the first real paragraph.
    for para in paras:
        #- A leading * is either the attribution aside or a bold label
        #  such as an empty **Keywords:** line. Neither says anything
        #  about the chapter.
        if not para or para.startswith(("#", "[FIGURE", "Caption:", "|", ">",
                                        "<", "!", "$$", "*")):
            continue
        if ATTRIBUTION.search(para[:120]):
            continue
        para = re.sub(r"\s+", " ", para)
        s = re.split(r"(?<=[.!?])\s", para)[0]
        return s.strip().rstrip(" ,.")
    return ""


def demote(body):
    """Push every heading down one level, so chapters can own H1.

    Fences are tracked because a # inside a listing is a comment in some
    language, not a heading, and demoting it would edit the code.
    """
    out = []
    fence = None
    for line in body.split("\n"):
        m = re.match(r"^\s*(```+|~~~+)", line)
        if m:
            tok = m.group(1)[0] * 3
            fence = None if fence == tok else (fence or tok)
            out.append(line)
            continue
        if fence is None and re.match(r"^#{1,5}\s", line):
            line = "#" + line
        out.append(line)
    return "\n".join(out)


def cited_keys(text):
    """Every bibtex key referenced, in order of first appearance."""
    keys = []
    #- The lookbehind keeps an email address out of the bibliography:
    #  carsten@wulff.no is not a citation of wulff.no.
    for m in re.finditer(r"(?<![A-Za-z0-9_.])@([A-Za-z][A-Za-z0-9_:.#$%&+?<>~/-]*)",
                         text):
        k = m.group(1)
        if k not in keys:
            keys.append(k)
    return keys


def references(bib, text):
    """The bibliography for one text: only what it actually cites."""
    lines = []
    for k in cited_keys(text):
        if k not in bib:
            continue
        item = bib[k]
        parts = []
        if "author" in item:
            parts.append(item["author"])
        if "title" in item:
            parts.append('"' + item["title"] + '"')
        if "year" in item:
            parts.append(item["year"])
        if "url" in item:
            parts.append(item["url"])
        elif "doi" in item:
            parts.append("https://doi.org/" + item["doi"])
        lines.append(f"- [@{k}]: " + ", ".join(parts))
    return lines


#- What a reader has to know to make sense of the two things this edition
#  does differently from the book: it has no pictures, and it leaves the
#  citation keys alone.
CONVENTIONS = (
    "Figures are drawings, and this edition has none. Each figure appears\n"
    "as a block delimited by [FIGURE <name>] and [/FIGURE], holding the\n"
    "caption from the book and, where one has been written, a description\n"
    f"of what the figure shows. The drawing itself is at\n"
    f"{SITE}/assets/media/<name>.svg\n\n"
    "Citations are left as [@key], resolved in the References section.\n"
)


def preamble(what, conventions=True):
    today = datetime.date.today().isoformat()
    #- A list, not a run of bare lines: everything here is rewrapped to
    #  80 columns, and a run of bare lines is one paragraph to a wrapper,
    #  so Author, Course and Edition would end up in the same sentence.
    ss = (f"# {TITLE}\n\n"
          f"> {SUMMARY}\n\n"
          f"- Author: Carsten Wulff <carsten@wulff.no>\n"
          f"- Course: TFE4188 Advanced Integrated Circuits, NTNU\n"
          f"- Edition: {aic_version}, generated {today}\n"
          f"- Licence: CC BY 4.0\n"
          f"- Source: https://github.com/wulffern/{aic_version}\n"
          f"- Site: {SITE}/\n\n"
          f"{what}\n")
    if conventions:
        ss += "\n" + CONVENTIONS
    return ss


#- Marks where a chapter starts. Unique per chapter, unlike the title,
#  and mdwrap leaves a line opening with < alone, so it survives the
#  rewrap and can be found again to number the contents.
MARK = "<!-- chapter: %s |"


def _headings(body_lines, chapters):
    """Line index of each chapter heading in the assembled body."""
    at, last = {}, None
    for i, line in enumerate(body_lines):
        if line.startswith("# "):
            last = i
        for lid, _, _ in chapters:
            if line.startswith(MARK % lid):
                at[lid] = last if last is not None else i
                break
    for i, line in enumerate(body_lines):
        if line == "# References":
            at["__refs__"] = i
    return at


def contents(at, chapters):
    """A table of contents with the line number of every chapter.

    The numbers point into the finished file, so a reader can jump
    straight to a chapter with sed or an editor instead of scrolling
    through a megabyte. Indented four spaces, which keeps the columns
    aligned: py/mdwrap.py leaves an indented block alone. The field is a
    fixed width so the block is exactly as tall whatever the numbers
    are, which is what lets the numbering converge.
    """
    #- Hand-wrapped: the contents is assembled after py/mdwrap.py has run
    #  and is never passed through it, because rewrapping would pull the
    #  indented block out of alignment.
    out = ["## Contents", "",
           "Chapters in the order of the book. Line numbers are into this "
           "file, and each",
           "chapter also starts with a level 1 heading, so searching for the "
           "title works too.", ""]
    for lid, title, _ in chapters:
        out.append(f"    {at.get(lid, 0) + 1:>7}  {title}")
    out.append(f"    {at.get('__refs__', 0) + 1:>7}  References")
    return "\n".join(out)


def assemble(head, body, chapters):
    """head + contents + body, with the contents numbered for the result.

    The contents pushes the body down, which changes the numbers the
    contents holds. Rather than predict the shift, measure it: build the
    document, read the real line numbers out of it, rebuild, and stop
    when the contents stops changing.
    """
    def build(toc):
        return head + "\n" + toc + "\n\n" + body

    toc = contents({}, chapters)
    for _ in range(6):
        doc = build(toc)
        new = contents(_headings(doc.split("\n"), chapters), chapters)
        if new == toc:
            return doc
        toc = new
    return build(toc)


def _kb(n):
    return f"{round(n / 1024):,} kB"


def _tokens(n):
    """A rough token count, for deciding whether something will fit.

    Four characters to the token is the usual rule for English prose. It
    understates a book this full of LaTeX maths, so it is offered as an
    order of magnitude and said to be one.
    """
    return f"~{round(n / 4000):,}k tokens"


def howto(doc, sizes):
    """What an agent needs to decide what to fetch, before fetching it.

    The one thing a reader cannot work out from a list of links is how
    much any of them costs. Without that, an agent either pulls a
    megabyte to answer a question about one chapter, or never pulls
    anything. So: the sizes, and where the map is in the big file.
    """
    lines = doc.split("\n")
    start = end = None
    for i, line in enumerate(lines):
        if line == "## Contents":
            start = i + 1
        elif start and re.match(r"^#{1,2} [^C]", line):
            end = i - 1
            break
    end = end or len(lines)

    return "\n".join([
        "## How to read this",
        "",
        #- The median as well as the range: the smallest chapter is a
        #  four-question FAQ, and quoting it alone as "from 1 kB" would
        #  suggest a chapter is cheaper than it usually is.
        f"- Chapters run from {_kb(min(sizes))} to {_kb(max(sizes))}, median "
        f"{_kb(statistics.median(sizes))}. If you know which chapter answers "
        "the question, fetch that one and stop.",
        f"- The complete text is {_kb(len(doc))}, {_tokens(len(doc))}. Fetch "
        "it only to search across chapters, and expect it to be a large "
        "fraction of a context window.",
        f"- Lines {start}-{end} of llms-full.md are its table of contents, "
        "which gives the line number every chapter starts at. Reading that "
        "range first lets you seek to a chapter instead of reading forward "
        "to it.",
        "- Every chapter is also a level 1 heading in llms-full.md, so "
        "searching for a title from the list below works as well.",
    ])


def publish(name, text):
    """Write the document under both names it needs.

    The content is Markdown, so .md is what it should be called and what
    an editor or a forge will highlight. The llms.txt convention asks for
    the .txt name at the site root, and an agent looking for the book
    will look there, so the same bytes are written twice.
    """
    for ext in (".md", ".txt"):
        with open(os.path.join(BOOK, name + ext), "w") as fo:
            fo.write(text)


def main():
    os.makedirs(TXT, exist_ok=True)
    for f in os.listdir(TXT):
        os.remove(os.path.join(TXT, f))

    bib = Bibtex(os.path.join(ROOT, "pdf", "aic.bib"))
    order = files_list()
    chapters = []
    missing = []
    sizes = []

    for lid in order:
        path = os.path.join(BUILD, lid + ".llm.md")
        if not os.path.exists(path):
            missing.append(lid)
            continue
        with open(path) as fi:
            text = fi.read()
        title, body = split_title(text)
        if title is None:
            title = lid
        chapters.append((lid, title, body))

        #- A chapter is read on its own, so it carries the conventions,
        #  says which book it came out of, and resolves its own
        #  citations rather than pointing at a section it does not have.
        chapter_refs = references(bib, body)
        chapter = (f"# {title}\n\n"
                   f"<!-- {TITLE} ({aic_version}) by Carsten Wulff, "
                   f"CC BY 4.0. Chapter {lid}.\n"
                   f"     The whole book: {SITE}/llms-full.md -->\n\n"
                   + CONVENTIONS + "\n"
                   + body.strip() + "\n")
        if chapter_refs:
            chapter += "\n## References\n\n" + "\n".join(chapter_refs) + "\n"
        chapter = mdwrap.wrap(chapter)
        sizes.append(len(chapter))
        with open(os.path.join(TXT, lid + ".md"), "w") as fo:
            fo.write(chapter)

    if missing:
        print("mkllms: no .build/<id>.llm.md for "
              + ", ".join(missing) + " - run `make texts`")

    #- The whole book
    full = []
    for lid, title, body in chapters:
        full.append(f"# {title}\n\n"
                    f"{MARK % lid} {SITE}/txt/{lid}.md -->\n\n"
                    + demote(body).strip() + "\n\n")

    body_text = "".join(full)
    refs = references(bib, body_text)
    if refs:
        body_text += "# References\n\n" + "\n".join(refs) + "\n"

    head = mdwrap.wrap(preamble(
        "This is the complete text. The per-chapter files are at "
        f"{SITE}/txt/<id>.md\nand the index at {SITE}/llms.md"))
    body_text = mdwrap.wrap(body_text).strip()

    doc = assemble(head, body_text, chapters) + "\n"
    publish("llms-full", doc)

    #- The index
    idx = [preamble(
        "This is the index. Each chapter below links to its own Markdown "
        f"file.\nThe complete text in one file is at {SITE}/llms-full.md",
        conventions=False)]
    idx.append("\n\n" + howto(doc, sizes) + "\n")
    idx.append("\n\n## Chapters\n\n")
    idx.append("In the order of the book.\n\n")
    for lid, title, body in chapters:
        b = blurb(body)
        idx.append(f"- [{title}]({SITE}/txt/{lid}.md)"
                   + (f": {b}\n" if b else "\n"))

    idx.append("\n## Optional\n\n")
    idx.append(f"- [Complete text]({SITE}/llms-full.md): "
               "every chapter in one file\n")
    idx.append(f"- [PDF book]({SITE}/assets/aic.pdf): "
               "the typeset edition, with the figures\n")
    idx.append(f"- [EPUB book]({SITE}/assets/aic.epub): "
               "the same, as an ebook\n")

    publish("llms", mdwrap.wrap(re.sub(r"\n{3,}", "\n\n", "".join(idx))))

    nfig = body_text.count("\n[FIGURE ")
    ndesc = body_text.count("\nDescription: ")
    print(f"mkllms: {len(chapters)} chapters, {nfig} figures "
          f"({ndesc} described), {len(refs)} references, "
          f"{len(body_text) // 1024} kB")


if __name__ == "__main__":
    main()
