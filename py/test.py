#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt

N = 2**14
bit = 10

t = np.arange(0,N)

fbin = int(N/8 + 1)


x = np.sin(2*np.pi*fbin/N*t) + 1/(2**21)*np.random.randn(N)

x = np.round(x*2**(bit-1))/2**(bit-1) + 1/(2**21)*np.random.randn(N)

y = np.fft.fft(x)

y = y/N*2

yo = y[1:int(N/2)]

NR = 1
NSIG= fbin
sig = y[NSIG-NR:NSIG+NR+1]
noise = np.concatenate([yo[1:NSIG-NR],yo[NSIG+NR+1:]])

sigp= 10*np.log10(np.abs(np.power(sig,2).sum()))
noisep = 10*np.log10(np.abs(np.power(noise,2).sum()))

SNR = sigp-noisep
print(sigp)
print(noisep)

ENOB = (SNR - 1.76)/6.02

print("SNR %.2f" % SNR)
print("ENOB %.2f" % ENOB)

#yp = y +  1/(2**28)*np.random.randn(N)
#plt.subplot(3,1,1)
#plt.plot(20*np.log10(abs(sig)))
#plt.subplot(3,1,2)
#plt.plot(20*np.log10(abs(noise)))
#plt.subplot(3,1,3)
plt.plot(20*np.log10(np.abs(y)))
plt.show()
