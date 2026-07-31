"""The SUN_PLL locking, from power-up to steady state.

Output frequency against time, measured the way a frequency counter
would: find every rising edge of CK, take the reciprocal of the interval
between consecutive edges, and average.

The averaged curve is the useful one. A single period is a noisy
estimate, because the charge pump kicks the oscillator once per
reference cycle and the instantaneous frequency moves with it. Averaging
over 200 edges shows the loop dynamics rather than the ripple, and both
are plotted so the difference is visible.

Data from the SUN_PLL transient in the sun_pll_sky130nm repository, the
extracted layout at the typical corner, vendored into `ex/data/` by
`ex/fetch_data.py`.
"""

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
WINDOW = 200            # edges in the moving average, as in freq.py
TARGET_MHZ = 256.0


def main():
    with open(os.path.join(DATA, "pll_settling.csv")) as fi:
        rows = list(csv.reader(fi))[1:]
    t = np.array([float(r[0]) for r in rows]) * 1e6          # us
    freq = 1 / np.array([float(r[1]) for r in rows]) / 1e6   # MHz

    avg = np.convolve(freq, np.ones(WINDOW)/WINDOW, mode="valid")
    t_avg = t[WINDOW-1:]

    settled = avg[t_avg > 12]
    print(f"{len(t)} edges over {t[-1]:.1f} us; "
          f"settled mean {settled.mean():.2f} MHz, "
          f"spread {settled.max()-settled.min():.2f} MHz")

    fig = Figure(f"""The SUN_PLL locking, from power-up to steady state.

The loop starts with the oscillator at its fastest, overshoots to about
500 MHz, and is pulled down past the target before settling at
{TARGET_MHZ:.0f} MHz around 12 us. That undershoot is the loop's own
second order ringing, and its size is what the phase margin is about.

The grey trace is the frequency of each individual cycle, the black one
a 200 cycle average. The width of the grey band is the charge pump
kicking the oscillator once per reference period; it does not narrow as
the loop settles, because it is not an error that the loop can correct -
it is how a charge pump PLL works.""")

    ax = fig.axes(xlabel="Time [$\\mu$s]", ylabel="Frequency [MHz]",
                  ylim=(0, 600), width=11.0, height=6.0,
                  legend_pos="north east")
    ax.plot(t, freq, colour="gray", style="thin",
            label="Cycle by cycle")
    ax.plot(t_avg, avg, colour="black", label=f"{WINDOW} cycle average")
    ax.hline(TARGET_MHZ, colour="armygreen",
             label=f"{TARGET_MHZ:.0f} MHz target")
    fig.save("sun_pll_lay_typ")


if __name__ == "__main__":
    main()
