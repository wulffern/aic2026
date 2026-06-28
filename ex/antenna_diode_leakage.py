#!/usr/bin/env python3
# Reverse leakage current of an n+/p-well antenna ndiode from
# 200 K to 1000 K, normalised to a 1 um^2 junction so it can be
# scaled to any diode area. Based on ex/vd.py.

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

    # Antenna ndiode: n+ source/drain implant placed in the NMOS
    # p-well. Typical doping ranges:
    #   p-substrate (handle) ~ 2e14 - 1e15 1/cm^3
    #   p-well (retrograde)  ~ 1e17 - 1e18 1/cm^3
    #   n+ source/drain      ~ 1e19 - 2e20 1/cm^3
    # The junction sees the well doping, not the substrate.
    NA = 1e17    # p-well doping under n+ [1/cm^3]
    ND = 1e20    # n+ source/drain doping  [1/cm^3]

    # 1 um^2 reference junction area in cm^2 (same as ex/vd.py).
    # Reverse leakage scales linearly with area, so for a real diode
    # multiply by A_real_in_um2. A typical antenna ndiode is 0.2-1 um
    # per side.
    A = 1e-8

    # Minority-carrier transport. Reference values at 300 K from
    # ex/vd.py. Both D and tau depend on temperature:
    #   phonon-limited mobility mu ~ T^-2.4, and Einstein gives
    #   D = mu*kT/q ~ T^-1.4
    #   SRH lifetime tau = 1/(sigma*v_th*N_t), v_th ~ sqrt(T) so
    #   tau ~ T^-1/2
    T_REF = 300.0
    Dn_300, Dp_300 = 36.0, 12.0          # cm^2/s at 300 K
    tau_n_300, tau_p_300 = 1e-7, 1e-7    # s at 300 K
    Dn = Dn_300 * (T/T_REF)**(-1.4)
    Dp = Dp_300 * (T/T_REF)**(-1.4)
    tau_n = tau_n_300 * (T/T_REF)**(-0.5)
    tau_p = tau_p_300 * (T/T_REF)**(-0.5)

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
    ax.set_ylabel(r"Reverse leakage per 1 $\mu m^2$ [A]")
    ax.grid(True, which="both")
    ax.legend()
    ax.set_title(r"n+/p-well antenna ndiode, $V_R = 1$ V, "
                 r"per 1 $\mu m^2$, 200-1000 K")
    plt.tight_layout()

    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "media", "antenna_diode_leak.pdf")
    plt.savefig(out)
    print(f"wrote {os.path.normpath(out)}")
