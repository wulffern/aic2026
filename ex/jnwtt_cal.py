#!/usr/bin/env python3
"""What each oven visit buys, one figure per sensor.

The question a product asks is not how linear a sensor is, but how many
calibration temperatures it has to pay for. Each curve is the error
against the chamber's own probe after fitting one, two or three points.

Split by sensor rather than by scheme so the three schemes sit on one
axis and can be compared directly - which is the whole point, and which
is what makes GR07's second curve being worse than its first visible at
a glance.

Data: ex/data/jnwtt_cal.csv, jnwtt_cal_names.csv."""

import csv
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

DATA = Path(__file__).resolve().parent / "data"

rows = list(csv.DictReader(open(DATA / "jnwtt_cal.csv")))
names = list(csv.DictReader(open(DATA / "jnwtt_cal_names.csv")))
ref = [float(r["ref_c"]) for r in rows]

COLOURS = ["gray!60!black", "orange", "armygreen"]

for sensor, story in (
    ("GR06", "GR06 behaves the way a sensor should: every extra trim "
             "point buys accuracy, ending at 0.35 K over 5 to 70 "
             "degrees C."),
    ("GR07", "GR07 gets worse going from one point to two. A two-point "
             "fit corrects a slope, and GR07's error is not a slope but "
             "a 4.75 K staircase from re-timing its output on the "
             "project clock; trimming the line only pivots it and puts "
             "the residual somewhere else."),
):
    fig = Figure(
        f"""Reading minus reference for {sensor} after calibrating at one,
two and three temperatures. {story}""")
    ax = fig.axes(xlabel="Chamber reference [$^\\circ$C]",
                  ylabel=f"{sensor} reading $-$ reference [K]",
                  xlim=(0, 75), ylim=(-2.5, 2.5))
    ax.hline(0, colour="gray!60", style="thin")
    for i, n in enumerate(names):
        ax.plot(ref, [float(r[f"{sensor}_{i}"]) for r in rows],
                colour=COLOURS[i],
                label=f"{n['name']}, worst {float(n[sensor + '_max_k']):.2f} K",
                style="very thick", decimate=False)
    fig.save(f"jnwtt_cal_{sensor.lower()}")
