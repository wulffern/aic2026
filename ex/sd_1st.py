#!/usr/bin/env python3

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "py"))
from tikzplot import Figure

#- Create a time vector
N = 2**12
#t = np.linspace(0,N,N+1)
t = np.arange(0,N)
#- Create the "continuous time" signal
fbin = 47
fm1 = 1/N*213
f1 = 1/128 - 1/N
#f1 = fbin
fd = fm1
#- 0.7 of full scale: a true 1-bit loop overloads at full-scale input
x_s = 0.7*np.sin(2*np.pi*f1*t) + 1/2**15*np.random.randn(N)

#----------------------------------------------
#- Model an ADC
#----------------------------------------------

## Sample
#- Sampling frequency is 1/nfs of the time vector
nfs = 4
u = x_s[0::nfs]

#- Overridable, so the three variants the lecture uses can be
#- regenerated without editing the file:
#-   SD_BITS=1 SD_DITHER=0 python3 sd_1st.py
bits = int(os.environ.get("SD_BITS", 1))

def quantize(v,bits):
    #- 2**bits levels reaching +/-1, so bits=1 is a genuine two-level
    #- quantizer. Without the clamp the "1-bit" output takes more than two
    #- values whenever the integrator runs past full scale.
    levels = 2**bits
    if(levels == 2):
        return 1.0 if v >= 0 else -1.0
    step = 2/(levels-1)
    return float(np.clip(np.round(v/step)*step,-1,1))

y_sn = np.array([quantize(v,bits) for v in u])

dither = int(os.environ.get("SD_DITHER", 1))
M = len(u)
y_sd = np.zeros(M)
x = np.zeros(M)
for n in range(1,M):
    x[n] = x[n-1] + (u[n]-y_sd[n-1])
    #- dither is a quarter of a quantizer step, as before the clamp fix
    y_sd[n] = quantize(x[n] + dither*np.random.randn()/(4*2**bits),bits)

#- Remove the first samples to get rid of the initial
# settling
y_sd = y_sd[2:]

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
    X = X/np.max(np.abs(X[int(N/4):N-int(N/4)]))
    return X
X_s = freqDomain(x_s)
u = freqDomain(u)
Y_sn = freqDomain(y_sn)
Y_sdn = freqDomain(y_sd )

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
plt.plot(faxis(u),20*np.log10(np.abs(u)),color="black",linewidth=0.7)
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
plt.plot(faxis(Y_sdn),20*np.log10(np.abs(Y_sdn)),color="black",linewidth=0.7)
plt.grid(True)
plt.xlabel("f / fs\nNoise-shaped")
plt.text(0.1,-150,"dither=" + str(dither))
plt.ylim(-160,0)

fig = plt.gcf()
fig.set_size_inches(12, 7)
plt.tight_layout()
plt.savefig(f"l6_sd_d{dither}_b{bits}.pdf")


plt.figure()

NN = int(len(Y_sdn)/2)
Y_sdn_short = Y_sdn[NN:]
x_sdn_short = np.arange(0,NN)/NN/2
plt.semilogx(x_sdn_short,20*np.log10(np.abs(Y_sdn[int(len(Y_sdn)/2):])),color="black")
plt.xlabel("Normalized frequency")
plt.ylabel("Magnitude [dB20]")
plt.grid(True)

plt.savefig(f"l6_sdlog_d{dither}_b{bits}.pdf")

#- The same panels as TikZ, so the plots match the schematics.
dither_note = "with dither" if dither else "no dither"
tfig = Figure(f"""A first order sigma-delta modulator, {bits}-bit, {dither_note}.

Four spectra: continuous, sampled, quantized without shaping, and then
the modulator output. The last panel is the one to look at. The noise is
not smaller in total - it cannot be - it has been pushed away from zero
frequency, which is where the signal is.""", columns=4)

panels = ((X_s, "Continuous time, continuous value", None),
          (u, "Discrete time, continuous value", None),
          (Y_sn, "Discrete time, discrete value", f"{bits}-bit"),
          (Y_sdn, "Noise-shaped", f"dither = {dither}"))
for i, (spec, name, note) in enumerate(panels):
    ax = tfig.axes(xlabel="$f/f_s$", title=name,
                   ylabel="Magnitude [dB20]" if i == 0 else None,
                   ylim=(-160, 0), width=3.5, height=4.6)
    ax.plot(faxis(spec), 20*np.log10(np.abs(spec)), colour="black")
    if note:
        #- bottom left, since the noise-shaped trace lives at the top
        ax.annotate(-0.47, -155, note, anchor="south west")
tfig.save(f"l6_sd_d{dither}_b{bits}")

#- and the log-frequency view, where first order shaping is a straight line
lfig = Figure(f"""The same {bits}-bit modulator output on a log frequency axis.

Only the positive frequencies are shown. First order shaping is a
straight 20 dB per decade rise on this axis, which is far easier to
recognise than the curve it makes on a linear one.""")
ax = lfig.axes(xlabel="Normalized frequency", ylabel="Magnitude [dB20]",
               xlog=True, width=10.0, height=6.0)
ax.plot(x_sdn_short[1:], 20*np.log10(np.abs(Y_sdn_short[1:])), colour="black")
lfig.save(f"l6_sdlog_d{dither}_b{bits}")
