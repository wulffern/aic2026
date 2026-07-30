#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt


#- Enable hanning window
hann = True

#- Create a time vector
N = 2**13
t = np.arange(N)

#- Create the "continuous time" signal
fdivide = 2**6
f1 = 1/fdivide - 1/N
x_s = np.sin(2*np.pi*f1*t) + + 1/2**15*np.random.randn(N)

#----------------------------------------------
#- Model an ADC
#----------------------------------------------

## Sample
#- Sampling frequency is 1/nfs of the time vector
nfs = 4
x_sn = x_s[0::nfs]

def adc(x,bits):
    levels = 2**bits
    y = np.round(x*levels)/levels
    return y

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
plt.show()
