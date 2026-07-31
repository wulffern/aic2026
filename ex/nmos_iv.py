"""The three basic NMOS curves for the MOSFET chapter.

A transfer curve, an output curve, and intrinsic gain against gate
voltage. Between them they carry most of what the chapter asks you to
believe about a transistor, and all three come from the same 130 nm
device.

Data from the AIM-Spice testbenches in the dicex course material
(github.com/wulffern/dicex, sim/spice/NCHIO). Only regenerating the
figures needs that repo; the generated tikz/*.tex are committed.
"""

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

HOME = os.getenv("HOME")
NCHIO = f"{HOME}/pro/dicex/sim/spice/NCHIO"


def load(name):
    """Read one AIM-Spice CSV; the header sits below four banner lines."""
    with open(f"{NCHIO}/{name}.csv") as fi:
        rows = list(csv.reader(fi))
    start = next(i for i, r in enumerate(rows)
                 if r and r[0].startswith(("v", "V")) and len(r) > 1)
    header, body = rows[start], rows[start + 1:]
    cols = {h: [] for h in header}
    for row in body:
        if len(row) != len(header):
            continue
        for h, v in zip(header, row):
            cols[h].append(float(v))
    return {h: np.array(v) for h, v in cols.items()}


def main():
    # ---- transfer curve, log current ------------------------------------
    d = load("vgate")
    fig = Figure("""Drain current against gate voltage, on a log current axis.

Six decades of current over less than two volts of gate. The straight
part below threshold is weak inversion, where the gate is moving a
barrier and the current is exponential in gate voltage; above threshold
the curve bends over as the channel becomes a resistance instead.

A linear axis would show only the top decade, which is why this plot is
always drawn on a log one, and why a transistor that looks firmly off on
a linear plot is still passing nanoamps.""")
    ax = fig.axes(xlabel="$V_{GS}$ [V]", ylabel="$I_D$ [A]", ylog=True,
                  width=10.0, height=6.0)
    ax.plot(d["vgate"], np.abs(d["i(vcur)"]), colour="black",
            decimate=False)
    fig.save("vgate")

    # ---- output curve ---------------------------------------------------
    d = load("vdrain")
    fig = Figure("""Drain current against drain voltage at a fixed gate voltage.

The steep part on the left is the triode region, where the device is a
voltage controlled resistor. Past roughly 0.2 V it saturates and the
current stops caring much about the drain.

"Stops caring much" is the useful part. The curve is not flat, it keeps
a small slope, and that slope is the output conductance that limits the
gain of every amplifier in this course.""")
    ax = fig.axes(xlabel="$V_{DS}$ [V]", ylabel="$I_D$ [$\\mu$A]",
                  width=10.0, height=6.0)
    ax.plot(d["vdrain"], np.abs(d["i(vcur)"])*1e6, colour="black",
            decimate=False)
    fig.save("vdrain")

    # ---- intrinsic gain -------------------------------------------------
    d = load("vgaini")
    fig = Figure("""Intrinsic gain against gate voltage.

The quantity plotted is gm/gds, the most gain a single transistor can
give however it is loaded. It falls by more than half across the sweep,
from about 13 near threshold to 5 in strong inversion, and the fall is
monotonic.

That is the trade the chapter keeps returning to. Driving a device hard
buys speed and headroom and costs gain, and no amount of circuit
cleverness recovers what the device itself does not have.""")
    ax = fig.axes(xlabel="$V_{GS}$ [V]",
                  ylabel="Intrinsic gain $g_m/g_{ds}$ [V/V]",
                  width=10.0, height=6.0)
    ax.plot(d["vgaini"], d["v(a)"], colour="black", decimate=False)
    fig.save("vgaini")


if __name__ == "__main__":
    main()
