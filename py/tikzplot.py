#!/usr/bin/env python3
"""Emit TikZ/pgfplots figures from the scripts in `ex/`.

Most of the plots in this book came out of matplotlib, so they carry
matplotlib's look: its fonts, its default blue, its tick style, and its
habit of parking a legend on top of an axis label. Next to a circuitikz
schematic they read as pasted in from somewhere else, which is exactly
what they are.

This renders the same data through `tikz/fig_header.tex`, so a plot and a
schematic on the same page share a font, a line width and a palette.
`pgfplots` is already in that preamble, so there is nothing new to
install.

Usage from a script in `ex/`::

    from tikzplot import Figure

    fig = Figure("What the figure shows, and why it is drawn this way.")
    ax = fig.axes(xlabel="$f/f_s$", ylabel="Magnitude [dB]")
    ax.plot(f, mag)
    fig.save("l5_iir")          # writes tikz/l5_iir.tex

Then `make tikz-one FNAME=l5_iir` builds `media/l5_iir_tikz.{pdf,svg}`
like any other figure, and the lecture references the `_tikz.pdf`. The
generated `.tex` is committed, so building the book never needs numpy.

The one thing worth understanding before using this is DECIMATION. An
FFT of a 2**13 point record is 8192 coordinate pairs per trace, and
pasting those into a `.tex` file produces a megabyte of numbers that
pdflatex will chew on for a while and that no reader can see. `plot()`
reduces each trace to a fixed number of columns, keeping the minimum and
maximum within each column so a noise floor still looks like a noise
floor rather than a thin line through its average. Set `decimate=False`
for a smooth curve you want exactly.
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# House palette. Black is the default; the rest carry meaning, as set out
# in tikz/STYLE.md.
COLOURS = ("black", "blue", "red", "armygreen", "orange")


def _fmt(v):
    """Trim a float to something a human could read in the .tex file."""
    s = f"{v:.5g}"
    return "0" if s in ("-0", "-0.0") else s


def _envelope(x, y, columns):
    """Reduce a trace to at most `columns` columns, keeping the extremes.

    Averaging or subsampling a noisy spectrum turns a noise floor into a
    thin wandering line, which misrepresents it. Keeping both the minimum
    and the maximum of each column preserves the band the noise actually
    occupies, and that is what the reader is being asked to look at.
    """
    n = len(x)
    if n <= columns * 2:
        return list(zip(x, y))

    out = []
    edges = [round(i * n / columns) for i in range(columns + 1)]
    for lo, hi in zip(edges, edges[1:]):
        if hi <= lo:
            continue
        seg_y = y[lo:hi]
        seg_x = x[lo:hi]
        imin = min(range(len(seg_y)), key=seg_y.__getitem__)
        imax = max(range(len(seg_y)), key=seg_y.__getitem__)
        first, second = sorted((imin, imax))
        out.append((seg_x[first], seg_y[first]))
        if second != first:
            out.append((seg_x[second], seg_y[second]))
    return out


class Axes:
    """One pgfplots axis. Made by `Figure.axes`, not directly."""

    def __init__(self, **opts):
        self.opts = opts
        self.traces = []
        self.extra = []

    def plot(self, x, y, colour=None, label=None, style="very thick",
             decimate=True, columns=600):
        """Add a line. `colour` defaults to the next one in the palette."""
        x = [float(v) for v in x]
        y = [float(v) for v in y]
        if colour is None:
            colour = COLOURS[len(self.traces) % len(COLOURS)]
        pts = _envelope(x, y, columns) if decimate else list(zip(x, y))
        self.traces.append((pts, colour, style, label, "line"))
        return self

    def stem(self, x, y, colour="red", label=None, baseline=0.0):
        """Add vertical sticks, for a harmonic or an impulse response."""
        for xi, yi in zip(x, y):
            self.extra.append(
                f"\\draw[{colour}, very thick] "
                f"(axis cs:{_fmt(xi)},{_fmt(baseline)}) -- "
                f"(axis cs:{_fmt(xi)},{_fmt(yi)});")
        self.traces.append(([], colour, "very thick", label, "stem"))
        return self

    def hline(self, y, colour="armygreen", label=None, style="dashed, very thick"):
        """A horizontal reference level across the whole axis."""
        self.traces.append(([("\\pgfkeysvalueof{/pgfplots/xmin}", y),
                             ("\\pgfkeysvalueof{/pgfplots/xmax}", y)],
                            colour, style, label, "hline"))
        return self

    def annotate(self, x, y, text, anchor="south west", colour="black"):
        self.extra.append(
            f"\\node[anchor={anchor}, {colour}, scale=0.85] "
            f"at (axis cs:{_fmt(x)},{_fmt(y)}) {{{text}}};")
        return self

    # Options every axis in the book shares. Kept in one place so a
    # grouped figure can hoist them into the groupplot preamble instead
    # of repeating them on every panel.
    @staticmethod
    def _shared_opts():
        return [
            "scale only axis",
            "grid=both",
            "grid style={gray!22, very thin}",
            "tick align=outside",
            "tick label style={font=\\small}",
            "label style={font=\\small}",
            "legend cell align=left",
            "legend style={font=\\small, draw=gray!50, fill=white, "
            "fill opacity=0.85, text opacity=1}",
        ]

    def _opts(self, grouped):
        o = dict(self.opts)
        opts = [f"width={o.pop('width', 8.5)}cm",
                f"height={o.pop('height', 5.5)}cm"]
        if not grouped:
            opts.extend(self._shared_opts())
        if o.pop("xlog", False):
            opts.append("xmode=log")
        if o.pop("ylog", False):
            opts.append("ymode=log")
        for key in ("xlabel", "ylabel", "title"):
            v = o.pop(key, None)
            if v:
                opts.append(f"{key}={{{v}}}")
        for key, pg in (("xlim", ("xmin", "xmax")), ("ylim", ("ymin", "ymax"))):
            v = o.pop(key, None)
            if v is not None:
                opts.append(f"{pg[0]}={_fmt(v[0])}")
                opts.append(f"{pg[1]}={_fmt(v[1])}")
        legend_pos = o.pop("legend_pos", "north east")
        if any(t[3] for t in self.traces):
            opts.append(f"legend pos={legend_pos}")
        opts.extend(o.pop("options", []))
        if o:
            raise TypeError(f"unknown axes options: {sorted(o)}")
        return opts

    def _body(self):
        lines = []
        for pts, colour, style, label, kind in self.traces:
            if kind == "stem":
                # the sticks are drawn separately; this empty plot exists
                # only so the legend has something to point at
                lines.append(f"\\addplot[{colour}, very thick] "
                             f"coordinates {{}};")
            else:
                coords = " ".join(
                    f"({p[0] if isinstance(p[0], str) else _fmt(p[0])},"
                    f"{_fmt(p[1])})" for p in pts)
                lines.append(
                    f"\\addplot[{colour}, {style}, mark=none] "
                    f"coordinates {{{coords}}};")
            if label:
                lines.append(f"\\addlegendentry{{{label}}}")
        lines.extend(self.extra)
        return lines

    def _render(self, grouped=False):
        opts = self._opts(grouped)
        if grouped:
            head = ["\\nextgroupplot[", "  " + ",\n  ".join(opts), "]"]
            return "\n".join(head + self._body())
        head = ["\\begin{axis}[", "  " + ",\n  ".join(opts), "]"]
        return "\n".join(head + self._body() + ["\\end{axis}"])


class Figure:
    """A whole figure: one axis, or a grid of them.

    A grid is laid out with pgfplots' `groupplots`, which is what keeps
    the panels from landing on top of each other and gives every panel
    the same size without any arithmetic here.
    """

    def __init__(self, comment, columns=1, hsep=1.7, vsep=1.5):
        self.comment = comment
        self.columns = columns
        self.hsep = hsep
        self.vsep = vsep
        self._axes = []

    def axes(self, **opts):
        ax = Axes(**opts)
        self._axes.append(ax)
        return ax

    def _header(self):
        comment = "\n".join("% " + line if line else "%"
                            for line in self.comment.strip().split("\n"))
        return ("\\input{tikz/fig_header.tex}\n\n"
                f"{comment}\n%\n"
                "% Generated by py/tikzplot.py. Edit the script in ex/ that\n"
                "% produced it and re-run that, not this file.\n\n"
                "\\begin{tikzpicture}[thick]\n\n")

    def render(self):
        if len(self._axes) == 1:
            body = self._axes[0]._render()
        else:
            rows = -(-len(self._axes) // self.columns)
            group = [
                f"group style={{group size={self.columns} by {rows}, "
                f"horizontal sep={self.hsep}cm, "
                f"vertical sep={self.vsep}cm}}",
            ] + Axes._shared_opts()
            parts = ["\\begin{groupplot}[", "  " + ",\n  ".join(group), "]"]
            for ax in self._axes:
                parts.append(ax._render(grouped=True))
            parts.append("\\end{groupplot}")
            body = "\n".join(parts)
        return self._header() + body + "\n\n\\end{tikzpicture}\n\\end{document}\n"

    def save(self, name):
        """Write `tikz/<name>.tex`. Accepts `sub/name` for subdirectories."""
        path = os.path.join(ROOT, "tikz", name + ".tex")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fo:
            fo.write(self.render())
        print(f"tikzplot: wrote {os.path.relpath(path, ROOT)}")
        return path
