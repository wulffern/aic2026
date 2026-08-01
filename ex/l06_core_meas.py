#!/usr/bin/env python3
"""Measured performance of the core-transistor SAR ADC (lecture 6,
figure 6), re-plotted from the JSSC 2016 paper's embedded data so the
figure matches the book instead of arriving in the paper's own
styling. Data vendored in ex/data/l06_meas_*.csv, extracted from the
paper sources kept in cictikz/examples/jssc2016-sar."""

import csv
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

DATA = Path(__file__).resolve().parent / "data"


def spectrum(name):
    f, m = [], []
    with open(DATA / name) as fh:
        for row in csv.DictReader(fh):
            f.append(float(row["freq_mhz"]))
            m.append(max(float(row["mag_db"]), -95))
    return f, m


def series(name):
    out = {}
    with open(DATA / name) as fh:
        for row in csv.DictReader(fh):
            out.setdefault(row["series"], ([], []))
            out[row["series"]][0].append(float(row["x"]))
            out[row["series"]][1].append(float(row["y"]))
    return out


fig = Figure(
    """Measured performance of the core-transistor ADC, four panels:
output spectra at 0.69 V / 20 MS/s and 0.47 V / 2 MS/s, peak ENOB
against supply, and SNDR/SFDR against input frequency. Re-plotted from
the JSSC 2016 data so the palette and weights match the rest of the
book.""",
    columns=2,
)

for name, csvfile, note in [
    ("(a)", "l06_meas_spec20.csv",
     "ENOB = 7.82 b\\\\SNDR = 48.8 dB, SFDR = 63.1 dBc\\\\"
     "VDD = 0.69 V, IDD = 23 $\\mu$A\\\\FoM = 3.51 fJ/conv.step"),
    ("(b)", "l06_meas_spec2.csv",
     "ENOB = 7.42 b\\\\SNDR = 46.4 dB, SFDR = 61.7 dBc\\\\"
     "VDD = 0.47 V, IDD = 2 $\\mu$A\\\\FoM = 2.73 fJ/conv.step"),
]:
    f, m = spectrum(csvfile)
    fs_half = max(f)
    ax = fig.axes(xlabel=f"Frequency [MHz] {name}", ylabel="Magnitude [dBFS]",
                  xlim=(0, fs_half), ylim=(-95, 0))
    ax.plot(f, m, colour="blue", style="thin")
    ax.annotate(fs_half * 0.05, -12, note, anchor="north west")

enob = series("l06_meas_enob_vdd.csv")
ax = fig.axes(xlabel="VDD [V] (c)", ylabel="Peak ENOB @ $f_s/2$ [bit]",
              xlim=(0.4, 1.1), ylim=(6.4, 8.5), legend_pos="south east")
for (label, (x, y)), colour in zip(enob.items(),
                                   ("black", "blue", "red", "armygreen")):
    ax.plot(x, y, colour=colour, label=label, style="thick, mark=*, mark size=1.2",
            decimate=False)

sndr = series("l06_meas_sndr_fin.csv")
ax = fig.axes(xlabel="Input frequency [MHz] (d)", ylabel="Magnitude [dB]",
              xlim=(0, 10.5), ylim=(40, 70), legend_pos="south west")
for (label, (x, y)), colour in zip(sndr.items(), ("blue", "red")):
    ax.plot(x, y, colour=colour, label=label, style="thick, mark=*, mark size=1.2",
            decimate=False)

fig.save("l06_core_meas")
