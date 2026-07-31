#!/usr/bin/env python3
"""Shrink the images inside an EPUB.

The book's figures are generated at print resolution, which is right for
the PDF and silly for an ebook: a 2800 pixel wide PNG of a schematic is
several megabytes that no reader will ever display at that size. This
rewrites the archive with every image downsampled to a sensible maximum
dimension and re-encoded, and leaves everything else byte for byte
alone.

Two encoding tricks do most of the work:

  * Figures converted from PDF/SVG arrive as RGBA with a fully opaque
    alpha channel. Dropping the alpha and compositing on white removes
    a whole channel for free.
  * A line drawing has very few distinct colours, so a palette (mode P)
    encodes it far smaller than truecolour with no visible loss.
    Photographs are left as truecolour and only resized.

Usage: python3 py/epubshrink.py pdf/aic.epub [maxpx]
"""

import io
import os
import shutil
import sys
import zipfile

from PIL import Image

MAXPX = 1400          # longest side, in pixels
PALETTE_COLOURS = 256


def shrink(data, name, maxpx):
    """Return smaller image bytes, or None to keep the original."""
    try:
        im = Image.open(io.BytesIO(data))
        im.load()
    except Exception:
        return None

    fmt = (im.format or "").upper()
    changed = False

    if max(im.size) > maxpx:
        s = maxpx / max(im.size)
        im = im.resize((max(1, round(im.width * s)),
                        max(1, round(im.height * s))), Image.LANCZOS)
        changed = True

    if fmt in ("JPEG", "JPG"):
        if not changed:
            return None
        out = io.BytesIO()
        im.convert("RGB").save(out, "JPEG", quality=85, optimize=True,
                               progressive=True)
        return out.getvalue()

    # PNG: flatten a pointless alpha channel, then try a palette
    if im.mode in ("RGBA", "LA", "P"):
        rgba = im.convert("RGBA")
        alpha = rgba.getchannel("A")
        if alpha.getextrema()[0] == 255:           # nothing is transparent
            bg = Image.new("RGB", rgba.size, (255, 255, 255))
            bg.paste(rgba, mask=alpha)
            im = bg
            changed = True
        else:
            im = rgba

    best = None
    if im.mode == "RGB":
        colours = im.getcolors(maxcolors=PALETTE_COLOURS * 8)
        if colours is not None and len(colours) <= PALETTE_COLOURS * 4:
            p = io.BytesIO()
            im.convert("P", palette=Image.ADAPTIVE,
                       colors=PALETTE_COLOURS).save(p, "PNG", optimize=True)
            best = p.getvalue()

    o = io.BytesIO()
    im.save(o, "PNG", optimize=True)
    cand = o.getvalue()
    if best is not None and len(best) < len(cand):
        cand = best

    if not changed and len(cand) >= len(data):
        return None
    return cand if len(cand) < len(data) else None


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "aic.epub"
    maxpx = int(sys.argv[2]) if len(sys.argv) > 2 else MAXPX
    tmp = path + ".shrunk"

    before = os.path.getsize(path)
    saved = 0
    touched = 0

    with zipfile.ZipFile(path) as zin:
        names = zin.namelist()
        # mimetype must be the first entry and stored uncompressed
        order = (["mimetype"] if "mimetype" in names else []) + \
                [n for n in names if n != "mimetype"]
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for n in order:
                info = zin.getinfo(n)
                data = zin.read(n)
                if n.lower().endswith((".png", ".jpg", ".jpeg")):
                    new = shrink(data, n, maxpx)
                    if new:
                        saved += len(data) - len(new)
                        touched += 1
                        data = new
                if n == "mimetype":
                    zi = zipfile.ZipInfo("mimetype", date_time=info.date_time)
                    zi.compress_type = zipfile.ZIP_STORED
                    zout.writestr(zi, data)
                else:
                    zi = zipfile.ZipInfo(n, date_time=info.date_time)
                    zi.compress_type = zipfile.ZIP_DEFLATED
                    zi.external_attr = info.external_attr
                    zout.writestr(zi, data)

    shutil.move(tmp, path)
    after = os.path.getsize(path)
    print(f"epubshrink: {touched} images, "
          f"{before/1048576:.1f} MB -> {after/1048576:.1f} MB "
          f"({100*(before-after)/before:.0f} % smaller)")


if __name__ == "__main__":
    main()
