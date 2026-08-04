"""The two Seebeck figures in lx_energysrc, as house plots.

Both replaced Wikimedia images (Nanite, CC0) that rendered poorly in
the book - the metals plot was a 216 pt matplotlib SVG with tiny text,
the silicon plot a 440 px PNG.

The metals data is digitized from the marker coordinates in the
original SVG (Absolute_Seebeck_coefficients_of_various_metals_up_to_
high_temperatures.svg, Nanite, CC0), calibrated against its axis
ticks, so the curves are the original's curves.

The silicon plot is computed rather than digitized: a two-carrier
Boltzmann model with S_p = (k/q)((mu - E_V)/kT + A) and its n-type
mirror, conductivity-weighted, reproduces the original's shape - the
|S| that grows toward midgap, the sign flip of width ~4kT where the
carriers trade places, and the conductivity minimum at the same spot.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

#- Digitized from the original SVG's markers: (T [K], S [uV/K])
METALS = {
    "Cu": [(100, 1.19), (150, 1.12), (200, 1.29), (273, 1.7), (300, 1.83),
           (400, 2.34), (500, 2.83), (600, 3.33), (700, 3.83), (800, 4.34),
           (900, 4.85), (1000, 5.37), (1100, 5.89), (1200, 6.41),
           (1300, 6.91)],
    "Ag": [(100, 0.73), (150, 0.85), (200, 1.05), (273, 1.38), (300, 1.51),
           (400, 2.08), (500, 2.82), (600, 3.72), (700, 4.72), (800, 5.77),
           (900, 6.85), (1000, 7.95), (1100, 9.06), (1200, 10.15)],
    "Au": [(100, 0.82), (150, 1.02), (200, 1.34), (273, 1.79), (300, 1.94),
           (400, 2.46), (500, 2.86), (600, 3.18), (700, 3.43), (800, 3.63),
           (900, 3.77), (1000, 3.85), (1100, 3.88), (1200, 3.86),
           (1300, 3.78)],
    "Pt": [(100, 4.29), (150, 1.32), (200, -1.27), (273, -4.45),
           (300, -5.28), (400, -7.83), (500, -9.89), (600, -11.66),
           (700, -13.24), (800, -14.81), (900, -16.32), (1000, -17.79),
           (1100, -19.22), (1200, -20.62), (1300, -21.97), (1400, -23.32),
           (1600, -25.97), (1800, -28.57), (2000, -31.23)],
    "Pd": [(100, 2.0), (150, -1.63), (200, -4.85), (273, -9.0),
           (300, -9.99), (400, -13.0), (500, -16.03), (600, -19.06),
           (700, -22.09), (800, -25.12), (900, -28.15), (1000, -31.18),
           (1100, -34.21), (1200, -37.24), (1300, -40.27), (1400, -43.3),
           (1600, -49.36), (1800, -55.42), (2000, -61.48)],
    "W":  [(273, 0.13), (300, 1.07), (400, 4.44), (500, 7.53),
           (600, 10.29), (700, 12.66), (800, 14.65), (900, 16.28),
           (1000, 17.57), (1100, 18.53), (1200, 19.18), (1300, 19.53),
           (1400, 19.6), (1600, 18.97), (1800, 17.41), (2000, 15.05),
           (2200, 12.01), (2400, 8.39)],
    "Mo": [(273, 4.71), (300, 5.57), (400, 8.52), (500, 11.12),
           (600, 13.27), (700, 14.94), (800, 16.13), (900, 16.86),
           (1000, 17.16), (1100, 17.08), (1200, 16.65), (1300, 15.92),
           (1400, 14.94), (1600, 12.42), (1800, 9.52), (2000, 6.67),
           (2200, 4.3), (2400, 2.87)],
    "Pb": [(7, -0.2), (20, -0.63), (40, -0.66), (60, -0.71), (90, -0.83),
           (120, -0.92), (160, -1.03), (200, -1.1), (233, -1.18)],
}

#- Colours follow the original where the name exists; the label at the
#  end of each line does the identifying, the colour only separates.
COLOURS = {"Cu": "blue", "Ag": "armygreen", "Au": "red", "Pt": "cyan",
           "Pd": "magenta", "W": "olive", "Mo": "black", "Pb": "gray"}

#- Where each end label sits relative to the last point
ANCHOR = {"Cu": "west", "Ag": "west", "Au": "west", "Pt": "west",
          "Pd": "west", "W": "west", "Mo": "west", "Pb": "west"}


def metals():
    fig = Figure("""Absolute Seebeck coefficient of eight metals against
