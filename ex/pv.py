#!/usr/bin/env python3

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

m = 1e-3
i_load = np.logspace(-5,-3)
i_load = np.linspace(1e-5,1e-3,200)

i_s = 1e-12

i_ph = 1e-3

V_T = 1.38e-23*300/1.6e-19

V_D = V_T*np.log((i_ph - i_load)/(i_s) + 1)

P_load = V_D*i_load


plt.subplot(2,1,1)
plt.plot(i_load/m,V_D)

plt.ylabel("Diode voltage [V]")
plt.grid()
plt.subplot(2,1,2)
plt.plot(i_load/m,P_load/m)
plt.xlabel("Current load [mA]")
plt.ylabel("Power Load [mW]")
plt.grid()
#- next to the script, not into media/: the figure the book uses is
#- the TikZ one below, and ex/*.pdf is gitignored
plt.savefig("pv.pdf")

#- The same two panels as TikZ, so the plot matches the schematics.
tfig = Figure("""A photovoltaic cell's diode voltage and delivered power against load.

The cell is a current source of 1 mA in parallel with a diode. Draw
little current and the diode takes it all, so the voltage is high and
the power low. Draw all of it and the voltage collapses. The power peaks
somewhere in between, and finding that point is what a maximum power
point tracker does.""", columns=1)

ax = tfig.axes(xlabel="Current load [mA]", ylabel="Diode voltage [V]",
               width=9.0, height=3.6)
ax.plot(i_load/m, V_D, colour="black", decimate=False)

ax = tfig.axes(xlabel="Current load [mA]", ylabel="Power to load [mW]",
               width=9.0, height=3.6)
ax.plot(i_load/m, P_load/m, colour="black", decimate=False)

tfig.save("pv")
