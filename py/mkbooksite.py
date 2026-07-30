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


def main():
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

    for n, lid in enumerate(order, start=1):
        text = posts[lid]
        m = re.search(r"^---\n(.*?)\n---\n", text, re.S)
        head, body = m.group(1), text[m.end():]
        title = re.search(r"title:\s*(.*)", head).group(1).strip()
        permalink = re.search(r"permalink:\s*(.*)", head).group(1).strip()

        front = "\n".join(
            [
                "---",
                "layout: default",
                f"title: {title}",
                f"nav_order: {n}",
                f"permalink: {permalink}",
                "---",
                "",
            ]
        )
        out = os.path.join(CHAPTERS, f"{n:02d}_{lid}.md")
        with open(out, "w") as fo:
            fo.write(front + body)
    print(f"wrote {len(order)} chapters to docs-book/chapters/")

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
