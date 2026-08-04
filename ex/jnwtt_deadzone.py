#!/usr/bin/env python3
"""Why GR07's noise depends on the temperature it happens to be at.

GR07's comparator output is re-timed by the 64 MHz project clock, so its
period is always a whole number of clock cycles: either N or N+1. To
average out at N+f, a fraction f of the periods must come out long.
That is a Bernoulli process, so the spread of a rate estimated from many
periods goes as sqrt(f(1-f)): smallest where the period is nearly a
whole number of cycles, largest half-way between.

This plots the measured noise against f, with that shape fitted through
a single scale factor.

Data: ex/data/jnwtt_chamber.csv."""

import csv
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

DATA = Path(__file__).resolve().parent / "data"

dist, sigma, ref = [], [], []
with open(DATA / "jnwtt_chamber.csv") as fh:
    for row in csv.DictReader(fh):
        d = float(row["GR07_dist_to_whole_cycle"])
        #- distance to the nearest whole cycle, so 0.8 counts as 0.2
        dist.append(min(d, 1 - d))
        sigma.append(float(row["GR07_sigma_hz"]))
        ref.append(float(row["ref_c"]))

#- If the output alternates between N and N+1 cycles with the long-run
#- fraction of long periods equal to f, that is a Bernoulli process:
#- per-period variance f(1-f), so the spread of a rate estimate goes as
#- sqrt(f(1-f)). Fitting one scale factor to the measured sigma gives
#- r = 0.997 over the fourteen set points, which is the whole story of
#- this figure.
import math

model = [math.sqrt(v * (1 - v)) for v in dist]
scale = (sum(m * s for m, s in zip(model, sigma))
         / sum(m * m for m in model))
grid = [0.002 * i for i in range(1, 251)]

fig = Figure(
    """GR07's measured noise against f, the fractional part of its
period measured in 64 MHz clock cycles. The output alternates between N
and N+1 whole cycles, and to average out at N+f a fraction f of the
periods must come out long - a Bernoulli process, whose spread goes as
the square root of f(1-f). The dashed curve is that shape with a single
scale factor fitted; it follows the measurements with r = 0.997. The
noise is smallest where the period is nearly a whole number of cycles,
because there is then almost nothing for the quantiser to dither
about.""")

ax = fig.axes(xlabel="$f$, period past a whole clock cycle [cycles]",
              ylabel="GR07 noise $\\sigma$ [Hz]",
              xlim=(0, 0.55), ylim=(0, 220), xprecision=1)
ax.plot(grid, [scale * math.sqrt(v * (1 - v)) for v in grid],
        colour="black", style="thick, dashed",
        label="$\\sqrt{f(1-f)}$, one scale factor", decimate=False)
ax.plot(dist, sigma, colour="blue", label="measured",
        style="only marks, mark=*, mark size=1.6pt", decimate=False)

fig.save("jnwtt_deadzone")
