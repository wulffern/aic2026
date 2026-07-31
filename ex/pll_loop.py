"""The linear phase-domain model of the SUN_PLL, drawn in TikZ.

Loop gain and closed loop response of the charge-pump PLL the Clocks and
PLLs chapter works through. Everything here is analytic, so unlike the
other converted plots this one needs no simulation data at all - only
the component values from the design, which are repeated below.

Two things the chapter asks the reader to check are computed rather than
asserted: the phase margin, and the unity-gain frequency against the
reference, which is what decides whether the linear model is entitled to
be believed in the first place.

Originally jupyter/pll.ipynb in the sun_pll_sky130nm repository.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

#- Design values, see the SUN_PLL schematics and sim/ROSC.
#-
#- The oscillator gain is quoted twice on purpose. 1.6 GHz/V is what the
#- schematic gave; 1.01 GHz/V is the typical corner of the extracted
#- layout (sim/ROSC, VIEW=Lay, which includes SUN_PLL_ROSC_lpe.spi), and
#- is the number ex/rosc_kvco.py measures. Parasitic capacitance in the
#- ring costs a third of the gain, and the loop notices.
KVCO_SCH = 1.6e9                # Hz/V, schematic
KVCO_LAY = 1.013e9              # Hz/V, extracted layout, typical corner
KVCO = 2 * np.pi * KVCO_LAY     # rad/s per volt on VDD_ROSC
ICP = 1e-6                      # charge pump current
R = 32e3 * 2                    # loop filter series resistor
C1 = 6.024e-12                  # loop filter main capacitor
C2 = 0.33e-12                   # loop filter shunt capacitor
N = 32                          # feedback divider
FREF = 8e6                      # reference frequency, 256 MHz / 32


def loop(kvco_hz, f):
    """Loop gain and closed loop response for one oscillator gain."""
    s = 1j * 2 * np.pi * f
    kpd = ICP / (2 * np.pi)
    klp_hlp = (1 / ((C1 + C2) * s)
               * (1 + s * R * C1) / (1 + s * R * (C1 * C2) / (C1 + C2)))
    Ls = 2 * np.pi * kvco_hz * kpd * klp_hlp / (N * s)
    return Ls, Ls / (1 + Ls)


def crossover(f, Ls):
    """Unity gain frequency and phase margin, interpolated.

    Taking the first sample below 0 dB instead, as the original notebook
    did on a 50 point grid, put the crossing at 720 kHz rather than
    589 kHz and reported 55 degrees rather than 51.
    """
    mag = 20 * np.log10(np.abs(Ls))
    ph = np.angle(Ls, deg=True)
    i = int(np.where(mag < 0)[0][0])
    j = i - 1
    t = (0 - mag[j]) / (mag[i] - mag[j])
    fc = np.exp(np.log(f[j]) + t*(np.log(f[i]) - np.log(f[j])))
    pm = ph[j] + t*(ph[i] - ph[j]) + 180
    return fc, pm


def main():
    f = np.logspace(3, 8, 2000)

    Ls, Cs = loop(KVCO_LAY, f)
    fc, pm = crossover(f, Ls)
    fc_s, pm_s = crossover(f, loop(KVCO_SCH, f)[0])

    print(f"schematic  Kvco = {KVCO_SCH/1e9:.3f} GHz/V -> "
          f"crossover {fc_s/1e6:.2f} MHz, phase margin {pm_s:.1f} deg")
    print(f"layout     Kvco = {KVCO_LAY/1e9:.3f} GHz/V -> "
          f"crossover {fc/1e6:.2f} MHz, phase margin {pm:.1f} deg, "
          f"f_ref/f_c = {FREF/fc:.0f}")

    fig = Figure(f"""Loop gain and closed loop response of the SUN_PLL.

The loop gain rises as 1/s towards low frequency, so its DC gain is
infinite. That is the whole trick of a PLL, and it is why the divided
feedback phase ends up exactly equal to the reference phase rather than
merely close to it.

Drawn with the oscillator gain measured on the extracted layout,
{KVCO_LAY/1e9:.2f} GHz/V, which puts crossover at {fc/1e6:.2f} MHz with
{pm:.0f} degrees of phase margin. The schematic gave {KVCO_SCH/1e9:.1f}
GHz/V and would have said {fc_s/1e6:.2f} MHz and {pm_s:.0f} degrees, so a
third of the oscillator gain and eight degrees of margin went into
parasitic capacitance that only appears once the ring is laid out.

Worth checking against the assumption the linear model rests on: the
reference is {FREF/1e6:.0f} MHz, so the loop bandwidth is a
{FREF/fc:.0f}'th of it, comfortably inside the one tenth rule. If it were
not, the phase margin printed here would be a number about a model that
does not describe the circuit, which is worse than a poor phase margin
because it looks fine.""", columns=1)

    ax = fig.axes(xlabel="Frequency [Hz]", ylabel="Magnitude [dB]",
                  xlog=True, width=10.0, height=4.2,
                  legend_pos="north east")
    ax.plot(f, 20*np.log10(np.abs(Ls)), colour="blue", label="$L(s)$",
            decimate=False)
    ax.plot(f, 20*np.log10(np.abs(Cs)), colour="red",
            label="$\\phi_{div}/\\phi_{in}$", decimate=False)
    ax.hline(0, colour="black", style="dashed, thin")

    ax = fig.axes(xlabel="Frequency [Hz]", ylabel="Phase [degrees]",
                  xlog=True, width=10.0, height=4.2,
                  legend_pos="south west")
    ax.plot(f, np.angle(Ls, deg=True), colour="blue", label="$L(s)$",
            decimate=False)
    ax.plot(f, np.angle(Cs, deg=True), colour="red",
            label="$\\phi_{div}/\\phi_{in}$", decimate=False)
    ax.vline(fc, colour="armygreen")
    ax.annotate(fc * 1.15, pm - 180 + 8,
                f"Phase margin {pm:.0f}$^\\circ$", anchor="south west")

    fig.save("pll")


if __name__ == "__main__":
    main()
