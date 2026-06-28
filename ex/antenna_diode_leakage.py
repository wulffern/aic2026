#!/usr/bin/env python3
# Reverse leakage current of an antenna ndiode
# (n+ implant in a doped p-substrate) from 200 K to 600 K
# for a 0.2 x 0.2 um^2 junction. Based on ex/vd.py.

import os
from scipy import constants
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

h = constants.physical_constants["Planck constant"][0]
k = constants.Boltzmann
pi = constants.pi
m0 = constants.m_e
q = constants.physical_constants["elementary charge"][0]
eV = constants.physical_constants["electron volt"][0]

cm3 = 1e-6                        # 1/m^3 -> 1/cm^3
eps0_cm = 8.8541878128e-14        # F/cm
eps_si = 11.7 * eps0_cm           # F/cm

Eg = 1.12 * eV


def calc_ni(T):
    # Intrinsic carrier concentration as a function of T [K], see ex/vd.py
    mn = (0.98*0.19*0.19)**(1/3)*m0
    mp = 0.81*m0
    Nc = 2*np.sqrt(np.power((2*pi*k*T*mn)/(h*h), 3))
    Nv = 2*np.sqrt(np.power((2*pi*k*T*mp)/(h*h), 3))
    ni = np.sqrt(Nc*Nv)*np.exp(-Eg/(2*k*T))
    return ni*cm3


if __name__ == "__main__":
    T = np.linspace(200, 1000, 801)

    # Antenna ndiode: n+ in a doped p-substrate / p-well.
    # Typical doping ranges (bulk CMOS):
    #   bare p-substrate ~ 2e14 - 1e15 1/cm^3
    #   p-well           ~ 1e16 - 1e17 1/cm^3
    #   n+ source/drain  ~ 1e19 - 1e20 1/cm^3
    # We pick a doped p-substrate / shallow p-well midpoint, and a
    # canonical n+ source/drain.
    NA = 1e16    # p-substrate doping [1/cm^3]
    ND = 1e20    # n+ implant doping  [1/cm^3]

    # 0.2 x 0.2 um^2 junction area in cm^2
    side_um = 0.2
    A = (side_um*1e-4)**2

    # Minority-carrier transport in moderately doped silicon
    Dn = 36      # cm^2/s
    Dp = 12      # cm^2/s
    tau_n = 1e-7 # s
    tau_p = 1e-7 # s

    ni = calc_ni(T)

    # Shockley diffusion saturation current
    I_s = q*A*ni**2 * (1/NA*np.sqrt(Dn/tau_n) + 1/ND*np.sqrt(Dp/tau_p))

    # Built-in voltage
    V_bi = (k*T/q) * np.log(NA*ND/(ni**2))

    # Reverse bias (worst case ~ supply voltage)
    V_R = 1.0

    # Depletion width of a one-sided n+/p junction (NA << ND)
    W = np.sqrt(2*eps_si*(V_bi + V_R)/(q*NA))   # cm

    # Sah-Noyce-Shockley depletion-region generation current
    tau_g = 2*tau_n
    I_gen = q*A*ni*W/tau_g

    I_leak = I_s + I_gen

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.semilogy(T, I_s,   label=r"Diffusion $I_S$")
    ax.semilogy(T, I_gen, label=r"Generation $I_{gen}$")
    ax.semilogy(T, I_leak, label="Total", linewidth=2)
    ax.set_xlabel("Temperature [K]")
    ax.set_ylabel("Reverse leakage current [A]")
    ax.grid(True, which="both")
    ax.legend()
    ax.set_title(r"0.2$\times$0.2 $\mu m^2$ antenna ndiode (n+/p-sub), "
                 r"$V_R = 1$ V, 200-1000 K")
    plt.tight_layout()

    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "media", "antenna_diode_leak.pdf")
    plt.savefig(out)
    print(f"wrote {os.path.normpath(out)}")
