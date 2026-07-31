"""LDO pass-fet current against gate drive, over five decades.

The testbench ramps a load current from nothing to half an amp while a
behavioural OTA holds the output at 0.8 V, so sweeping time sweeps the
pass-fet's operating point. Plotting the result against V_GS rather than
against time turns a transient into the device curve the regulator
designer actually needs.

The point of the figure is the *range*. Five decades of current over one
volt of gate drive is what a single pass-fet has to cover, and since
transconductance tracks current, the loop gain covers five decades too.

Data from `cnr_atr_sky130nm/sim/LDO_PFET/loadreg.spi`, vendored into
`ex/data/` by `ex/fetch_data.py`.
"""

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def main():
    with open(os.path.join(DATA, "ldo_loadreg.csv")) as fi:
        rows = list(csv.reader(fi))[1:]
    vgs = np.array([float(r[0]) for r in rows])
    idd = np.array([float(r[1]) for r in rows])

    decades = np.log10(idd.max()/idd.min())
    print(f"Vgs {vgs.min():.3f}..{vgs.max():.3f} V, "
          f"Id {idd.min():.3g}..{idd.max():.3g} A, {decades:.2f} decades")

    fig = Figure(f"""Pass-fet current against gate drive for a 500 mA LDO.

Five decades of drain current, from about 5 uA to 500 mA, across one
volt of gate-source voltage. The curve bends because the device starts
in weak inversion, where current is exponential in V_GS, and ends in
strong inversion, where it is closer to square law.

The range is the design problem. A pass-fet's transconductance is
roughly proportional to its current, and that transconductance sets the
loop gain of the regulator, so a compensation network chosen at 500 mA
is wrong by five orders of magnitude at 5 uA. Splitting the range, which
the next figure covers, is the usual answer.""")

    ax = fig.axes(xlabel="$V_{GS}$ [V]", ylabel="$I_D$ [A]", ylog=True,
                  width=10.0, height=6.0)
    ax.plot(vgs, idd, colour="black")
    fig.save("l7_loadreg")


if __name__ == "__main__":
    main()
