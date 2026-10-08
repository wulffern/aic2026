#!/usr/bin/env python3
"""Is the GR06 telegraph signal one trap, or the supply?

GR06 compares its ramp against VDD/3 from a resistive divider, so a step
in the supply would look exactly like a trap. GR07, on the same die,
references VDD/4 the same way: a fractional supply step moves GR07's
frequency by minus the step in GR06's width. The first figure is one
minute of both sensors sampled on one loop, on the same ppm scale. GR06
switches by about 1800 ppm; GR07 does not follow.

The second figure is 26 minutes of GR06 alone, cut into dwell times in
each state. A trap is a memoryless two-state process, so the time spent
in each state is exponential: a straight line on a log survival plot.

Data: ex/data/jnwtt_trap_*.csv, reduced by fetch_data.py."""

import csv
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

DATA = Path(__file__).resolve().parent / "data"


def rows(name):
    with open(DATA / name) as fh:
        return list(csv.DictReader(fh))


#- one minute of both sensors
r = rows("jnwtt_trap_supply.csv")
t = [float(x["t_s"]) for x in r]
g6 = [float(x["GR06_ppm"]) for x in r]
g7 = [float(x["GR07_ppm"]) for x in r]
step = rows("jnwtt_trap_supply_step.csv")[0]

fig = Figure(
    """One minute of GR06 and GR07 recorded together, each as a
fractional deviation from its own 30 s median, in 50 ms means. GR06
switches between two levels about 1800 ppm apart. A supply step would
move GR07 by the same amount with the opposite sign; it does not move.""",
    vsep=0.9)
for name, y, colour, label in (("GR06 width", g6, "red", "GR06"),
                               ("GR07 frequency", g7, "blue", "GR07")):
    ax = fig.axes(ylabel=f"{name} [ppm]",
                  xlabel="Time [s]" if label == "GR07" else "",
                  xlim=(0, 60), ylim=(-2500, 2500), height=4.2,
                  options=[] if label == "GR07" else ["xticklabels={}"])
    ax.plot(t, y, colour=colour, style="thin")
    ax.hline(0, colour="gray!60", style="thin")
#- the verdict, on the GR07 panel
ax.annotate(1, 2350,
            f"while GR06 reads low, GR07 moves {float(step['GR07_step_ppm']):+.0f} "
            f"$\\pm$ {float(step['GR07_null_rms_ppm']):.0f} ppm\\\\"
            f"a supply step would move it {-float(step['GR06_step_ppm']):.0f} ppm",
            anchor="north west", colour="gray!50!black")
fig.save("jnwtt_trap_supply")

#- the dwell times
d = rows("jnwtt_trap_dwell.csv")
fig = Figure(
    """Dwell times of the GR06 trap over 26 minutes at about 31 degrees
C, as a survival curve: the fraction of visits that lasted longer than
t. A memoryless two-state process gives an exponential, a straight line
on this axis; the dashed lines are exponentials with the measured
means, not fits.""")
ax = fig.axes(xlabel="Dwell time $t$ [s]",
              ylabel="Fraction of visits longer than $t$",
              ylog=True, xlim=(0, 16), ylim=(0.003, 1.2))
means = []
for state, colour, name in ((0, "blue", "high reading"),
                            (1, "red", "low reading")):
    dw = sorted(float(x["dwell_s"]) for x in d if int(x["state"]) == state)
    n = len(dw)
    means.append((sum(dw) / n, colour))
    ax.plot(dw, [1 - i / n for i in range(n)], colour=colour,
            style="only marks, mark=*, mark size=0.9pt", decimate=False,
            label=f"{name}: {n} visits, mean {means[-1][0]:.1f} s")
#- after the marks, so the legend entries stay on the marks
for mean, colour in means:
    ax.plot([0, 16], [1, math.exp(-16 / mean)], colour=colour,
            style="thick, dashed", decimate=False)
fig.save("jnwtt_trap_dwell")
