footer: Carsten Wulff 2021
slidenumbers:true
autoscale:true
theme: Plain Jane, 1
text:  Helvetica
header:  Helvetica
date: 2025-01-08

<!--pan_skip: -->

#[fit] Passives

---

<!--pan_title: Integrated Passives -->


# Metal in ICs is not wire in schematic

Resistance ~ m$$\Omega$$/$$\square$$

Capacitance ~ aF/$$\mu$$m to fF/$$\mu$$m

Inductance ~ nH/mm

Max current ~ mA/$$\square$$

<!--pan_skip: -->

![right fit](https://www.researchgate.net/publication/329551868/figure/fig1/AS:702470942629891@1544493532703/General-structure-of-an-IC-with-BEOL-evidenced-a-SEM-section-of-an-Intel-Broadwell.jpg)

---

| Layout | Must simulate/know |
|:--: | :--: |
| All | C Imax |
| Analog, Power | R C Imax |
| Some RF, Some Power | R L C Imax |

---

[.column]

 Layout parasitic extraction
 [Calibre xRC](https://eda.sw.siemens.com/en-US/ic/calibre-design/circuit-verification/xrc/)
 [Synopsys StarRC](https://eda.sw.siemens.com/en-US/ic/calibre-design/circuit-verification/xrc/)
 [Cadence
 Quantus](https://eda.sw.siemens.com/en-US/ic/calibre-design/circuit-verification/xrc/)
 [Magic VLSI](http://opencircuitdesign.com/magic/)
 
[.column]

 3D EM Simulators
 [Keysight ADS](https://www.keysight.com/zz/en/products/software/pathwave-design-software/pathwave-advanced-design-system.html)
 [HFSS](https://www.keysight.com/zz/en/products/software/pathwave-design-software/pathwave-advanced-design-system.html)

 Transistor CAD (TCAD)
 [Synopsys TCAD](https://www.synopsys.com/silicon/tcad.html)

---

#[fit] Resistors

---

# Polysilicon

Can be both N-doped, and P-doped

Often with two flavors, with, and without silicide 

Silicide reduces resistance of polysilicon

![right](../media/l6/poly.pdf)

---

# Diffusion

Use doped region as resistor

Usually without silicide

Non-linear capacitance

Tricky temperature dependence


![right fit](../media/l6/ndiff.pdf)

---

# Metal

Usually too low omhic to be a useful resistor

Useful for "separating nets" in schematic and layout

Must be considered for power supply and ground routing (high currents)


![right fit](../media/l6/metal.pdf)

---

#[fit] Capacitors

---
# What is S, M, L, XL on a chip?

[nRF52832](https://www.nordicsemi.com/products/nrf52832) $$ 3200 \mu m \times 3000 \mu m = 9600 k \mu m^2$$ 

S $$ < 5 \text{ } k\mu m^2$$
M $$ < 50 \text{ } k\mu m^2$$
L $$ < 200 \text{ } k\mu m^2$$
XL $$ > 200 \text{ } k\mu m^2$$

---

# Metal-Oxide-Metal finger capacitors

Unit capacitance $$ \approx 1 fF/\mu m^2/layer $$

 $$ 10 pF = 100 \mu m \times 100 \mu m = 10 k \mu m^2$$

![right fit](../media/l6/fig_capacitors_vertical.pdf)

---

# MOS capacitors

![right fit](../media/inversion.pdf)

---

[.column]

dicex/sim/spice/NCHIO/vcap.cir

```
* gate cap

.include ../../../models/ptm_130.spi

vdrain D 0 dc 1
vgaini G 0 dc 0.5
vbulk B 0 dc 0
vcur S 0 dc 0

M1 D G S B nmos  w=1u  l=1u

.op
```

Moscap $$ \approx 10 fF / \mu m^2 $$

 $$ 10 pF = 31 \mu m \times 31 \mu m \approx 1 k \mu m^2$$

[.column]

dicex/sim/spice/NCHIO/vcap.vlog

```
Device m1:
	Vgs     (gate-source voltage)        [V] : 0.5
	Vgd     (gate-drain voltage)         [V] : -0.5
	Vds     (drain-source voltage)       [V] : 1
	Vbs     (bulk-source voltage)        [V] : 1.90808e-12
	Vbd     (bulk-drain voltage)         [V] : -1
	Id      (drain current)              [A] : 7.32634e-06
	Is      (source current)             [A] : -7.32633e-06
	Ibd     (bulk-drain current)         [A] : -1.01e-12
	Ibs     (bulk-source current)        [A] : 9.581e-25
	Vt      (threshold voltage)          [V] : 0.378198
	Vgt     (gate overdrive voltage)     [V] : 0.121802
	Vgsteff (effective vgt)              [V] : 0.12515
	Gm      (transconductance)           [S] : 8.44164e-05
	Gmb     (bulk bias transconductance) [S] : 2.00071e-05
	Ueff    (mobility)             [cm^2/Vs] : 417.675
	Gds     (channel conductance)        [S] : 1.95043e-07
	Rds     (output resistance)        [Ohm] : 5.12708e+06
	Vdsat   (drain saturation voltage)   [V] : 0.14171
	IC      (inversion coefficient)       [] : 4.42478
	Cgs     (gate-source capacitance)    [F] : 9.98457e-15
	Csg     (source-gate capacitance)    [F] : 5.86932e-15
	Cgd     (gate-drain capacitance)     [F] : 3.98239e-16
	Cdg     (drain-gate capacitance)     [F] : 3.91086e-15
	Cds     (drain-source capacitance)   [F] : 4.30968e-15
	Cgg     (gate-gate capacitance)      [F] : 1.05198e-14
	Cdd     (drain-drain capacitance)    [F] : 1.05198e-14
	Css     (source-source capacitance)  [F] : 0
	Cgb     (gate-bulk capacitance)      [F] : 1.05198e-14
	Cbg     (bulk-gate capacitance)      [F] : 1.74123e-15
	Cbs     (bulk-source capacitance)    [F] : 8e-16
	Cbd     (bulk-drain capacitance)     [F] : 3.97768e-16
```


---

#[fit] Varactors (voltage dependent capacitor)


---

![original fit](../media/l6/pn.pdf)

---

#[fit] Inductors

Usually two top metals, because they are thick (low ohmic)

Use foundry model

3D electro magnetic simulation often needed

![right 200%](https://s.zeptobars.com/nRF51822.jpg) 

---

# Variation in passives

Absolute value for resistors and capacitors $$ \approx \pm 10 $$ % to $$ \pm 20 $$ %

Relative precision for closely spaced devices $$ \approx $$ 0.1 % to  1 % 

Relative precision for devices on same die $$ > 2 $$% or more 

---

# Relative precision

Resistors and Capacitors can be matched extremely well

![right fit ](../media/l6/pres_good.pdf)



---

[.column]

![inline 50% ](../media/l6/pres_bad.pdf)

 $$ i_3 = 0  = i_1 - i_2$$ 
 $$ 0 = \frac{V_i - V_o}{R} - \frac{V_o}{1/sC} $$  
 $$ 0 = V_i - V_o - V_o s R C $$ 
 $$ V_o (1 + sRC) = V_i $$ 
 
[.column]
 
 $$ \frac{V_o}{V_i} = \frac{1}{1 + sRC} $$

 
 Assume standard deviation ($$\sigma$$)[^1] of
 
 $$ \sigma_R = 20$$%, $$ \sigma_C = 20$$%   
 
 $$ \sigma_{RC} = \sqrt{0.2^2 + 0.2^2} = 28$$%
 

[^1]: If you don't remember how standard deviation works, read [Introduction to mathematics of noise sources](http://www.wulff.no/publications/noise.pdf)

---

# Diodes

Many, many ways

Reverse bias diodes to ground are useful for signals with long routing to transistor gate. Protects gate from breakdown during chemical mechanical polish.

![right fit](../media/l6/diodes.pdf)

---




#[fit] Thanks!




