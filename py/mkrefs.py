#!/usr/bin/env python3
"""Generate the book's closing References chapter.

Collects every [@key] citation across the lectures in book (FILES) order,
emits a pandoc document that nocites them all, and runs the same
pandoc/citeproc/CSL pipeline the chapters use, so the entries look
identical to the per-chapter reference lists. Book only: nothing here
touches the website output.
"""

import os
import re
import subprocess
import sys


def main():
    files = subprocess.check_output(
        ["make", "-s", "--no-print-directory", "print-files"], text=True).split()
    keys = []
    for f in files:
        path = f"lectures/{f}.md"
        if not os.path.exists(path):
            continue
        for m in re.finditer(r"\[@([^\]\s]+)\]", open(path).read()):
            k = m.group(1)
            if k not in keys:
                keys.append(k)
    if not keys:
        print("mkrefs: no citations found")
        return 1

    md = "---\nnocite: |\n  " + ", ".join("@" + k for k in keys) + "\n---\n\n"
    with open(".build/references.md", "w") as fo:
        fo.write(md)

    subprocess.run(["pandoc", "--citeproc", "--bibliography=pdf/aic.bib",
                    "--csl=pdf/ieee-with-url.csl", "-o", ".build/references.latex",
                    ".build/references.md"], check=True)

    #- Same citeproc-output normalization as py/lecture.py
    buff = open(".build/references.latex").read()
    buff = re.sub(
        r"\\leavevmode\\vadjust pre\{\\hypertarget\{(ref-[^}]+)\}\{\}\}%",
        r"\\bibitem[\\citeproctext]{\1}",
        buff)
    open(".build/references.latex", "w").write(buff)

    with open(".build/references_chapter.inc", "w") as fo:
        fo.write("\\setchapterstyle{kao}\n"
                 "\\chapter{References}\n"
                 "\\input{references_fiximg.tex}\n\n")
    print(f"mkrefs: {len(keys)} references collected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
