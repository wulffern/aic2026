footer: Carsten Wulff 2026
slidenumbers:true
autoscale:true
theme:Plain Jane,1



<!--pan_skip: -->

**Who:** Carsten Wulff, Principal Radio Architect, Short Range Business Unit, Nordic Semiconductor
**Why:** Life without challenges is boring,  **What:** Responsible for Short-Range Radio across spacetime

<!--pan_title: Low Power Radio -->

![inline  fit](../media/timeline.pdf)



---

[.column]

## Data 

<!--pan_doc:

A mouse reports on the relative X and Y displacement of the mouse as a function of time. A mouse has buttons. There can be many mice in a room, as such, they must have an address , so 
PCs can tell them apart. 

A mouse must be low-power. As such, the radio cannot be on all the time. The radio must start up and be ready to receive quickly. 

We don't know how far 
away from the PC the mice might be, as such, we don't know the dB loss in the communication channel. As a result, the radio needs to have a high dynamic range, from weak signals
to strong signals. In order for the radio to adjust the gain of the receiver we should include a pre-amble, a known sequence, for example 01010101, such that the radio can 
adjust the gain, and also, recover the symbol timing. 

All in all, the packets we send from the mouse may need to have the following bits.

-->

| What | Bits | Why |
| ----  | ---- | ---- |
| X displacement | 8 | |
| Y displacement | 8 | |
| CRC | 4 | Bit errors|
| Buttons| 16 | One-hot coding. Most mice have buttons|
| Preamble| 8 | Synchronization|
| Address | 32 | Unique identifier |
| Total | 76 | |


[.column]

## Rate

Assume 1 ms update rate


## Data Rate



Application Data Rate > 76 bits/ms = 76 kbps

Assume 30 % packet loss

Raw Data Rate > 228 kbps

Multiply by 3.14 > 716 kbps

Round to nearest nice number = 1Mbps

<!--pan_doc:

The above statements are a exact copy of what happens in industry when we start design of something. We make an educated guess and multiply by a number.
More optimistic people would multiply with $e$. 

-->

---

# [fit] Carrier Frequency & Range

<!--pan_doc:

Below is a table of the available frequencies, but how should we pick which one to use? There are at least two criteria that should be investigated. Antenna and Range. 

-->

| Flow| Fhigh | Bandwidth | Description|
|:---|:---|:---|:---|
|40.66 MHz|40.7 MHz|40 kHz|Worldwide| 
|433.05 MHz|434.79 MHz|1.74 MHz|Region 1|
|902 MHz|928 MHz|26 MHz|Region 2| 
|2.4 GHz|2.5 GHz|100 MHz|Worldwide|
|5.725 GHz|5.875 GHz|150 MHz|Worldwide|
|24 GHz|24.25 GHz|250 MHz|Worldwide|
|61 GHz|61.5 GHz|500 MHz|Subject to local acceptance|


---

## Antenna

<!--pan_doc:

For a mouse we want to hold in our hand, there is a size limit to the antenna. There are many types of antenna, but 
-->


[.column]
assume wavelength/4 is an OK antenna size (wavelength = lightspeed/frequency)

<!--pan_doc:

The below table shows the ISM band and the size of a quarter wavelength antenna. Any frequency above 2.4 GHz may be OK from a size perspective. 

-->

[.column]
| ISM band |$$\lambda/4$$ | Unit|OK/NOK|
|---|---:|---:|---:|
| 40.68 MHz | 1.8  | m |:x:|
| 433.92 MHz | 17 | cm|:x:|
| 915 MHz | 8.2 | cm||
| 2450 MHz | 3.06 | cm|:white_check_mark:|
| 5800 MHz | 1.29 | cm|:white_check_mark:|
| 24.125 GHz | 3.1 | mm|:white_check_mark:|
| 61.25 GHz | 1.2 | mm|:white_check_mark:|

---

## Range (Friis)

<!--pan_doc:

One of the worst questions a radio designer can get is "What is the range of your radio?", especially if the people asking are those that don't understand
physics, or the real world. The answer to the question is incredibly complicated, as it depends on exactly what is between two devices talking. 

If we assume, however, that there is only free space, and no real reflections from anywhere, then we can make an estimate of the range. 

-->

[.column]

Assume no antenna gain, power density p at distance D is

$$ p = \frac{P_{TX}}{4 \pi D^2}$$

