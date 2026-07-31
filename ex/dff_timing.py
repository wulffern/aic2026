"""Setup and hold time of a D flip-flop, measured rather than quoted.

Setup and hold are not numbers a flip-flop advertises, they are numbers
you measure: sweep where the data edge sits relative to the clock edge,
simulate, and find where the output stops following the input. These
four transients are two points either side of each boundary.

The sweep parameter is in picoseconds and is part of each file name:
`dff_setup_8` is 8 ps of setup, `dff_hold_-40` is -40 ps of hold, that
is, the data changing 40 ps *before* the clock edge.

Data from the AIM-Spice runs in the dicex course material
(github.com/wulffern/dicex, lectures/l14), vendored into `ex/data/` by
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

# name, the sweep point in ps, and what the reader should see
CASES = (
    ("dff_setup_8", 8,
     """A D flip-flop with 8 ps of setup time: not enough.

The data changes too close to the rising clock edge at 0.5 ns, so the
flip-flop does not capture it and q only goes high at the second edge at
1.5 ns.

That is the failure mode a setup violation produces in silicon. Nothing
is stuck and nothing looks broken on a scope; the data simply arrives a
cycle late, and only in the corners where the launching path is
slowest."""),
    ("dff_setup_10", 10,
     """The same flip-flop with 10 ps of setup time: enough.

The data has settled before the rising clock edge at 0.5 ns, and q
follows it on that edge rather than the next one. Two picoseconds
separate this from the previous figure."""),
    ("dff_hold_-40", -40,
     """A D flip-flop whose data changes 40 ps before the clock edge.

Far enough from the second rising edge at 1.5 ns that the flip-flop
takes the new low value, so q falls there."""),
    ("dff_hold_-30", -30,
     """The same flip-flop with the data edge 30 ps before the clock edge.

Ten picoseconds closer than the previous figure, and now the change is
not taken: q stays high for another period.

Hold violations are worse than setup violations. A setup violation can
be fixed by slowing the clock down, because the path just needs more
time. A hold violation does not care about the clock period at all - the
data races the clock over a distance that has nothing to do with it - so
a chip that fails hold fails at every frequency including DC, and the
only fix is more silicon."""),
)

SIGNALS = (("v(d)", "$d$"), ("v(ck)", "$ck$"),
           ("v(q)", "$q$"), ("v(qn)", "$\\overline{q}$"))


def load(name):
    """Read one AIM-Spice CSV. The header sits below four banner lines."""
    with open(os.path.join(DATA, f"{name}.csv")) as fi:
        rows = list(csv.reader(fi))
    for i, row in enumerate(rows):
        if row and row[0] == "Time":
            header = row
            body = rows[i + 1:]
            break
    else:
        raise SystemExit(f"no data header in {name}.csv")
    cols = {h: [] for h in header}
    for row in body:
        if len(row) != len(header):
            continue
        for h, v in zip(header, row):
            cols[h].append(float(v))
    return {h: np.array(v) for h, v in cols.items()}


def main():
    for name, ps, comment in CASES:
        d = load(name)
        t = d["Time"] * 1e9                       # ns
        fig = Figure(comment, columns=1, vsep=0.55)
        for i, (col, label) in enumerate(SIGNALS):
            last = i == len(SIGNALS) - 1
            fig.axes(
                ylabel=label,
                xlabel="Time [ns]" if last else None,
                ylim=(-0.2, 1.7), xlim=(0, float(t.max())),
                width=8.0, height=1.5,
                options=[] if last else ["xticklabels={}"],
            ).plot(t, d[col], colour="black", decimate=False)
        fig.save(name)


if __name__ == "__main__":
    main()
