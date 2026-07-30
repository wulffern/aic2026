#!/usr/bin/env python3
"""gm/ID design curve for the MOSFET lecture.

Reads the DC gate sweep of a sky130 nfet_01v8 (JNWATR_NCH_2C1F2, W/L =
2x1u/0.23u? see jnw_atr_sky130a) simulated with ngspice via cicsim, and
plots the measured gm/ID against the two hand-calculation asymptotes the
lecture derives:

  weak inversion:   gm/ID = 1/(n VT), n taken from the subthreshold slope
  strong inversion: gm/ID = 2/Veff = 2/(VGS - VTH)

Needs the aicex simulation data (github.com/wulffern/aicex) at
~/pro/aicex, so this is not part of the CI build; the committed
media/gmid.{pdf,svg} are its output.
"""

import os

import cicsim as cs
import matplotlib.pyplot as plt
import numpy as np

home = os.getenv("HOME")
jnwatr = "pro/aicex/ip/jnw_atr_sky130a/sim"
tr = "JNWATR_NCH_2C1F2"
raw = "output_dc/dc_SchGtKttTtVt.raw"

df = cs.toDataFrame(f"{home}/{jnwatr}/{tr}/{raw}")

VT = 8.617333e-5 * (273.15 + 27)  # kT/q at the simulation's 27 C

vgs = df["v(v-sweep)"].to_numpy()
gm = df["gm"].to_numpy()
id_ = np.abs(df["i(id)"].to_numpy())
vth = df["v(vth)"].to_numpy()

gmid = gm / id_

#- Slope factor from the simulation itself: in weak inversion
#  gm/ID = 1/(n VT), so read it where the curve flattens (well below VTH)
weak = vgs < (vth - 0.15)
n = 1 / (np.max(gmid[weak]) * VT)
print(f"n = {n:.2f}, 1/nVT = {1/(n*VT):.1f} 1/V")

plt.figure()
plt.plot(vgs, gmid, color="black", linewidth=1.2, label="sky130 nfet_01v8 (ngspice)")

#- Weak inversion asymptote
plt.axhline(1 / (n * VT), color="black", linewidth=0.7, linestyle="--",
            label=f"$1/(nV_T)$, n = {n:.2f}")

#- Strong inversion asymptote, drawn where Veff > 50 mV
veff = vgs - vth
strong = veff > 0.05
plt.plot(vgs[strong], 2 / veff[strong], color="black", linewidth=0.7,
         linestyle=":", label=r"$2/V_{eff}$")

#- Threshold voltage marker
vt0 = float(vth[np.argmin(np.abs(vgs - vth))])
plt.axvline(vt0, color="black", linewidth=0.5)
plt.text(vt0 + 0.02, 20, f"$V_{{tn}} \\approx$ {vt0:.2f} V")

plt.xlabel(r"$V_{GS}$ [V]")
plt.ylabel(r"$g_m/I_D$ [1/V]")
plt.ylim(0, 30)
plt.xlim(0, max(vgs))
plt.grid(True)
plt.legend()

fig = plt.gcf()
fig.set_size_inches(8, 5)
plt.tight_layout()
plt.savefig("gmid.pdf")
plt.savefig("gmid.svg")
plt.show()
