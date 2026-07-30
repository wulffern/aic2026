#!/usr/bin/env python3
"""Build standalone chapter PDFs, skipping chapters whose content is unchanged.

The generated pdf/<f>.tex wrapper embeds the build date and git hash, so its
bytes change on every commit even when the chapter does not. The cache key
therefore hashes what actually determines the PDF's content:

  - pdf/<f>_fiximg.tex          (the full chapter body, images substituted)
  - every media file it \\includegraphics's
  - pdf/<f>_chapter.inc         (carries the chapter title)
  - pdf/short_tmplt.tex, pdf/pandoc.tex, pdf/version.tex? no — version is
    excluded on purpose: an unchanged chapter keeps the date it was last
    actually built, which is what that date claims to be anyway.

On a hit the cached PDF is copied out; on a miss the chapter is built with
`make -C pdf standalone` and stored. Entries whose key no longer matches any
current lecture are pruned, so the cache directory stays one file per
chapter.

Usage: python3 py/pdfcache.py --cache <dir> f1 f2 ...
"""

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys


def fiximg_path(name):
    #- The _fiximg file is named after the lecture *title*, not the source
    #  basename; the generated wrapper pdf/<name>.tex knows the mapping.
    with open(f"pdf/{name}.tex") as fi:
        m = re.search(r"\\input\{([^}]*_fiximg)(?:\.tex)?\}", fi.read())
    if not m:
        raise SystemExit(f"pdfcache: no _fiximg input found in pdf/{name}.tex")
    return f"pdf/{m.group(1)}.tex"


def chapter_key(name):
    h = hashlib.sha256()
    for path in [fiximg_path(name), f"pdf/{name}_chapter.inc",
                 "pdf/short_tmplt.tex", "pdf/pandoc.tex"]:
        with open(path, "rb") as fi:
            body = fi.read()
        h.update(body)
        if path.endswith("_fiximg.tex"):
            for m in re.finditer(rb"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", body):
                img = os.path.join("pdf", m.group(1).decode())
                h.update(m.group(1))
                try:
                    with open(img, "rb") as fi:
                        h.update(fi.read())
                except FileNotFoundError:
                    #- fix_svg warned already; the build will say the rest
                    h.update(b"missing")
    return h.hexdigest()[:32]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()

    cache = os.path.expanduser(args.cache)
    os.makedirs(cache, exist_ok=True)
    os.makedirs("docs/assets", exist_ok=True)

    wanted = {}
    hits = misses = 0
    for f in args.files:
        key = chapter_key(f)
        entry = os.path.join(cache, f"{f}-{key}.pdf")
        wanted[f"{f}-{key}.pdf"] = True
        if os.path.exists(entry):
            print(f"pdfcache: {f} unchanged, reusing cached PDF")
            shutil.copyfile(entry, f"pdf/{f}.pdf")
            hits += 1
        else:
            print(f"pdfcache: {f} changed, building")
            subprocess.run(["make", "-C", "pdf", "standalone", f"FNAME={f}.tex"],
                           check=True)
            shutil.copyfile(f"pdf/{f}.pdf", entry)
            misses += 1
        shutil.copyfile(f"pdf/{f}.pdf", f"docs/assets/{f}.pdf")

    #- Prune superseded entries for the lectures this run covered, so the
    #  cache stays one file per chapter. Entries belonging to other shards
    #  are left alone.
    prefixes = tuple(f + "-" for f in args.files)
    for e in os.listdir(cache):
        if e.startswith(prefixes) and e not in wanted:
            os.remove(os.path.join(cache, e))

    print(f"pdfcache: {hits} reused, {misses} built")
    return 0


if __name__ == "__main__":
    sys.exit(main())
