footer: Carsten Wulff 2026
slidenumbers:true
autoscale:true
theme: Plain Jane, 1
text:  Helvetica
header:  Helvetica
date: 2026-01-16


<!--pan_title: OTAs -->

<!--pan_doc:

**Keywords:** OTA, Headroom, Five Transistor, Current Mirror OTA, Two-Stage, Miller Compensation, Folded Cascode, Inverter-Based, Nauta, CMFB, Dynamic Amplifiers

-->

# OTAs

<!--pan_doc:

An operational transconductance amplifier (OTA) takes a differential
voltage in and pushes a current out. Load it with a capacitor and it
integrates; wrap feedback around it and it becomes whatever the feedback
network says - a switched capacitor integrator, a filter, an ADC residue
amplifier, a regulator error amplifier. Almost every analog system in this
book has an OTA somewhere inside it.

This chapter walks through the OTA topologies that still make sense in
nanoscale CMOS, where the supply is around 0.8 V. That last constraint is
the important one: half the classic topologies in the textbooks were
invented for 5 V, and do not survive the trip down.

-->

---

# The headroom budget

<!--pan_doc:

Start with the arithmetic that kills topologies. At $V_{DD}$ = 0.8 V, with
a threshold voltage around 0.4 V:

-->

$$ V_{DD} = 0.8 \text{ V}, V_{t} \approx 0.4\text{ V} $$

One gate-source voltage

 $$ V_{GS} \approx 0.5 \text{ V} $$

One saturated current source, one cascode

 $$ V_{DSAT} \approx 0.1 \text{ V each} $$

**Stack of two gate-source voltages? Dead.**

**Telescopic cascode with swing? Dead.**

<!--pan_doc:

A gate-source voltage plus a tail current source plus a load already sums
to about 0.7 V, so the five transistor OTA barely fits. Add a cascode on
both sides and the output can still move a little. Stack two gate-source
voltages - a telescopic cascode with wide swing, a folded mirror with
source degeneration - and there is nothing left.

The consequences run through the whole chapter: we get gain from long
transistors and from more stages, not from stacking; we bias at moderate
or weak inversion, where $V_{GS}$ is low and $g_m/I_D$ is high; and every
volt of output swing has to be argued for.

-->

---

# Five transistor OTA

<!--pan_doc:

The five transistor OTA in Figure 1 is the differential pair from the
circuits chapter with its loads folded into a current mirror: the mirror
takes the left branch current, flips it over, and slams it into the right
branch, so the full differential current reaches the single ended output.

-->

![left fit](../media/ota_5t_tikz.pdf)

<!--pan_doc:
<sub>Figure 1: Five transistor OTA</sub>
-->

$$ A = g_{m1} (r_{ds2} || r_{ds4}) $$

$$ \omega_{ugf} = \frac{g_{m1}}{C_L} $$

Output swing: $$V_{DD} - 2 V_{DSAT}$$

<!--pan_doc:

The gain is one intrinsic gain - 20 to 40 dB in a nanoscale process -
and the unity gain frequency is set by the input pair transconductance
over the load capacitance. The swing is generous: only a $V_{DSAT}$ lost
at each rail.

For a buffer, a modest filter, or a bias loop, this is the correct
answer, and reaching for anything fancier is vanity. When it is not
enough, it is for one of two reasons: not enough gain, or not enough
drive - and the two failures point to two different upgrades.

-->

---

# Current mirror OTA

<!--pan_doc:

If the problem is drive - a big load capacitor and a tail current that
cannot slew it - the current mirror OTA in Figure 2 helps. Both branch
currents are mirrored outwards with a gain $K$, and the output branch can
source and sink $K$ times the tail current.

-->

![left fit](../media/ota_cm_tikz.pdf)

<!--pan_doc:
<sub>Figure 2: Current mirror OTA with mirror ratio $K$</sub>
-->

$$ A = K g_{m1} (r_{ds6} || r_{ds8}) $$

$$ \omega_{ugf} = \frac{K g_{m1}}{C_L} $$

Slew rate: $$ \pm K I_{tail} / C_L$$

<!--pan_doc:

The price is the extra mirror pole - the diode connected loads and their
mirror partners add a pole at roughly $g_{m3}/C_{mirror}$, which eats
phase margin as $K$ grows - and the noise and offset of four more
transistors. $K$ of 2 to 5 is typical. All transistors sit one $V_{GS}$
or one $V_{DSAT}$ from a rail, so the topology is fully at home at
0.8 V, which is why it is everywhere in low voltage design.

-->

---

# Two stage (Miller) OTA

<!--pan_doc:

