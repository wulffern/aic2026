"""Random telegraph signal, and why many of them make flicker noise.

The MOSFET chapter argues that a single trap capturing and releasing a
carrier produces a two-level random telegraph signal, that its spectrum
is a Lorentzian, and that summing many such traps with a spread of time
constants gives 1/f. All three are easy to show and much better shown
than asserted, so this draws them.

Everything here is generated, not measured: it is the model the chapter
describes, which is the point.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

#- Fixed seed, so the figure is the same every time it is built
SEED = 21
N = 2**20                   # long enough that the lowest FFT bin (30 Hz)
FS = 1e6                    # sits below the slowest trap's corner


def rts(tau, n=N, rng=None):
    """A two-level signal that flips with mean dwell time tau seconds."""
    rng = rng or np.random.default_rng(SEED)
    p = 1.0/(tau*FS)        # flip probability per sample
    flips = rng.random(n) < p
    return np.where(np.cumsum(flips) % 2 == 0, 0.0, 1.0)


def psd(x, nseg=32):
    """Welch: average the periodograms of overlapping segments.

    A single periodogram of a random signal has 100 % standard deviation
    in every bin, which is enough to hide the shape entirely. Averaging
    64 segments is what turns a black smear into a visible corner.
    """
    n = len(x)//nseg
    #- N+1 with the last point dropped: the periodic Hann window, which
    #  tiles continuously the way the DFT assumes (aic2023 issue #10)
    w = np.hanning(n + 1)[:n]
    acc = np.zeros(n//2 + 1)
    for k in range(2*nseg - 1):          # 50 % overlap
        seg = x[k*n//2 : k*n//2 + n]
        if len(seg) < n:
            break
        acc += np.abs(np.fft.rfft((seg - seg.mean())*w))**2
    f = np.fft.rfftfreq(n, 1/FS)
    return f[1:], acc[1:]/(2*nseg - 1)


def main():
    rng = np.random.default_rng(SEED)
    t = np.arange(N)/FS

    #- one trap
    single = rts(2e-4, rng=rng)
    f1, p1 = psd(single)

    #- many traps, time constants spread over decades
    taus = np.logspace(-5, -2, 40)
    total = np.zeros(N)
    for tau in taus:
        total += rts(tau, rng=rng)
    f2, p2 = psd(total)

    fig = Figure("""One trap gives a random telegraph signal; many give 1/f.

The top panel is a single trap capturing and releasing a carrier: the
current has two values and jumps between them at random, which is why it
is called popcorn or burst noise. Its spectrum, below left, is flat out
to a corner set by the dwell time and then falls as 1/f^2 - a
Lorentzian.

The bottom panel is forty such traps with time constants spread evenly
in log over three decades, as a real device has. Each contributes its
own corner, and the sum is a straight 1/f - measured slope -1.02 between
100 Hz and 10 kHz, which is the band where those corners lie. Flicker
noise is not a separate mechanism; it is what a population of traps
looks like from far enough away.

Above about 16 kHz the line steepens, because past the corner of the
fastest trap every trap is in its own 1/f^2 tail and there are no
faster ones left to hold the slope up. Real flicker noise ends the same
way and for the same reason.""", columns=1)

    ax = fig.axes(xlabel="Time [ms]", ylabel="Trap state",
                  xlim=(0, 20), ylim=(-0.2, 1.4), width=11.0, height=3.0)
    ax.plot(t*1e3, single, colour="black")

    ax = fig.axes(xlabel="Frequency [Hz]", ylabel="PSD, one trap",
                  xlog=True, ylog=True, width=11.0, height=3.6)
    ax.plot(f1, p1, colour="black")

    ax = fig.axes(xlabel="Frequency [Hz]", ylabel="PSD, 40 traps",
                  xlog=True, ylog=True, width=11.0, height=3.6)
    ax.plot(f2, p2, colour="red")

    #- the caption quotes these, so check them rather than trust them
    def slope(f, p, lo, hi):
        m = (f > lo) & (f < hi)
        return np.polyfit(np.log10(f[m]), np.log10(p[m]), 1)[0]
    print(f"one trap, tail 20-300 kHz: {slope(f1, p1, 2e4, 3e5):+.2f} "
          f"(Lorentzian, expect -2)")
    print(f"40 traps, 100 Hz-10 kHz  : {slope(f2, p2, 1e2, 1e4):+.2f} "
          f"(flicker, expect -1)")

    fig.save("rts_noise")


if __name__ == "__main__":
    main()
