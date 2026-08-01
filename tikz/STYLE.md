# Figure style guide

Every figure in `tikz/` is built by `make tikz-one FNAME=<name>` (or
`make tikz` for all of them) into `media/<name>_tikz.{pdf,svg}`, and the
lectures reference the `_tikz.pdf`. Figures in a subdirectory follow the
same rule: `tikz/l13/nand.tex` becomes `media/l13/nand_tikz.pdf`, built
with `make tikz-one FNAME=l13/nand`.

The point of this file is that a figure drawn next year should sit next
to one drawn last year without either looking out of place.

## Line width

One width for everything: the environment's `thick`, which is 0.8 pt.

```latex
\begin{circuitikz}[american, thick, transform shape, circuit ee IEC]
\begin{tikzpicture}[thick]
```

Do not set `line width=` on ordinary wires or devices. `fig_header.tex`
sets

```latex
\ctikzset{bipoles/thickness=1}
```

because circuitikz otherwise draws resistors, capacitors and diodes at
*twice* the ambient width, which makes them heavier than the wires they
sit on and heavier than the hand rolled zig-zag in `ckt_lib.tex`. With
that setting a circuitikz `R` and a `ckt_lib` `\vresistor` weigh the
same.

Heavier strokes are for **annotation**, not for circuitry: the green
"becomes" arrows, the red De Morgan arrows, a highlighted signal path.
`very thick` is the annotation width.

## Arrow tips

One filled tip everywhere: `Latex` from `arrows.meta`, set globally in
`fig_header.tex` as

```latex
\tikzset{>={Latex}}
```

So a figure only ever writes `->`, `<-` or `<->` and gets the house tip.
Do not write `-latex`, `-stealth` or `-{Triangle}` in a figure: if the
tip ever needs to change, it should change in one place.

`Latex` scales with the line width, so an arrow on a `very thick`
annotation stroke stays in proportion instead of looking undersized.

`tikz/_arrowopts.tex` renders the candidates side by side, if the
question ever comes up again.

## Colour

Black is the default for circuits. Colour carries meaning, never
decoration:

| colour | meaning |
|---|---|
| `red` | the thing the figure is about; danger; a bit value |
| `blue` / `mOne` | metal, signals in a layout sense, the combinational cloud |
| `armygreen` | equivalences, "becomes", derived quantities |
| `poly`, `active`, `cut`, `mOne`..`mFour` | layout layers, from `fig_header.tex` |
| `echarge` / `hcharge` | electrons and holes in device cartoons |

If a figure would read the same in black, draw it in black.

## Shared libraries

- `ckt_lib.tex` — the schematic vocabulary: `\lvnmos`, `\lvmnmos`,
  `\lvpmos`, `\lvmpmos` (each spans `\grid` = 1.6 vertically),
  `\vground`, `\vsupply`, `\portOut`, `\portIn`, `\vresistor`,
  `\vcapacitor`, the OTA outlines. Use these rather than re-inventing a
  transistor.
- `mos_lib.tex` — the MOSFET cross-section cartoons.
- `sfg_lib.tex` — summing nodes, boxes and dots for block diagrams.
- `spec_lib.tex`, `plane_lib.tex`, `dacsm_lib.tex`, `sc_lib.tex`,
  `gmc_lib.tex`, `rdac_lib.tex`, `boot_lib.tex` — domain specific.

Junction dots are `\fill (x,y) circle (0.075);`. Wires that cross
without a dot are not connected — that convention is used throughout, so
do not add a hop.

Resistors are always the hand-rolled zig-zag (`\vresistor` /
`\hresistor`). Never draw circuitikz's own `to [resistor]` or `to [R]`
bipole: it is visibly larger than the house zig-zag and the two styles
must not mix on a page.

## What the preamble does not have

`fig_header.tex` is fixed and shared. It does **not** load `calc`, so
`($(a)+(1,0)$)` syntax fails — use named `\coordinate`s and `|-` / `-|`
instead. It does not load `shapes.geometric`, so there is no `ellipse`
node shape — use a rounded rectangle. `\usetikzlibrary` inside a figure
works but prefer not to: a figure that needs a library the others do not
have is a figure that will drift.

