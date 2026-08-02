#!/usr/bin/env python3
"""Carrier velocity against channel length (MOSFET refresher, figure
33). Replaces the old rough estimate with the actual physics: the
mobility model v = mu*E with E = V/L grows without bound as L shrinks,
but real carriers follow the Caughey-Thomas expression
v = mu*E / (1 + (mu*E/v_sat)^beta)^(1/beta), which saturates at
v_sat ~ 1e7 cm/s. The speed of light is drawn in the same units, three
decades up, where it belongs."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

MU = 400.0        # cm^2/Vs, mid-range of the 100-600 the lecture quotes
V = 1.0           # V across the channel
VSAT = 1.0e7      # cm/s, electron saturation velocity in silicon
BETA = 2.0        # Caughey-Thomas exponent for electrons
C = 3.0e10        # cm/s, speed of light

# channel length sweep, 20 nm to 4 um, log spaced
N = 240
L_um = [0.02 * (4.0 / 0.02) ** (i / (N - 1)) for i in range(N)]

v_mob, v_ct = [], []
for L in L_um:
    E = V / (L * 1e-4)                       # V/cm
    v = MU * E
    v_mob.append(v)
    v_ct.append(v / (1.0 + (v / VSAT) ** BETA) ** (1.0 / BETA))

fig = Figure(
    """Carrier velocity against channel length at a fixed 1 V across
the channel. The mobility model grows without bound as L shrinks; the
Caughey-Thomas curve is what carriers actually do - they saturate at
v_sat about 1e7 cm/s. The speed of light sits three decades above,
drawn in the same units.""")

ax = fig.axes(xlabel="Channel length [$\\mu$m]", ylabel="Velocity [cm/s]",
              xlog=True, ylog=True,
              xlim=(0.02, 4.0), ylim=(1e5, 1e11),
              legend_pos="north east")
ax.plot(L_um, v_mob, colour="blue", label="$v = \\mu E$", decimate=False)
ax.plot(L_um, v_ct, colour="red", label="with velocity saturation",
        decimate=False)
ax.plot([0.02, 4.0], [VSAT, VSAT], colour="armygreen", style="thick, dashed",
        label="$v_{sat}$ in silicon", decimate=False)
ax.plot([0.02, 4.0], [C, C], colour="black", style="thin",
        label="speed of light", decimate=False)

fig.save("lr0_velocity")
