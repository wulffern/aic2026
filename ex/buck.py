"""A buck converter, integrated by hand, in PWM and in PFM.

Four figures for the voltage regulator chapter. All of it is a
trapezoidal integration of two state variables, the inductor current and
the output voltage, so nothing here needs a simulator - which is rather
the point. A switching regulator is simple enough to model in thirty
lines, and doing so makes the waveforms mean something.

Originally jupyter/buck.ipynb and jupyter/buck_pfm.ipynb, where the PWM
run needed a variable edited by hand and the cells re-run in order to
produce each of its three figures.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

U = 1e-6


def pwm(mode):
    """Fixed frequency, fixed duty cycle. Returns t, ix, io, vo, a."""
    L, Rs, C, R = 1*U, 1.0, 1*U, 1000.0
    T, dtc, VDDH = 0.1*U, 0.25, 4.0
    vo0, ix0 = 0.0, 0.0
    N, t_end = 2**15, 10e-6

    if mode == "settled":
        #- R*C here is 1 ms against a 0.1 us switching period, so a run
        #- starting from a discharged output cannot both settle and
        #- resolve the ripple. Start at the operating point instead.
        t_end, N = 50e-6, 2**16
        vo0 = VDDH*dtc/(1 + Rs/R)
        ix0 = vo0/R
    elif mode == "start":
        t_end = 0.25e-6

    t = np.linspace(0, t_end, N)
    vo = np.ones(N)*vo0
    ix = np.zeros(N); ix[0] = ix0
    vx = np.zeros(N)
    io = np.zeros(N)
    ivdd = np.zeros(N)
    a = np.zeros(N)

    for i in range(1, N):
        pmos = 1 if (t[i] % T) < dtc*T else 0
        a[i] = pmos
        dt = t[i] - t[i-1]
        vx[i] = pmos*VDDH - Rs*ix[i-1] - vo[i-1]
        ix[i] = ix[i-1] + 1/L * (vx[i] + vx[i-1])/2 * dt
        if pmos:
            ivdd[i] = ix[i]
        io[i] = vo[i-1]/R
        vo[i] = vo[i-1] + 1/C * ((ix[i] + ix[i-1])/2
                                 - (io[i] + io[i-1])/2) * dt
    return t, ix, io, vo, a, ivdd, VDDH


def pfm():
    """Pulse frequency modulation: fixed pulse, variable rate."""
    L, Rs, C, R = 5*U, 1.0, 1*U, 1000.0
    VDDH, VREF = 1.8, 1.0
    N, t_end, t_switch = 2**18, 10e-3, 0.5*U

    t = np.linspace(0, t_end, N)
    vo = np.ones(N)*0.99
    ix = np.zeros(N)
    vx = np.zeros(N)
    io = np.zeros(N)
    state = np.zeros(N)

    st, t_start = 0, 0.0
    for i in range(1, N):
        ts = t[i]
        dt = ts - t[i-1]
        if st == 0:                       # idle, both switches off
            pmos = 0
            #- a large resistance stands in for the high impedance the
            #- open switches present
            vx[i] = -100*ix[i-1]
            if vo[i-1] < VREF:
                st, t_start = 1, ts
        elif st == 1:                     # charging through the PMOS
            pmos = 1
            vx[i] = VDDH - Rs*ix[i-1] - vo[i-1]
            if ts - t_start > t_switch:
                st = 2
        else:                             # freewheeling through the NMOS
            pmos = 0
            vx[i] = -Rs*ix[i-1] - vo[i-1]
            if ix[i-1] < 0:
                st = 0
        state[i] = st
        ix[i] = ix[i-1] + 1/L * (vx[i] + vx[i-1])/2 * dt
        io[i] = vo[i]/R
        vo[i] = vo[i-1] + 1/C * ((ix[i] + ix[i-1])/2
                                 - (io[i] + io[i-1])/2) * dt
    return t, ix, io, vo, state


def panels(fig, t, ix, io, vo, last, last_label, xlim=None,
           ylim0=None, ylim1=None, vo_precision=3):
    ax = fig.axes(ylabel="Current [A]", xlim=xlim, ylim=ylim0,
                  width=9.5, height=3.4, legend_pos="north east",
                  options=["xticklabels={}"])
    ax.plot(t/U, ix, colour="blue", label="$I_x$, inductor")
    ax.plot(t/U, io, colour="red", label="$I_o$, load")

    ax = fig.axes(ylabel="$V_o$ [V]", xlim=xlim, ylim=ylim1,
                  width=9.5, height=3.4,
                  yprecision=vo_precision,
                  options=["xticklabels={}"])
    ax.plot(t/U, vo, colour="black")

    ax = fig.axes(ylabel=last_label, xlabel="Time [$\\mu$s]", xlim=xlim,
                  width=9.5, height=1.4)
    ax.plot(t/U, last, colour="armygreen")


def main():
    for mode, comment, xlim, y0, y1 in (
        ("", """A PWM buck converter over ten microseconds.

