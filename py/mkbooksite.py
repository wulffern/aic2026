#!/usr/bin/env python3
"""Assemble the book-style site prototype in docs-book/.

Takes the already generated Jekyll posts in docs/_posts and rewrites them
as ordered just-the-docs pages in docs-book/chapters/, one per lecture,
in the order of the FILES list in the root Makefile. Assets are shared
with docs/ through a copy.

Usage: python3 py/mkbooksite.py
"""

import os
import re
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "docs", "_posts")
BOOK = os.path.join(ROOT, "docs-book")
CHAPTERS = os.path.join(BOOK, "chapters")


def makefile_files():
    out = subprocess.check_output(
        ["make", "-s", "--no-print-directory", "print-files"], cwd=ROOT, text=True
    )
    return out.split()


def post_lecture_id(text):
    """The lecture id is in the PDF download link of every post."""
    m = re.search(r"/assets//?([a-z0-9_]+)\.pdf", text)
    return m.group(1) if m else None


# top level pages from docs/, in sidebar order ahead of the chapters
PAGES = ["plan", "syllabus", "downloads", "examples", "about"]

# titles for decks that are not lectures (the s_* standalone decks)
DECK_TITLES = {
    "s_exam": "Exam notes",
    "s_maxwell": "Maxwell",
    "s_need_to_know": "Need to know",
    "s_mac": "Analog neural networks (MAC)",
    "s_chinf": "Channel information",
    "s_tut2": "Tutorial 2",
    "s_project_scratch": "Project scratch",
    "tex_intro": "LaTeX introduction",
}


def front_matter(text):
    m = re.search(r"^---\n(.*?)\n---\n", text, re.S)
    return m.group(1), text[m.end():]


# just-the-docs' collapsible in-page TOC, replacing the wall of links the
# kramdown TOC painted at the top of every chapter. The sidebar and the
# anchored headings do the heavy lifting; this stays folded until asked.
JTD_TOC = """<details markdown="block">
  <summary>Table of contents</summary>
  {: .text-delta }
- TOC
{:toc}
</details>"""


def fold_toc(body):
    return re.sub(r"\*\s*TOC\s*\n\{:toc\s*\}", JTD_TOC, body)


def nav_title(heading):
    """A sidebar-safe title from a markdown heading: no math, no markup."""
    t = heading.strip()
    t = re.sub(r"\$\$?([^$]*)\$\$?", r"\1", t)     # drop math markers
    t = re.sub(r"\\[a-zA-Z]+", "", t)              # latex commands
    t = t.replace("{", "").replace("}", "").replace("_", "")
    t = re.sub(r"\s+", " ", t).strip()
    return t or heading.strip()


def split_sections(body):
    """Split a chapter body on its top level '# ' headings.

    Returns (preamble, [(heading, section_body), ...]). Fenced code blocks
    are respected so a '# comment' inside code does not split anything.
    """
    lines = body.split("\n")
    sections = []
    current = []
    heading = None
    preamble = []
    in_code = False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if not in_code and re.match(r"# [^#]", line):
            if heading is None:
                preamble = current
            else:
                sections.append((heading, current))
            heading = line[2:].strip()
            current = []
        else:
            current.append(line)
    if heading is None:
        preamble = current
    else:
        sections.append((heading, current))
    return "\n".join(preamble), [(h, "\n".join(c)) for h, c in sections]


def footnote_defs(body):
    """The kramdown footnote definitions of a chapter, one block."""
    return re.findall(r"^\[\^[^\]]+\]:.*(?:\n(?!\[\^|\n).*)*", body, re.M)


def write_chapter(n, lid, title, permalink, body):
    """One chapter as a parent page with its main headers as children.

    The sidebar gets the theme's expander arrow on the chapter, opening
    to the top level sections. Content under a first heading that just
    repeats the chapter title stays on the parent page.
    """
    preamble, sections = split_sections(body)
    if sections and nav_title(sections[0][0]).lower() == title.lower():
        preamble += "\n" + sections[0][1]
        sections = sections[1:]

    # a chapter without real sections stays a single page
    if len(sections) < 2:
        write_page(os.path.join(CHAPTERS, f"{n:02d}_{lid}.md"),
                   title, n + 10, permalink, body)
        return 1

    defs = footnote_defs(body)

    front = "\n".join([
        "---", "layout: default", f"title: {title}",
        f"nav_order: {n + 10}", f"permalink: {permalink}",
        "has_children: true", "has_toc: false", "---", "",
    ])
    with open(os.path.join(CHAPTERS, f"{n:02d}_{lid}.md"), "w") as fo:
        fo.write(front + fold_toc(preamble))

    seen = {}
    for i, (heading, sbody) in enumerate(sections, start=1):
        stitle = nav_title(heading)
        if stitle.lower() in seen or stitle.lower() == title.lower():
            seen[stitle.lower()] = seen.get(stitle.lower(), 1) + 1
            stitle = f"{stitle} ({seen[stitle.lower()]})"
        else:
            seen[stitle.lower()] = 1
        slug = re.sub(r"[^a-z0-9]+", "-", stitle.lower()).strip("-")
        # keep the original heading in the page, and re-attach the
        # chapter's footnote definitions where they are referenced
        text = f"# {heading}\n{sbody}"
        if defs and re.search(r"\[\^[^\]]+\](?!:)", sbody):
            for d in defs:
                if d not in sbody:
                    text += "\n\n" + d
        front = "\n".join([
            "---", "layout: default", f"title: {stitle}",
            f"parent: {title}", f"nav_order: {i}",
            f"permalink: {permalink}/{slug}/", "---", "",
        ])
        with open(os.path.join(CHAPTERS, f"{n:02d}_{lid}_{i:02d}.md"), "w") as fo:
            fo.write(front + fold_toc(text))
    return 1 + len(sections)


