footer: Carsten Wulff 2025
slidenumbers:true
autoscale:true
theme: Plain Jane, 1
text:  Helvetica
header:  Helvetica
date: 2025-02-06

<!--pan_title: Noise-->

<!--pan_doc:

**Keywords:** Statistics, Average Power, PSD, White Noise, Thermal Noise, SNR, Noise Figure, Friis

-->

# Noise

Noise is a phenomenon that occurs in all electronic circuits. It places a
lower limit on the smallest signal we can use. Many now have super audio
compact disc (SACD) players with 24bit converters, 24 bits is around
$2^{24} = 16.78$ Million different levels. If 5V is the maximum voltage,
the minimum would have to be $\frac{5V}{2^{24}} \approx 298nV$. That
level is roughly equivalent to the noise in a 50 Ohm resistor with a
bandwidth of 96kHz. There exists an equation that relates number of bits
to signal to noise ratio [@johns], the equation specifies
that $SNR = 6.02*Bits +
1.76 = 146.24dB$. Back in 2005 the best digital to analog converter
(DAC) that Analog Devices (a very big semiconductor company) had was a
DAC with 120dB SNR, that equals around $Bits = (120-1.76)/6.02 =
19.64$. In other words, the last four bits of your SACD player is
probably noise!

# Statistics

The mean of a signal x(t) is defined as

$$\overline{x(t)} = \lim_{T\to\infty} \frac{1}{T}\int^{+T/2}_{-T/2}{ x(t) dt} \tag{1}$$
The mean square of x(t) defined as

$$\overline{x^2(t)} =\lim_{T\to\infty} \frac{1}{T}\int^{+T/2}_{-T/2}{ x^2(t) dt} \tag{2}$$
The variance of x(t) defined as

$$\sigma^2 = \overline{x^2(t)} - \overline{x(t)}^2 \tag{3}$$ 
For a signal with
a mean of zero the variance is equal to the mean square. The
auto-correlation of x(t) is defined as

$$\begin{aligned}
  R_x(\tau ) &= \overline{x(t)x(t + \tau)} \\
&= \: \lim_{T\to\infty} \frac{1}{T}\int^{+T/2}_{-T/2}{ x(t)x(t+\tau) dt}
\end{aligned}$$

# Average Power

Average power is defined for a continuous system by (4), and for
discrete samples by (5). 

$P_{av}$ usually has the
unit $A^2$ or $V^2$, so we have to multiply/divide by the impedance to
get the power in Watts. To get Volts and Amperes we use the
root-mean-square (RMS) value which is defined as $\sqrt{P_{av}}$.

$$P_{av} = \lim_{T\to\infty} \frac{1}{T} \int^{+T/2}_{-T/2} x^2(t) dt \tag{4}$$

$$P_{av} = \frac{1}{N}\sum_{i=0}^N x^2(i) \tag{5}$$

If x(t) has a mean of zero then, according to (3), $P_{av}$ is equal
to the variance of x(t).

Many different notations are used to denote average power and RMS value
of voltage or current, some of them are listed in the two tables below.
Notation can be a confusing thing, it changes from book to book and
makes expressions look different. 

It is important to realize that it
does not matter how you write average power and RMS value. If you want
you can invent your own notation for average power and RMS value.
However, if you are presenting your calculations to other people it is
convenient if they understand what you have written. In the remainder of
this chapter we will use $\overline{e_n^2}$ for average power when we talk
about voltage noise source and $\overline{i_n^2}$ for average power when
we talk about current noise source. The n subscript is used to identify
different sources and can be whatever.

<div class="minipage" markdown="1">

<div id="t:rms" markdown="1">


|      Voltage       |      Current       |
|:------------------:|:------------------:|
|    $V_{rms}^2$     |    $I_{rms}^2$     |
| $\overline{V_n^2}$ | $\overline{I_n^2}$ |
| $\overline{v_n^2}$ | $\overline{i_n^2}$ |

</div>

</div>

<div class="minipage" markdown="1">

<div id="t:rms" markdown="1">

|          Voltage          |          Current          |
|:-------------------------:|:-------------------------:|
|         $V_{rms}$         |         $I_{rms}$         |
| $\sqrt{\overline{V_n^2}}$ | $\sqrt{\overline{I_n^2}}$ |
| $\sqrt{\overline{v_n^2}}$ | $\sqrt{\overline{i_n^2}}$ |


</div>

</div>

# Noise Spectrum

