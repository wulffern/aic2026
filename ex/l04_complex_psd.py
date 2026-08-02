#!/usr/bin/env python3
"""Why a complex modulator is worth the cross-coupling: a real loop
must place its noise notch symmetrically about zero, a complex loop
does not have to.

Both panels are simulated, not drawn. A first-order sigma-delta loop
is run twice: once real (the integrator's pole at z = 1, so the
noise transfer function 1 - z^-1 has its zero at DC) and once complex
(the pole rotated to z = exp(j w0), so the zero sits at +f0 alone).
The complex quantizer is the real quantizer applied to the real and
imaginary parts separately - which is what two ADCs in an i/q pair
actually do.

The spectra are plotted over the full -fs/2 to +fs/2, because that is
the whole point: a real signal's spectrum is conjugate symmetric and
cannot tell +f from -f, a complex one can."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

N = 1 << 15
fs = 1.0
f0 = 0.08                      # where the complex loop puts its notch
fin = f0 + 0.004               # a tone just inside the band
rng = np.random.default_rng(2026)


def modulate(alpha, u):
    """First-order sigma-delta with integrator pole at `alpha`.

    alpha = 1 gives the ordinary real loop, notch at DC. alpha =
    exp(j w0) rotates the notch to +f0 and nowhere else.
    """
    v = 0.0 + 0.0j
    y = np.zeros(len(u), dtype=complex)
    for n in range(len(u)):
        v = alpha * v + (u[n] - y[n - 1] if n else u[n])
        # a complex quantizer is two real quantizers, one per path
        y[n] = (quantize(v.real) + 1j * quantize(v.imag))
    return y


def quantize(x, bits=3, full=4.0):
    """A mid-tread quantizer. Multi-bit, because a one-bit loop is
    dominated by idle tones and the point here is the noise shape."""
    step = full / (2 ** bits)
    return np.clip(np.round(x / step) * step, -full / 2, full / 2)


def psd(y, segments=16):
    """Welch: average the periodogram over segments, so the noise floor
    is a floor and not a thicket."""
    L = len(y) // segments
    w = np.hanning(L)
    acc = np.zeros(L)
    for k in range(segments):
        seg = y[k * L:(k + 1) * L] * w
        acc += np.abs(np.fft.fftshift(np.fft.fft(seg)) / (L * 0.5)) ** 2
    f = np.fft.fftshift(np.fft.fftfreq(L, 1 / fs))
    return f, 10 * np.log10(np.maximum(acc / segments, 1e-12))


t = np.arange(N)
u = 1.2 * np.exp(2j * np.pi * fin * t) + 0.004 * (rng.standard_normal(N)
                                                 + 1j * rng.standard_normal(N))

f_r, P_r = psd(modulate(1.0, u))
f_c, P_c = psd(modulate(np.exp(2j * np.pi * f0), u))

fig = Figure(
    """Simulated output spectra of a first-order sigma-delta loop, real
and complex, over the full sample rate. The real loop's noise notch is
symmetric about zero because its coefficients are real; the complex
loop rotates the notch to +f0 and leaves -f0 noisy, which is what lets
a near zero-IF receiver keep the wanted side and throw the image
away.""",
    columns=2)

ax = fig.axes(xlabel="Frequency [$f_s$] (a) real loop",
              ylabel="Magnitude [dBFS]",
              xlim=(-0.5, 0.5), ylim=(-110, 5))
ax.plot(f_r, P_r, colour="blue", style="thin")
ax.vline(0.0, colour="black", style="dashed, thin")
ax.annotate(0.0, -102, "notch at DC", anchor="south")
ax.annotate(0.11, -14, "the signal sits\\\\out in the noise", anchor="south west")

ax = fig.axes(xlabel="Frequency [$f_s$] (b) complex loop",
              ylabel="Magnitude [dBFS]",
              xlim=(-0.5, 0.5), ylim=(-110, 5))
ax.plot(f_c, P_c, colour="red", style="thin")
ax.vline(f0, colour="black", style="dashed, thin")
ax.vline(-f0, colour="black", style="dashed, thin")
ax.annotate(f0, -102, "notch at $+f_0$", anchor="south west")
ax.annotate(-f0, -26, "$-f_0$ left noisy:\\\\that is the image", anchor="south east")

fig.save("l04_complex_psd")
