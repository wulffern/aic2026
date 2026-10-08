#!/usr/bin/env python3
"""Render a Deckset lecture as a Marp deck.

Prototype. The lectures stay Deckset source; this writes a Marp copy to
.build/marp/<name>.md and, with --html or --pdf, runs marp-cli on it.

    python3 py/marp.py lectures/lr1_transistor_noise.md --html --pdf

What changes on the way:

    header lines (footer:, slidenumbers:, ...)   YAML front matter
    <!--pan_doc: ... -->                         speaker notes (press p)
    <!--pan_latex: ... -->, pan_title/author     dropped
    <!--pan_skip: -->                            marker dropped, slide kept
    #[fit] Heading                               a section slide
    ![left fit](x) / ![right fit](x)             ![bg left contain](x)
    ![fit](x) alone on a slide                   ![bg contain](x)
    ![fit](x) next to text, ![inline ...](x)     an image in the flow
    [.column]                                    a CSS grid column
    [.background-color: c]                       <!-- _backgroundColor: c -->
    figure.pdf                                   figure.svg, made if missing

The look is slides/marp/aic.css.
"""

import os
import re
import subprocess
import sys

import click

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, ".build", "marp")
THEME = os.path.join(ROOT, "slides", "marp", "aic.css")

HEADER_RE = re.compile(r"^(footer|slidenumbers|autoscale|theme|text|header"
                       r"|date|build-lists|slide-transition)\s*:(.*)$")
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
PAN_RE = re.compile(r"<!--\s*pan_([a-z]+)\s*:(.*)$")
FIT_RE = re.compile(r"^(#+)\s*\[fit\]\s*(.*)$")
BG_RE = re.compile(r"^\[\.background-color:\s*([^\]]+)\]\s*$")
DIRECTIVE_RE = re.compile(r"^\[\.[a-z-]+[^\]]*\]\s*$")


def svg_for(path, src_dir):
    """Browsers cannot show a PDF in an <img>. Use the SVG twin the tikz
    build already makes, or convert one."""
    if not path.endswith(".pdf"):
        return path
    abs_pdf = os.path.normpath(os.path.join(src_dir, path))
    abs_svg = abs_pdf[:-4] + ".svg"
    if not os.path.isfile(abs_svg) and os.path.isfile(abs_pdf):
        subprocess.run(["pdftocairo", "-svg", abs_pdf, abs_svg], check=True)
    return path[:-4] + ".svg"


def split_header(lines):
    meta = {}
    i = 0
    while i < len(lines):
        m = HEADER_RE.match(lines[i].strip())
        if m:
            meta[m.group(1)] = m.group(2).strip()
        elif lines[i].strip():
            break
        i += 1
    return meta, lines[i:]


def strip_pan(lines):
    """Turn pan_doc blocks into plain comments (Marp's speaker notes) and
    drop everything else that only the book needs."""
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = PAN_RE.match(line.strip())
        if not m:
            out.append(line)
            i += 1
            continue
        kind, rest = m.group(1), m.group(2)
        # collect the whole comment
        block = [rest]
        if "-->" not in rest:
            i += 1
            while i < len(lines) and "-->" not in lines[i]:
                block.append(lines[i])
                i += 1
            if i < len(lines):
                block.append(lines[i])
        i += 1
        text = "\n".join(block)
        text = text[: text.rfind("-->")] if "-->" in text else text
        if kind == "doc" and text.strip():
            # a note may not contain "-->", nor start a directive
            text = text.replace("--", "–").strip()
            out.append("<!--\n" + text + "\n-->")
    return out


def slides_of(lines):
    cur, out = [], []
    for line in lines:
        if line.strip() == "---":
            out.append(cur)
            cur = []
        else:
            cur.append(line)
    out.append(cur)
    return [s for s in out if any(l.strip() for l in s)]


def is_content(line):
    s = line.strip()
    return bool(s) and not s.startswith("<!--") and not IMG_RE.fullmatch(s) \
        and not DIRECTIVE_RE.match(s)