With random noise it is useful to relate the average power to frequency.
We call this Power Spectral Density (PSD). A PSD plots how much power a
signal carries at each frequency. In literature $S_x(f)$ is often used
to denote the PSD. In the same way that we use $V^2$ as unit of average
power, the unit of the PSD is $\frac{V^2}{Hz}$ for voltage and
$\frac{A^2}{Hz}$ current. The root spectral density is defined as
$\sqrt{S_x(f)}$ and has unit $\frac{V}{\sqrt{Hz}}$ for voltage and
$\frac{A}{\sqrt{Hz}}$ for current.

The power spectral density is defined as two times the Fourier transform
of the auto-correlation function [@ziel]

$$S_x(f) = 2\int_{-\infty}^{\infty}{R_x(\tau)e^{-j2\pi f \tau}d\tau} \tag{6}$$
This can also be written as

$$\begin{aligned}
S_x(f) &= 2\left[\int_{-\infty}^{\infty}{R_x(\tau)\cos(\omega \tau)d\tau} - \int_{-\infty}^{\infty}{R_x(\tau)j\sin(\omega  \tau)d\tau}\right] \\
&= 2\left[\int_{-\infty}^{0}{R_x(\tau)\cos(\omega \tau)d\tau}
 +\int_{0}^{\infty}{R_x(\tau)\cos(\omega \tau)d\tau}\right] \\
&- 2j\left[\int_{-\infty}^{0}{R_x(\tau)\sin(\omega \tau)d\tau}
 +  \int_{0}^{\infty}{R_x(\tau)\sin(\omega \tau)d\tau} \right] \\
&= 4\int_{0}^{\infty}{R_x(\tau)\cos(\omega \tau)d\tau} \\
&- 2j\left[- \int_{0}^{\infty}{R_x(\tau)\sin(\omega \tau)d\tau} +  \int_{0}^{\infty}{R_x(\tau)\sin(\omega \tau)d\tau} \right] \\
&= 4\int_{0}^{\infty}{R_x(\tau)\cos(\omega \tau)d\tau}
\end{aligned}$$

, since $e^{-j\omega \tau} = \cos(\omega \tau) - j \sin (\omega
  \tau)$, $R_x(\tau)$ and $\cos(\omega \tau)$ are symmetric around
$\tau=0$ while $\sin(\omega \tau)$ is asymmetric around $\tau = 0$.

The inverse of power spectral density is defined as

$$R_x(\tau)  = \frac{1}{2}\int_{-\infty}^{\infty}{S_x(f)e^{j 2 \pi f \tau} df} = \int_{0}^{\infty}{S_x(f) \cos(\omega \tau)df}$$

If we set $\tau=0$ we get

$$\overline{x^2(t)} = \int_{0}^{\infty}{S_x(f)df} \tag{7}$$ which means we can
easily calculate the average power if we know the power spectral
density. As we will see later it is common to express noise sources in
PSD form.

Another very useful theorem when working with noise in the frequency
domain is this

$$S_y(f) = S_x(f)|H(f)|^2 \tag{8}$$ , where $S_y(f)$ is the output power
spectral density, $S_x(f)$ is the input power spectral density and
$H(f)$ is the transfer function of a time-invariant linear system.

If we insert (8) into (7), with $S_x(f) = a\:constant = D_v$ we get

$$\overline{x^2(t)} = \int{S_y(f)df} = D_v\int{|H(f)|^2 df} = D_v f_x$$
, where $f_x$ is what we call the noise bandwidth. For a single time
constant RC network the noise bandwidth is equal to

$$f_x = \frac{\pi f_0}{2} = \frac{1}{4 R C}$$ where $f_x$ is the noise
bandwidth and $f_0$ is the 3dB frequency.

We haven’t told you this yet, but thermal noise is white and white means
that the power spectral density is flat (constant over all frequencies).
If $S_x(f)$ is our thermal noise source and $H(f)$ is a standard low
pass filter, then (8) tells us that the output spectral density will
be shaped by $H(f)$. At frequencies above the
$f_x$ in $H(f)$ we expect the root power spectral density to fall by
20dB per decade.

# Probability Distribution

<div class="theorem" markdown="1">

**Theorem 1** (Central limit theorem). *The sum of $n$ independent
random variables subjected to the same distribution will always approach
a normal distribution curve as $n$ increases.*

</div>

