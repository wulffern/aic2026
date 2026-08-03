#!/usr/bin/env python3
"""Two sensors watching the same thing happen.

Everything else in the chapter is a sensor measured against a reference.
These are the two sensors measured against each other, while something
real happens to the die: a can of freeze spray, and then somebody
breathing on the package.

Both runs are on one capture, so the two traces share a time base and a
thermal environment exactly. That is what makes the comparison worth
anything.

Data: ex/data/jnwtt_spray.csv, jnwtt_breath.csv."""

import csv
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

DATA = Path(__file__).resolve().parent / "data"


def trace(name, col):
    """Contiguous runs of one sensor's trace.

    The captures are half a second long with dead time between them, and
    a line drawn straight across that dead time is an invention - it
    shows a smooth ramp where there is simply no data. Split wherever
    the gap is several times the sample spacing and draw each run
    separately.
    """
    x, y = [], []
    with open(DATA / name) as fh:
        for row in csv.DictReader(fh):
            if row[col]:
                x.append(float(row["t_s"]))
                y.append(float(row[col]))
    #- defensively in time order: a trace that steps backwards would be
    #- split into one run that spans the whole record and draws as a
    #- straight line across it
    order = sorted(range(len(x)), key=lambda i: x[i])
    x = [x[i] for i in order]
    y = [y[i] for i in order]
    steps = sorted(b - a for a, b in zip(x, x[1:]))
    typical = steps[len(steps) // 2] if steps else 1.0
    runs, run = [], [(x[0], y[0])]
    for i in range(1, len(x)):
        if x[i] - x[i - 1] > 4 * typical:
            runs.append(run)
            run = []
        run.append((x[i], y[i]))
    runs.append(run)
    return [r for r in runs if len(r) > 1]


def draw(ax, name, col, colour, label, offset=0.0):
    for i, run in enumerate(trace(name, col)):
        ax.plot([p[0] for p in run], [p[1] - offset for p in run],
                colour=colour, label=label if i == 0 else None,
                style="thin", decimate=False)


# ---- freeze spray, then a fingertip ----
fig = Figure(
    """A can of freeze spray at 13 s, then a fingertip held on the
package from 88 s to 122 s, with both sensors on one capture. The die
falls 13 K in 1.4 seconds - a peak rate of 37 K/s - and both sensors
follow it together. Gaps are dead time between captures, drawn as gaps
rather than interpolated.""")

ax = fig.axes(xlabel="Time [s]", ylabel="Temperature [$^\\circ$C]",
              xlim=(0, 180), ylim=(5, 26))
for col, colour, label in (("GR07_c", "blue", "GR07"),
                           ("GR06_c", "red", "GR06")):
    draw(ax, "jnwtt_spray.csv", col, colour, label)
ax.annotate(16, 9.5, "freeze spray", anchor="west", colour="gray!50!black")
ax.annotate(95, 24.6, "finger on", anchor="south", colour="gray!50!black")

fig.save("jnwtt_spray")

# ---- four breaths ----
fig = Figure(
    """Four breaths on the package, both sensors on one capture. Each
breath moves both, and both agree that something happened - but GR06
reads about 2.4 times the excursion GR07 does. Over the 15 K spray run
above the two agree to within a few per cent, so this is not a
difference in sensitivity: it is GR07 sitting close to a clock edge,
where a one-kelvin breath is a small fraction of its 4.75 K step and the
reading is compressed.""")

ax = fig.axes(xlabel="Time [s]", ylabel="Temperature rise [K]",
              xlim=(0, 115), ylim=(-0.5, 3.5))
base = {"GR07_c": 23.102658, "GR06_c": 23.051302}
for col, colour, label in (("GR07_c", "blue", "GR07"),
                           ("GR06_c", "red", "GR06")):
    draw(ax, "jnwtt_breath.csv", col, colour, label, offset=base[col])
ax.hline(0, colour="gray!60", style="thin")

fig.save("jnwtt_breath")
