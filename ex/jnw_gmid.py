#!/usr/bin/env python3
"""The gm/ID design curves for the Circuits lecture, drawn in TikZ.

These seven figures used to come out of `jupyter/circuits.ipynb`, which
is fine for exploring and poor for a book: a notebook re-run in a
different order, or with a cell edited and not re-run, produces figures
that no longer agree with each other. This script produces all seven
from one pass over the same data, so they cannot drift apart.

The notebook is still worth keeping for looking at the data. It is no
longer what the book is built from.

Reads the DC gate sweeps of two sky130 nfets, simulated with ngspice and
vendored into `ex/data/` by `ex/fetch_data.py`, so it runs anywhere the
repository does.

The two devices differ only in length. JNWATR_NCH_2C1F2 is the short
one, 2C5F0 the long one, and most of what these plots show is the price
of that choice.
"""

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SHORT = "JNWATR_NCH_2C1F2"
LONG = "JNWATR_NCH_2C5F0"

# The two gm/ID values the lecture keeps coming back to: 15 is roughly
# where a low power design wants to sit, 10 where a fast one does.
MARKS = (10, 15)


def load(device, corner="KttTtVt"):
    """Read one corner of one device from ex/data/."""
    path = os.path.join(DATA, f"{device}_{corner}.csv")
    with open(path) as fi:
        rows = list(csv.reader(fi))
    header, body = rows[0], rows[1:]
    return {h: np.array([float(r[i]) for r in body])
            for i, h in enumerate(header)}