This is a neat theorem, it explains why many noise sources we encounter
in the real world are Gaussian.[^1] Take thermal noise for example, it is
generated by random motion of carriers in materials. If we look at a
single electron moving through the material the probability distribution
might not be Gaussian. But summing probability distribution of the
random movements with a large number of electrons will give us a Gaussian
distribution, thus thermal noise is Gaussian.

# PSD of a white noise source

If we have a true random process with Gaussian distribution we know that
the autocorrelation function only has a value for $\tau=0$. From the
definition of auto-correlation we have that

$$\begin{aligned}
R_x(\tau ) &={}  \lim_{T\to\infty} \frac{1}{T}\int^{+T/2}_{-T/2}{ x(t)x(t - \tau) dt} \\
&={} \left[ \lim_{T\to\infty} \frac{1}{T}\int^{+T/2}_{-T/2}{ x^2(t) dt} \right] \delta(\tau) \\
&={}\: \overline{x^2(t)}\delta(\tau)
\end{aligned}$$

The reason being that in a true random process $x(t)$ is uncorrelated
with $x(t + \tau )$ for any $\tau \neq 0$. If we use (6) we see
that

$$\begin{aligned}
  S_x(f) &=\: 2\int_{-\infty}^{\infty}{\overline{x^2(t)}\delta(\tau)e^{-j 2 \pi f \tau} d\tau} \\
&=\:2\overline{x^2(t)} \int_{-\infty}^{\infty}{\delta(\tau)e^{-j 2 \pi f \tau}
    d\tau} \\
&= 2\overline{x^2(t)}
\end{aligned}$$

, since

$$\int{\delta(\tau)e^{-j 2 \pi f \tau} d\tau} = e^0 = 1$$ This means
that the power spectral density of a white noise source is flat, or in
other words, the same for all frequencies.

# Summing noise sources

Summing noise sources is usually trivial, but we need to know why and
when it is not. If we write the time dependant noise signals as

$$v_{tot}^2(t) = (v_1(t) + v_2(t))^2 = v_1^2(t) + 2v_1(t)v_2(t) + v_2^2(t)$$
The average power is defined as

$$\begin{aligned}
  \overline{e_{tot}^2} &= \lim_{T\to\infty} \frac{1}{T}\int^{+T/2}_{-T/2}{ v_{tot}^2(t) dt} \\
&= \lim_{T\to\infty} \frac{1}{T}\int^{+T/2}_{-T/2}{ v_1^2(t) dt} \\
&+  \lim_{T\to\infty} \frac{1}{T}\int^{+T/2}_{-T/2}{ v_2^2(t) dt} \\
&+ \lim_{T\to\infty} \frac{1}{T}\int^{+T/2}_{-T/2}{ 2v_1(t)v_2(t) dt} \\
&= \overline{e_{1}^2} + \overline{e_{2}^2}
+ \lim_{T\to\infty} \frac{1}{T}\int^{+T/2}_{-T/2}{ 2v_1(t)v_2(t) dt}
\end{aligned}$$

If $\overline{e_{1}^2}$ and $\overline{e_{2}^2}$ are uncorrelated noise
sources we can skip the last term in
the sum above and just write

$$\overline{e_{tot}^2} = \overline{e_{1}^2} + \overline{e_{2}^2}$$ Most
natural noise sources are uncorrelated.

# Signal to Noise Ratios

Signal to Noise Ratio (SNR) is a common method to specify the relation
between signal power and noise power in linear systems. It is defined as

$$\begin{aligned}
  SNR &= 10 \log\left(\frac{Signal\:power}{Noise\:power}\right)\\
    &= 10 \log\left(\frac{\overline{v_{sig}^2}}{\overline{e_{n}^2}}\right)\\
  &=  20 \log\left(\frac{v_{rms}}{\sqrt{\overline{e_{n}^2}}}\right)
\end{aligned}$$

Another useful ratio is Signal to Noise and Distortion (SNDR), since
most real systems exhibit non-linearities it is useful to include
distortion in the ratio. One can calculate SNR and SNDR in many ways. If
we don’t know the expression for $\overline{e_{n}^2}$ we can do a FFT of
our output signal. From this FFT we sum spectral components except at
the signal frequency to get noise and distortion. SNR is normally
calculated as

$$SNR = 10
  \log\left(\frac{Signal\:power}{Noise\:power\:-\:6
\:first\:harmonics}\right)$$ 

And SNDR is calculated as

$$SNDR = 10\log\left(\frac{Signal\:power}{Noise\:  power}\right)$$

# Noise figure and Friis formula

