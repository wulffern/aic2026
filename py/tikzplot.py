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
        self.background = []
        self.legend_patches = []
        self.legend_lines = []

    def plot(self, x, y, colour=None, label=None, style="very thick",
             decimate=True, columns=600):
        """Add a line. `colour` defaults to the next one in the palette."""
        x = [float(v) for v in x]
        y = [float(v) for v in y]
        if colour is None:
            colour = COLOURS[len(self.traces) % len(COLOURS)]
        x, y = self._clip(x, y)
        pts = _envelope(x, y, columns) if decimate else list(zip(x, y))
        self.traces.append((pts, colour, style, label, "line"))
        return self

    def _clip(self, x, y):
        """Drop data outside the axis window, and clamp what is left.

        pgfplots clips the drawing but still has to place every
        coordinate, and a transient that runs to 10 ms while the axis
        shows 50 us overflows TeX's dimension limit and fails the build
        outright. Trimming here also keeps the .tex small.

        One point either side of the window is kept, so a line still
        enters and leaves the frame instead of stopping at its edge.
        """
        xlim = self.opts.get("xlim")
        ylim = self.opts.get("ylim")
        if xlim:
            lo, hi = xlim
            keep = [i for i, v in enumerate(x) if lo <= v <= hi]
            if not keep:
                return x, y
            a = max(0, keep[0] - 1)
            b = min(len(x), keep[-1] + 2)
            x, y = x[a:b], y[a:b]
        if ylim:
            lo, hi = ylim
            pad = (hi - lo) * 0.5
            y = [min(max(v, lo - pad), hi + pad) for v in y]
        return x, y

    def stem(self, x, y, colour="red", label=None, baseline=0.0):
        """Add vertical sticks, for a harmonic or an impulse response."""
        for xi, yi in zip(x, y):
            self.extra.append(
                f"\\draw[{colour}, very thick] "
                f"(axis cs:{_fmt(xi)},{_fmt(baseline)}) -- "
                f"(axis cs:{_fmt(xi)},{_fmt(yi)});")
        self.traces.append(([], colour, "very thick", label, "stem"))
        return self

    def hline(self, y, colour="black", label=None,
              style="dashed, thick"):
        """A horizontal reference level spanning the axis."""
        # (A |- B) takes x from A and y from B, so the frame supplies the
        # ends and the data supplies the level. Using -| here silently
        # draws a zero length line somewhere near the origin.
        self._rule(f"{{rel axis cs:0,0}} |- {{axis cs:0,{_fmt(y)}}}",
                   f"{{rel axis cs:1,0}} |- {{axis cs:0,{_fmt(y)}}}",
                   colour, style, label)
        return self

    def vline(self, x, colour="black", label=None,
              style="dashed, thick"):
        """A vertical reference line spanning the axis."""
        self._rule(f"{{axis cs:{_fmt(x)},0}} |- {{rel axis cs:0,0}}",
                   f"{{axis cs:{_fmt(x)},0}} |- {{rel axis cs:0,1}}",
                   colour, style, label)
        return self

    def _rule(self, a, b, colour, style, label):
        # One coordinate comes from the data and the other from the axis
        # frame, combined with |- or -|. Reaching for /pgfplots/ymin
        # instead only works when the limit was set by hand, and fails
        # silently when it was not.
        self.extra.append(f"\\draw[{colour}, {style}] ({a}) -- ({b});")
        if label:
            self.legend_lines.append((colour, style, label))

    def vspan(self, x0, x1, colour="blue", opacity=0.12, label=None):
        """Shade a vertical band, for a region of interest on the x axis.

        Drawn on the axis background so it sits under the traces rather
        than washing them out.
        """
        # x comes from the data, y from the axis frame. Reading ymin and
        # ymax out of pgfplots only works when they were set explicitly,
        # and on an auto-scaled log axis they are not, so take the full
        # height from `rel axis cs` and combine the two with |-.
        self.background.append(
            f"\\fill[{colour}, opacity={opacity}] "
            f"({{axis cs:{_fmt(x0)},0}} |- {{rel axis cs:0,0}}) "
            f"rectangle ({{axis cs:{_fmt(x1)},0}} |- {{rel axis cs:0,1}});")
        if label:
            self.legend_patches.append((colour, opacity, label))
        return self

    def annotate(self, x, y, text, anchor="south west", colour="black"):
        self.extra.append(
            f"\\node[anchor={anchor}, {colour}, scale=0.85, align=left] "
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
            "title style={font=\\small, yshift=-1mm}",
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
        # Fixed-point tick labels with a chosen number of decimals. Note
        # the fully qualified keys: writing `/pgf/number format/.cd` here
        # leaves that key directory active, and pgfplots' own `at` for
        # the axis scale label is then looked up inside it and the build
        # fails with a baffling pgfkeys error.
        for axis in ("x", "y"):
            prec = o.pop(f"{axis}precision", None)
            if prec is None:
                continue
            opts.append(f"scaled {axis} ticks=false")
            opts.append(
                f"{axis}ticklabel style={{"
                f"/pgf/number format/fixed, "
                f"/pgf/number format/zerofill, "
                f"/pgf/number format/precision={prec}}}")

        for key, pg in (("xlim", ("xmin", "xmax")), ("ylim", ("ymin", "ymax"))):
            v = o.pop(key, None)
            if v is not None:
                opts.append(f"{pg[0]}={_fmt(v[0])}")
                opts.append(f"{pg[1]}={_fmt(v[1])}")
        legend_pos = o.pop("legend_pos", "north east")
        if any(t[3] for t in self.traces) or self.legend_patches or self.legend_lines:
            opts.append(f"legend pos={legend_pos}")
        opts.extend(o.pop("options", []))
        if o:
            raise TypeError(f"unknown axes options: {sorted(o)}")
        return opts

    def _body(self):
        lines = list(self.background)
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
        for colour, style, label in self.legend_lines:
            lines.append(f"\\addlegendimage{{{colour}, {style}}}")
            lines.append(f"\\addlegendentry{{{label}}}")
        for colour, opacity, label in self.legend_patches:
            # an invisible plot whose legend mark is the shaded colour
            lines.append(
                f"\\addlegendimage{{area legend, fill={colour}, "
                f"opacity={opacity}, draw=none}}")
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
