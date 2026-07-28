footer: Carsten Wulff 2024
slidenumbers:true
autoscale:true
theme: Plain Jane, 1
text:  Helvetica
header:  Helvetica
date: 2026-01-30

<!--pan_skip: -->

## TFE4188 - Lecture 3
# Reference and bias

---
<!--pan_skip: -->
# Goal for today

Understand **why** we need reference and bias circuits

Introduction to **circuit architectures** 

---
<!--pan_skip: -->

#[fit] Why

---

<!--pan_title: References and bias -->

<!--pan_doc:

**Keywords:** VREF, IREF, VD, BGAP, LVBGAP, VI, GMCELL

**Status:** 1.0

<iframe width="560" height="315" src="https://www.youtube.com/embed/3Z4YXoVmxx8?si=9JI3Cw1d8Fdip_7t" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

In our SPICE testbenches, and trial schematics, it's common to include voltage sources and current sources,
like the symbols in Figure 1. 

The 
ideal voltage source, or ideal current source, does not exist in the real world. There is no such thing.

We can come close to creating a voltage source, a known voltage,
with a low source impedance, but not zero impedance.
And it won't be infinitely fast either. If we suddenly decide to pull 1 kA 
from a lab supply I promise you the voltage will drop. 

How do we create something that is a _good enough_ voltage and current source on an IC? That's the goal of this chapter.
To give you an introduction to "voltage sources" and "current sources" that we can
make on an integrated circuit. 

But before we take a take a look at the voltage and current source, 
I want you to think about how you would route a current, or a voltage on an IC.

-->

![fit](../media/l3_sources_tikz.pdf)

<!--pan_doc:

<sub>Figure 1: Symbols for voltage source and current source  </sub>
-->

---

<!--pan_doc: 

# Routing


Assume we have a known voltage on our IC, a reference voltage. How can we make sure we can share that voltage across an IC? 

A voltage is only defined between two points. 
There is no such thing as the _voltage at a point on a wire_, nor _voltage in a node_. 
Yes, I know we say that, but it's not right. What we forget is that by _voltage in a node_ 
we always, always mean _voltage in a node referred to ground_.

We've invented this magical place called _ground_, 
the final resting place of electrons, and we have agreed that voltages refer to that point.

As such, when we say "Voltage in node A is 1V", what we actually 
mean is "Voltage in node A is 1 V referred to ground".

Maybe you now understand why we can't just route a voltage across the IC, 
the _other side_ might not have the same ground. The _other side_
might have a different impedance to ground, and the impedance might 
be a function of time, voltage, frequency temperature, pressure and presence of gremlins.

Consider Figure 2. The ground impedance may depend on time, voltage, frequency, temperature, pressure (yes, stress
in silicon can change the band structure, thus the conduction band energy levels, and thus the available charge carriers in the conduction band).

If there is no current flowing in the ground impedance at the destination we may be OK, but usually, there is some current
flowing into ground at the destination. There is a circuit there. 

If we choose to route a reference as a voltage we need to be careful with the ground.

-->

![fit](../media/l3_vsrc_tikz.pdf)

<!--pan_doc:

<sub>Figure 2: Voltage source with ground impedance. Routing long distances it's not possible to have
guarantee we have the same ground impedance at the destination.</sub>
-->

---

<!--pan_doc:

Most of the time, in order not to think about the ground impedance, we choose to route a known quantity, the reference, 
as a current instead of a voltage. That means, however,
we must convert from a voltage to a current, but we can do that with a resistor (you'll see later), 
and as long as the resistor is the same on the other side of the IC, 
then we'll know what the voltage is.

-->

![fit](../media/l3_isrc_tikz.pdf)

<!--pan_doc:
<sub>Figure 3: Routing a reference as a current. </sub>
-->

<!--pan_doc:

Resistors have finite matching across die, let's say 2 % 3-sigma variation. A limitation on how accurate we can distribute 
reference across the IC with current method. 

For most voltage regulators (think about the circuit that delivers the digital voltage for an MCU)
2 % percent may be an acceptable portion of the error budget. 
For a battery charger, however, the termination voltage of Li-ion batteries need to be precise, more accurate than 1 %.

For that application we cannot distribute current, we must distribute voltage, but we need to care deeply about ground. 

But how can "It's better to distribute a voltage as a current across the IC, it's more accurate" 
and "If you need something really accurate, you must distribute voltage" both be true?

Imagine I have a 0.5 % 3-sigma accurate voltage reference at 1.22 V, that’s a sigma of 2 mV. 
I need this reference voltage on a block on the other side of the IC, I don’t want to distribute 
voltage, because I don’t know that the ground is the same on the other side, at least not to a precision of 2 mV. 
I convert the voltage into a current, however, I know the R has a 2 % 3-sigma across die, 
so my error budget immediately increases to 2.06%. 

But what if I must have 0.5 % 3-sigma voltage in the block? For example in a battery charger, 
where the 4.3 V termination voltage must be 1 % accurate? 
I have no choice but to go with voltage directly from the reference, 
but the key point,  is then the receiving block **cannot** be on the other side of the IC. 
The reference must be right next to my block.

I could use two references on my IC, one for the ADC and one for the battery charger.
Ask yourself, “Why do we care if there is two references?” 
And the answer is “Silicon area is expensive, to make things cheep, we must make things small”,  
in other words,  we should not duplicate features unless we absolutely have to.

-->



---

#[fit] Bandgap voltage reference

---

<!--pan_doc:

One of the ways to create a known reference on an integrated circuit is the "bandgap voltage reference". There are
flavors of bandgaps, but all rely on the bandgap of silicon, which is about 1.12 eV.

We can't access the bandgap voltage directly, but we can use the fact that diodes, and BJTs all have a voltage 
across the PN junction of about 1.12 V at absolute zero (actually, slightly higher, maybe 1.2 V), and that they
have a well known temperature dependence from that point. 

-->


## A voltage complementary to temperature (CTAT)

<!--pan_doc: 
A diode connected bipolar transistor, shown in Figure 4, or indeed a PN diode, 
assuming a fixed current, will have a voltage across that is temperature dependent
-->

$$ I_D = I_S \left(e^{\frac{V_{BE}}{V_T}} - 1\right)  + I_B \approx I_S e^{\frac{ V_{BE}}{V_T}}$$

![left fit](../media/l3_bjtonly_tikz.pdf)

<!--pan_doc:

<sub>Figure 4: Diode connected bipolar transistor </sub>
-->
 

<!--pan_doc:

As $I_S$ is much smaller that $I_D$ we can ignore the -1, 
and we assume that the base current is much smaller than the drain current.

Re-arranging for $V_{BE}$ and inserting for 

-->

 $$V_T = \frac{kT}{q}$$

 $$ V_{BE} = \frac{k T}{q} \ln{\frac{I_C}{I_S}}$$
 
 $$I_S = q A n_i^2 \left[\frac{D_n}{L_n N_A} + \frac{D_p}{L_p N_D}\right]$$
 
 
<!--pan_doc: 

From this equation, it looks like the voltage $V_{BE}$ is proportional to temperature, however, 
it turns out that the $V_{BE}$ decreases with 
temperature due to the temperature dependence of $I_S$.

The $V_{BE}$ is almost linear with temperature with a property that 
if you extrapolate the $V_{BE}$ line to zero Kelvin, then all diode voltages 
seem to meet at the bandgap voltage of silicon (approx 1.12 eV). 

To see the temperature coefficient, I find it easier to re-arrange the equation above.

-->

---

Some algebra (see [Diodes](https://analogicus.com/aic2026/diodes))
 
 $$ V_{BE} = \frac{kT}{q}(\ell  - 3 \ln T) + V_G $$ 

<!--pan_doc:

The $\ell$ is a temperature independent constant given by 

--->


 $$ 
 \begin{split}
 \ell= \ln{I_C} - 
 \ln{qA} - \ln{\left[\frac{D_n}{L_n N_A} + \frac{D_p}{L_p N_D}\right]}
 \\ - 2 \ln{2}
  - \frac{3}{2} \ln{m_n^*} - \frac{3}{2}\ln{m_p^*}
 - 3 \ln{\frac{2 \pi k}{h^2}} 
 \end{split}
 $$

---

<!--pan_doc:

And if we plot the diode voltage, we can see that the voltage decreases as a function of temperature.

-->

![fit](../media/vd.svg)

<!--pan_doc:

<sub>Figure 5: Diode voltage versus temperature. Bottom plot shows deviation from a straight line. </sub>
-->


---

## A current proportional to temperature (PTAT)

<!--pan_doc: 

If we take two diodes, or bipolars, biased at different current densities, as shown in Figure 6, then

$$ V_{D1} = V_T \ln{\frac{I_{D}}{I_{S1}}} $$

$$ V_{D2} = V_T \ln{\frac{I_{D}}{I_{S2}}} $$

The OTA will force the voltage on top of the resistor to be equal to $V_{D1}$, 
thus the voltage across the resistor $R_1$ is 

-->

$$ V_{D1} - V_{D2} = V_T \ln{\frac{I_{D}}{I_{S1}}} - V_T \ln{\frac{I_{D}}{I_{S2}}} = V_T \ln{\frac{I_{S2}}{I_{S1}} }  = V_T \ln N $$

<!--pan_doc:

This is a remarkable result. The difference between two voltages is only defined by Boltzmann's constant, 
temperature, charge, and a know size difference.

This differential voltage can be used to read out directly the temperature on an IC, 
provided we can compare to a known voltage. 

We often call this voltage $\Delta V_D$ or $\Delta V_{BE}$, 
and we can see it's proportional to absolute temperature. 

We know that the $V_D$ decreases linearly with temperature, so if we combined a multi-plum of the 
$\Delta V_{BE}$ with a $V_D$ voltage, then we should get a constant voltage.

-->

![left fit](../media/l03_ptat_tikz.pdf)

<!--pan_doc:
<sub>Figure 6: Circuit to create a PTAT current controlled by the resistor and $\Delta V_{BE}$ </sub>
-->

---

## How to combine a CTAT with a PTAT ?

---

<!--pan_doc:

One method is Figure 7. The voltage across resistor $R_2$ would compensate for the decrease in $V_{D3}$,
as such, $R_2$ would be bigger than $R_1$.

-->

![fit](../media/l03_vref1_tikz.pdf)

<!--pan_doc:

<sub>Figure 7: A bandgap voltage reference with a constant output voltage. </sub>
-->

---

<!--pan_doc:

Another method would be to stack the $R_2$ on top of $R_1$ as shown in Figure 8. 

-->

![fit](../media/l03_vref2_tikz.pdf)


<!--pan_doc:

<sub>Figure 8: Another  bandgap voltage reference with a constant output voltage. </sub>
-->


<!--pan_doc:

-->

---

<!--pan_doc:

## Widlar reference

The first bandgap reference was not Brokaw's. Bob Widlar built one in 1971 for
the LM113, three years before the cell on the next slide, and it is worth
starting here. Partly for the history, and partly because it does the entire
job with three transistors, three resistors, and no amplifier anywhere. It was
published in
[New developments in IC voltage regulators](https://ieeexplore.ieee.org/document/1050151).

Figure 9 is the circuit. It is a two terminal shunt reference: you feed it a
bias current down from the supply and it holds its own terminal at $V_{REF}$,
the way a zener does, except that it does it at 1.2 V, where no zener will.

-->

![left fit](../media/l3_widlar_tikz.pdf)

<!--pan_doc:

<sub>Figure 9: Widlar's bandgap reference, the first one, from 1971 </sub>
-->

<!--pan_doc:

$Q_1$ is diode connected, so its collector sits one $V_{BE}$ above ground.
$Q_3$ holds its own base, which is the collector of $Q_2$, one $V_{BE}$ above
ground as well. Both $R_1$ and $R_2$ therefore have very nearly the same
voltage across them, and the current ratio falls out of the resistors alone.

-->

$$ \frac{I_1}{I_2} = \frac{R_2}{R_1} $$

<!--pan_doc:

$Q_1$ and $Q_2$ are the same size and share a base, so that difference in
current density lands across $R_3$

$$ I_2 R_3 = V_{BE1} - V_{BE2} = \frac{kT}{q}\ln{\frac{I_1}{I_2}} = \frac{kT}{q}\ln{\frac{R_2}{R_1}} $$

which is PTAT, and depends only on a resistor ratio, so it is as accurate as
your matching. That current runs up through $R_2$, and the output is that drop
stacked on top of the $V_{BE}$ of $Q_3$.

-->

$$ V_{REF} = V_{BE3} + \frac{R_2}{R_3}\frac{kT}{q}\ln{\frac{R_2}{R_1}} $$

<!--pan_doc:

CTAT plus PTAT, and we are about to do it again with an amplifier. With
$R_2/R_1 = 10$ the log term is about 60 mV at room temperature, $R_2/R_3 = 10$
scales that to 600 mV, and stacked on a 600 mV $V_{BE}$ you land at the 1.22 V
the LM113 was sold as.

Notice what is doing the job of the OTA. $Q_3$ is the gain element. If the
terminal tries to rise, the collector of $Q_2$ follows it up, $Q_3$ conducts
harder, and shunts the extra current away. The loop closes through a single
transistor. That is why the circuit fits in a process where you count your
transistors, and it is also why it has less loop gain, and therefore worse line
regulation, than the amplifier based cells that came after it. Widlar was not
short of ideas, he was short of devices.

One more thing worth taking from this circuit is where the current density
ratio comes from. Here it is $R_2/R_1$, a ratio of resistors. In the Brokaw
cell it is an emitter area ratio instead. Both work, and both are asking a
ratio of like things to be accurate, which is the only kind of accuracy an
integrated circuit actually has.

-->

---

<!--pan_doc:

## Brokaw reference 

Paul Brokaw was a pioneer within reference circuits 
( I met him once in the restroom queue in Tropisueno behind the Marriot hotel in SF during ISSCC). 
Below is the Brokaw reference, 
which I think was first published in 
[A simple three-terminal IC bandgap reference](https://ieeexplore.ieee.org/document/1050532).

-->

![left fit](../media/l3_brokaw_tikz.pdf)

<!--pan_doc:

<sub>Figure 10: Brokaw bandgap voltage reference  </sub>
-->

<!--pan_doc:

The opamp ensures the two bipolars have the same current. $Q_1$ is larger than $Q_2$. 
The $\Delta V_{BE}$ is across the $R_2$, so we know the current $I$. We know that $R_1$ must then have $2I$. 

The voltage at the output will then be.

-->

$$ V_{BG} = V_{G0} + (m-1)\frac{kT}{q}\ln{\frac{T_0}{T}} +T\left[\frac{k}{q}\ln{\frac{J_2}{J_1}}\frac{2R2}{R1} - \frac{V_{G0}- V_{be0}}{T_0}\right] $$

<!--pan_doc:

where $V_{G0}$ is the bandgap, $V_{be0}$ is the base emitter measured at a temperature $T_0$ and the $J$'s are the current densities.

To get a constant output voltage, the relationship between the resistors should be approximately

$$ \frac{R2}{R1} = \frac{V_{G0} - V_{be0}}{2 T_0 \frac{k}{q}\ln(\frac{J_2}{J_1})} $$

-->


---

<!--pan_doc:

In typical simulations, the variation can be  
low over the temperature range. The second order error is the remaining error from

$$ V_{BG} = V_{G0} + (m-1)\frac{kT}{q}\ln{\frac{T_0}{T}} +T\left[\frac{k}{q}\ln{\frac{J_2}{J_1}}\frac{2R2}{R1} - \frac{V_{G0}- V_{be0}}{T_0}\right] $$

Where the last term is zero, so 

$$ V_{BG} = V_{G0} + (m-1)\frac{kT}{q}\ln{\frac{T_0}{T}} $$

-->

![original](../media/l3_bgsim.pdf)

<!--pan_doc:

<sub>Figure 11: Simulation of a Brokaw reference in GF 130 nm.  </sub>
-->


---

<!--pan_doc: 

Over corners, I do expect that there is variation, as we can see from Figure 12. It may be that the $V_D$ modeling is not perfect, 
which means the cancellation of the last term is incomplete. 

We could include trimming of PTAT to calibrate for the remaining error, however, if we 
wanted to remove the linear gradient, we would need a two point temperature test of every
IC, which too expensive for low-cost devices.

-->

![original](../media/l3_bgsimtfs.pdf)

<!--pan_doc:
<sub>Figure 12: Typical, Slow, Fast simulation of the Brokaw bandgap </sub>
-->


---

##[fit] Low voltage bandgap

---

<!--pan_doc: 

The Brokaw reference, and others, have a 1.2 V output voltage, which is hard to make if your
supply is below about 1.4 V. 
As such, people have investigated lower voltage references. The original circuit 
was presented by Banba [A CMOS bandgap reference circuit with sub-1-V operation](https://ieeexplore.ieee.org/document/760378)

In real ICs though, you should ask yourself long and hard whether you 
really need these low-voltage references. 
Most ICs today still have a high voltage, either 1.8 V or 3.0 V. 

If you do need them, consider the circuit in Figure 13. We have two diodes at different current densities.
The $\Delta V_D$ will be across $R_1$. The voltage at the input of the OTA will be $V_D$ 
and the OTA will ensure the both inputs are equal. 

The current will then be 

$$ I_1 = \frac{\Delta V_{D}}{R_1}$$

and we know the current increases with temperature, since $\Delta V_D$ increases with temperature.



-->

![left fit](../media/l3_ptat_tikz.pdf)

<!--pan_doc:

<sub>Figure 13: PTAT current generator </sub>
-->

---



<!--pan_doc: 

I use $\Delta V_{BE}$ and $\Delta V_D$ interchangeably, appologies. 

In Figure 14 we copy the $V_D$ to another node, and place it across a second resistor $R_2$.

The current in this second resistor is then 

$$ I_2 = \frac{V_D}{R_2}$$

and we know the current decreases with temperature, since $V_D$ decreases with temperature.

From before, we know the current in $R_1$ is proportional to temperature. As such, 
if we combine the two current with the correct proportions, 
then we can get a current that does not change with temperature.

-->


![right fit](../media/l3_ptat1_tikz.pdf)

<!--pan_doc:

<sub>Figure 14: Extending the PTAT current generator </sub>
-->


---

<!--pan_doc:

Let's remove the OTA, and connect $R_2$ directly to $V_D$ nodes, as shown in Figure 15. 

You should convince yourself 
of the fact that this does not change $I_1$. 

-->

![right fit](../media/l3_ptat2_tikz.pdf)

<!--pan_doc:

<sub>Figure 15: The Banba bandgap voltage reference core </sub>
-->

<!--pan_doc:

It does, however, change the current in the PMOS.
Provided we scale $R_2$ correctly, then the PTAT $I_1$ can compensate for CTAT $I_2$, 
and we have a current that is independent of temperature. 

-->

$$ I_{PMOS} = \frac{V_D}{R_2} + \frac{\Delta V_D}{R_1}$$

---

<!--pan_doc:

Assuming we copy the current into another resistor $R_3$, as shown in Figure 16, we can get a voltage that is 

$$ V_{OUT} = R_3\left[\frac{V_D}{R_2} + \frac{\Delta V_D}{R_1}\right]$$

We can choose the output voltage freely, and it be lower than 1.2 V.

-->

![original fit](../media/l3_ptat3_tikz.pdf)

<!--pan_doc:
<sub>Figure 16: The Banba bandgap voltage reference </sub>
-->


---

##[fit] Curvature correction

---

<!--pan_doc:

Go back and look at Figure 12 again. Over corners the reference is not flat,
and even the typical curve in Figure 11 has a bend in it. That bend is not
noise, and it is not a mistake in the design. It is a term we agreed to ignore,
and it is time to stop ignoring it.

We picked the resistor ratio so the bracket that multiplies $T$ is zero, which
removes everything linear in temperature. It does nothing at all to what is
left,

-->

$$ V_{BG} = V_{G0} + (m-1)\frac{kT}{q}\ln{\frac{T_0}{T}} $$

<!--pan_doc:

and that is the bow you can see in Figure 12. It comes from the temperature
dependence of $I_S$, the $-3\ln{T}$ we carried through the $V_{BE}$ algebra
earlier, so $m \approx 3$ and the coefficient is about 2.

No choice of $R_2/R_1$ can remove it. A resistor ratio can only add something
proportional to $T$, and what is left over is proportional to $T\ln{T}$. If we
want to cancel it, we have to build a $T\ln{T}$ term.

-->

---

<!--pan_doc:

Here is where one comes from. Take two identical bipolars at the same
temperature. The difference of their base-emitter voltages is

-->

$$ V_{BE,A} - V_{BE,B} = \frac{kT}{q}\ln{\frac{I_A}{I_B}} $$

<!--pan_doc:

and this one is exact, not an approximation. $I_S$ cancels completely, because
it is the same device at the same temperature.

This is the same $\Delta V_{BE}$ we have used all chapter, and every time so
far the current ratio has been a fixed number set by device sizes. That is what
made it PTAT. So make the ratio depend on temperature instead: bias $Q_A$ with
a PTAT current, and $Q_B$ with the temperature compensated current the
reference already produces. Then $I_A/I_B = K T/T_0$ and

-->

$$ V_{BE,A} - V_{BE,B} = \frac{kT}{q}\ln{K} + \frac{kT}{q}\ln{\frac{T}{T_0}} $$

<!--pan_doc:

The first term is PTAT, and we know what to do with those. The second term is
the $T\ln{T}$ we needed, and it comes with the right sign.

-->

---

<!--pan_doc:

Figure 17 turns that voltage into a current. The OTA holds the right hand end
of $R_4$ at $V_{BE,A}$, the left hand end sits on $V_{BE,B}$, and $M_{PC}$
supplies whatever current that requires. $M_{PD}$ copies it into the summing
node from Figure 16, so the $V_{OUT}$ of that circuit becomes

-->

![fit](../media/l3_curv_tikz.pdf)

<!--pan_doc:

<sub>Figure 17: Curvature correction. $Q_A$ and $Q_B$ are the same device at
different bias currents, so the voltage across $R_4$ carries a $T\ln{T}$ term.
</sub>
-->

$$ I_{NL} = \frac{V_{BE,A} - V_{BE,B}}{R_4} = \frac{kT}{qR_4}\left[\ln{K} + \ln{\frac{T}{T_0}}\right] $$

$$ V_{REF} = R_3\left[\frac{V_D}{R_2} + \frac{\Delta V_D}{R_1} + I_{NL}\right] $$

---

<!--pan_doc:

The curvature the $V_D$ term brings in is
$\frac{R_3}{R_2}(m-1)\frac{kT}{q}\ln{\frac{T_0}{T}}$, the curvature the new
branch adds is $\frac{R_3}{R_4}\frac{kT}{q}\ln{\frac{T}{T_0}}$, and they cancel
when

-->

$$ R_4 = \frac{R_2}{m-1} $$

<!--pan_doc:

which is a nice result. The correction is set by a resistor ratio, like
everything else in this chapter, and with $m \approx 3$ it makes $R_4$ about
half of $R_2$. The $\frac{kT}{q}\ln{K}$ half of $I_{NL}$ is PTAT, so it simply
adds to the PTAT current already there, and you retrim $R_1$ to take it back
out.

Three things to watch.

$I_{NL}$ leaves $R_4$ and flows into the emitter of $Q_B$, so $Q_B$ does not
carry exactly $I_{REF}$. It is a small perturbation, but it is real, and it
makes the sizing slightly iterative.

$V_{BE,A}$ has to stay above $V_{BE,B}$ across the whole temperature range, or
the current in $R_4$ reverses and the loop runs out of room. The ratio is
$K T/T_0$, so pick $K$ large enough that it is still comfortably above one at
the cold end.

And $m$ is not a number the foundry hands you to three digits. Curvature
correction typically buys a factor of five to ten in temperature drift, not a
factor of a thousand, and what it buys is limited by how well you know $m$. It
is worth the area when you need 10 ppm/$^\circ$C. It is a waste of area when
50 ppm/$^\circ$C is fine, which it usually is.

-->

---

##[fit] MOS references

<sub><sub> Recognise this one. Do not build it. </sub></sub>

---

<!--pan_doc:

Everything so far has needed a bipolar. In a pure CMOS process that is
irritating, and the temptation is obvious. The MOS transistor has a threshold
voltage, thresholds fall with temperature at roughly $-1$ mV/K, and if two
devices have different thresholds then the difference between them ought to be
flat. A reference with no bipolar in it.

If you read older books you will find this done with an enhancement device and
a depletion device. Forget that circuit. It relied on a threshold below zero,
so that a device with its gate tied to its own source still conducted, and in a
nanoscale CMOS process there is no such device. Essentially everything on the
menu sits at 300 mV or more. What you get instead is a handful of implant
flavours, standard, low $V_t$ and high $V_t$, separated by a hundred millivolts
or so, plus the native device, which skips the channel implant altogether and
is the only one that lands anywhere near zero.

So the modern version of the idea pairs two of those flavours, and it looks
like Figure 18.

You have seen this loop before, or rather you are about to see it: it is the GM
cell from later in this chapter, with the size ratio taken out and a second
implant put in its place. The PMOS mirror forces the same current down both
branches, $M_1$ and $M_2$ have the same $W/L$, and the only thing left that
distinguishes them is which channel implant they were given.

Both gates sit on the same node, so $V_{GS1} = V_{GS2} + I R$, and writing each
gate-source voltage as a threshold plus an overdrive

-->

![left fit](../media/l3_mosref_tikz.pdf)

<!--pan_doc:

<sub>Figure 18: A reference built on the difference between two threshold
voltages. Learn to recognise it. Do not build it. </sub>
-->

$$ I R = (V_{t1} + V_{eff1}) - (V_{t2} + V_{eff2}) $$

<!--pan_doc:

Equal current in equal $W/L$ means equal overdrive, so the $V_{eff}$ terms
cancel and what is left is the entire reference

-->

$$ I = \frac{V_{t1} - V_{t2}}{R} = \frac{\Delta V_t}{R} $$

---

**MOS based references that rely on the difference between two threshold
voltages are very risky and should not be attempted.**

<!--pan_doc:

I want you to leave this slide able to recognise that circuit, and unwilling to
build it. Process control over the two threshold sources is poor, and their
stability is poor, so the difference is neither well controlled nor stable.

Put Figure 18 next to Figure 20 and the problem is visible in one look. They
are the same loop. The GM cell puts a 4:1 size ratio in it, and a size ratio is
lithography, two drawings of the same thing, which is about as well controlled
as anything on a die gets. This circuit puts the difference of two channel
implants in the same place. Those are two separate recipes, aimed separately,
monitored separately, and drifting separately. Nothing makes them move
together.

Watch what the numbers do. Take standard against low $V_t$: two devices at
maybe 450 mV and 350 mV, each with a spread of $\pm 50$ mV over process. Each
threshold on its own is known to about $\pm 12$ %. The difference you actually
use is 100 mV, and if the two spreads are independent it is known to about
$\pm 70$ %. If they happen to move in opposite directions it is worse than
that, and nothing in the process says they will not. Subtracting two similar,
poorly known numbers is the worst thing you can do to an error budget.

-->

---

## The native threshold is set when the ingot is grown

<!--pan_doc:

Reach for the native device to get a bigger difference and you have picked the
least controlled transistor in the process. Its threshold is whatever is left
when you leave the channel implant out, which means it rides on the doping of
the silicon underneath it, and that is not a number the fab sets.

Think about where it does get set. Not in an implanter, where the dose is
metered to about a percent and measured on every lot. It is fixed when the
ingot is grown, by how much boron went into the melt before the crystal was
pulled out of it, and the boule is usually not even grown by the company that
builds your chip. You buy wafers, and what you buy is a resistivity range, not
a resistivity.

It is worse than a range. Boron has a segregation coefficient below one, so it
would rather stay in the melt than join the crystal. As the boule is pulled the
melt gets steadily richer, and the silicon that freezes out near the tail end
is more heavily doped than the silicon at the seed end, by tens of percent over
the length of one crystal. Wafers sliced from the two ends of the same boule
are not the same wafer. There is a radial gradient across each wafer on top of
that, and well proximity and STI stress move it again locally.

None of this is visible to the fab's process control, which watches implants
and etches, and none of it is correctable there either. So one end of your
subtraction is set by an implanter recipe inside the fab, and the other end is
set by a crystal grower at a different company, to a different specification,
probably on a different continent. Those two numbers have no reason on earth to
move together. In most PDKs the native device duly comes with the widest
corners and the thinnest model guarantees of anything on the menu.

If the process runs on epitaxial wafers the native device sees the epi layer
rather than the bulk, and epi doping is better controlled than a pulled
crystal. It is still a deposition specification rather than a metered implant,
and it is still usually somebody else's specification.

Compare that with what a bandgap does. A bandgap gets its number from $E_g$ of
silicon. That is a property of the material, it is the same in every fab on
earth, and no process engineer can move it. This circuit gets its number from
the difference between an implant recipe and a crystal pull.

Stability is the other half, and trimming does not save you. You can trim out
the initial spread in production test, once. Then the thresholds move over the
life of the part. NBTI and hot carrier stress shift them, and they shift by
different amounts, because the two devices see different fields, different bias
and different channel doping. Nothing anchors the difference, so it walks.

The derivation has a hole in it as well. It assumed the two devices are
identical apart from $V_t$, which is the only reason the overdrives cancelled.
They are not. The implant that moves the threshold also moves the mobility, the
body effect coefficient and the subthreshold slope, so $V_{eff1}$ and
$V_{eff2}$ do not quite cancel, and what is left over has its own temperature
dependence. On top of that $M_2$ has its source $\Delta V_t$ above ground while
its bulk is at ground, so the body effect raises $V_{t2}$ by an amount that
depends on the answer.

If you need a reference in a pure CMOS process, use the parasitic vertical PNP
that every CMOS process has, in the circuits from earlier in this chapter. If
what you actually need is a bias current rather than a reference, use the GM
cell a few slides from here. Neither of those asks two implants to agree with
each other.

-->

---



#[fit] Bias

<sub><sub> Sometimes we just need a current </sub></sub>

---

## Voltage to current conversion

<!--pan_doc: 

With a known voltage, we can convert to a known current with the circuit in Figure 19. 

On-chip we don't have accurate resistors, 
but for bias currents, it's usually ok with $+- 20 %$ variation  (the variation of R). 

Across a IC, we can expect the resistors to match within 2 % percent, as such, we can recreate a 
voltage with a accuracy of about 2 %percent difference from the original if we have a 
second resistor on the other side of the IC.

If we wanted to create an accurate current, then we'd trim the R in production test 
until the current is what we want. 

-->

![inline 200%](../media/l3_vi_tikz.pdf)


<!--pan_doc:
<sub>Figure 19: Voltage to current converter</sub>
-->

---


## GM Cell




<!--pan_doc: 

Sometimes we don't need a full bandgap reference. In those cases, 
we can use a GM cell, as shown in Figure 20. 

-->

![left fit](../media/l3_gmcell_tikz.pdf)

<!--pan_doc:

<sub>Figure 20: GM cell. </sub>

The top PMOS current mirror ensures that both branches have the same current. The middle NMOS current mirror copies
the drain voltage on top of the diode connected bottom NMOS to the left NMOS.
Consider the bottom transitors, those marked with "1" and "4".  The $V_o$ voltage is

-->


$$ V_o = V_{GS1}  - V_{GS2}  = V_{eff1} + V_{tn} - V_{eff2} - V_{tn} = V_{eff1} - V_{eff2}$$

<!--pan_doc:

Assuming transistors in strong inversion, then 

$$ I_{D1} = \frac{1}{2} \mu_n C_{ox} \frac{W_1}{L_1} V_{eff1}^2 $$ 

$$ I_{D2} = \frac{1}{2} \mu_n C_{ox} 4 \frac{W_1}{L_1} V_{eff2}^2 $$ 



$$ I_{D1} = I_{D2} $$

-->

$$ \frac{1}{2} \mu_n C_{ox} \frac{W_1}{L_1} V_{eff1}^2 = \frac{1}{2} \mu_n C_{ox} 4 \frac{W_1}{L_1} V_{eff2}^2 $$

$$ V_{eff1} = 2 V_{eff2} $$

<!--pan_doc:

Inserted into above


$$V_o = V_{eff1} - \frac{1}{2} V_{eff1} = \frac{1}{2}V_{eff1}$$


Still assuming transistors in strong inversion, such that

-->


$$ g_{m} = \frac{2 I_d}{V_{eff}} $$

<!--pan_doc:

we find that


-->

$$ I = \frac{ V_{eff1}}{2Z} $$



$$ Z \Rightarrow \frac{1}{g_m} $$

<!--pan_doc:

If we use a resistor for Z, then we can get a transconductance that is proportional to a resistor, or a constant $g_{m}$ bias.

We can use other things for Z, like  a switched capacitor

-->

---

![original fit](../media/l3_gmcap_tikz.pdf)

---



# Want to learn more?

[New developments in IC voltage regulators](https://ieeexplore.ieee.org/document/1050151)

[A simple three-terminal IC bandgap reference](https://ieeexplore.ieee.org/document/1050532)

[A CMOS bandgap reference circuit with sub-1-V operation](https://ieeexplore.ieee.org/document/760378)

[A sub-1-V 15-ppm//spl deg/C CMOS bandgap voltage reference without requiring low threshold voltage device](https://ieeexplore.ieee.org/document/991391)

[The Bandgap Reference](https://ieeexplore.ieee.org/document/7559954)

[The Design of a Low-Voltage Bandgap Reference](https://ieeexplore.ieee.org/document/9523469)

---


#[fit] Thanks!

---