temperature, digitized from the Wikimedia original (Nanite, CC0) that
this figure replaces. The span is the lecture's point: from about
+20 uV/K for tungsten down to -60 uV/K for palladium, so a couple that
pairs a positive metal with a negative one doubles the voltage per
kelvin.""")

    ax = fig.axes(xlabel="Temperature [K]", ylabel="Seebeck coef.\\ [$\\mu$V/K]",
                  width=10.5, height=8.0)
    for name, pts in METALS.items():
        t = np.array([p[0] for p in pts], dtype=float)
        s = np.array([p[1] for p in pts], dtype=float)
        ax.plot(t, s, colour=COLOURS[name], decimate=False)
        ax.annotate(t[-1] + 30, s[-1], name, anchor=ANCHOR[name],
                    colour=COLOURS[name])

    fig.save("seebeck_metals")


def silicon():
    #- Nondegenerate two-carrier model at room temperature
    kT = 0.02585            # eV
    eg = 1.12               # eV
    kq = 86.17              # uV/K, k/q
    aa = 2.0                # scattering constant in S = k/q (E/kT + A)
    q = 1.602e-19
    nc, nv = 2.8e19, 1.04e19        # cm^-3
    mun, mup = 1400.0, 450.0        # cm^2/Vs

    mu = np.linspace(0.0, eg, 600)  # Fermi level, E_V = 0
    n = nc * np.exp((mu - eg) / kT)
    p = nv * np.exp(-mu / kT)
    sig_n = q * n * mun * 100.0     # S/m
    sig_p = q * p * mup * 100.0
    sigma = sig_n + sig_p

    s_n = -kq * ((eg - mu) / kT + aa) * 1e-3     # mV/K
    s_p = +kq * (mu / kT + aa) * 1e-3
    s = (sig_n * s_n + sig_p * s_p) / sigma

    #- Where the two conductivities are equal: the centre of the flip
    flip = mu[np.argmin(np.abs(sig_n - sig_p))]

    fig = Figure("""Seebeck coefficient and conductivity of silicon
against the Fermi level, computed from a two-carrier Boltzmann model
(the figure it replaces was Nanite's, CC0, via Wikimedia). |S| grows as
the Fermi level moves away from a band edge - fewer carriers, more
entropy per carrier - until, near midgap, the minority carriers catch
up and the sign flips over a window of about 4kT. The conductivity
bottoms out at the same spot, which is the thermoelectric designer's
dilemma: the doping that maximizes S minimizes sigma.""")

    ax = fig.axes(ylabel="$S$ [mV/K]", width=10.0, height=4.2,
                  options=["xtick={0,%.2f}" % eg,
                           "xticklabels={$E_V$,$E_C$}"])
    ax.plot(mu, s, colour="black", decimate=False)
    ax.annotate(flip, -1.9, "$\\leftrightarrow 4kT$", anchor="north",
                colour="black")

    ax = fig.axes(xlabel="Fermi level $\\mu$", ylabel="$\\sigma$ [S/m]",
                  width=10.0, height=4.2,
                  options=["ymode=log", "xtick={0,%.2f}" % eg,
                           "xticklabels={$E_V$,$E_C$}"])
    ax.plot(mu, sigma, colour="blue", decimate=False)

    fig.save("seebeck_silicon")


if __name__ == "__main__":
    metals()
    silicon()