Noise factor is a measure on the noise performance of a system. It is
defined as

$$F =
  \frac{\overline{v_o^2}}{source\:contribution\:to\:\overline{v_o^2}}$$
where $\overline{v_o^2}$ 

is the total output noise. The noise figure is defined as (noise factor in dB)

$$NF = 10 \log(F)$$ The noise factor can also be defined as

$$F = \frac{SNR_{input}}{SNR_{output}}$$

This brings us right into what is known as Friis formula. The noise factor
definition is only correct at room temperature, for more details, see [@friis].
If we have a
multistage system, for example several amplifiers in cascade, the total
noise figure of the system is defined as

$$F = 1 + F_1 - 1 + \frac{F_2 -1}{G_{1}} +
  \frac{F_3-1}{G_{1}G_{2}} + ....$$ 
  
Here $F_i$ is the noise figures of
the individual stages and $G_i$ is the available gain of each stage.
This can be rewritten as

$$F = F_1 + \sum_{i=1}^N{\frac{F_{i+1} - 1}{\prod_{k=1}^{i}{G_{k}}}}$$

Friis' formula tells us that it is the noise in the first stage that is
the most important if $G_1$ is large. We could say that in a system it
is important to amplify the noise as early as possible!

[^1]: Gaussian distribution = normal distribution. Gaussian describes
    the amplitude distribution; white describes a flat spectral density.
    Thermal noise happens to be both.

# Spectral Density 

Warning: This is not an introduction to spectral density. If the subject
is completely unfamiliar I’d advise reading another source. For example
chapter 4 in [@johns] or chapter 7 in
[@razavi].

## Definition of Spectral Density

There are two different definitions of spectral density used in the
literature. They differ by a factor of two. The one used in signal
processing books, like [@gray.r.m], is

$$S_{x1}(f) = \int_{-\infty}^{\infty}{R_{x1}(\tau)e^{-j\omega\tau}d\tau}$$
And the one often used in books about noise, like [@ziel],
is

$$S_{x2}(f) = 2\int_{-\infty}^{\infty}{R_{x2}(\tau)e^{-j\omega\tau}d\tau}$$
In both cases $R_{xi}(\tau)$ is the auto-correlation function defined as

$$R_{xi}(\tau) = \overline{x_i(t)x_i(t+\tau)}$$ As we can plainly see

$$S_{x1}(f) \neq S_{x2}(f)$$ , there is no way these two can be made
equal if

$$R_{x1}(\tau) = R_{x2}(\tau)$$ This is ok, there is
no problem having two different definitions for two different functions.
In reality $S_{x1}(f)$ and $S_{x2}(f)$ are different functions of
frequency, and we could say that

$$S_{x2}(f) = 2S_{x1}(f)$$ if the two auto-correlation functions are
equal.

## Sources of Confusion

The problem with spectral density arises when reading literature from
different communities, for example [@gray.r.m] and
[@ziel] where $S_x(f)$ is used for both $S_{x1}(f)$ and
$S_{x2}(f)$. When I started investigating spectral densities this lead
me to believe that different sources defined the same measure “spectral
density” in two different ways. The more sources I investigated the more
unsure I was about which of the two definitions that was correct. After
months of searching (not actively, but sporadically) I eventually found
the original source of the definition of spectral density
[@einstein14]. Having the original source helped, but I
still don’t know when the original definition split into the
$S_{x1}$ and $S_{x2}$ forms above. However, I’m pretty sure it’s just
a matter of convenience. To see why the $S_{x2}$ form is the most
common among sources concerning noise we look at the inverse Fourier
Transform. By the way, if you had not noticed yet, both forms say that
*Spectral density is the Fourier Transform of the Auto-Correlation
function*. The inverse Fourier Transform of $S_{x1}$ is

$$R_{x1}(\tau) = \frac{1}{2\pi}\int_{-\infty}^{\infty}{S_{x1}(f)e^{j\omega\tau}dw} = \int_{-\infty}^{\infty}{S_{x1}(f)e^{j\omega\tau}df}$$
,since $dw = df dw/df = 2\pi df$. And for $S_{x2}$

$$R_{x2}(\tau) = \frac{1}{2}\int_{-\infty}^{\infty}{S_{x2}(f)e^{jw\tau}df}$$
Before we proceed lets get rid of the $e$’s. We know that $e^{j\alpha} =
\cos \alpha + j \sin \alpha$. So we could rewrite $S_{x1}$ as