def main():
    s = load(SHORT)
    l = load(LONG)
    for d in (s, l):
        d["gmid"] = d["gm"] / d["id"]
        d["gmgds"] = d["gm"] / d["gds"]

    def marks(ax):
        for m in MARKS:
            ax.vline(m)

    # ---- I_D against V_GS, log current ----------------------------------
    fig = Figure("""Drain current against gate voltage, on a log current axis.

The straight part at low VGS is weak inversion, where the current is
exponential in gate voltage; the bend is where the channel stops being a
barrier problem and starts being a resistance problem. A log axis is the
only way to see both regions in one plot, and both regions matter.""")
    ax = fig.axes(xlabel="$V_{GS}$ [V]", ylabel="$I_D$ [A]", ylog=True,
                  width=11.0, height=6.0, legend_pos="north west")
    ax.plot(s["v(g)"], s["id"], colour="blue", label=SHORT.replace("_", "\\_"),
            decimate=False)
    ax.plot(l["v(g)"], l["id"], colour="red", label=LONG.replace("_", "\\_"),
            decimate=False)
    fig.save("jnw_id_vgs")

    # ---- gm/ID against V_GS, with the two asymptotes --------------------
    fig = Figure("""gm/ID against gate voltage, with the hand-calculation asymptotes.

The point of the figure is that the two asymptotes the lecture derives
bracket the real device and neither describes it in the middle, which is
exactly where most designs sit. Weak inversion gives the flat ceiling
1/(n VT); strong inversion gives 2/Veff falling away to the right.""")
    ax = fig.axes(xlabel="$V_{GS}$ [V]", ylabel="$g_m/I_D$ [1/V]",
                  ylim=(0, 30), width=11.0, height=6.0)
    ax.plot(s["v(g)"], s["gmid"], colour="blue",
            label=SHORT.replace("_", "\\_"), decimate=False)
    ax.plot(l["v(g)"], l["gmid"], colour="red",
            label=LONG.replace("_", "\\_"), decimate=False)
    #- Only where the asymptote means something. 2/Veff runs to infinity
    #- as Veff goes to zero, which is both a plotting problem and a
    #- reminder that strong inversion is not a description of a device
    #- sitting at threshold.
    veff = s["v(g)"] - s["vth"]
    above = veff > 0.05
    ax.plot(s["v(g)"][above], (2 / veff)[above],
            colour="black", style="dotted, thick",
            label="Strong inversion, $2/V_{eff}$", decimate=False)
    ax.hline(1 / 1.5 / 26e-3, colour="black",
             label="Weak inversion, $1/nV_T$")
    fig.save("jnw_gmid_vgs")

    # ---- intrinsic gain against gm/ID -----------------------------------
    fig = Figure("""Intrinsic gain against gm/ID: what efficiency costs in gain.

Read it right to left. Moving towards higher gm/ID buys transconductance
per unit current, and the long device keeps its gain while the short one
gives it away. The two dashed lines are the gm/ID values the lecture
keeps returning to.""")
    ax = fig.axes(xlabel="Bang-for-the-buck, $g_m/I_D$ [1/V]",
                  ylabel="Intrinsic gain $g_m/g_{ds}$ [dB]",
                  width=11.0, height=6.0)
    ax.plot(s["gmid"], 20 * np.log10(s["gmgds"]), colour="blue",
            label=SHORT.replace("_", "\\_"), decimate=False)
    ax.plot(l["gmid"], 20 * np.log10(l["gmgds"]), colour="red",
            label=LONG.replace("_", "\\_"), decimate=False)
    marks(ax)
    fig.save("jnw_gmgds_gmid")

    # ---- Vdsat and Vgs against gm/ID ------------------------------------
    for name, key, ylabel, ylim, xlim, comment in (
        ("jnw_vdsat_gmid", "vdsat", "$V_{dsat}$ [V]", None, None,
         """Saturation voltage against gm/ID: what efficiency costs in headroom.

Every volt spent keeping a device saturated is a volt the signal cannot
use, and at 0.8 V supplies that is the binding constraint more often
than gain is."""),
        ("jnw_vg_gmid", "v(g)", "Gate-source voltage [V]", (0.5, 0.75),
         (5, 20),
         """Gate voltage against gm/ID, over the useful range.

This is the plot to design from: pick a gm/ID and read off the bias
voltage the device needs."""),
    ):
        fig = Figure(comment)
        ax = fig.axes(xlabel="Bang-for-the-buck, $g_m/I_D$ [1/V]",
                      ylabel=ylabel, ylim=ylim, xlim=xlim,
                      width=11.0, height=6.0)
        ax.plot(s["gmid"], s[key], colour="blue",
                label=SHORT.replace("_", "\\_"), decimate=False)
        ax.plot(l["gmid"], l[key], colour="red",
                label=LONG.replace("_", "\\_"), decimate=False)
        marks(ax)
        fig.save(name)

    # ---- the same two, across corners -----------------------------------
    corners = (("KssTlVt", "Slow-slow, low temperature", "blue"),
               ("KssTahVt", "Slow-slow, high temperature", "red"),
               ("KffTlVt", "Fast-fast, low temperature", "armygreen"),
               ("KffTahVt", "Fast-fast, high temperature", "orange"))
    loaded = [(load(SHORT, c), name, colour) for c, name, colour in corners]
    for d, _, _ in loaded:
        d["gmid"] = d["gm"] / d["id"]

    for name, key, ylabel, ylim, comment in (
        ("jnw_vg_gmid_corners", "v(g)", "Gate-source voltage [V]",
         (0.5, 0.75),
         """Gate voltage against gm/ID over process and temperature.

The spread is the answer to "what bias voltage should I use?": there is
no single one. A design that picks a gate voltage and hopes lands at a
different gm/ID in every corner, which is the argument for biasing a
current and letting the voltage fall where it will."""),
        ("jnw_vdsat_gmid_corners", "vdsat", "$V_{dsat}$ [V]", None,
         """Saturation voltage against gm/ID over process and temperature.

The headroom a device needs is not a constant either. Size for the worst
corner shown here, not for the typical one."""),
    ):
        fig = Figure(comment)
        ax = fig.axes(xlabel="Bang-for-the-buck, $g_m/I_D$ [1/V]",
                      ylabel=ylabel, ylim=ylim, xlim=(5, 20),
                      width=11.0, height=6.0)
        for d, label, colour in loaded:
            ax.plot(d["gmid"], d[key], colour=colour, label=label,
                    decimate=False)
        marks(ax)
        fig.save(name)


if __name__ == "__main__":
    main()
