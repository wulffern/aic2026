#!/usr/bin/env python3
"""Ring oscillator frequency against supply and against temperature.

These two figures are the empirical half of the argument the logic
chapter makes about ring oscillators: they are cheap and they are not
stable. Nothing about a ring sets its frequency except how fast its own
inverters happen to switch, so anything that changes an inverter's delay
changes the clock.

The data comes from AIM-Spice transient sweeps in the dicex course
material (github.com/wulffern/dicex), summarised into YAML by the sweep
scripts there. Only regenerating the figures needs that repo; the
generated tikz/rosc_*.tex are committed.
"""

import os
import sys

import numpy as np
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

HOME = os.getenv("HOME")
EX4 = f"{HOME}/pro/dicex/ex4"


def sweep(name, field="f_mean"):
    """Return the sweep variable and one measured field, sorted."""
    with open(f"{EX4}/{name}.yaml") as fi:
        obj = yaml.safe_load(fi)
    keys = sorted(k for k in obj if obj[k] and field in obj[k])
    x = np.array(keys, dtype=float)
    y = np.array([obj[k][field] for k in keys], dtype=float)
    return x, y


def main():
    # ---- against supply ------------------------------------------------
    v, f = sweep("rosc_vdd")
    _, i = sweep("rosc_vdd", "i_vdd")
    p = np.abs(i) * v                       # W
    dfdv = np.gradient(f) / np.gradient(v)

    fig = Figure("""Ring oscillator frequency and power against supply voltage.

The top left panel is why a ring oscillator is never used as a frequency
reference and always used as a supply monitor: frequency tracks VDD over
more than a decade, from 100 MHz to 3.6 GHz here.

The bottom left panel is the sensitivity, and it has a maximum. Around
0.6 V the oscillator changes by more than 4 GHz per volt, so a
millivolt of supply ripple is megahertz of frequency error. The two
right hand panels are the price: power grows faster than frequency does,
so the energy per cycle is worst exactly where the ring is fastest.""",
                 columns=2, hsep=2.2)

    ax = fig.axes(ylabel="Frequency [MHz]", xlabel="$V_{DD}$ [V]",
                  width=6.0, height=3.8)
    ax.plot(v, f/1e6, colour="black", decimate=False)

    ax = fig.axes(ylabel="Power [$\\mu$W]", xlabel="$V_{DD}$ [V]",
                  width=6.0, height=3.8)
    ax.plot(v, p*1e6, colour="black", decimate=False)

    ax = fig.axes(ylabel="$df/dV_{DD}$ [MHz/V]", xlabel="$V_{DD}$ [V]",
                  width=6.0, height=3.8)
    ax.plot(v, dfdv/1e6, colour="red", decimate=False)

    ax = fig.axes(ylabel="$E$/cycle [pJ]", xlabel="$V_{DD}$ [V]",
                  width=6.0, height=3.8)
    ax.plot(v, p/f*1e12, colour="red", decimate=False)

    fig.save("rosc_vdd")

    # ---- against temperature -------------------------------------------
    t, ft = sweep("rosc_temp")
    dfdt = np.gradient(ft) / np.gradient(t)

    fig = Figure("""Ring oscillator frequency and its slope against temperature.

Frequency falls by a factor of 2.6 from -40 to 150 degrees, because
mobility falls with temperature and the inverters get slower. A ring
oscillator is therefore a usable temperature sensor and an unusable
clock, and the two statements are the same statement.

The lower panel gives the number to design with: roughly -12 MHz per
degree in the cold, -3 MHz per degree when hot. The sensitivity is
itself temperature dependent, which is what makes compensating a ring
oscillator harder than it first looks.""", columns=1)

    ax = fig.axes(ylabel="Frequency [MHz]",
                  xlabel="Temperature [$^\\circ$C]",
                  width=9.5, height=3.8)
    ax.plot(t, ft/1e6, colour="black", decimate=False)

    ax = fig.axes(ylabel="$df/dT$ [MHz/$^\\circ$C]",
                  xlabel="Temperature [$^\\circ$C]",
                  width=9.5, height=3.8)
    ax.plot(t, dfdt/1e6, colour="red", decimate=False)

    fig.save("rosc_temp")


if __name__ == "__main__":
    main()
