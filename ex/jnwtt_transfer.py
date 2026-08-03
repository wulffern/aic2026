#!/usr/bin/env python3
"""Both sensors against a climate chamber: the transfer curve, and what
is left after the best straight line through it.

A PTAT current charging a fixed capacitor into a comparator makes a time
inversely proportional to absolute temperature, so the rate is
proportional to it. The left panel is that line for both sensors; the
right is the residual, converted to kelvin through each sensor's own
slope so the two are comparable despite rates that differ sixfold.

Data: ex/data/jnwtt_chamber.csv and jnwtt_inl.csv, vendored from
jnw-tt-2025/meas by ex/fetch_data.py."""

import csv
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

DATA = Path(__file__).resolve().parent / "data"


def _lstsq(A, y):
    """Normal equations, solved by Gaussian elimination. Three unknowns
    and fourteen well-conditioned rows: numpy would be a dependency for
    nothing."""
    n = len(A[0])
    M = [[sum(A[k][i] * A[k][j] for k in range(len(A))) for j in range(n)]
         + [sum(A[k][i] * y[k] for k in range(len(A)))] for i in range(n)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i]))
        M[i], M[p] = M[p], M[i]
        for r in range(n):
            if r != i:
                f = M[r][i] / M[i][i]
                for c in range(i, n + 1):
                    M[r][c] -= f * M[i][c]
    return [M[i][n] / M[i][i] for i in range(n)]


def column(name, *cols):
    out = [[] for _ in cols]
    with open(DATA / name) as fh:
        for row in csv.DictReader(fh):
            for i, c in enumerate(cols):
                out[i].append(float(row[c]))
    return out


ref, r07, r06 = column("jnwtt_chamber.csv", "ref_c", "GR07_rate_hz", "GR06_rate_hz")
iref, inl07, inl06 = column("jnwtt_inl.csv", "ref_c", "GR07_inl_k", "GR06_inl_k")

fig = Figure(
    """Both sensors measured against a Voetsch climate chamber from 5 to
70 degrees C. (a) The output rate against the chamber's own probe: a
PTAT current into a fixed capacitor should give a rate proportional to
absolute temperature, and it does. GR06 is plotted on the right axis
scale, six times lower, because it is read once per reset rather than
free-running. (b) What is left after the best straight line, expressed
in kelvin through each sensor's own slope. Neither is limited by
linearity: GR07's 1.6 K is dominated by the 4.75 K staircase from
re-timing its output on the project clock.""",
    columns=2)

#- Both rates divided by their own value at 25 C. Plotted raw the two
#- lines sit six times apart and say nothing; normalised they fall on
#- the same line, which is the actual claim: same physics, read out two
#- ways. The dashed line is what a current strictly proportional to
#- absolute temperature would do.
def normalise(rate):
    i = min(range(len(ref)), key=lambda k: abs(ref[k] - 25))
    return [v / rate[i] for v in rate]


ideal = [(t + 273.15) / (25 + 273.15) for t in ref]

ax = fig.axes(xlabel="Chamber reference [$^\\circ$C]",
              ylabel="Rate / rate at 25 $^\\circ$C",
              xlim=(0, 75), ylim=(0.92, 1.18), yprecision=2)
ax.plot(ref, ideal, colour="black", label="proportional to $T$ [K]",
        style="thick, dashed", decimate=False)
ax.plot(ref, normalise(r07), colour="blue", label="GR07, 2.98 kHz/K",
        style="very thick", decimate=False)
ax.plot(ref, normalise(r06), colour="red", label="GR06, 0.48 kHz/K",
        style="very thick", decimate=False)

#- Does a bandgap curvature term account for what is left? Fit
#- rate = a + b*T + c*T*ln(T) and see how much of the residual it takes
#- away. Over a 65 K span T*ln(T) and T^2 are nearly collinear, so this
#- cannot distinguish the two - but the size and sign are the question.
def residual(rate, curvature):
    T = [c + 273.15 for c in ref]
    #- the kelvin scale is always the straight-line sensitivity. With a
    #- T ln T term in the fit the linear coefficient is no longer the
    #- slope of anything, and dividing by it gives a meaningless axis.
    base = _lstsq([[1.0, v] for v in T], rate)
    slope = base[1]
    cols = [[1.0] * len(T), T]
    if curvature:
        cols.append([v * math.log(v) for v in T])
    A = [[col[i] for col in cols] for i in range(len(T))]
    coef = _lstsq(A, rate)
    fit = [sum(c * a for c, a in zip(coef, row)) for row in A]
    return [(r - f) / slope for r, f in zip(rate, fit)]


fig.save("jnwtt_transfer")

#- the residual is its own figure: in a two column layout a panel is
#- half a column wide, and these curves have detail worth seeing
fig = Figure(
    """What is left of each sensor's transfer after the best straight
line, and what is left after also allowing a T ln T term - the bandgap
curvature the references chapter warns about. Almost all of GR06's
residual is that curvature; almost none of GR07's is.""")

ax = fig.axes(xlabel="Chamber reference [$^\\circ$C]",
              ylabel="Residual [K]",
              xlim=(0, 75), ylim=(-2, 2))
ax.hline(0, colour="gray!60", style="thin")
ax.plot(iref, inl07, colour="blue", label="GR07", style="very thick",
        decimate=False)
ax.plot(iref, inl06, colour="red", label="GR06", style="very thick",
        decimate=False)
ax.plot(ref, residual(r06, True), colour="red",
        label="GR06, less a $T\\ln T$ term", style="thick, dashed",
        decimate=False)
ax.plot(ref, residual(r07, True), colour="blue",
        label="GR07, less a $T\\ln T$ term", style="thick, dashed",
        decimate=False)

fig.save("jnwtt_inl")
