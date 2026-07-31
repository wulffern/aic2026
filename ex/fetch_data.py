#!/usr/bin/env python3
"""Copy the simulation data the plot scripts need into ex/data/.

Several figures are drawn from simulations that live in other
repositories. Depending on those directly means the figures can only be
regenerated on a machine that happens to have them checked out in the
right place, and it means a script fails with a confusing path error
rather than an explanation.

So the data is vendored: this script reads the source repositories,
keeps only the columns the figures actually use, and writes plain CSV
into `ex/data/`, which is committed. Everything in `ex/` then reads from
there and needs nothing but numpy.

Run this only when a simulation has been re-run:

    python3 ex/fetch_data.py

It needs, at the paths below:

  * github.com/wulffern/aicex   at ~/pro/aicex
  * github.com/wulffern/dicex   at ~/pro/dicex
  * sun_pll_sky130nm            at ~/pro/aicex/ip/sun_pll_sky130nm

Trimming matters. The gm/ID sweeps are cicsim raw files with sixty-odd
columns of which six are plotted, and reading them needs cicsim
installed; the trimmed CSV is a tenth the size and needs nothing.
"""

import csv
import os
import sys

HOME = os.path.expanduser("~")
AICEX = os.environ.get("AICEX", f"{HOME}/pro/aicex")
DICEX = os.environ.get("DICEX", f"{HOME}/pro/dicex")
SUNPLL = os.environ.get("SUNPLL", f"{AICEX}/ip/sun_pll_sky130nm")
CNRATR = os.environ.get("CNRATR", f"{AICEX}/ip/cnr_atr_sky130nm")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

#- gm/ID sweeps: device, corner, output name
JNW = f"{AICEX}/ip/jnw_atr_sky130a/sim"
JNW_WANT = ("gm", "gds", "id", "vth", "vdsat", "v(g)")
JNW_RUNS = [
    ("JNWATR_NCH_2C1F2", "KttTtVt"),
    ("JNWATR_NCH_2C5F0", "KttTtVt"),
    ("JNWATR_NCH_2C1F2", "KssTlVt"),
    ("JNWATR_NCH_2C1F2", "KssTahVt"),
    ("JNWATR_NCH_2C1F2", "KffTlVt"),
    ("JNWATR_NCH_2C1F2", "KffTahVt"),
]

#- straight copies, source relative to DICEX
DICEX_FILES = [
    f"lectures/l14/dff_{n}.csv" for n in
    ("setup_8", "setup_10", "hold_-40", "hold_-30")
] + [
    "ex4/rosc_temp.yaml",
    "ex4/rosc_vdd.yaml",
    "sim/spice/NCHIO/vgate.csv",
    "sim/spice/NCHIO/vdrain.csv",
    "sim/spice/NCHIO/vgaini.csv",
]


def short(col):
    """cicsim names a column @m.xdut.xm1.msky130_..._01v8[gm]; want 'gm'."""
    return col[col.index("[") + 1:col.index("]")] if "[" in col else col


def fetch_jnw():
    try:
        import cicsim as cs
    except ImportError:
        print("  skipped gm/ID sweeps: cicsim not installed")
        return 0
    n = 0
    for device, corner in JNW_RUNS:
        src = f"{JNW}/{device}/output_dc/dc_SchGt{corner}.raw"
        if not os.path.exists(src):
            print(f"  missing {src}")
            continue
        df = cs.toDataFrame(src)
        #- cicsim returns both `@m.xdut...[gm]` and a plain `gm`, so
        #- keep the first of each short name rather than both
        keep, seen = [], set()
        for c in df.columns:
            k = short(c)
            if k in JNW_WANT and k not in seen:
                seen.add(k)
                keep.append(c)
        out = os.path.join(DATA, f"{device}_{corner}.csv")
        with open(out, "w", newline="") as fo:
            w = csv.writer(fo)
            w.writerow([short(c) for c in keep])
            for row in zip(*(df[c] for c in keep)):
                w.writerow([f"{v:.7g}" for v in row])
        print(f"  {os.path.basename(out)} "
              f"({len(df)} rows, {len(keep)} of {len(df.columns)} columns)")
        n += 1
    return n


def fetch_dicex():
    n = 0
    for rel in DICEX_FILES:
        src = os.path.join(DICEX, rel)
        if not os.path.exists(src):
            print(f"  missing {src}")
            continue
        dst = os.path.join(DATA, os.path.basename(rel))
        with open(src) as fi, open(dst, "w") as fo:
            fo.write(fi.read())
        print(f"  {os.path.basename(dst)}")
        n += 1
    return n


