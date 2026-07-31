"""Two DAC linearity figures: quantization error, and INL/DNL.

Both are constructed rather than simulated, which is the point: the
second one uses a deliberately imperfect DAC so that INL and DNL have
something to show.

Originally two cells of jupyter/dac.ipynb. The INL cell drew its
mismatch from an unseeded `np.random.randn`, so it produced a different
figure on every run and the one in the book could not be reproduced. The
seed is fixed here.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

SEED = 4


def quantization_error():
    """A 2-bit DAC, and where you put the output level within a code."""
    vref = 1
    n = 2
    lsb = vref / 2**n
    a = np.linspace(0, vref - lsb*2/3, 400)
    d = np.round(a / lsb)

    vb = vref/4 * d              # level at the bottom of the code
    vd = vref/4 * (d + 1)        # level at the top of the code

    fig = Figure("""Quantization error of a 2-bit DAC, and where it comes from.

The top panel is the digital code against the input it represents: a
staircase, because that is all a converter can produce.

The middle panel shows two ways of turning that code back into a
voltage, differing only in whether the output sits at the bottom or the
top of the code's band. Both are defensible and neither is the ideal
line.

The bottom panel is the difference, and it is the whole argument. The
choice does not change the size of the error, it changes its sign: one
convention errs low everywhere, the other high. Only a half-LSB offset
centres it, and that is why converters are specified with one.""",
                 columns=1)

    ax = fig.axes(ylabel="Digital code", width=9.5, height=3.0,
                  options=["xticklabels={}"])
    ax.plot(a, d, colour="black", decimate=False)

    ax = fig.axes(ylabel="DAC output [V]", width=9.5, height=3.0,
                  legend_pos="north west", options=["xticklabels={}"])
    ax.plot(a, vb, colour="blue", label="$V_o = \\frac{1}{4}d$",
            decimate=False)
    ax.plot(a, vd, colour="red", label="$V_o = \\frac{1}{4}(d+1)$",
            decimate=False)
    ax.plot(a, a, colour="armygreen", label="Ideal", decimate=False)

    ax = fig.axes(ylabel="Error [V]", xlabel="Input voltage [V]",
                  width=9.5, height=3.0, legend_pos="north west")
    ax.plot(a, a - vd, colour="red", label="$a - \\frac{1}{4}(d+1)$",
            decimate=False)
    ax.plot(a, a - vb, colour="blue", label="$a - \\frac{1}{4}d$",
            decimate=False)

    fig.save("dac_error")


def inl_dnl():
    """A deliberately non-ideal 5-bit DAC, measured the standard way."""
    rng = np.random.default_rng(SEED)
    vref = 1
    n = 5
    d = np.arange(2**n, dtype=float)
    lsb = vref / 2**n

    #- gain error, offset, second and third order curvature, and a little
    #- random mismatch: enough imperfection for INL and DNL to be worth
    #- plotting
    vb = ((lsb - lsb/32) * d - lsb/2
          + d**2 * lsb**2 / 16 + d**3 * lsb**3 / 16
          + rng.standard_normal(2**n) * lsb/100)

    fit = np.polyval(np.polyfit(d, vb, 1), d)
    inl = (vb - fit) / lsb
    dnl = np.diff(vb) / lsb - 1

    fig = Figure(f"""Integral and differential non-linearity of a 5-bit DAC.

The DAC is deliberately imperfect, with gain error, curvature and a
little random mismatch, because a perfect one has nothing to show.

INL, in the middle, is the distance from the best straight line, and it
measures whether the transfer curve is straight. DNL, at the bottom, is
the error in each individual step, and it measures whether any step is
missing. They answer different questions: a converter can have small DNL
and large INL if it bends smoothly, and small INL with large DNL if one
step is wrong and the rest compensate.

The mismatch is drawn with a fixed seed, {SEED}, so this figure is the
same every time it is built. It used to come from an unseeded generator,
which meant the figure in the book could not be reproduced.""",
                 columns=1)

    ax = fig.axes(ylabel="Output voltage [V]", width=9.5, height=3.0,
                  legend_pos="north west", options=["xticklabels={}"])
    ax.plot(d, vb, colour="blue", label="DAC output", decimate=False)
    ax.plot(d, fit, colour="armygreen", label="Best fit line",
            decimate=False)

    ax = fig.axes(ylabel="INL [LSB]", width=9.5, height=3.0,
                  options=["xticklabels={}"])
    ax.plot(d, inl, colour="blue", decimate=False)

    ax = fig.axes(ylabel="DNL [LSB]", xlabel="Digital code",
                  width=9.5, height=3.0)
    ax.plot(d[:-1], dnl, colour="red", decimate=False)

    fig.save("dac_inl_dnl")
    print(f"INL {inl.min():+.2f} to {inl.max():+.2f} LSB, "
          f"DNL {dnl.min():+.2f} to {dnl.max():+.2f} LSB")


if __name__ == "__main__":
    quantization_error()
    inl_dnl()
