#!/usr/bin/env python3
"""How far averaging actually helps, for both sensors.

The Allan deviation answers a question a standard deviation cannot: if I
average for tau seconds, how repeatable is the answer? A falling curve
means more averaging buys precision. A rising one means drift has taken
over and averaging longer makes the answer worse.

Data: ex/data/jnwtt_allan.csv, from fifteen minutes of both sensors
captured on the same time base."""

import csv
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

DATA = Path(__file__).resolve().parent / "data"

tau, dev07, dev06 = [], [], []
with open(DATA / "jnwtt_allan.csv") as fh:
    for row in csv.DictReader(fh):
        tau.append(float(row["tau_s"]))
        dev07.append(float(row["GR07_dev_c"]) * 1e3)
        dev06.append(float(row["GR06_dev_c"]) * 1e3)

fig = Figure(
    """Allan deviation of both sensors over a fifteen minute run in a
quiet room, in millikelvin. Lower is better, and the slope is the point:
white noise falls as one over the square root of the averaging time, so
a falling curve means averaging still buys precision. GR07 starts four
times more precise - it produces two hundred times more events - but
stops improving after about ten seconds and then gets worse, because its
output is re-timed by the project clock and the resulting idle-tone
plateaus read as drift. GR06 has no clock in its path and keeps
improving out past a minute.""")

ax = fig.axes(xlabel="Averaging time $\\tau$ [s]",
              ylabel="Allan deviation [mK]",
              xlog=True, ylog=True,
              xlim=(1, 200), ylim=(20, 200),
              #- plain numbers on a log axis: 10^{1.6} is not a
              #- millikelvin anybody can read off a page
              options=["log ticks with fixed point",
                       "ytick={20,30,50,70,100,200}",
                       "xtick={1,3,10,30,100}"])
ax.plot(tau, dev07, colour="blue", label="GR07", style="very thick",
        decimate=False)
ax.plot(tau, dev06, colour="red", label="GR06", style="very thick",
        decimate=False)

#- where each one is at its best
i7 = min(range(len(tau)), key=lambda k: dev07[k])
i6 = min(range(len(tau)), key=lambda k: dev06[k])
ax.annotate(tau[i7] * 1.15, dev07[i7] * 1.06,
            f"{dev07[i7]:.0f} mK at {tau[i7]:.0f} s", anchor="south west",
            colour="blue")
ax.annotate(tau[i6], dev06[i6] * 0.93,
            f"{dev06[i6]:.0f} mK at {tau[i6]:.0f} s", anchor="north",
            colour="red")

fig.save("jnwtt_allan")
