#!/usr/bin/env python3
"""GR06 does not drift. It switches.

Ninety seconds of GR06 held at a fixed chamber temperature, with the
slow dwell drift removed. Thermal noise would give a fuzzy band around
zero. This sits flat, drops to a second flat level, stays there for a
second or two, and comes back: one charge trap in the silicon capturing
and emitting a single carrier.

The second figure is the trap's mean lifetime against temperature. A
straight line on a log axis against 1/kT is an Arrhenius law, which is
what identifies it as a trap rather than as something in the
instrument.

Data: ex/data/jnwtt_rts*.csv."""

import csv
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

DATA = Path(__file__).resolve().parent / "data"


def column(name, *cols):
    out = [[] for _ in cols]
    with open(DATA / name) as fh:
        for row in csv.DictReader(fh):
            for i, c in enumerate(cols):
                out[i].append(float(row[c]))
    return out


t, dev = column("jnwtt_rts.csv", "t_s", "dev_mk")
ref, step, life, frac, ok = column(
    "jnwtt_rts_life.csv", "ref_c", "step_mk", "life_ms", "frac", "resolved")

fig = Figure(
    """Ninety seconds of GR06 at a fixed chamber temperature, with the
slow dwell drift removed. Thermal noise would give a fuzzy band around
zero. This sits flat, drops about half a kelvin to a second level, stays
there a second or two, and comes back: one charge trap in the silicon
capturing and emitting a single carrier.""")

ax = fig.axes(xlabel="Time [s]",
              ylabel="GR06 deviation [mK]",
              xlim=(0, max(t)), ylim=(-900, 400))
ax.plot(t, dev, colour="red", style="thin")
ax.hline(0, colour="gray!60", style="thin")
ax.annotate(31, -700, "trapped", anchor="west", colour="gray!50!black")
ax.annotate(31, 300, "free", anchor="west", colour="gray!50!black")

fig.save("jnwtt_rts")

#- Arrhenius: lifetime against 1/kT, with kT in eV
K_EV = 8.617333e-5
x = [1.0 / (K_EV * (c + 273.15)) for c, good in zip(ref, ok) if good]
y = [ms for ms, good in zip(life, ok) if good]

fig = Figure(
    """The trap's mean lifetime in the low state against inverse thermal
energy, one point per chamber dwell. A straight line on this axis is an
Arrhenius law, which is what identifies it as a trap in the silicon
rather than as something in the instrument. Above about 55 degrees C the
two levels merge into the noise and the fit stops meaning anything, so
those dwells are left out.""")

ax = fig.axes(xlabel="$1/kT$ [eV$^{-1}$]",
              ylabel="Mean time in the low state [ms]",
              ylog=True,
              xlim=(min(x) * 0.99, max(x) * 1.01), ylim=(200, 5000),
              options=["log ticks with fixed point",
                       "ytick={200,500,1000,2000,5000}"])
ax.plot(x, y, colour="red",
        style="only marks, mark=*, mark size=1.6pt", decimate=False)
#- the fitted slope, drawn through the middle of the data
n = len(x)
mx = sum(x) / n
my = sum(math.log(v) for v in y) / n
sxy = sum((a - mx) * (math.log(b) - my) for a, b in zip(x, y))
sxx = sum((a - mx) ** 2 for a in x)
slope = sxy / sxx
ax.plot([min(x), max(x)],
        [math.exp(my + slope * (min(x) - mx)),
         math.exp(my + slope * (max(x) - mx))],
        colour="black", style="thick, dashed", decimate=False)
ax.annotate(min(x) + 0.3, 260, f"$E_a$ = {slope * 1e3:.0f} meV",
            anchor="south west", colour="gray!50!black")

fig.save("jnwtt_rts_life")
