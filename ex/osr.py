#!/usr/bin/env python3

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure



#- Create a time vector
N = 2**13
t = np.arange(N)

#- Create the "continuous time" signal
fbin = 10
fm1 = 1/N*213
f1 = 1/64 - 1/N
fd = fm1
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
bits = 10
y_sn = adc(x_sn,bits)

#- Oversample
OSR = 4

def oversample(x,OSR):

    N = len(x)
    y = np.zeros(N)

    for n in range(0,N):
        for k in range(0,OSR):
            m = n+k
            if(m < N):
                y[n] += x[m]
    return y

y_on = oversample(y_sn,OSR)

#----------------------------------------------
# Plot spectrum
#----------------------------------------------
def freqDomain(x):
    N = len(x)
    # Use hanning window to prevent FFT bin energy spread
    w = np.hanning(N+1)

    # Convert to frequency domain
    X= np.fft.fftshift(np.fft.fft(np.multiply(w[0:N],x)))

    # Normalize to max output power
    X = X/np.max(np.abs(X))
    return X
X_s = freqDomain(x_s)
X_sn = freqDomain(x_sn)
Y_sn = freqDomain(y_sn)
Y_on = freqDomain(y_on)

#- Frequency axes normalized to each record's own sample rate, so 0 Hz is
#- in the middle and the edges are +/- fs/2
def faxis(X):
    M = len(X)
    return (np.arange(0,M,1) - M/2)/M

plt.subplot(1,4,1)
plt.plot(faxis(X_s),20*np.log10(np.abs(X_s)),color="black",linewidth=0.7)
plt.grid(True)
plt.xlabel("f / fs\nContinuous time, continuous value")
plt.ylabel("Frequency Domain [dB20]")
plt.ylim(-160,0)
plt.subplot(1,4,2)
plt.plot(faxis(X_sn),20*np.log10(np.abs(X_sn)),color="black",linewidth=0.7)
plt.grid(True)
plt.xlabel("f / fs\nDiscrete time, continuous value")
plt.ylim(-160,0)
plt.subplot(1,4,3)
plt.plot(faxis(Y_sn),20*np.log10(np.abs(Y_sn)),color="black",linewidth=0.7)
plt.grid(True)
plt.xlabel("f / fs\nDiscrete time, Discrete value")
plt.text(0.25,-10,str(bits) + "-bit")
plt.ylim(-160,0)
plt.subplot(1,4,4)
plt.plot(faxis(Y_on),20*np.log10(np.abs(Y_on)),color="black",linewidth=0.7)
plt.grid(True)
plt.xlabel("f / fs\nOversampled")
plt.text(0.25,-10,"OSR=" + str(OSR))
plt.ylim(-160,0)

fig = plt.gcf()
fig.set_size_inches(12, 7)
plt.tight_layout()
plt.savefig("l6_osr_" + str(OSR) + ".pdf")

#- The same four panels as TikZ, so the plot matches the schematics.
tfig = Figure(f"""Oversampling with a moving average, OSR = {OSR}.

Four spectra of the same signal: continuous, sampled, quantized, and
then filtered by a length-{OSR} moving average. Read the last panel
carefully. The nulls are the filter's zeros, but the floor near zero
frequency is not lower than in the panel before it - if anything it is
slightly higher, because the low frequency noise components add.

What oversampling buys is not visible here, because these panels are
never decimated. The gain comes from counting only the noise inside the
narrower band, and the filter's job is to stop the rest folding back in
when the decimation does happen.""", columns=4)

panels = ((X_s, "Continuous time, continuous value", None),
          (X_sn, "Discrete time, continuous value", None),
          (Y_sn, "Discrete time, discrete value", f"{bits}-bit"),
          (Y_on, "Oversampled", f"OSR = {OSR}"))
for i, (spec, name, note) in enumerate(panels):
    ax = tfig.axes(xlabel="$f/f_s$", title=name,
                   ylabel="Magnitude [dB20]" if i == 0 else None,
                   ylim=(-160, 0), width=3.5, height=4.6)
    ax.plot(faxis(spec), 20*np.log10(np.abs(spec)), colour="black")
    if note:
        ax.annotate(-0.47, -12, note, anchor="north west")

tfig.save("l6_osr_" + str(OSR))
