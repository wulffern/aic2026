#!/usr/bin/env python3
"""Why GR07's noise depends on the temperature it happens to be at.

GR07's comparator output is re-timed by the 64 MHz project clock, so its
period is always a whole number of clock cycles: either N or N+1. The
circuit dithers between the two, and averaging reads the ratio - which
is a first-order sigma-delta, arrived at by accident.

That works only while it is dithering. Where the period lands close to a
whole number of cycles the output stops alternating, every period gives
the same answer, and the sensor goes quiet by going deaf. The left panel
is that: measured noise against distance to the nearest whole cycle. The
right panel is the same staircase seen as a converter's code widths.

Data: ex/data/jnwtt_chamber.csv, jnwtt_dnl.csv."""

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

code, width, lsb, dnl = [], [], [], []
with open(DATA / "jnwtt_dnl.csv") as fh:
    for row in csv.DictReader(fh):
        code.append(float(row["code"]))
        width.append(float(row["width_k"]))
        lsb.append(float(row["lsb_k"]))
        dnl.append(float(row["dnl_lsb"]))

fig = Figure(
    """GR07's measured noise against where its period falls between two
clock edges, one point per chamber set point. The noise collapses where
the period lands on a whole number of 64 MHz cycles and peaks half-way
between. That is not precision, it is a dead zone: the noise can no
longer straddle the clock edge, the dither that carries the resolution
has switched off, and the sensor has stopped responding.""")

ax = fig.axes(xlabel="Distance to a whole clock cycle [cycles]",
              ylabel="GR07 noise $\\sigma$ [Hz]",
              xlim=(0, 0.55), ylim=(0, 220), xprecision=1)
ax.plot(dist, sigma, colour="blue",
        style="only marks, mark=*, mark size=1.6pt", decimate=False)
ax.annotate(0.02, 200, "dithering:\\\\resolution comes\\\\from the ratio",
            anchor="north west", colour="gray!50!black")
ax.annotate(0.03, 30, "dead zone", anchor="south west", colour="red")

fig.save("jnwtt_deadzone")

fig = Figure(
    """The same staircase read as a converter: the width of each fully
traversed code against the ideal 4.75 K step, from the temperature
chamber sweep. GR06, with no clock anywhere in its path, has no
equivalent.""")

ax = fig.axes(xlabel="Code (period in whole clock cycles)",
              ylabel="Code width [K]",
              xlim=(min(code) - 1, max(code) + 1), ylim=(0, 6))
ax.plot(code, width, colour="blue", label="measured width",
        style="only marks, mark=*, mark size=1.6pt", decimate=False)
ax.hline(lsb[0], colour="red", style="thick, dashed",
         label=f"ideal step, {lsb[0]:.2f} K")
ax.annotate(min(code), 0.6,
            f"worst DNL {max(abs(v) for v in dnl):.2f} LSB",
            anchor="south west", colour="gray!50!black")

fig.save("jnwtt_dnl")
