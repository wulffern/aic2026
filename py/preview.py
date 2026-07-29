#!/usr/bin/env python3
"""Render lecture figures to PNG so they can be eyeballed without a PDF viewer.

Handles the artwork formats used in media/: PDF via pypdfium2, SVG via cairosvg,
and bitmaps via a straight copy.

    pip install -r requirements-preview.txt
    python3 py/preview.py media/l3_vsrc_tikz.pdf -o preview/
    python3 py/preview.py --compare l03_ptat -o preview/

This reads committed artwork only; it does not compile TikZ. Use
`make tikz-one FNAME=<basename>` for that, or let the CI tikz job do it.

--compare renders the original artwork and the TikZ redraw side by side, which
is the form the approval gate in tikz_translation_plan.md needs.
"""

import os
import shutil
import sys

import click

RASTER = (".png", ".jpg", ".jpeg", ".gif")


def flatten(im):
    """Composite onto white. The lecture artwork has a transparent background,
    and dropping the alpha channel instead would leave it black — which makes a
    dark-stroked drawing look like a light-on-dark export rather than the
    hand-drawn figure it is."""
    from PIL import Image

    if im.mode not in ("RGBA", "LA", "P"):
        return im.convert("RGB")
    im = im.convert("RGBA")
    canvas = Image.new("RGB", im.size, "white")
    canvas.paste(im, mask=im.split()[-1])
    return canvas


def render_pdf(src, dst, scale):
    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(src)
    page = pdf[0]
    flatten(page.render(scale=scale).to_pil()).save(dst)
    pdf.close()
    return dst


def render_svg(src, dst, scale):
    import cairosvg

    cairosvg.svg2png(url=src, write_to=dst, scale=scale,
                     background_color="white")
    return dst


def render(src, outdir, scale=2.0):
    """Render one figure to PNG in outdir. Returns the output path."""
    if not os.path.exists(src):
        raise click.ClickException(f"No such figure: {src}")

    os.makedirs(outdir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(src))[0]
    dst = os.path.join(outdir, stem + ".png")
    ext = os.path.splitext(src)[1].lower()

    if ext == ".pdf":
        return render_pdf(src, dst, scale)
    if ext == ".svg":
        return render_svg(src, dst, scale)
    if ext in RASTER:
        from PIL import Image

        with Image.open(src) as im:
            flatten(im).save(dst)
        return dst
    raise click.ClickException(f"Cannot render {ext} figures: {src}")


def resolve(name, mediadir):
    """Map a bare basename to its artwork, preferring SVG over PDF."""
    if os.path.exists(name):
        return name
    for ext in (".svg", ".pdf", ".png"):
        path = os.path.join(mediadir, name + ext)
        if os.path.exists(path):
            return path
    return None


@click.command()
@click.argument("figures", nargs=-1, required=True)
@click.option("-o", "--outdir", default="preview", help="Directory for the PNGs.")
@click.option("-s", "--scale", default=2.0, help="Render scale, higher is sharper.")
@click.option("-m", "--mediadir", default="media", help="Where to look up bare names.")
@click.option("--compare", is_flag=True,
              help="Render <name> and <name>_tikz together for review.")
def main(figures, outdir, scale, mediadir, compare):
    """Render FIGURES (paths or bare basenames) to PNG."""
    failed = False

    for name in figures:
        targets = []
        if compare:
            original = resolve(name, mediadir)
            redraw = resolve(name + "_tikz", mediadir)
            if original is None:
                click.echo(f"no original artwork for {name}", err=True)
                failed = True
            else:
                targets.append(("original", original))
            if redraw is None:
                click.echo(f"no TikZ redraw for {name} — build it first "
                           f"with: make tikz-one FNAME={name}", err=True)
                failed = True
            else:
                targets.append(("tikz", redraw))
        else:
            path = resolve(name, mediadir)
            if path is None:
                click.echo(f"not found: {name}", err=True)
                failed = True
            else:
                targets.append(("", path))

        for label, path in targets:
            try:
                out = render(path, outdir, scale)
            except Exception as e:
                click.echo(f"{path}: {e}", err=True)
                failed = True
                continue
            click.echo(f"{label + ': ' if label else ''}{path} -> {out}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