If the problem is gain, add a stage. The two stage OTA in Figure 3 puts a
common source stage after the five transistor OTA: two intrinsic gains
multiplied, and the output stage swings to within one $V_{DSAT}$ of each
rail - the best swing any OTA can offer, which matters when the supply is
0.8 V and every millivolt of signal range counts.

-->

![left fit](../media/ota_two_stage_tikz.pdf)

<!--pan_doc:
<sub>Figure 3: Two stage OTA with Miller compensation</sub>
-->

$$ A = g_{m1}(r_{ds2}||r_{ds4}) \times g_{m6}(r_{ds6}||r_{ds7}) $$

$$ \omega_{ugf} = \frac{g_{m1}}{C_c} $$

Pole splitting: dominant pole down, output pole out to $$\approx \frac{g_{m6}}{C_L}$$

<!--pan_doc:

Two stages means two poles, and two poles in a feedback loop must be
pushed apart. That is the Miller capacitor $C_c$'s job: it is $C_{gd}$
multiplied by the second stage gain, on purpose - the Miller effect from
the MOSFET chapter, hired instead of feared. The input pole drops, the
output pole rises to about $g_{m6}/C_L$, and the amplifier crosses unity
at $g_{m1}/C_c$ with the second pole safely beyond.

The famous flaw: $C_c$ also feeds the input signal forward past the
second stage, creating a right half plane zero at $g_{m6}/C_c$ that
steals phase. The standard fix is a resistor in series with $C_c$, which
moves the zero to infinity - or on top of the second pole, if you are
feeling precise.

-->

---

# Folded cascode

<!--pan_doc:

When one stage must deliver more gain than a five transistor OTA - a
switched capacitor integrator that settles to 10 bits, say - the folded
cascode in Figure 4 buys a factor $g_m r_{ds}$ more. The input pair
current folds outwards into cascoded branches: cascodes multiply output
resistance, and folding means the input pair and the cascodes do not
stack on top of each other in the same headroom.

-->

![left fit](../media/ota_folded_tikz.pdf)

<!--pan_doc:
<sub>Figure 4: Folded cascode OTA</sub>
-->

$$ A \approx g_{m1} \left( g_{m8} r_{ds8} (r_{ds10}||r_{ds2}) \, || \, g_{m6} r_{ds6} r_{ds4} \right) $$

$$ \omega_{ugf} = \frac{g_{m1}}{C_L} $$

Output swing: $$ V_{DD} - 4 V_{DSAT} $$

<!--pan_doc:

At 0.8 V the folded cascode is possible, but on a diet: four $V_{DSAT}$
of about 0.1 V each leaves 0.4 V of output swing, and the bias voltages
$V_{B1}$ to $V_{B3}$ must be generated carefully (wide swing mirrors,
see CJM) or the diet fails. It is also the last stop: the
telescopic cascode, which stacks the input pair under the cascodes,
needs the swing and the input common mode to share headroom that is not
there at 0.8 V.

The load capacitor is the compensation - no Miller capacitor needed -
so for switched capacitor circuits, where the load is a known sampling
capacitor, this topology is the default single stage answer.

-->

---

# Inverter based OTAs

<!--pan_doc:

Every topology so far spends half its current on transistors that do not
amplify. The inverter, Figure 5, does not: the PMOS and NMOS share the
same current, both amplify the same input, and the transconductances add.

-->

![left fit](../media/ota_inv_tikz.pdf)

<!--pan_doc:
<sub>Figure 5: The inverter as a transconductor</sub>

The inverter gives $g_{mn} + g_{mp}$ for one branch current - twice the
transconductance per microampere of anything above, which at 0.8 V, in
weak inversion, is exactly the currency that matters. The catch: an
inverter has no tail current source, so its current and its common mode
are set by $V_{DD}$ and the process. It rejects nothing - supply noise
and corners go straight through.

-->

---

<!--pan_doc:

Nauta showed in 1992 how to make a real OTA out of nothing but inverters,
Figure 6 [@Nauta95]. Two inverters amplify differentially. On the outputs,
a cross coupled pair fights common mode motion and a shorted inverter on
each output loads it resistively - together they hold the output common
mode without a single tail source or CMFB loop, and the differential gain
survives.

-->

![fit](../media/ota_nauta_tikz.pdf)

<!--pan_doc:
<sub>Figure 6: Nauta's inverter based transconductor</sub>

Because every device is part of an inverter, the whole OTA works at any
supply where an inverter has gain - which in weak inversion means a few
hundred millivolts. Inverter based OTAs run the switched capacitor
filters and sigma-delta modulators of most sub-1V papers of the last
decade. The supply sensitivity does not disappear, though: it moves into
the bias, so the supply of an inverter based OTA is usually a regulated
one - see the voltage regulation chapter.

