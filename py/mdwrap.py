#!/usr/bin/env python3
"""Rewrap Markdown to a fixed width, leaving alone what must not move.

The text edition is read in a terminal and in a context window, and both
are easier on 80 columns than on paragraphs that run to whatever length
the author's editor happened to be. Rewrapping prose is safe; rewrapping
a SPICE netlist, a table or a display equation is not, so those are
copied through untouched.

Only the text edition uses this. The site, the PDF and the EPUB take the
lectures as written.
"""

import re
import textwrap

WIDTH = 80

FENCE = re.compile(r"^\s*(```+|~~~+)")
LIST = re.compile(r"^(\s*(?:[-*+]|\d+[.)])\s+)")
LABEL = re.compile(r"^((?:Caption|Description):\s+)")
QUOTE = re.compile(r"^(>\s*)")

#- Lines that carry their own layout. A table's columns, a listing's
#  indentation and a display equation all mean something in the
#  character positions themselves.
def _verbatim(line):
    return (
        "$$" in line                     # display maths
        or re.match(r"^ {4,}\S", line)   # indented listing
        or line.startswith("#")          # heading, already short
        or line.startswith("<")          # raw HTML
        or line.startswith("[FIGURE ")
        or line.startswith("[/FIGURE]")
        or re.match(r"^[-=*_]{3,}\s*$", line)
    )


def _table(line):
    return line.lstrip().startswith("|")


SEP = re.compile(r"^:?-{2,}:?$")


def _cells(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def _align(rows):
    """Pad a Markdown table so its columns line up in a monospace font.

    The tables in the lectures are written by hand, so their pipes land
    wherever the typing stopped. The content is unchanged: only the
    padding inside each cell moves, which Markdown ignores and a reader
    in a terminal does not.
    """
    grid = [_cells(r) for r in rows]
    n = max(len(r) for r in grid)
    grid = [r + [""] * (n - len(r)) for r in grid]

    #- ---: is right, :---: is centre, anything else left.
    how = ["l"] * n
    seps = [i for i, r in enumerate(grid) if all(SEP.match(c) for c in r if c)]
    for i in seps:
        for j, c in enumerate(grid[i]):
            if c.startswith(":") and c.endswith(":"):
                how[j] = "c"
            elif c.endswith(":"):
                how[j] = "r"

    #- The separator rows are rebuilt to fit, so their current length
    #  must not decide the column width.
    w = []
    for j in range(n):
        lens = [len(r[j]) for i, r in enumerate(grid) if i not in seps]
        w.append(max([3] + lens))

    def rule(j):
        body = "-" * (w[j] - (how[j] == "c") - (how[j] in "cr"))
        return (":" if how[j] == "c" else "") + body + \
               (":" if how[j] in "cr" else "")

    def pad(text, j):
        if how[j] == "r":
            return text.rjust(w[j])
        if how[j] == "c":
            return text.center(w[j])
        return text.ljust(w[j])

    out = []
    for i, r in enumerate(grid):
        cells = [rule(j) if i in seps else pad(r[j], j) for j in range(n)]
        out.append("| " + " | ".join(cells) + " |")
    return out


def _flush(out, buf, initial, subsequent, width):
    if not buf:
        return
    text = re.sub(r"\s+", " ", " ".join(buf)).strip()
    if text:
        out.extend(textwrap.wrap(
            text, width=width,
            initial_indent=initial, subsequent_indent=subsequent,
            #- A URL and a hyphenated part number are single words. A
            #  wrap that splits either one makes the line shorter and
            #  the content wrong.
            break_long_words=False, break_on_hyphens=False))
    buf.clear()


def wrap(text, width=WIDTH):
    out = []
    buf = []
    table = []
    initial = subsequent = ""
    fence = None
    figure = False

    def end_table():
        if table:
            out.extend(_align(table))
            table.clear()

    for line in text.split("\n"):
        if fence is None and _table(line):
            _flush(out, buf, initial, subsequent, width)
            table.append(line)
            continue
        end_table()

        m = FENCE.match(line)
        if m:
            _flush(out, buf, initial, subsequent, width)
            tok = m.group(1)[0] * 3
            fence = None if fence == tok else (fence or tok)
            out.append(line)
            continue
        if fence is not None:
            out.append(line)
            continue

        if not line.strip():
            _flush(out, buf, initial, subsequent, width)
            out.append("")
            continue

        if _verbatim(line):
            _flush(out, buf, initial, subsequent, width)
            out.append(line)
            #- Inside a figure block every paragraph is part of what the
            #  figure shows, so it keeps the indent of the label above
            #  it even across a blank line.
            if line.startswith("[FIGURE "):
                figure, initial, subsequent = True, "", ""
            elif line.startswith("[/FIGURE]"):
                figure, initial, subsequent = False, "", ""
            continue

        for pattern, indent in ((LABEL, "  "), (LIST, None), (QUOTE, None)):
            m = pattern.match(line)
            if not m:
                continue
            _flush(out, buf, initial, subsequent, width)
            initial = m.group(1)
            subsequent = indent if indent is not None else " " * len(m.group(1))
            if pattern is QUOTE:
                subsequent = m.group(1)
            buf.append(line[m.end():])
            break
        else:
            if not buf:
                initial = subsequent = "  " if figure else ""
            buf.append(line)

    _flush(out, buf, initial, subsequent, width)
    end_table()
    return "\n".join(out)