def in_note(lines):
    """Mask of the lines that sit inside a speaker-note comment."""
    mask, inside = [], False
    for l in lines:
        s = l.strip()
        if s.startswith("<!--") and not s.endswith("-->"):
            inside = True
            mask.append(True)
            continue
        mask.append(inside or (s.startswith("<!--") and s.endswith("-->")))
        if inside and s.endswith("-->"):
            inside = False
    return mask


def convert_slide(lines, src_dir, first=False, meta={}):
    notes = in_note(lines)
    visible = [l for l, n in zip(lines, notes) if not n]
    has_text = any(is_content(l) for l in visible)
    head, body, cols = [], [], []
    section = False

    def image(m):
        opts = m.group(1).split()
        path = svg_for(m.group(2), src_dir)
        side = next((o for o in opts if o in ("left", "right")), None)
        size = next((o for o in opts if o.endswith("%")), None)
        if side:
            return f"![bg {side} {size or 'contain'}]({path})"
        if "inline" in opts or has_text:
            return f"![]({path})"
        return f"![bg {size or 'contain'}]({path})"

    for line, note in zip(lines, notes):
        if note:
            body.append(line)
            continue
        s = line.strip()
        if s.startswith("<!--") and s.endswith("-->"):
            continue
        m = FIT_RE.match(s)
        if m:
            section = True
            body.append(f"{m.group(1)} {m.group(2)}")
            continue
        m = BG_RE.match(s)
        if m:
            head.append(f"<!-- _backgroundColor: {m.group(1).strip()} -->")
            continue
        if s == "[.column]":
            cols.append(len(body))
            continue
        if DIRECTIVE_RE.match(s):
            continue
        body.append(IMG_RE.sub(image, line))

    words = sum(len(l.split()) for l in body
                if l.strip() and not l.strip().startswith(("<", "!", "|", "$$")))
    if section:
        head.append("<!-- _class: section -->")
    elif first:
        head.append("<!-- _class: title -->")
        body.append("")
        body.append(" · ".join(x for x in (meta.get("footer"), meta.get("date"))
                                if x))
    elif words > 110:
        head.append("<!-- _class: dense -->")
    if cols:
        # everything from the first [.column] on is laid out side by side
        pre = body[:cols[0]]
        parts = [body[a:b] for a, b in zip(cols, cols[1:] + [len(body)])]
        body = pre + ['<div class="columns">'] + sum(
            (["<div>", ""] + p + ["", "</div>"] for p in parts), []) + ["</div>"]
    return "\n".join(head + [""] + body).strip() + "\n"


def convert(src):
    src_dir = os.path.dirname(os.path.abspath(src))
    lines = open(src).read().split("\n")
    meta, lines = split_header(lines)
    lines = strip_pan(lines)
    slides = [convert_slide(s, src_dir, i == 0, meta)
              for i, s in enumerate(slides_of(lines))]
    front = ["---", "marp: true", "theme: aic", "paginate: true",
             "_paginate: false", "_footer: ''",
             "math: mathjax", "size: 16:9"]
    if meta.get("footer"):
        front.append(f"footer: '{meta['footer']}'")
    front.append("---")
    return "\n".join(front) + "\n\n" + "\n---\n\n".join(slides)


@click.command()
@click.argument("src")
@click.option("--html", is_flag=True, help="render HTML with marp-cli")
@click.option("--pdf", is_flag=True, help="render PDF with marp-cli")
def main(src, html, pdf):
    os.makedirs(OUT, exist_ok=True)
    name = os.path.splitext(os.path.basename(src))[0]
    md = os.path.join(OUT, name + ".md")
    # paths in the lecture are relative to lectures/; .build/marp is one
    # level deeper, so ../media becomes ../../media
    text = convert(src).replace("](../", "](../../")
    open(md, "w").write(text)
    print(f"marp: wrote {os.path.relpath(md, ROOT)}")
    for flag, ext in ((html, "html"), (pdf, "pdf")):
        if not flag:
            continue
        out = os.path.join(OUT, f"{name}.{ext}")
        cmd = ["marp", "--theme", THEME, "--html", "--allow-local-files",
               f"--{ext}", md, "-o", out]
        if ext == "pdf":
            cmd.insert(1, "--pdf-notes")
        subprocess.run(cmd, check=True)
        print(f"marp: wrote {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
