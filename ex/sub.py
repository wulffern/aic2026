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

#- Create the "continuous time" signal with multiple sinusoidal signals and some noise
f1 = 3023/N
fd = 1/N*119
#- Fixed seed, so `make plots` reproduces the committed figure
#- rather than a new noise realisation every time. The noise is
#- meant to look like noise, not to be any particular noise.
np.random.seed(16)
x_s = np.sin(2*np.pi*f1*t) + 1/1024*np.random.randn(N) +   0.5*np.sin(2*np.pi*(f1-fd)*t) + 0.5*np.sin(2*np.pi*(f1+fd)*t)

#- Create the sampling vector, and the sampled signal
t_s_unit = [1,1,0,0,0,0,0,0]
t_s = np.tile(t_s_unit,int(N/len(t_s_unit)))
x_sn = x_s*t_s

#- Convert to frequency domain with a hanning window to avoid FFT bin
#- energy spread
Hann = True
if(Hann):
    w = np.hanning(N+1)
else:
    w = np.ones(N+1)

X_s = np.fft.fftshift(np.fft.fft(np.multiply(w[0:N],x_s)))
X_sn = np.fft.fftshift(np.fft.fft(np.multiply(w[0:N],x_sn)))


plt.subplot(2,2,1)
plt.plot(x_s)
plt.ylabel("Time Domain")
plt.subplot(2,2,2)
plt.plot(x_sn)
plt.subplot(2,2,3)
plt.plot(20*np.log10(np.abs(X_s)))
plt.xlabel("Continuous time, continuous value")
plt.ylabel("Frequency Domain")
plt.subplot(2,2,4)
plt.plot(20*np.log10(np.abs(X_sn)))
plt.xlabel("Discrete time, continuous value")

fig = plt.gcf()
fig.set_size_inches(10, 7)
plt.tight_layout()
plt.savefig("l5_dtsub.pdf")

#- The same four panels as TikZ, so the plot matches the schematics.
tfig = Figure("""Sub-sampling: a signal above half the sample rate folds down.

The input sits above $f_s/2$, so sampling does not merely copy its
spectrum, it brings a copy down to low frequency. That is aliasing used
deliberately rather than avoided, which is what makes sub-sampling a
technique rather than a bug.""", columns=2)

n = np.arange(len(x_s))
fn = (np.arange(len(X_s)) - len(X_s)/2)/len(X_s)

ax = tfig.axes(xlabel="Continuous time, continuous value",
               ylabel="Time domain", width=6.4, height=3.8)
ax.plot(n, x_s, colour="black")
ax = tfig.axes(xlabel="Discrete time, continuous value",
               width=6.4, height=3.8)
ax.plot(n, x_sn, colour="black")
ax = tfig.axes(xlabel="$f/f_s$", ylabel="Frequency domain [dB20]",
               width=6.4, height=3.8)
ax.plot(fn, 20*np.log10(np.abs(X_s)), colour="black")
ax = tfig.axes(xlabel="$f/f_s$", width=6.4, height=3.8)
ax.plot(fn, 20*np.log10(np.abs(X_sn)), colour="black")

tfig.save("l5_dtsub")
