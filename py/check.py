#!/usr/bin/env python3
"""Mechanical correctness checks for the lecture sources and generated output.

Runs in a couple of seconds with no TeX. Exits non-zero on the first class of
problem found, so CI fails the push instead of the site shipping it:

 1. every image a lecture references exists on disk (local paths only)
 2. every [@key] citation exists in pdf/aic.bib
 3. every lecture has balanced $$ display-math fences
 4. every lectures/*.md is either built (in the Makefile FILES list) or
    explicitly listed as excluded below
 5. generated posts (docs/_posts) contain no leftover Deckset directives
    and no duplicate/undefined footnotes -- skipped with a note if the posts
    have not been generated

Run as: python3 py/check.py   (from the repo root, same as py/lecture.py)
"""

import collections
import glob
import os
import re
import subprocess
import sys

#- Lectures that exist but are deliberately not built. Anything new in
#  lectures/ that is neither here nor in FILES fails check 4, so a lecture
#  cannot silently rot outside the build.
#  s_* are standalone decks: not part of the lecture series or the book,
#  but rendered to HTML slides (see SLIDEFILES in the Makefile).
EXCLUDED = {
    "g00_m1p1",         # guest lectures, slides live elsewhere
    "g01_m1p2",
    "g03",
    "lp_radio_guest",
    "s_chinf",
    "s_exam",
    "s_mac",
    "s_maxwell",
    "s_need_to_know",
    "s_project_scratch",
    "s_teach",
    "s_tut2",
    "tex_intro",        # book front matter, built via texfiles, not FILES
}

DECKSET_DIRECTIVE = re.compile(r"\[\.[a-zA-Z-]+[^\]]*\]")

errors = []


def err(msg):
    errors.append(msg)
    print("FAIL:", msg)


def files_list():
    #- -s / --no-print-directory: when check.py itself runs under make (make
    #  check), the sub-make otherwise prints "make[1]: Entering directory ..."
    #  lines into the output.
    out = subprocess.check_output(
        ["make", "-s", "--no-print-directory", "print-files"], text=True)
    return [f for f in out.split() if f]


def check_lectures(files):
    bib = set(re.findall(r"@\w+\{([^,\s]+)\s*,", open("pdf/aic.bib").read()))

    for f in files:
        path = f"lectures/{f}.md"
        if not os.path.exists(path):
            err(f"{path} is in FILES but does not exist")
            continue
        text = open(path).read()

        #- 1. local image references resolve
        for m in re.finditer(r"!\[[^\]]*\]\(([^)\s]+)", text):
            src = m.group(1)
            if src.startswith("http"):
                continue
            if not os.path.exists(os.path.join("lectures", src)):
                err(f"{path}: image {src} not found")

        #- 2. citations exist
        for m in re.finditer(r"\[@([^\]]+)\]", text):
            if m.group(1) not in bib:
                err(f"{path}: citation @{m.group(1)} not in pdf/aic.bib")

        #- 3. balanced display math
        if text.count("$$") % 2:
            err(f"{path}: odd number of $$ fences")


def check_coverage(files):
    built = set(files) | EXCLUDED
    for path in sorted(glob.glob("lectures/*.md")):
        name = os.path.basename(path)[:-3]
        if name not in built:
            err(f"{path} is neither in the Makefile FILES list nor in "
                "the EXCLUDED set in py/check.py")


def check_posts():
    posts = sorted(glob.glob("docs/_posts/*.markdown"))
    if not posts:
        print("note: docs/_posts is empty, run `make posts-parallel` first "
              "to check the generated output")
        return
    for path in posts:
        text = open(path).read()

        #- 5a. Deckset directives must not survive into published output.
        #  Skip HTML comments: a commented-out ![left](...) is harmless.
        for line in text.splitlines():
            if line.lstrip().startswith("<!--"):
                continue
            m = DECKSET_DIRECTIVE.search(line)
            if m:
                err(f"{path}: leftover Deckset directive {m.group(0)}")

        #- 5b. footnotes: defined once, and every reference resolves
        defs = re.findall(r"^\[\^(\d+)\]:", text, re.M)
        refs = set(re.findall(r"\[\^(\d+)\](?!:)", text))
        for k, n in collections.Counter(defs).items():
            if n > 1:
                err(f"{path}: footnote [^{k}] defined {n} times")
        for k in sorted(refs - set(defs), key=int):
            err(f"{path}: footnote [^{k}] referenced but never defined")


def main():
    files = files_list()
    check_lectures(files)
    check_coverage(files)
    check_posts()
    if errors:
        print(f"\n{len(errors)} problem(s) found")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
