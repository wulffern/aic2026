#!/usr/bin/env python3
#
import numpy as np
import matplotlib.pyplot as plt

Hann = True

#- Create a time vector
N = 2**13
t = np.arange(N)

#- Create the "continuous time" signal with multiple sinusoidal signals and some noise
#- f1 is deliberately halfway between FFT bins, so the record is not
#- coherent and the window below has a job to do
f1 = 233.5/N
fd = 1/N*119
x_s = np.sin(2*np.pi*f1*t) + 1/1024*np.random.randn(N) +   0.5*np.sin(2*np.pi*(f1-fd)*t) + 0.5*np.sin(2*np.pi*(f1+fd)*t)

#- Create the sampling vector, and the sampled signal
t_s_unit = [1,1,0,0,0,0,0,0]
t_s = np.tile(t_s_unit,int(N/len(t_s_unit)))
x_sn = x_s*t_s

#- Convert to frequency domain with a hanning window to avoid FFT bin
#- energy spread
if(Hann):
    w = np.hanning(N+1)
else:
    w = np.ones(N+1)
X_s = np.fft.fftshift(np.fft.fft(np.multiply(w[0:N],x_s)))
X_sn = np.fft.fftshift(np.fft.fft(np.multiply(w[0:N],x_sn)))

#- Frequency axis normalized to the emulation rate, so 0 Hz is in the
#- middle and the edges are +/- fs/2
f = (np.arange(N) - N/2)/N

plt.subplot(2,2,1)
plt.ylabel("Time Domain")
plt.plot(x_s,color="black",linewidth=0.7)
plt.grid(True)
plt.xlabel("Continuous time, continuous value")
plt.subplot(2,2,2)
plt.plot(x_sn,color="black",linewidth=0.7)
plt.grid(True)
plt.xlabel("Discrete time, continuous value")
plt.subplot(2,2,3)
plt.ylabel("Frequency Domain [dB20]")
plt.plot(f,20*np.log10(np.abs(X_s)),color="black",linewidth=0.7)
plt.grid(True)
plt.xlabel("f / fs")
plt.subplot(2,2,4)
plt.plot(f,20*np.log10(np.abs(X_sn)),color="black",linewidth=0.7)
plt.grid(True)
plt.xlabel("f / fs")

fig = plt.gcf()
fig.set_size_inches(12, 7)
plt.tight_layout()
plt.savefig(f"l5_dtfig.pdf")
plt.show()