Assume receiver antenna has no gain, then the effective aperture is

$$ A_e = \frac{\lambda^2}{4 \pi}$$

[.column]

Power received is then

$$P_{RX} = \frac{P_{TX}}{D^2} \left[\frac{\lambda}{4 \pi}\right]^2$$

Or in terms of distance

$$ D = 10^\frac{P_{TX} - P_{RX} + 20 log_{10}\left(\frac{c}{4 \pi f}\right)}{20} $$

---

## Range (Free space)

<!--pan_doc:

If we take the ideal equation above, and use some realistic numbers for TX and RX power, we can estimate a range. 
-->

Assume TX = 0 dBm, assume RX sensitivity is -80 dBm

| Freq | **$$20 log_{10}\left(c/4 \pi f\right)\text{ [dB]}$$** | D [m]| OK/NOK|
| ----|:----:| ---: | ---:|
| 915 MHz | -31.7 | 260.9 | :white_check_mark:|
| **2.45 GHz** | **-40.2** | **97.4** |:white_check_mark:|
| 5.80 GHz | -47.7 | 41.2 |:white_check_mark:|
| 24.12 GHz | -60.1 | 9.9 | :x:|
| 61.25 GHz | -68.2 | 3.9 | :x:|
| 160 GHz | -76.52| 1.5 | :x:|

---

## Range (Real world)

<!--pan_doc:

In the real world, however, the 
-->

path loss factor, $$ n \in [1.6,6]$$, $$ D = 10^\frac{P_{TX} - P_{RX} + 20 log_{10}\left(\frac{c}{4 \pi f}\right)}{n
\times 10} $$

<!--pan_doc:

So the real world range of a radio can vary more than an order of magnitude. Still, 2.4 GHz seems like a good choice for a mouse. 
-->

| Freq | **$$20 log_{10}\left(c/4 \pi f\right)\text{ [dB]}$$**| D@n=2 [m]|D@n=6 [m] | OK/NOK|
| ----|:----:| ---: | ---:| ---:|
| **2.45 GHz** | **-40.2** | **97.4** | **4.6** |:white_check_mark:|
| 5.80 GHz | -47.7 | 41.2 | 3.45 |:white_check_mark:|
| 24.12 GHz | -60.1 | 9.9 | 2.1 | :x:|


---

#[fit] Modulation 

---

<!--pan_doc:

Any modulation can be described by the function below. 

-->

#[fit] $$ A_m(t) \left[\frac{e^{i\left[ 2 \pi f_{carrier}(t)t + \phi(t)\right]} + e^{-i\left[ 2 \pi f_{carrier}(t)t + \phi(t)\right]}}{2}\right]$$

---

<!--pan_doc:

The amplitude of the carrier can be modulated, or the phase of the carrier. 

People have been creative over the last 50 years in terms of encoding bits onto carriers. Below is a small excerpt of some common schemes. 

-->

| Scheme | Acronym|Pro | Con |
| ----| ----|----| ----|
| Binary phase shift keying | BPSK | Simple | Not constant envelope|
| Quadrature phase-shift keying | QPSK |2bits/symbol| Not constant envelope|
| Offset QPSK |OQPSK| 2bits/symbol | Constant envelope with half-sine pulse shaping|
| Gaussian Frequency Shift Keying | GFSK | 1 bit/symbol| Constant envelope|
| Quadrature amplitude modulation| QAM | > 10 bits/symbol| Really non-constant envelope|

---

# Single carrier, or multi carrier?


<!--pan_doc:


Assume we wanted to send 1024 Mbps over the air. We could choose a bandwidth of a about 1 GHz with 1-bit per symbol, or  have a bandwidth of 1 MHz if
we sent 1024 QAM at 1MS/s. Both cases would look like the figure below.

In both cases we get problems with the physical communication channel, the change in phase and amplitude affect what is received. 
For a 1 GHz bandwidth at 2.4 GHz carrier we'd have problems with the phase. At 1024 QAM we'd have problems with the amplitude. 

-->

---

![inline fit](../media/l10_single_carrier.pdf)


<!--pan_doc:

Back in 1966 [Orthogonal frequency division multiplexing](https://en.wikipedia.org/wiki/Orthogonal_frequency-division_multiplexing#:~:text=OFDM%20is%20a%20frequency%2Ddivision,is%20divided%20into%20multiple%20streams.)
was introduced to deal with the communication channel. In OFDM we modulate a number of sub-carriers in the frequency space with our wanted modulation scheme (BPSK, PSK, QAM), then do an inverse fourier transform to 
get the time domain signal, mix on to the carrier, and transmit. At the receiver we take an FFT and do demodulation in the frequency space. See example in figure below.

The name "multiple carriers" is a bit misleading. Although there are multiple carriers on the left and right side of the figure, there is normally still just one carrier in the TX/RX. 

-->

---

![inline fit](../media/l10_multiple_carrier.pdf)

<!--pan_doc:

There are more details in OFDM than the simple statement above, but the details are just to fix challenges, such as "How do I recover the symbol timing? 
How do I correct for frequency offset? How do I ensure that my time domain signal terminates correctly for every FFT chunk"

The genius with OFDM is that we can pick a few of the sub-carriers to be pilot tones that carry no new information. If we knew exactly what was sent in phase and amplitude, 
then we could measure the phase and amplitude change due to the physical communication channel, and we could correct the frequency space before we tried to de-modulate.


It's possible to do the same with single carrier modulation also. Imagine we made a 128-QAM modulation on a single carrier. As long as we constructed the time domain signal
correctly (cyclic prefix to make the FFT work nicely, some preamble to measure the communication channel, then we could take an FFT at the receiver, correct 
the phase and amplitude, do an IFFT and demodulate the time-domain signal as normal. 


In radio design there are so many choices it's easy to get lost. 

-->


---

#[fit] TX

---

![inline fit](../media/l7_const_env.pdf)

---

![inline](../media/l08_pll_2mod.pdf)


---


<!--pan_doc:

For phase and amplitude modulation, or complex transmitters, we need a way to change the amplitude and phase. What a shocker. There are two ways to do that. A polar architecture 
where phase change is done in the PLL, and amplitude in the power amplifier. 

-->

![inline fit](../media/l7_polar.pdf)

---

<!--pan_doc:

Or a Cartesian architecture where we make the in-phase component, and quadrature-phase 
components in digital, then use two digital to analog converters, and a set of complex mixers to encode onto the carrier. The power amplifier would not need to change
the amplitude, but it does need to be linear. 
-->

![inline fit](../media/l8_cartesian.pdf)

---


#[fit] RX

---

## Use a Software Defined Radio 

<!--pan_doc:

For our mouse, what radio scheme should we choose? One common instances of "how to make a choice" in industry is "Delay the choice as long as possible so
your sure the choice is right". 

Maybe the best would be to use a software defined radio receiver? Something like the picture below, an antenna, low noise amplifier, and a 
analog-to-digital converter. That way we could support any transmitter. Fantastic idea, right?

-->

![left fit](../media/lg_lna_adc.pdf)

<!--pan_doc:

Well, lets check if it's a good idea. We know we'll use 2.4 GHz, so we need about 2.5 GHz bandwidth, at least. We know we want good range, so maybe 100 dB
dynamic range. 
In analog to digital 
converter design there are figure of merits, so we can actually compute a rough power consumption for such an ADC. 
-->

ADC FOM $$ = \frac{P}{2 BW 2^n}$$

State of the art FOM $$\approx 1 \text{ fJ/step}$$
 
 $$ BW = 2.5\text{ GHz}$$

 $$ \text{Bits }?= 18 $$ 
 
 $$ SNDR = 6.02\times18+1.76 = 110\text{ dB} $$ 
 
 $$ P = 1\text{ fJ/step} \times 5 \text{ GHz} \times 2^{18} = 1.3\text{ W}$$

<!--pan_doc:

At 1.3 W our mouse would only last for 2 hours. That's too short. It will never be a low power idea to convert the full 2.5 GHz bandwidth to digital, we need some bandwidth selectivity 
in the receive chain. 

-->


---


<!--pan_skip: -->

<!--![fit](https://www.bluetooth.com/wp-content/themes/bluetooth/images/logos/bluetooth-logo-color-black.svg)-->
![fit](../media/bluetooth-logo-color-black.svg)

---

## Bluetooth Low Energy

- 2.400 GHz to 2.480 GHz
- 2 MHz channel spacing
- 40 Channels (3 primary advertising channels)
- Up to 20 dBm 
- Minimum -70 dBm sensitivity (1 Mbps)
- 1 MHz GFSK (1 Mbps, 500 kbps, 125 kbps), 2 MHz GFSK (2 Mbps)
+ Channel Sounding
+ Direction Finding

---
<!--pan_skip: -->

#[fit] Low Power Receivers

---


![inline fit](../media/l10_lprxarch.pdf)

---

<!--pan_doc:

In the typical radio we'll need the blocks below. I've added a column for how many people I would want if I was to lead development of a new radio.

-->

| Blocks            | Key parameter                         | Architecture  | Complexity (nr people) |
|-------------------|---------------------------------------|---------------|------------------------|
| Antenna           | Gain, impedance                       | lambda/4      | <1                     |
| RF match          | loss, input impedance                 | PI-match      | <1                     |
| Low noise amp     | NF, current, linearity                | LNTA          | 1                      |
| Mixer             | NF, current, linearity                | Passive       | 1                      |
| Anti-alias filter | NF, current, linearity                | Active-RC     | 1                      |
| ADC               | Sample rate, dynamic range, linearity | NS-SAR        | 1 - 2                  |
| PLL               | Phase noise, current                  | AD-PLL        | 2-3                    |
| Baseband          | Eb/N0, gate count, current.           | SystemVerilog | > 10                   |

---

## [fit] LNTA

---

<!--pan_doc:

The first thing that must happen in the radio is to amplify the noise as early as possible. Any circuit has inherent noise, be it thermal-, flicker-, burst-, or shot-noise. 
The earlier we can amplify the input noise, the less contribution there will be from the radio circuits.

The challenges in the low noise amplifier is to provide the right gain. If there is a strong input signal, then reduce the gain. If there is a low input signal, then 
increase the gain. 

One way to implement variable gain is to reconfigure the LNA. For an example, see 

-->

[30.5 A 0.5V BLE Transceiver with a 1.9mW RX Achieving -96.4dBm Sensitivity and 4.1dB Adjacent Channel Rejection at 1MHz Offset in 22nm FDSOI](https://ieeexplore.ieee.org/document/9063021) 


<!--pan_doc:

A typical Low Noise Transconductance Amplifier is seen below. It's a combination of both a common source, and a common gate amplifier. The current in the NMOS and PMOS is controlled by Vgp and Vgn. Keep in mind that at RF frequencies the signals are weak, so it's easy to provide the DC for the LNA with a resistor to a diode connected PMOS or NMOS.

In a LNA the input impedance must be matched to what is required by the antenna/match in order to have maximum power transfer, that's the role of the inductors/capacitors.


-->

![left fit](../media/l10_lna.pdf)

---

## [fit] MIXER

---

<!--pan_doc:

In the mixer we multiply the input signal with our local oscillator. Most often a complex mixer is used. There is nothing complex about complex signal processing, 
just read

-->

[Complex signal processing is not complex](https://ieeexplore.ieee.org/document/1333231)

<!--pan_doc:

In order to reduce power, it's most common with a passive mixer as shown below. A passive mixer is just MOS that we turn on and off with 25% duty-cycle. See example in 

-->

[A 370uW 5.5dB-NF BLE/BT5.0/IEEE 802.15.4-Compliant Receiver with >63dB Adjacent Channel Rejection at >2 Channels Offset in 22nm FDSOI](https://ieeexplore.ieee.org/document/9062973/)



![left fit](../media/l10_mix.pdf)


---

<!--pan_doc:

To generate the quadrature and in-phase clock signals, which must be 90 degrees phase offset, it's common to generate twice the frequency in the 
local oscillator (4.8 GHz), and then divide down to 4 2.4 GHz clock signals. 

If the LO is the same as the carrier, then the modulation signal 
will be at DC, often called direct conversion. 

The challenge at DC is that there is flicker noise, offset, and burst noise. The modulation type, however, can impact whether low frequency noise is an issue. In OFDM we
can choose to skip the sub-carriers around 0 Hz, and direct conversion works well. An advantage with direct conversion is that there is no "image frequency" and 
we can use the full complex bandwidth. 

For FSK and direct conversion the low frequency noise can cause issues, as such, it's common to offset the LO from the transmitted signal, for example 4 MHz offset. 
The low frequency noise problem disappears, however, we now have a challenge with the image frequency (-4 MHz) that must be rejected, and we need an increased bandwidth.

There is no "one correct choice", there are trade-offs that both ways. KISS (Keep It Simple Stupid) is one of my guiding principles when working on radio architecture. 

These days most de-modulation happens in digital, and we need to convert the analog signal to digital, but first AAF.

-->


## [fit] AAF

<!--pan_doc:


The anti alias filter rejects frequencies that can fold into the band of interest due to sampling. A simple active-RC 
filters is often good enough. 

We often need gain in the AAF, as the LNA does not have sufficient gain for the weakest signals. -100 dBm in 50 ohm is 6.2 nV RMS, while input 
range of an ADC may be 1 V. Assume we place the lowest input signal at 0.1 V, so we need a voltage gain of $20\log(0.1/6.2e-9) = 76$dB in the receiver.

-->

---

![inline fit](../media/l4_activebiquad.pdf)


---

## [fit] ADC

<!--pan_doc:

Aaah, ADCs, an IP close to my heart. I did my Ph.d and Post-Doc on ADCs, and the Ph.D students I've co-supervised have worked on ADCs. 

At NTNU there have been multiple students through the years that have made world-class ADCs, and there's still students at NTNU working on state-of-the-art ADCs. 

These days, a good option is a SAR, or a Noise-Shaped SAR. 

If I were to pick, I'd make something like [A 68 dB SNDR Compiled Noise-Shaping SAR ADC With On-Chip CDAC Calibration](https://ieeexplore.ieee.org/document/9056925) as shown in the figure below.

-->

---

![left fit](../media/l6_harald_arch.gif)

![right fit](../media/l6_fig_harald_circuit.gif)


---

## [fit] AD-PLL

<!--pan_doc:

The phase locked loop is the heart of the radio, and it's probably the most difficult part to make. Depends a bit on technology, but these days, All Digital PLLs are cool. Start by reading Razavi's PLL book. 

You can spend your life on PLLs. 

-->

---

AD-PLL with Bang-Bang phase detector for steady-state 

![inline](../media/pll_master_arch_28feb2020.pdf)

---

##[fit] Baseband

<!--pan_doc:

Once the signal has been converted to digital, then the de-modulation, and signal fixing start. That's for another course, but there are interesting challenges. 

-->

---


|Baseband block | Why |
|---|---|
| Mixer? | If we're using low intermediate frequency to avoid DC offset problems and flicker noise|
| Channel filters?| If the AAF is insufficient for adjacent channel|
| Power detection | To be able to control the gain of the radio|
| Phase extraction| Assuming we're using FSK|
| Timing recovery | Figure out when to slice the symbol|
| Bit detection | single slice, multi-bit slice, correlators etc|
| Address detection | Is the packet for us?|
| Header detection | What does the packet contain|
| CRC  | Does the packet have bit errors|
| Payload de-crypt| Most links are encrypted by AES|
| Memory access| Payload need to be stored until CPU can do something|

---

![150%](../media/nRF51822.jpg)

---

#[fit] Thanks!

---

<!--pan_doc:

# Want to learn more?

-->

[A 0.5V BLE Transceiver with a 1.9mW RX Achieving -96.4dBm Sensitivity and 4.1dB Adjacent Channel Rejection at 1MHz Offset in 22nm FDSOI](https://ieeexplore.ieee.org/document/9063021), M. Tamura, Sony Semiconductor Solutions, Atsugi, Japan, 30.5, ISSCC 2020

[A 370uW 5.5dB-NF BLE/BT5.0/IEEE 802.15.4-Compliant Receiver with >63dB Adjacent Channel Rejection at >2 Channels Offset in 22nm FDSOI](https://ieeexplore.ieee.org/document/9062973/), B. J. Thijssen, University of Twente, Enschede, The Netherlands

[A 68 dB SNDR Compiled Noise-Shaping SAR ADC With On-Chip CDAC Calibration](https://ieeexplore.ieee.org/document/9056925), H. Garvik, C. Wulff, T. Ytterdal

[A Compiled 9-bit 20-MS/s 3.5-fJ/conv.step SAR ADC in 28-nm FDSOI for Bluetooth Low Energy Receivers](https://ieeexplore.ieee.org/document/7906479), C. Wulff, T. Ytterdal

Cole Nielsen, <https://github.com/nielscol/thesis_presentations>

"Python Framework for Design and Simulation of Integer-N ADPLLs", Cole Nielsen, <https://github.com/nielscol/tfe4580-report/blob/master/report.pdf>

[Design of CMOS Phase-Locked Loops](https://doi.org/10.1017/9781108626200), Behzad Razavi, University of California, Los Angeles