The inductor current is a triangle wave: rising while the PMOS connects
the inductor to the supply, falling while it does not. The output
voltage is the average of that, filtered by the output capacitor.

Ten microseconds is not long enough for it to settle. The output RC is
1 ms against a 0.1 us switching period, so this figure shows the start
of a very long exponential, not steady state.""", None, None, None),
        ("start", """The first quarter microsecond of the same converter.

Two and a half switching periods, so the mechanism is visible: current
ramps up while the switch is on, ramps down while it is off, and the
output creeps up because slightly more charge arrives than leaves each
cycle.""", None, None, None),
        ("settled", """The same converter in steady state, zoomed onto the ripple.

Started from the operating point rather than from zero, because it
cannot both settle and resolve the ripple in one run.

This is the figure to read specifications off. The inductor current
swings 76 mA peak to peak to supply a 1 mA load - seventy-six times the
load current sloshing back and forth - and all of that ripple has to be
absorbed by the output capacitor, which reduces it to 1.6 mV on a
998 mV output. Both numbers follow from the inductor, the capacitor and
the switching period, and both are the price of switching rather than
dissipating.""",
         #- The notebook pinned this panel to 0.987..0.990, which the
         #- settled output voltage of 0.998 V never enters, so the
         #- published figure has been shipping with an empty middle
         #- panel. Let it scale to the data.
         (49.6, 50), (-0.06, 0.06), None),
    ):
        t, ix, io, vo, a, ivdd, vddh = pwm(mode)
        fig = Figure(comment, columns=1, vsep=0.5)
        panels(fig, t, ix, io, vo, a, "$\\phi$", xlim=xlim,
               ylim0=y0, ylim1=y1,
               vo_precision=4 if mode == "settled" else 2)
        fig.save(f"l07_buck_pwm_fig_{mode}")

        half = slice(len(t)//2, None)
        #- Only meaningful once the tank has settled; averaged over a run
        #- that is still ringing it comes out negative.
        if mode == "settled":
            eff = (np.mean(vo[half])*np.mean(io[half])
                   / (np.mean(ivdd[half])*vddh) * 100)
            win = (t/U >= 49.6) & (t/U <= 50)
            print(f"settled: Vo = {np.mean(vo[half])*1e3:.1f} mV, "
                  f"ripple = {(vo[win].max()-vo[win].min())*1e3:.2f} mV, "
                  f"Ix ripple = {(ix[win].max()-ix[win].min())*1e3:.0f} mA, "
                  f"efficiency = {eff:.1f} %")

    t, ix, io, vo, state = pfm()
    fig = Figure("""A PFM buck converter, with the state machine below.

Pulse frequency modulation does not vary a duty cycle, it varies how
often it bothers. The controller waits until the output has drooped
below the reference, delivers one fixed pulse of charge, waits for the
inductor current to reach zero, and goes back to idle.

That idle state is the whole point. At light load a PWM converter keeps
switching at full rate and pays for it, while a PFM converter simply
pulses less often, so the switching loss falls with the load rather than
staying constant. The cost is a ripple whose frequency depends on the
load, which is a genuine nuisance if the load is a radio.""",
                 columns=1, vsep=0.5)
    panels(fig, t, ix, io, vo, state, "State", xlim=(50, 105))
    fig.save("l07_buck_pfm_fig_save")


if __name__ == "__main__":
    main()
