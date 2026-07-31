"""Ring oscillator frequency against control voltage, over nine corners.

This is where K_osc comes from in the PLL chapter's linear model. The
chapter says the gain "must be determined by simulation"; this is that
simulation, and it says more than one number.

Data from the SUN_PLL ROSC testbench in the sun_pll_sky130nm repository,
vendored into `ex/data/` by `ex/fetch_data.py`.
"""

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

#- The oscillator has to reach this for the loop to lock at 256 MHz with
#- the divider set to 32 and an 8 MHz reference.
TARGET_MHZ = 256.0

#- Colour by process corner, so the three temperatures of one corner read
#- as a family rather than as three unrelated curves.
STYLE = {
    "Kff": ("red", "Fast-fast"),
    "Ktt": ("black", "Typical"),
    "Kss": ("blue", "Slow-slow"),
}
TEMP = {"Tl": ("dashed", "cold"), "Tt": ("solid", "27 C"),
        "Th": ("dotted", "hot")}


def load():
    with open(os.path.join(DATA, "rosc_kvco.csv")) as fi:
        rows = list(csv.reader(fi))[1:]
    out = {}
    for corner, v, f in rows:
        out.setdefault(corner, ([], []))
        out[corner][0].append(float(v))
        out[corner][1].append(float(f)/1e6)
    return out


def main():
    d = load()

    fig = Figure(f"""Ring oscillator frequency against its supply, over nine corners.

Simulated on the extracted layout, not the schematic, which matters:
the schematic gave 1.6 GHz/V and this gives 1.01 GHz/V at the typical
corner. The missing third is parasitic capacitance in the ring.

The control node is the oscillator's own supply, so this curve is both
the tuning characteristic and a statement about how badly a ring
oscillator tracks its supply. The slope is the K_osc the linear model
needs.

Read the spread rather than any single curve. At 1.2 V the frequency
varies by a factor of eleven between the fast-hot and slow-cold corners,
narrowing to under three at 1.5 V, and the dashed line marks the
{TARGET_MHZ:.0f} MHz the loop has to reach. Every corner crosses it, but
slow-cold only at about 1.44 V, near the top of the range. That crossing
is what limits the tuning range the design has left, not the width of
the control range on paper.

One point is missing from the slow-cold curve at 1.1 V. The oscillator
was too slow there to produce enough edges inside the simulated window,
so the measurement failed rather than returning a wrong number. That is
the corner to worry about.""")

    ax = fig.axes(xlabel="$V_{DD,ROSC}$ [V]", ylabel="Frequency [MHz]",
                  width=11.0, height=6.5, legend_pos="north west")
    for corner in sorted(d, key=lambda c: (c[:3], c[3:])):
        v, f = d[corner]
        colour, pname = STYLE[corner[:3]]
        style, tname = TEMP[corner[3:]]
        ax.plot(v, f, colour=colour, style=f"{style}, very thick",
                label=f"{pname}, {tname}", decimate=False)
    ax.hline(TARGET_MHZ, colour="armygreen",
             label=f"{TARGET_MHZ:.0f} MHz target")
    fig.save("SUN_PLL_ROSC_KVCO")

    #- the numbers the chapter quotes, printed so they cannot drift
    print(f"{'corner':10s} {'f min':>9s} {'f max':>9s} "
          f"{'K_osc':>12s}  reaches target")
    for corner in sorted(d):
        v, f = d[corner]
        k = np.polyfit(v, f, 1)[0]
        ok = "yes" if max(f) >= TARGET_MHZ else "NO"
        print(f"{corner:10s} {min(f):8.0f}M {max(f):8.0f}M "
              f"{k:9.0f} MHz/V  {ok}")


if __name__ == "__main__":
    main()