$$S_{x1}(f) = \int_{-\infty}^{\infty}{R_{x1}(\tau)[\cos(\omega \tau) + j \sin( \omega
  \tau)]d\tau}$$ and it turns out that since $R_{x1}(\tau)$ is an even
function we can drop the $j\sin{\omega \tau}$ term. $S_{x1}(f)$ is also
an even function since the Fourier Transform of an even function is
even.

The definitions then become

$$\begin{aligned}
S_{x1}(f) &= \int_{-\infty}^{\infty}{R_{x1}(\tau)\cos(\omega\tau)d\tau}\\
R_{x1}(\tau) &= \int_{-\infty}^{\infty}{S_{x1}(f)\cos(\omega\tau)df}
\end{aligned}$$

and

$$\begin{aligned}
S_{x2}(f) &= 2\int_{-\infty}^{\infty}{R_{x2}(\tau)\cos(\omega\tau)d\tau}\\
R_{x2}(\tau) &= \frac{1}{2}\int_{-\infty}^{\infty}{S_{x2}(f)\cos(\omega\tau)df}
\end{aligned}$$

We can rewrite $R_{x2}(\tau)$ as

$$R_{x2}(\tau) = \overline{x_2(t)x_2(t + \tau)} = \int_0^{\infty}{S_{x2}(f)\cos(\omega\tau)df}$$
and if $\tau = 0$

$$\overline{x_2^2(t)} = \int_0^{\infty}{S_{x2}(f)df}$$ So using the
$S_{x2}$ definition we see that average power (mean square value of
$x_2(t)$) is equal to the integral from 0 to infinity of the spectral
density. If we use $S_{x1}$ instead, average power would be

$$\overline{x_1^2(t)} = 2\int_0^{\infty}{S_{x1}(f)df}$$ But if
$R_{x1}(\tau) = R_{x2}(\tau)$ then

$$\overline{x_2^2(t)} = \overline{x_1^2(t)}$$ even though
$S_{x1}(f) \neq S_{x2}(f)$.

$S_{x1}$ is called the two-sided spectral density, and $S_{x2}$ the
one-sided spectral density.

## Example: Thermal Noise

The spectral density of thermal noise in electronic circuit should be
known to anyone that has studied analog electronics. We normally define
the voltage spectral density of thermal noise as

$$S_{th}(f) = 4kTR$$ where k is Boltzmann’s constant, T the temperature in
Kelvin and R the resistance. But that is the spectral density in the
one-sided $S_{x2}$ definition. If we were to use the two-sided
$S_{x1}$ definition, then the spectral density of thermal noise would
be

$$S_{th}(f) = 2kTR$$ Both these spectral densities would give the same
average power value if we use the inverse Fourier Transform of the
matching definition.[^2]

## Einstein: The source

In his 1914 paper [@einstein14] Albert Einstein described,
supposedly for the first time, the auto-correlation function and what we
have come to know as the spectral density. He defined the
auto-correlation function as

$$\mathfrak{M} (\Delta) = \overline{F(t)F(t + \Delta)}$$ and the
intensity (spectral density) as

$$I(\theta) =  \int_0^{T}{\mathfrak{M}(\Delta) \cos ( \pi \frac{\Delta}{\theta})d\Delta}$$
,where the period $\theta = T/n$ and $T$ is a very large value. The
paper is very short, only 1 page, but it is worth reading. Note that
the spectral density as the Fourier Transform of the auto-correlation
function is often referred to as the *Wiener-Khintchine* theorem.

[^2]: Note that if you calculate the average power of $S_{th}(f)$ you’ll
    get infinity. You have to include the bandwidth of the circuit you
    are considering for average power to have a finite value.

---

# Summary
<!--pan_doc:

The one-page version of this chapter:

-->

- Noise is random: describe the amplitude by its distribution (usually Gaussian) and the power by its spectral density
- Thermal noise is 4kTR in every resistor and kT/C on every sampled capacitor - no cleverness removes it
- Flicker noise comes from traps: 1/f density, quieter with bigger devices
- Integrate the density over the band you keep to get the power the signal must beat
- Friis: with gain up front, only the first stage's noise matters - spend your current there

---

# Would you like to know more?

<!--pan_doc:

The classic on noise in solid state devices, still the reference [@ziel]

Friis' original, short and still the clearest statement of why the first stage decides the noise figure [@friis]

Chapter-length treatments of circuit noise, either of which will do [@razavi] [@johns]

The random walk that thermal noise is made of, from the source [@einstein14]

-->
