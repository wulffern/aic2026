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
x_s = np.sin(2*np.pi*f1*t) + 1/1024*np.random.randn(N) #+   0.5*np.sin(2*np.pi*(f1-fd)*t) + 0.5*np.sin(2*np.pi*(f1+fd)*t)

#- Create the sampling vector, and the sampled signal
t_s_unit = [1,1,0,0,0,0,0,0]
t_s = np.tile(t_s_unit,int(N/len(t_s_unit)))
x_sn = x_s*t_s

#- Second-order IIR filter with a complex conjugate pole pair at
#- z = a +/- jb. Stable as long as |a + jb| < 1.
b = 0.25
a = 0.85
z = a + 1j*b
z_abs = np.abs(z)
print("|z| = " + str(z_abs))
y = np.zeros(N)
for i in range(2,N):
    y[i] = b*x_sn[i-1] + 2*a*y[i-1] - (a*a + b*b)*y[i-2]


#- Convert to frequency domain with a hanning window to avoid FFT bin
#- energy spread
Hann = True
if(Hann):
    w = np.hanning(N+1)
else:
    w = np.ones(N+1)

#X_s = np.fft.fftshift(np.fft.fft(np.multiply(w[0:N],x_s)))
X_sn = np.fft.fftshift(np.fft.fft(np.multiply(w[0:N],x_sn)))
Y = np.fft.fftshift(np.fft.fft(np.multiply(w[0:N],y)))


#- Frequency axis normalized to the emulation rate, so 0 Hz is in the
#- middle and the edges are +/- fs/2
f = (np.arange(N) - N/2)/N

plt.subplot(2,2,1)
plt.plot(x_sn,color="black",linewidth=0.7)
plt.grid(True)
plt.axis([1000,1400,-1,1])
plt.ylabel("Time Domain")
plt.xlabel("Sampled")
plt.subplot(2,2,2)
plt.plot(y,color="black",linewidth=0.7)
plt.grid(True)
plt.axis([1000,1400,-1,1])
plt.xlabel("IIR Filter")
#- Same y-axis on both spectra, so the attenuation can be read directly
plt.subplot(2,2,3)
plt.plot(f,20*np.log10(np.abs(X_sn)),color="black",linewidth=0.7)
plt.grid(True)
plt.ylim(-60,60)
plt.xlabel("f / fs")
plt.ylabel("Frequency Domain [dB20]")
plt.subplot(2,2,4)
plt.plot(f,20*np.log10(np.abs(Y)),color="black",linewidth=0.7)
plt.grid(True)
plt.ylim(-60,60)
plt.xlabel("f / fs")

fig = plt.gcf()
fig.set_size_inches(10, 7)
plt.tight_layout()
plt.savefig("l5_iir.svg")

#- The same four panels as a TikZ figure, so the plot matches the
#- schematics it sits next to. See py/tikzplot.py.
tfig = Figure("""A second order IIR filter, in time and in frequency.

The top row is 400 samples of the sampled input and of the filter
output, so the shape of the ringing is visible. The bottom row is the
spectrum of each, on the same dB axis, so the attenuation can be read
off directly rather than inferred.

The pole pair sits at z = a +/- jb with a = 0.85 and b = 0.25, well
inside the unit circle, so the response decays.""", columns=2)

nlo, nhi = 1000, 1400
ax = tfig.axes(xlabel="Sample", ylabel="Sampled", xlim=(nlo, nhi),
               ylim=(-1, 1), width=6.4, height=3.8)
ax.plot(t[nlo:nhi], x_sn[nlo:nhi], colour="black")

ax = tfig.axes(xlabel="Sample", ylabel="IIR filtered", xlim=(nlo, nhi),
               ylim=(-1, 1), width=6.4, height=3.8)
ax.plot(t[nlo:nhi], y[nlo:nhi], colour="black")

ax = tfig.axes(xlabel="$f/f_s$", ylabel="Sampled [dB20]",
               ylim=(-60, 60), width=6.4, height=3.8)
ax.plot(f, 20*np.log10(np.abs(X_sn)), colour="black")

ax = tfig.axes(xlabel="$f/f_s$", ylabel="IIR filtered [dB20]",
               ylim=(-60, 60), width=6.4, height=3.8)
ax.plot(f, 20*np.log10(np.abs(Y)), colour="black")

tfig.save("l5_iir")
