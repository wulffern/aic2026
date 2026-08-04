#!/usr/bin/env python3
"""Build TikZ figures, skipping figures whose content is unchanged.

Same idea as pdfcache.py for the standalone chapters: the cache key hashes
what determines the figure's output —

  - the figure source tikz/<sub>/<name>.tex
  - every shared include (fig_header.tex and all *_lib.tex, several of
    which are symlinks into the cictikz submodule; reading them follows
    the link, so a submodule bump changes the key)

The shared includes are hashed once as a common prefix: any library edit
rebuilds every figure, which is exactly what such an edit means.

On a hit the cached <name>_tikz.pdf and .svg are copied into media<sub>/;
on a miss the figure is built with `make tikz-one FNAME=...` and both
outputs are stored. Superseded entries are pruned so the cache stays two
files per figure.

Usage: python3 py/tikzcache.py --cache <dir> tikz/a.tex tikz/l13/b.tex ...
"""

import argparse
import concurrent.futures
import hashlib
import os
import shutil
import subprocess
import sys


def include_hash():
    h = hashlib.sha256()
    names = sorted(e for e in os.listdir("tikz")
                   if e == "fig_header.tex" or e.endswith("_lib.tex"))
    for e in names:
        h.update(e.encode())
        with open(os.path.join("tikz", e), "rb") as fi:
            h.update(fi.read())
    return h


def figure_key(src, libs):
    h = libs.copy()
    with open(src, "rb") as fi:
        h.update(fi.read())
    return h.hexdigest()[:32]


def outputs(src):
    rel = os.path.splitext(os.path.relpath(src, "tikz"))[0]
    sub = os.path.dirname(rel)
    b = os.path.basename(rel)
    mdir = os.path.join("media", sub) if sub else "media"
    return [os.path.join(mdir, f"{b}_tikz.pdf"),
            os.path.join(mdir, f"{b}_tikz.svg")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()

    cache = os.path.expanduser(args.cache)
    os.makedirs(cache, exist_ok=True)

    libs = include_hash()
    wanted = set()
    hits = 0
    todo = []
    for src in args.files:
        key = figure_key(src, libs)
        outs = outputs(src)
        #- The flat cache name keeps subdirectory figures apart: l13/pdpu
        #  becomes l13__pdpu.
        stem = os.path.splitext(os.path.relpath(src, "tikz"))[0].replace("/", "__")
        entries = [os.path.join(cache, f"{stem}-{key}{os.path.splitext(o)[1]}")
                   for o in outs]
        wanted.update(os.path.basename(e) for e in entries)
        if all(os.path.exists(e) for e in entries):
            print(f"tikzcache: {src} unchanged, reusing cached figure")
            for entry, out in zip(entries, outs):
                os.makedirs(os.path.dirname(out), exist_ok=True)
                shutil.copyfile(entry, out)
            hits += 1
        else:
            todo.append((src, entries, outs))

    #- Four at a time, like `make tikz`: each figure lands in its own
    #  tikz/build/<sub>/<name>.* so the workers never touch the same file.
    def build(job):
        src, entries, outs = job
        print(f"tikzcache: {src} changed, building")
        subprocess.run(["make", "--no-print-directory", "tikz-one",
                        f"FNAME={src}"], check=True)
        for entry, out in zip(entries, outs):
            if not os.path.exists(out):
                raise SystemExit(f"tikzcache: {out} missing after build - "
                                 "is an svg converter installed?")
            shutil.copyfile(out, entry)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for _ in pool.map(build, todo):
            pass
    misses = len(todo)

    #- Prune superseded entries for the figures this run covered.
    stems = tuple(os.path.splitext(os.path.relpath(f, "tikz"))[0]
                  .replace("/", "__") + "-" for f in args.files)
    for e in os.listdir(cache):
        if e.startswith(stems) and e not in wanted:
            os.remove(os.path.join(cache, e))

    print(f"tikzcache: {hits} reused, {misses} built")
    return 0


if __name__ == "__main__":
    sys.exit(main())