def write_page(path, title, nav_order, permalink, body):
    front = "\n".join(
        [
            "---",
            "layout: default",
            f"title: {title}",
            f"nav_order: {nav_order}",
            f"permalink: {permalink}",
            "---",
            "",
        ]
    )
    with open(path, "w") as fo:
        fo.write(front + fold_toc(body))


def make_pages():
    pagedir = os.path.join(BOOK, "pages")
    os.makedirs(pagedir, exist_ok=True)
    for f in os.listdir(pagedir):
        os.remove(os.path.join(pagedir, f))

    # the landing page keeps the current site's content
    with open(os.path.join(ROOT, "docs", "index.md")) as fi:
        _, body = front_matter(fi.read())
    write_page(os.path.join(BOOK, "index.md"), "Home", 0, "/", body)

    n = 0
    for name in PAGES:
        src = os.path.join(ROOT, "docs", f"{name}.md")
        if not os.path.exists(src):
            print(f"no page found for: {name}")
            continue
        with open(src) as fi:
            head, body = front_matter(fi.read())
        title = re.search(r"title:\s*(.*)", head).group(1).strip()
        perm = re.search(r"permalink:\s*(.*)", head).group(1).strip()
        n += 1
        write_page(os.path.join(pagedir, f"{n:02d}_{name}.md"), title, n, perm, body)
    print(f"wrote {n + 1} pages to docs-book/")


def main():
    make_pages()
    os.makedirs(CHAPTERS, exist_ok=True)
    for f in os.listdir(CHAPTERS):
        os.remove(os.path.join(CHAPTERS, f))

    posts = {}
    for fname in sorted(os.listdir(POSTS)):
        if not fname.endswith(".markdown"):
            continue
        with open(os.path.join(POSTS, fname)) as fi:
            text = fi.read()
        lid = post_lecture_id(text)
        if lid:
            posts[lid] = text

    order = [f for f in makefile_files() if f in posts]
    missing = set(makefile_files()) - set(order)
    if missing:
        print("no post found for: " + " ".join(sorted(missing)))

    # posts outside the FILES list (guest lectures etc.) keep their URLs:
    # they go in after the ordered chapters
    extras = sorted(set(posts) - set(order))
    if extras:
        print("extra posts appended: " + " ".join(extras))
    order += extras

    npages = 0
    for n, lid in enumerate(order, start=1):
        text = posts[lid]
        head, body = front_matter(text)
        title = re.search(r"title:\s*(.*)", head).group(1).strip()
        permalink = re.search(r"permalink:\s*(.*)", head).group(1).strip()
        # chapters sort after the top level pages in the sidebar
        npages += write_chapter(n, lid, title, permalink, body)
    print(f"wrote {len(order)} chapters ({npages} pages) to docs-book/chapters/")

    make_slides_page(order, posts)


def make_slides_page(order, posts):
    """One page linking every HTML slide deck."""
    htmldir = os.path.join(ROOT, "docs", "assets", "html")
    if not os.path.isdir(htmldir):
        print("no docs/assets/html - skipping the slides page")
        return
    decks = {f[:-5] for f in os.listdir(htmldir) if f.endswith(".html")}

    lines = ["Every lecture as an HTML slide deck - scroll, swipe or use the",
             "arrow keys; `f` is fullscreen.", ""]
    listed = set()
    for lid in order:
        if lid not in decks:
            continue
        title = re.search(r"title:\s*(.*)", posts[lid]).group(1).strip()
        lines.append(f"- [{title}](/aic2026/assets/html/{lid}.html)")
        listed.add(lid)

    extras = sorted(decks - listed)
    if extras:
        lines += ["", "## Other decks", "",
                  "Not part of the lecture series or the book.", ""]
        for lid in extras:
            title = DECK_TITLES.get(lid, lid)
            lines.append(f"- [{title}](/aic2026/assets/html/{lid}.html)")

    write_page(
        os.path.join(BOOK, "pages", "06_slides.md"),
        "Slides", 6, "/slides/", "\n".join(lines) + "\n",
    )
    print(f"wrote slides page with {len(listed)} decks + {len(extras)} extras")

    # keep the 404 page working
    src404 = os.path.join(ROOT, "docs", "404.html")
    if os.path.exists(src404):
        with open(src404) as fi:
            _, body = front_matter(fi.read())
        with open(os.path.join(BOOK, "404.html"), "w") as fo:
            fo.write("---\nlayout: default\npermalink: /404.html\n"
                     "nav_exclude: true\n---\n" + body)

    # share the assets with the existing site - except the old theme's
    # stylesheet, which imports minima and breaks the just-the-docs build
    src = os.path.join(ROOT, "docs", "assets")
    dst = os.path.join(BOOK, "assets")
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
        css = os.path.join(dst, "css")
        if os.path.isdir(css):
            shutil.rmtree(css)
        print("copied docs/assets -> docs-book/assets (minus css/)")


if __name__ == "__main__":
    main()
