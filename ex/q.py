#!/usr/bin/env python3

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure


#- Enable hanning window
hann = True

#- Create a time vector
N = 2**13
t = np.arange(N)

#- Create the "continuous time" signal
fdivide = 2**6
f1 = 1/fdivide - 1/N
#- Fixed seed, so `make plots` reproduces the committed figure
#- rather than a new noise realisation every time. The noise is
#- meant to look like noise, not to be any particular noise.
np.random.seed(14)
x_s = np.sin(2*np.pi*f1*t) + + 1/2**15*np.random.randn(N)

#----------------------------------------------
#- Model an ADC
#----------------------------------------------

## Sample
#- Sampling frequency is 1/nfs of the time vector
nfs = 4
x_sn = x_s[0::nfs]

def adc(x,bits):
    """A true B-bit mid-rise quantizer: 2**bits levels spanning -1 to 1.

    np.round(x*2**bits)/2**bits looks like a quantizer but is not one:
    at bits=1 it gives five output levels, not two. A B-bit converter
    has exactly 2**B levels, spaced by Delta = 2/2**B, sitting half a
    step off zero - so a 1-bit converter is a sign detector.
    """
    levels = 2**bits
    delta = 2/levels
    y = np.floor(x/delta)*delta + delta/2
    return np.clip(y, -1 + delta/2, 1 - delta/2)

# To discrete value
bits = 1
y_sn = adc(x_sn,bits)

#----------------------------------------------
# Plot spectrum
#----------------------------------------------
def freqDomain(x,hann=True):
    N = len(x)
    # Use hanning window to prevent FFT bin energy spread
    if(hann):
        w = np.hanning(N+1)
    else:
        w = np.ones(N+1)

    # Convert to frequency domain
    X= np.fft.fftshift(np.fft.fft(np.multiply(w[0:N],x)))

    # Normalize to max output power
    X = X/np.max(np.abs(X))
    return X


X_s = freqDomain(x_s,hann)
X_sn = freqDomain(x_sn,hann)
Y_sn = freqDomain(y_sn,hann)

M = len(Y_sn)
#- Frequency axes normalized to each record's own sample rate, so 0 Hz is
#- in the middle and the edges are +/- fs/2
f_xs = (np.arange(0,N,1) - N/2)/N
f_xn = (np.arange(0,M,1) - M/2)/M

plt.subplot(1,3,1)
plt.plot(f_xs,20*np.log10(np.abs(X_s)),color="black",linewidth=0.7)
plt.grid(True)
plt.xlabel("f / fs\nContinuous time, continuous value")
plt.ylabel("Frequency Domain [dB20]")
plt.ylim(-160,0)
plt.subplot(1,3,2)
plt.plot(f_xn,20*np.log10(np.abs(X_sn)),color="black",linewidth=0.7)
plt.grid(True)
plt.xlabel("f / fs\nDiscrete time, continuous value")
plt.ylim(-160,0)
plt.subplot(1,3,3)
plt.plot(f_xn,20*np.log10(np.abs(Y_sn)),color="black",linewidth=0.7)
plt.grid(True)
plt.xlabel("f / fs\nDiscrete time, Discrete value")
plt.text(0.15,-35,str(bits) + "-bit\nf1 = bin " + str(int(f1*N)) + "\nf3 = bin " + str(int(f1*N*3)) + "\nf5 = bin " + str(int(f1*N*5)) + "\n(bin = f/fs × " + str(M) + ")")
plt.ylim(-160,0)

fig = plt.gcf()
fig.set_size_inches(12, 7)
plt.tight_layout()
plt.savefig("l6_quant.pdf")

#- The same three panels as TikZ, so the plot matches the schematics.
#- All three variants the lecture uses are emitted in one run, so
#- `make plots` reproduces every committed figure rather than only the
#- default one.
def tikz(bits, n_pow, fdiv, suffix=""):
    N = 2**n_pow
    t = np.arange(N)
    f1 = 1/2**fdiv - 1/N
    np.random.seed(14)
    x_s = np.sin(2*np.pi*f1*t) + 1/2**15*np.random.randn(N)
    x_sn = x_s[0::nfs]
    y_sn = adc(x_sn, bits)

    X_s = freqDomain(x_s, hann)
    X_sn = freqDomain(x_sn, hann)
    Y_sn = freqDomain(y_sn, hann)
    M = len(Y_sn)
    f_xs = (np.arange(0, N, 1) - N/2)/N
    f_xn = (np.arange(0, M, 1) - M/2)/M

    tfig = Figure(f"""Where quantization noise actually goes, for a {bits}-bit quantizer.

Three spectra of the same signal: continuous, then sampled, then
quantized. The middle panel's floor sits 10 log(nfs) above the left
one's, which is noise folding. The right panel is the point of the
figure: quantization noise is not a floor at all, it is a comb of odd
harmonics, and for a 1-bit quantizer their amplitudes are exactly 1/p.

Harmonics above half the sample rate fold back, so the ninth and
eleventh appear below the seventh on the frequency axis while still
being smaller in amplitude.""", columns=3)

    panels = ((f_xs, X_s, "Continuous time, continuous value"),
              (f_xn, X_sn, "Discrete time, continuous value"),
              (f_xn, Y_sn, "Discrete time, discrete value"))
    for i, (fx, spec, name) in enumerate(panels):
        ax = tfig.axes(xlabel="$f/f_s$", title=name,
                       ylabel="Magnitude [dB20]" if i == 0 else None,
                       ylim=(-160, 0), width=4.6, height=5.0)
        ax.plot(fx, 20*np.log10(np.abs(spec)), colour="black")
        if i == 2:
            #- the chapter argues in bins, so keep them on the figure
            ax.annotate(-0.47, -80,
                        f"{bits}-bit\\\\ $f_1$ = bin {int(f1*N)}"
                        f"\\\\ $f_3$ = bin {int(f1*N*3)}"
                        f"\\\\ $f_5$ = bin {int(f1*N*5)}"
                        f"\\\\ bin = $f/f_s \\times$ {M}",
                        anchor="north west")

    tfig.save(f"l6_q_{bits}{suffix}")


tikz(1, 13, 6)
tikz(10, 13, 6)
#- lower input frequency and a longer record, so the eleventh harmonic
#- lands below fs/2 and does not fold
tikz(1, 16, 9, "_fharm")