## Plots that come out of a script

Figures that plot data — spectra, sweeps, transients — should be drawn by
`py/tikzplot.py` rather than saved from matplotlib. A matplotlib figure
next to a circuitikz schematic reads as pasted in from somewhere else,
because it is: different font, different line weights, different palette.
`tikzplot` renders the same numbers through `fig_header.tex`, so the two
match.

The script in `ex/` keeps its matplotlib code (it is useful for looking
at data interactively) and gains a few lines at the end:

```python
from tikzplot import Figure

fig = Figure("""What the figure shows, and why it is drawn this way.""",
             columns=2)
ax = fig.axes(xlabel="$f/f_s$", ylabel="Magnitude [dB20]", ylim=(-60, 60))
ax.plot(f, mag, colour="black")
fig.save("l5_iir")            # writes tikz/l5_iir.tex
```

Then

```sh
make plots-one FNAME=iir     # run the script, rebuild what it produced
make plots                   # every plot script, four at a time
```

and the lecture references `media/l5_iir_tikz.pdf`. Any script in `ex/`
that imports `tikzplot` is picked up automatically, so adding one needs
no edit to the Makefile.

The generated `.tex` is committed, so building the book never needs
numpy or a simulator — only regenerating a figure does.

**Everything a plot script needs is in this repository.** Several
figures come from simulations that live in the aicex and dicex
repositories; the columns those figures use are vendored into `ex/data/`
as plain CSV, so the scripts run on any machine with numpy and nothing
else. `make plots-data` re-vendors them, and is the only target that
needs the other repositories checked out — run it after a simulation has
been re-run, not otherwise.

**Anything random is seeded.** A plot whose noise is drawn fresh on
every run cannot be reproduced, so `make plots` would rewrite figures
that nobody changed and a reader could never get back the one in the
book. The noise is meant to look like noise, not to be any particular
noise, so a fixed seed costs nothing.

Two things to know:

- **Decimation.** An 8192-point FFT is 8192 coordinate pairs, which is a
  megabyte of `.tex` that nobody can see. `plot()` reduces each trace to
  600 columns, keeping the *minimum and maximum* within each column, so a
  noise floor stays a band rather than collapsing to a thin line through
  its average. Pass `decimate=False` for a smooth analytic curve you want
  exactly.
- **`groupplots`** lays out multi-panel figures. `fig_header.tex` loads it
  and pins `compat=1.16`, so panel spacing does not shift when pgfplots
  is upgraded.

Figures whose data comes from a simulator rather than a script still need
the raw data exported before they can move; until then they stay as they
are.

## Redrawing a hand drawn figure

1. **Render the original with its CropBox**:
   `pdftoppm -png -r 90 -cropbox -singlefile media/<name>.pdf /tmp/o.png`
   and look at it. Many of the scanned pages are crops of a larger
   sheet, and without `-cropbox` you will see — and faithfully redraw —
   the neighbouring figure and its handwritten algebra. Six figures in
   this repo were drawn wrong exactly this way.
2. Draw it.
3. Render **your** result and look at it. A clean build says nothing
   about whether the drawing is right.
4. Compare against the original point by point: topology, every label,
   polarity, bubbles, arrow directions, truth table values.
5. Only then switch the lecture's reference from `<name>.pdf` (or
   `.svg`) to `<name>_tikz.pdf`, and grep for other lectures and decks
   that use the same figure.

Deviating from the original is allowed when the original is wrong — the
BPSK steering labels and the sigma-delta DAC orientation were both fixed
this way — but say so in the figure's header comment and in the commit
message, so the author can disagree.

## Figure comments

Every figure starts with a comment saying what it shows and why it is
drawn the way it is. Reasons ("the sources cross, so both b0 devices
would hang off one tail") are worth more than descriptions ("four
transistors").
