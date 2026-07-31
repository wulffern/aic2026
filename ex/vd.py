#!/usr/bin/env python3
# based on Streetman
import os
import sys

from scipy import constants
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

sns.set_theme(style="dark")

h = constants.physical_constants["Planck constant"][0]
k = constants.Boltzmann
pi = constants.pi
m0 = constants.m_e
q = constants.physical_constants["elementary charge"][0]
eV = constants.physical_constants["electron volt"][0]
cm3 = 1e-6
m = 1e3


# |----------------- Ec = Conduction band
# |  |
# |  Eg  = Band gap
# |  |
# |  |
# |----------------- Ev = Valence band
#
Eg = 1.12 *eV #Bandgap of Silicon, changes with temperature, but we ignore that



def calc_ni(T):
    #Calculate intrinsic carrier concentration as a function of temperature in Kelvin

    #http://apachepersonal.miun.se/~gorthu/halvledare/Effective%20mass%20in%20semiconductors.htm
    # According to above, the electron mass for density of states calculation is
    # (m_l*m_t^2)^(1/3), but silicon has SIX equivalent conduction band minima
    # and the density of states counts all of them, so the mass carries a
    # factor 6^(2/3). Without it m_n* comes out 0.33*m0 instead of 1.08*m0 and
    # n_i is a factor sqrt(6) too small.
    mn = 6**(2/3)*(0.98*0.19*0.19)**(1/3)*m0
    mp = 0.81*m0 #- Assuming a heavy hole

# The intrinsic carrier concentration depends on the fermi level and the density of states, which depends
# on the effective mass of electrons and holes. See page 90 - 95 in Streetman
    Nc = 2*np.sqrt(np.power((2*pi*k*T*mn)/(h*h),3))
    Nv = 2*np.sqrt(np.power((2*pi*k*T*mp)/(h*h),3))

    ni = np.sqrt(Nc*Nv)*np.exp(-Eg/(2*k*T))
    return ni*cm3

if __name__ == "__main__":
    TNOM = 300.15

    T = np.arange(TNOM-26.75 - 40,TNOM + 100)

    #- Doubling per 11 C
    n_i_simple = 1.1e10 * 2**((T - TNOM)/11)

    #- BSIM 4.8 model
    n_i_bsim = 1.45e10*(TNOM/300.15) * np.sqrt(T/300.15) \
        * np.exp(21.5565981 - (Eg)/(2*k*T))

    #- Use full calculation
    n_i_adv = calc_ni(T)

    #- Doping consentrations
    NA = 1e19
    ND = 1e19

    #- Area of diode cm^2
    A = 1e-8

    #- Diffusion constant of electrons
    Dn = 36 # cm^2/s
    Dp = 12 # cm^2/s

    #- Mean lifetime of electrons. Strongly depends on doping density.
    #http://www.ioffe.ru/SVA/NSM/Semicond/Si/electric.html
    tau_n = 8e-8
    tau_p = 8e-8

    I_s = q*A*n_i_adv**2*(1/NA*np.sqrt(Dn/tau_n) + 1/ND*np.sqrt(Dp/tau_n))

    I_c = 1e-6

    Vd = k*T/q*np.log(I_c/I_s)

    C = T - 273.15

    #- Find error from linear
    line = np.polynomial.polynomial.polyfit(T,Vd,1)
    vd_lin_err = Vd - (T*line[1] + line[0])


    #- Plot ni
    plt.subplot(3,1,1)
    plt.semilogy(C,n_i_adv,label="Advanced")
    plt.semilogy(C,n_i_simple,label="Simple")
    plt.semilogy(C,n_i_bsim,label="BSIM 4.8")
    plt.grid()
    plt.legend()
    plt.ylabel(" $n_i$ [$1/cm^3$]")

    #- Plot Vd
    plt.subplot(3,1,2)
    plt.plot(C,Vd)
    plt.grid(True)
    plt.ylabel("Diode voltage [V]")


    #- Plot Vd linear error
    plt.subplot(3,1,3)
    plt.grid(True)
    plt.plot(C,vd_lin_err*m)

    plt.ylabel("Non-linear component (mV)")
    plt.xlabel("Temperature [C]")

    plt.show()

    #- The same data as TikZ, split the way the lectures use it: the
    #- carrier concentration is its own figure, the diode voltage and its
    #- curvature another. See py/tikzplot.py.
    nfig = Figure("""Intrinsic carrier concentration of silicon against temperature.

Three ways of computing the same thing. The "simple" rule of doubling
every 11 degrees is the one worth carrying in your head, and the plot
shows where it stops being true: it is good around room temperature and
optimistic in the cold, because it takes no account of the bandgap
sitting in an exponent.

All three agree to within a factor of two over the range an integrated
circuit will actually see, which is the useful conclusion.""")
    ax = nfig.axes(xlabel="Temperature [$^\\circ$C]",
                   ylabel="$n_i$ [1/cm$^3$]", ylog=True,
                   width=10.0, height=6.0, legend_pos="north west")
    ax.plot(C, n_i_adv, colour="blue", label="Advanced", decimate=False)
    ax.plot(C, n_i_simple, colour="red", label="Simple, doubling per 11 $^\\circ$C",
            decimate=False)
    ax.plot(C, n_i_bsim, colour="armygreen", label="BSIM 4.8", decimate=False)
    nfig.save("ni")

    vfig = Figure("""Diode forward voltage against temperature, and its curvature.

The top panel is why a diode makes a usable temperature sensor: at a
fixed current the forward voltage falls almost exactly linearly, here
by 0.95 mV per degree. The textbook figure of about 2 mV per degree is
for a diode carrying rather more current than the 1 uA used here; the
slope depends on the bias, the linearity does not.

The bottom panel is the "almost". Subtracting the best straight line
leaves a bow of about 3 mV peak to peak, and that residual is the
curvature term a bandgap reference has to deal with. It is small, it is
systematic, and it is the reason a first order bandgap is flat to a few
millivolts rather than to nothing.""", columns=1)
    ax = vfig.axes(ylabel="Diode voltage [V]",
                   xlabel="Temperature [$^\\circ$C]",
                   width=9.5, height=3.6)
    ax.plot(C, Vd, colour="black", decimate=False)
    ax = vfig.axes(ylabel="Non-linear component [mV]",
                   xlabel="Temperature [$^\\circ$C]",
                   width=9.5, height=3.6)
    ax.plot(C, vd_lin_err*m, colour="red", decimate=False)
    vfig.save("vd")
