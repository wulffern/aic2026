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
JNWTT = os.environ.get("JNWTT", f"{HOME}/pro/jnw-tt-2025")

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


def _num(v):
    """The two sensors are sampled independently, so a row may carry a
    value for only one of them."""
    return "" if v is None else f"{float(v):.6g}"


def fetch_jnwtt():
    """The measured silicon: two student temperature sensors on Tiny
    Tapeout project 258, characterised against a climate chamber.

    Everything here is already reduced - the analysis lives in
    jnw-tt-2025/meas, not in this book - so this only trims it to the
    columns the figures draw and writes plain CSV.
    """
    import json

    src = f"{JNWTT}/meas/data"
    if not os.path.isdir(src):
        print(f"  {src} not found, skipping")
        return 0
    n = 0

    #- the chamber sweep: 5 to 70 C in 5 K steps, both sensors
    chamber = os.path.join(src, "2026-08-03_chamber_summary.csv")
    if os.path.isfile(chamber):
        keep = ["set_c", "ref_c", "GR07_rate_hz", "GR07_sigma_hz",
                "GR06_rate_hz", "GR06_sigma_hz",
                "GR07_clock_cycles", "GR07_dist_to_whole_cycle"]
        with open(chamber) as fi:
            rows = list(csv.DictReader(fi))
        with open(os.path.join(DATA, "jnwtt_chamber.csv"), "w", newline="") as fo:
            w = csv.writer(fo)
            w.writerow(keep)
            for r in rows:
                w.writerow([f"{float(r[k]):.6g}" for k in keep])
        print(f"  jnwtt_chamber.csv ({len(rows)} set points)")
        n += 1

    #- everything the slides computed, keyed by figure
    deck = os.path.join(src, "deck_data.json")
    if os.path.isfile(deck):
        d = json.load(open(deck))

        allan = {s: dict(d["sensors"][s]["allan_curve"]) for s in ("GR07", "GR06")}
        taus = sorted({t for s in allan for t in allan[s]})
        with open(os.path.join(DATA, "jnwtt_allan.csv"), "w", newline="") as fo:
            w = csv.writer(fo)
            w.writerow(["tau_s", "GR07_dev_c", "GR06_dev_c"])
            for tau in taus:
                w.writerow([f"{tau:.6g}",
                            f"{allan['GR07'].get(tau, float('nan')):.6g}",
                            f"{allan['GR06'].get(tau, float('nan')):.6g}"])
        print(f"  jnwtt_allan.csv ({len(taus)} points)")
        n += 1

        ch = d["chamber"]
        with open(os.path.join(DATA, "jnwtt_inl.csv"), "w", newline="") as fo:
            w = csv.writer(fo)
            w.writerow(["ref_c", "GR07_inl_k", "GR06_inl_k",
                        "GR07_noise_mk", "GR06_noise_mk"])
            for i, ref in enumerate(ch["ref_c"]):
                w.writerow([f"{ref:.6g}",
                            f"{ch['sensors']['GR07']['inl_k'][i]:.6g}",
                            f"{ch['sensors']['GR06']['inl_k'][i]:.6g}",
                            f"{ch['sensors']['GR07']['noise_mk'][i]:.6g}",
                            f"{ch['sensors']['GR06']['noise_mk'][i]:.6g}"])
        print(f"  jnwtt_inl.csv ({len(ch['ref_c'])} points)")
        n += 1

        #- what one, two and three oven visits buy
        with open(os.path.join(DATA, "jnwtt_cal.csv"), "w", newline="") as fo:
            w = csv.writer(fo)
            names = [c["name"] for c in ch["sensors"]["GR07"]["cal"]]
            w.writerow(["ref_c"] + [f"GR07_{i}" for i in range(len(names))]
                       + [f"GR06_{i}" for i in range(len(names))])
            for i, ref in enumerate(ch["ref_c"]):
                row = [f"{ref:.6g}"]
                for s in ("GR07", "GR06"):
                    row += [f"{c['err_k'][i]:.6g}" for c in ch["sensors"][s]["cal"]]
                w.writerow(row)
        with open(os.path.join(DATA, "jnwtt_cal_names.csv"), "w", newline="") as fo:
            w = csv.writer(fo)
            w.writerow(["index", "name", "GR07_max_k", "GR06_max_k"])
            for i, c in enumerate(ch["sensors"]["GR07"]["cal"]):
                w.writerow([i, c["name"], f"{c['max_k']:.6g}",
                            f"{ch['sensors']['GR06']['cal'][i]['max_k']:.6g}"])
        print(f"  jnwtt_cal.csv, jnwtt_cal_names.csv ({len(names)} schemes)")
        n += 2

        #- the single charge trap in GR06
        b = ch["burst"]
        with open(os.path.join(DATA, "jnwtt_rts.csv"), "w", newline="") as fo:
            w = csv.writer(fo)
            w.writerow(["t_s", "dev_mk"])
            for t, v in b["trace_mk"]:
                w.writerow([f"{t:.6g}", f"{v:.6g}"])
        with open(os.path.join(DATA, "jnwtt_rts_life.csv"), "w", newline="") as fo:
            w = csv.writer(fo)
            w.writerow(["ref_c", "step_mk", "life_ms", "frac", "resolved"])
            for r in b["per_dwell"]:
                w.writerow([f"{r['ref_c']:.6g}", f"{r['step_mk']:.6g}",
                            f"{r['life_ms']:.6g}", f"{r['frac']:.6g}",
                            int(r["resolved"])])
        print(f"  jnwtt_rts.csv, jnwtt_rts_life.csv")
        n += 2

        #- a can of freeze spray, then a fingertip on the package
        with open(os.path.join(DATA, "jnwtt_spray.csv"), "w", newline="") as fo:
            w = csv.writer(fo)
            w.writerow(["t_s", "GR07_c", "GR06_c"])
            #- keys forced to float: the source is a rolling display
            #- buffer and can hand back its tail before its head
            a = {float(k): v for k, v in d["sensors"]["GR07"]["trace"]}
            b = {float(k): v for k, v in d["sensors"]["GR06"]["trace"]}
            for ts in sorted(set(a) | set(b)):
                w.writerow([f"{ts:.6g}", _num(a.get(ts)), _num(b.get(ts))])
        print(f"  jnwtt_spray.csv ({len(a)} + {len(b)} points)")
        n += 1

        #- four breaths on the package: the same event, two sensors
        with open(os.path.join(DATA, "jnwtt_breath.csv"), "w", newline="") as fo:
            w = csv.writer(fo)
            w.writerow(["t_s", "GR07_c", "GR06_c"])
            a = {float(k): v for k, v in d["breath"]["trace"]["GR07"]}
            b = {float(k): v for k, v in d["breath"]["trace"]["GR06"]}
            for ts in sorted(set(a) | set(b)):
                w.writerow([f"{ts:.6g}", _num(a.get(ts)), _num(b.get(ts))])
        print(f"  jnwtt_breath.csv ({len(a)} points)")
        n += 1

        #- fifteen minutes of both sensors in a quiet room
        with open(os.path.join(DATA, "jnwtt_dual.csv"), "w", newline="") as fo:
            w = csv.writer(fo)
            w.writerow(["t_min", "GR07_c", "GR06_c"])
            for t, a, b2 in zip(d["series"]["t_min"], d["series"]["GR07"],
                                d["series"]["GR06"]):
                w.writerow([f"{t:.6g}", f"{a:.6g}", f"{b2:.6g}"])
        print(f"  jnwtt_dual.csv ({len(d['series']['t_min'])} readings)")
        n += 1
    return n


def main():
    os.makedirs(DATA, exist_ok=True)
    print(f"from {AICEX}:")
    a = fetch_jnw()
    print(f"from {SUNPLL}:")
    a += fetch_rosc_kvco()
    a += fetch_pll_settling()
    print(f"from {CNRATR}:")
    a += fetch_loadreg()
    print(f"from {JNWTT}:")
    a += fetch_jnwtt()
    print(f"from {DICEX}:")
    b = fetch_dicex()
    print(f"{a + b} files in {os.path.relpath(DATA, os.path.dirname(HERE))}")
    if a + b == 0:
        sys.exit("nothing copied; check the paths above")


if __name__ == "__main__":
    main()