-->

---

# Bulk driven input

<!--pan_doc:

One more low voltage trick from the MOSFET chapter: the bulk is a second
gate with $g_s \approx 0.2 g_m$, and it works with the source at the
rail. Feed the signal into the bulk of a transistor whose $V_{GS}$ is
tied fully on, and the input common mode range covers the whole supply -
no input pair $V_{GS}$ in the headroom budget at all.

The cost is honest: five times less transconductance for the same
current, more input capacitance, and the forward bias diode from bulk to
source limits the drive. Bulk driven input stages show up where the
input common mode is hostile - rail to rail buffers, sensor interfaces -
not where noise or speed matter most.

-->

Bulk as signal input

 $$ g_{s} \approx (n-1) g_m \approx 0.2 g_m $$

Input common mode: rail to rail

Cost: five times less transconductance, and the bulk-source diode must stay off

---

# Fully differential

<!--pan_doc:

At 0.8 V, going fully differential is not a luxury, it is where the
missing swing went: differential output doubles the signal amplitude for
free, cancels even order distortion, and rejects the supply and substrate
noise that a single ended output adds to the signal. Figure 7 shows a
fully differential current mirror OTA.

-->

![fit](../media/l04_ota_diff_tikz.pdf)

<!--pan_doc:
<sub>Figure 7: Fully differential current mirror OTA</sub>

The price of removing the diode connected definition of the output: the
output common mode is no longer defined by the circuit itself. Both
outputs can drift towards a rail together, and the differential loop
cannot see it. Every fully differential OTA therefore carries a common
mode feedback (CMFB) loop.

-->

---

## Common mode feedback

<!--pan_doc:

The CMFB loop in Figure 8 senses the average of the two outputs, compares
it against a reference - usually mid supply - and trims a bias current in
the OTA until the average sits where it should. The loop must be stable
on its own, and fast enough to catch common mode disturbances, which in
switched capacitor circuits usually means a switched capacitor CMFB
sensing network.

-->

![fit](../media/l04_ota_vcmfb_tikz.pdf)

<!--pan_doc:
<sub>Figure 8: A common mode feedback amplifier</sub>
-->

---

# Dynamic amplifiers

<!--pan_doc:

The newest branch of the family tree throws away the bias current
entirely. A dynamic amplifier integrates its input onto a capacitor for
a clocked instant and then stops: the "gain" is $g_m T / C$, the power
is $C V^2 f$, and between samples the amplifier burns nothing. Ring
amplifiers do the same with an inverter chain that slams the output and
then dead-bands itself into a precision settle.

They only work in sampled systems - a SAR or pipeline ADC stage, a
discrete time filter - but there they have taken over: an amplifier that
only exists while it is needed is the logical endpoint of the headroom
and power budget this chapter started with.

-->

Dynamic gain

 $$ A \approx \frac{g_m T}{C} $$

Power

 $$ P \propto C V_{DD}^2 f_s $$

Only in sampled systems, and everywhere in modern ADCs

---

# Choosing

| Topology | Gain | Swing | Best at |
| :--: | :--: | :--: | :--: |
| Five transistor | $$g_m r_{ds}$$ | good | buffers, bias loops |
| Current mirror | $$K g_m r_{ds}$$ | good | drive, SC circuits |
| Two stage Miller | $$(g_m r_{ds})^2$$ | best | gain + swing |
| Folded cascode | $$g_m (g_m r_{ds}^2)$$ | poor | SC settling |
| Inverter based | $$g_m r_{ds}$$ | good | sub-1V, low power |
| Dynamic | $$g_m T/C$$ | - | ADCs |

<!--pan_doc:

Read the table bottom up: at 0.8 V the pressure is towards the bottom
rows. Start with the five transistor OTA, and move only when a
measured, simulated shortfall - gain, swing, drive, power - pushes you
to a specific neighbor.

-->

---

## Summary

<!--pan_doc:

The one-page version of this chapter:

-->

- At 0.8 V: never stack two gate-source voltages, and count every saturation voltage
- Five transistor OTA first; upgrade only for a reason
- Need drive: current mirror OTA. Need gain: two stage. Need one-stage gain: folded cascode
- Miller compensation splits the poles; the unity gain frequency is gm over Cc; mind the RHP zero
- Inverters amplify: both transconductances for one branch current, and Nauta's OTA needs no tail
- Fully differential doubles swing but must pay the CMFB tax
- In sampled systems, dynamic amplifiers win the power argument

---
