footer: Carsten Wulff 2026
slidenumbers:true
autoscale:true
theme: Plain Jane, 1
text:  Helvetica
header:  Helvetica
date: 2026-02-06

<!--pan_title: Digital to analog conversion-->

<!--pan_doc 

**Keywords:**


-->

<!--pan_skip: -->



#[fit] Digital to Analog Conversion



---

<!--pan_doc: 

<iframe width="560" height="315" src="https://www.youtube.com/embed/tt12PDahC0Q?si=FAl1f51OmRpZPgxY" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Processing of signals has shifted into the digital domain. But the real world is
analog. In order to interact with the analog we need to convert the digital
signals (discrete-value, discrete-time) back to analog signals (continuous
value, continuous time).

The SI base units define the fundamental analog quantities as second, meter, kilogram,
ampere, kelvin, mole and candela (</aic2026/a_refresher>). Assume that
electronic circuits interact with the real world in terms of second and ampere.

Related to Ampere we have the derived units of charge (Ampere Seconds), Volt
(W/A), Ohm (V/A), or indeed Simens (1/$\Omega$). 

-->

<!--![left](https://www.nist.gov/sites/default/files/images/2021/08/23/NIST.SP_.1247.png)-->
![left fit](../media/NIST.SP_.1247.png)

<!--pan_doc:
<sub>Figure 1: NIST poster of the SI base units and the derived units</sub>
-->


<!--pan_doc:


As such, to create a digital to analog converter, we somehow have to create a
circuit that has a function of 

-->

 $$ I_{out} = D_{in} \times I_{ref}\text{ [I]} $$
 
 $$ t_{out} = D_{in} \times t_{ref}\text{ [s]} $$

 $$ Q_{out} = D_{in} \times Q_{ref}\text{ [C]} $$

 $$ V_{out} = D_{in} \times V_{ref}\text{ [V]} $$
 
 $$ R_{out} = D_{in} \times R_{ref}\text{ [}\Omega\text{]} $$
 
The digital value is dimensionless, as such, there must be a reference value

---

Digital to analog conversion can be indirect through the relations between voltage, resistance, current, time, inductance and capacitance. 

$$ V = R I $$

$$ Q = C V $$ 

$$ dt = \frac{C dV}{I} $$

$$ dt = \frac{L dI}{V} $$

--- 

#[fit] Resistor based DACs

---

![left fit](../media/dac_r_div_tikz.pdf)

<!--pan_doc:
<sub>Figure 2: 1-bit DAC: three series resistors with transistor switches selecting the output tap</sub>
-->



$$ I_{ref} = \frac{V_{ref}}{3 R}$$

$$ V_{out} = D_{in} R I_{ref} = \frac{D_{in} R V_{ref}}{3 R} \text{ [V]} $$


$$ V_{out} = \frac{b_0 2 R V_{ref}}{3 R}  + \frac{\overline{b_0} R V_{ref}}{3 R} $$

$$  V_{out} = \begin{cases} 
\frac{2}{3} V_{ref}, & b_0 = 1 \\
\frac{1}{3} V_{ref}, & b_0 = 0 
\end{cases}
$$


--- 

![left fit](../media/dac_r_div2_tikz.pdf)

<!--pan_doc:
<sub>Figure 3: 1-bit DAC with two resistors, selecting either $V_{REF}$ or the midpoint</sub>
-->


$$ I_{ref} = \frac{V_{ref}}{2 R}$$

$$ V_{out} = \frac{b_0 2 R V_{ref}}{2 R}  + \frac{\overline{b_0} R V_{ref}}{2 R} $$

$$  V_{out} = \begin{cases} 
 V_{ref}, & b_0 = 1 \\
\frac{1}{2} V_{ref}, & b_0 = 0 
\end{cases}
$$

---

![left fit](../media/dac_r_div2b_tikz.pdf)

<!--pan_doc:
<sub>Figure 4: Two possible 2-bit resistor string DACs with switch trees</sub>
-->


<!--pan_skip: -->

| b  | Vo/Vr | Vo/Vr |
|:---|:------|-------|
| 00 | 1/4   | 0/4   |
| 01 | 2/4   | 1/4   |
| 10 | 3/4   | 2/4   |
| 11 | 4/4   | 3/4   |

What is correct?

---

#[fit] DAC errors

---

Digital to analog converters do not add quantization error. The quantization error is already in the digital word.

$$ V_{out} = a_1^1 D_{in}^1 + B + \left( a_n^n D_{in}^n + ... a_2^2 D_{in}^2\right) $$

DAC output will contain gain errors, offset errors, and non-linear components

![left fit](../media/dac_error_tikz.pdf)

<!--pan_doc:
<sub>Figure 5: DAC output with gain error and non-linearity, and the resulting INL and DNL</sub>
-->


---


![left fit](../media/dac_inl_dnl_tikz.pdf)

<!--pan_doc:
<sub>Figure 6: DAC output compared to the ideal straight line, with INL and DNL versus digital code</sub>
-->



$$ DNL[k] = \frac{V[k+1] - V[k]}{V_{LSB}} - 1 $$

$$ INL[k] = \frac{V[k] - V_{ideal}[k]}{V_{LSB}} $$

--- 

#[fit] DAC complexity

---

![left fit](../media/dac_r_switches_tikz.pdf)

<!--pan_doc:
<sub>Figure 7: Binary switch tree for a resistor string DAC</sub>
-->


As number of resistors grow, the switches grow as 

$$ \sum_{n=1}^{N} 2^n = 2^{N+1} - 2 $$

--- 

![left fit](../media/dac_r_rows_tikz.pdf)

<!--pan_doc:
<sub>Figure 8: Row and column switch matrix for a resistor string DAC</sub>
-->


Use a matrix with R rows and C columns. Need R + C switches, or

$$ 2^{N} + 2^{N/2} $$

---

![left fit](../media/dac_r_segmented_tikz.pdf)

<!--pan_doc:
<sub>Figure 9: Segmented DAC switch arrangement combining switch matrices and a tree</sub>
-->


Switches in a 10-bit digital to analog converter.

$$
\begin{array}{ll}
\text{Tree: } &2^{N+1}-2 = 2046 \\
\text{Matrix : } &2^{N}  + 2^{N/2}  = 1056 \\ 
\text{6b Matrix + 4b Tree: } & 2^{M+1} - 2 + 2^{N} + 2^{N/2} = 80 
\end{array}
$$

Large number of bits, will be large number of resistors and switches. 

---

#[fit] Binary scaled DACs

---

$$ R_{in} = 2R || 2R = R $$

![left fit](../media/dac_2r_0_tikz.pdf)

<!--pan_doc:
<sub>Figure 10: R-2R ladder termination: two 2R resistors in parallel equal R</sub>
-->


---

$$ R_{in} = R + R = 2R $$

$$ I_{0} = \frac{V_0}{2R} = \frac{V_1}{4R} $$

![left fit](../media/dac_2r_1_tikz.pdf)

<!--pan_doc:
<sub>Figure 11: One R-2R ladder section: the series R makes the input resistance 2R</sub>
-->


---

$$ R_{in} = 2R || 2R = R $$

$$ I_{0} = \frac{V_0}{2R} = \frac{V_1}{4R} $$

$$ I_{1} = \frac{V_1}{2R}$$

![left fit](../media/dac_2r_2_tikz.pdf)

<!--pan_doc:
<sub>Figure 12: R-2R ladder section with the binary weighted branch currents $I_1$ and $I_0$</sub>
-->


---

$$ I_{RF} = I_1b_1 + I_0b_0 = \frac{V_{REF}}{2R}b_1 + \frac{V_{REF}}{4R}b_0 $$

$$ V_{O} = \left(\frac{V_{REF}}{2R}b_1 + \frac{V_{REF}}{4R}b_0\right)R_{F0}$$

![left fit](../media/dac_2r_full_tikz.pdf)

<!--pan_doc:
<sub>Figure 13: 2-bit R-2R DAC with switched branch currents summed by a transimpedance amplifier</sub>
-->


---

## Binary coding 

For 4 states (2-bit) there are 12 possible transitions

![left fit](../media/dac_bin_states_tikz.pdf)

<!--pan_doc:
<sub>Figure 14: The 12 possible transitions between the four 2-bit binary states</sub>
-->


---

Assume MSB first (left) 

$$ 1 \rightarrow 3 \rightarrow 2 $$

Assume LSB first (right) 

$$ 1 \rightarrow 0 \rightarrow 2 $$

Both cause a non-monotonic glitch during transition. 

![left fit](../media/dac_bin_btran_tikz.pdf)

<!--pan_doc:
<sub>Figure 15: Binary code transitions with MSB first (left) and LSB first (right), both non-monotonic</sub>
-->


--- 

## Thermometer encoding 


![left fit](../media/dac_thermo_states_tikz.pdf)

<!--pan_doc:
<sub>Figure 16: Transitions between the thermometer encoded states</sub>
-->


--- 

The sequence of MSB to LSB does not matter. 

$$ 0 \rightarrow 1 \rightarrow 2  \rightarrow 3$$



![left fit](../media/dac_thermo_tran_tikz.pdf)

<!--pan_doc:
<sub>Figure 17: Thermometer code transitions are monotonic regardless of bit order</sub>
-->

--- 


![right fit](../media/dac_r_thermo_tikz.pdf)

<!--pan_doc:
<sub>Figure 18: Thermometer coded resistor DAC with equal resistors summed by a transimpedance amplifier</sub>
-->


<!--pan_skip: -->

![left fit](../media/dac_thermo_tran_tikz.pdf)

--- 

#[fit] Current mode DACs

---

![fit](../media/dac_i_tikz.pdf)

<!--pan_doc:
<sub>Figure 19: Current mode DAC: binary sized differential current cells switched into a transimpedance output stage</sub>
-->



--- 

![fit](../media/dac_i_vbias_tikz.pdf)

<!--pan_doc:
<sub>Figure 20: Current mode DAC where the switch drive swings around $V_{bias}$ instead of rail to rail</sub>
-->


---

<!--pan_skip: -->

[.column]

$$ I_{out} = D_{in} \times I_{ref}\text{ [I]} $$

$$ V_{out} = D_{in} \times V_{ref}\text{ [V]} $$
 
$$ R_{out} = D_{in} \times R_{ref}\text{ [}\Omega\text{]} $$

<br>

$$ t_{out} = D_{in} \times t_{ref}\text{ [s]} $$

$$ Q_{out} = D_{in} \times Q_{ref}\text{ [C]} $$



[.column]

$$ V = R I $$

$$ Q = C V $$ 

$$ dt = \frac{C dV}{I} $$

$$ dt = \frac{L dI}{V} $$


<!--pan_doc: 

[@cjm11]
-->

---


# References



A 28-nm 75-fsrms Analog Fractional-N Sampling PLL With a Highly Linear DTC Incorporating Background DTC Gain Calibration and Reference Clock Duty Cycle Correction [@wu19]

A 10-bit Charge-Redistribution ADC Consuming 1.9 uW at 1 MS/s [@elzakker10]

A 6.3 uW 20 bit Incremental Zoom-ADC with 6 ppm INL and 1 uV Offset [@chae13]

A 12-Bit 1.25-GS/s DAC in 90 nm CMOS With >70 dB SFDR up to 500 MHz [@tseng11]