def fetch_rosc_kvco():
    """Ring oscillator frequency against control voltage, all corners.

    cicsim leaves the measurements in the ngspice log rather than in a
    data file, so they are parsed out here: a `vrosc = ` line sets the
    control voltage and the `tpd = ` line after it gives the period.
    A corner where the oscillator was too slow to produce enough edges
    inside the simulated window logs `Error: measure` instead, and that
    point is simply absent — which is itself a result worth keeping.
    """
    import glob
    import re
    logs = sorted(glob.glob(f"{SUNPLL}/sim/ROSC/output_tran/*.log"))
    if not logs:
        print(f"  missing {SUNPLL}/sim/ROSC/output_tran/*.log")
        return 0
    out = os.path.join(DATA, "rosc_kvco.csv")
    n = 0
    with open(out, "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["corner", "vrosc", "freq"])
        for path in logs:
            corner = (os.path.basename(path)
                      .replace("tran_LayGt", "").replace("Vt.log", ""))
            v = None
            for line in open(path):
                m = re.match(r"^vrosc\s+=\s+(\S+)", line)
                if m:
                    v = float(m.group(1))
                    continue
                m = re.match(r"^tpd\s+=\s+(\S+)", line)
                if m and v is not None:
                    w.writerow([corner, f"{v:.4g}", f"{1/float(m.group(1)):.7g}"])
                    n += 1
    print(f"  rosc_kvco.csv ({n} points from {len(logs)} corners)")
    return 1


def fetch_pll_settling():
    """PLL output frequency against time, from power-up to lock.

    The transient .raw is 35 MB; what the figure needs is the rising
    edge times of v(CK) and the period between them, which is a few
    thousand rows. Extracted here so the book does not carry the
    waveform.
    """
    try:
        import cicsim as cs
    except ImportError:
        print("  skipped PLL settling: cicsim not installed")
        return 0
    src = f"{SUNPLL}/sim/SUN_PLL/output_tran/full_1e4.raw"
    if not os.path.exists(src):
        print(f"  missing {src}")
        return 0
    df = cs.toDataFrames(cs.ngRawRead(src))[0].set_index("time")
    prev, falling, vth = 0.0, False, 0.8
    rows = []
    for t, v in df["v(ck)"].items():
        if not falling and v > vth:
            rows.append((t, t - prev))
            prev = t
            falling = True
        if falling and v < vth - 0.2:
            falling = False
    rows.pop(0)
    out = os.path.join(DATA, "pll_settling.csv")
    with open(out, "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["time", "period"])
        for t, p in rows:
            w.writerow([f"{t:.10g}", f"{p:.7g}"])
    print(f"  pll_settling.csv ({len(rows)} edges)")
    return 1


def fetch_loadreg():
    """LDO pass-fet current against gate drive.

    The testbench ramps a load current and lets a behavioural OTA hold
    the output at 0.8 V, so sweeping time sweeps the operating point.
    What the figure needs is the current against V_GS, which is
    V(VDD) - V(G); neither is saved under that name, so both are
    computed here.
    """
    try:
        import cicsim as cs
    except ImportError:
        print("  skipped loadreg: cicsim not installed")
        return 0
    src = f"{CNRATR}/sim/LDO_PFET/output_loadreg/loadreg_SchGtKttTtVt.raw"
    if not os.path.exists(src):
        print(f"  missing {src}")
        return 0
    import numpy as np
    df = cs.toDataFrames(cs.ngRawRead(src))[0]
    vgs = np.asarray(df["v(vdd)"], float) - np.asarray(df["v(g)"], float)
    il = np.asarray(df["v(il)"], float)
    #- below a hundred nanoamps the behavioural OTA has not settled and
    #- the current is not a transistor measurement
    keep = il > 1e-7
    out = os.path.join(DATA, "ldo_loadreg.csv")
    with open(out, "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["vgs", "id"])
        for a, b in zip(vgs[keep], il[keep]):
            w.writerow([f"{a:.6g}", f"{b:.6g}"])
    print(f"  ldo_loadreg.csv ({int(keep.sum())} points)")
    return 1


def main():
    os.makedirs(DATA, exist_ok=True)
    print(f"from {AICEX}:")
    a = fetch_jnw()
    print(f"from {SUNPLL}:")
    a += fetch_rosc_kvco()
    a += fetch_pll_settling()
    print(f"from {CNRATR}:")
    a += fetch_loadreg()
    print(f"from {DICEX}:")
    b = fetch_dicex()
    print(f"{a + b} files in {os.path.relpath(DATA, os.path.dirname(HERE))}")
    if a + b == 0:
        sys.exit("nothing copied; check the paths above")


if __name__ == "__main__":
    main()
