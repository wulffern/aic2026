footer: Carsten Wulff 2021
slidenumbers:true
autoscale:true
theme: Plain Jane, 1
text:  Helvetica
header:  Helvetica
date: 2025-01-08

<!--pan_skip: -->


# Circuits

---

<!--pan_title: Circuits -->

## But I just want a digital input, what do I need?

---

![original fit](../media/l6/esd.pdf)

---

#[fit] Input buffer

![right fit](../media/l6/fig_methodology.pdf)

---

#[fit] Latch-up

Logic cells close to large NMOS pad drivers are prone to latch-up.

The latch-up process can start with electrons injected into the p-type substrate.

![right 200%](../media/fig_inv.pdf)

---

1. Electrons injected into substrate, diffuse around, but will be accelerated by n-well to p-substrate built in voltage. Can end up in n-well
2. PMOS drain can be forward biased by reduced n-well potential. Hole injection into n-well. Holes diffuse around, but will be accelerated by n-well to p-substrate built in voltage. Can end up in p-substrate under NMOS
3. NMOS source pn-junction can be forward biased. Electrons injected into p-substrate. Diffuse around, but will be accelerated by n-well to p-substrate built in voltage.
4. Go to 2 (latch-up)
   
![right fit](../media/l8/scr_eh.pdf)

---

![original fit](../media/l8/scr_model.pdf)

---

#[fit] Current Mirrors

---

![fit](../media/l8/fig_current_mirrors.pdf)

---

- $$r_{in}$$
- $$r_{out}$$
- $$\frac{i_{o}}{i_{i}}$$
- Source degeneration
- Cascode

![right 200%](../media/l8/fig_cm.pdf)

---
 $$r_{in}$$

![original fit](../media/l8/cm_in.pdf)

---
 $$r_{out}$$


![original fit](../media/l8/cm_out.pdf)

---
 $$\frac{i_{o}}{i_{i}}$$


![original fit](../media/l8/cm_tf.pdf)

---

## Source degeneration

![left fit](../media/l8/fig_cmsf.pdf)

What is the operating region of M3 and M4?

What is the operating region of M1 and M2?

---



M1 and M2 are in linear region, can be simplified to resistors

 $$r_{in} = \frac{1}{g_{m1}}+ R_s$$

![left fit](../media/l8/fig_cmRdeg.pdf)

---



![right fit](../media/l8/cm_sdeg.pdf)

$$v_{gs} = -v_{s}$$, $$v_{s} = i_x R_s$$, $$r_{out} = \frac{v_x}{i_x}$$

$$i_x = g_{m2} v_{gs} + \frac{v_x - v_s}{r_{ds2}}$$

$$i_x = -i_x g_{m2} R_s + \frac{v_x - i_x R_s}{r_{ds2}}$$

$$v_x = i_x\left[ r_{ds2} + R_s(g_{m2} r_{ds2} + 1)\right]$$ 

Rearranging

$$ r_{out} =  r_{ds2}[1 + R_s(g_{m1} + g_{ds2})] \approx r_{ds2} [1 + g_{m1}R_s]$$ 


---

# Cascode

From source degeneration (ignoring bulk effect)

$$r_{out} =  r_{ds4}[1 + R_s(g_{m4} + g_{ds4})] $$

$$ R_S = r_{ds2} $$


$$
r_{out} =  r_{ds4}[1 + r_{ds2}(g_{m4} + g_{ds4})] 
$$

$$
r_{out} \approx  r_{ds2}(r_{ds4}g_{m4})
$$

![right fit](../media/l8/fig_cmCascode.pdf)

---


# One more thing ....

---

![fit](../media/l8/cm_gain_boost.pdf)

---

#[fit] Amplifiers

---

#[fit] Source follower

---

Input resistance $$\approx \infty$$

Gain $$ A = \frac{v_o}{v_i}$$

Output resistance $$r_{out}$$

![left fit](../media/l9/sf_ls.png)

---


![right fit](../media/l9/sf_ss.png)

<!--pan_skip: -->

![left fit](../media/l9/sf_ls.png)

---

## Gain

$$ i_o = v_o (g_{ds} + g_{s}) - g_{m} v_i + v_o g_m $$

$$ i_o = 0 $$

$$ g_m v_i = v_o ( g_m + g_s + g_{ds} ) $$

$$ A = \frac{v_o}{v_i} = \frac{g_m}{g_m + g_{ds} + g_s} $$

**Gain is less than 1**

<!--pan_skip: -->
    
![right fit](../media/l9/sf_ss.png)

---

## $$r_{out}$$

$$ i_o = v_o (g_{ds} + g_{s}) - g_{m} v_i + v_o g_m $$

$$v_i = 0$$

$$ i_o = v_o (g_{ds} + g_{s} + g_m) $$

$$ r_{out} = \frac{v_o}{i_o} = \frac{1}{g_m + g_{ds} + g_{s}} $$


$$ r_{out} \approx \frac{1}{g_m}$$

![right fit](../media/l9/sf_ss.png)

---

## Why use a source follower?

Assume 100 electrons

[.column]


$$ \Delta V  = Q/C  = -1.6 \times 10^{-19} \times 100 / (1\times 10^{-15}) = - 16\text{ mV} $$ 

![inline fit](../media/l9/why_sf.png)

[.column]

$$ \Delta V  = Q/C  = -1.6 \times 10^{-19} \times 100 / (1\times 10^{-12}) = - 16\text{ uV} $$ 


![inline fit](../media/l9/why_sf_not.png)

---

#[fit] Common gate

---



Input resistance 

Gain 

Output resistance  

![left fit](../media/l9/cg_ls_rin.png)

---

![right fit](../media/l9/cg_ss_rin.png)

<!--pan_skip: -->

![left fit](../media/l9/cg_ls_rin.png)

---

## $$r_{in}$$

$$ i = g_m v + g_{ds} v $$

$$ r_{in} = \frac{1}{g_m + g_{ds}} \approx \frac{1}{g_m}$$

However, we've ignored load resistance. 

$$ r_{in}  \approx \frac{1}{g_m}\left(1 + \frac{R_L}{r_{ds}}\right) $$

<!--pan_skip: -->

![right fit](../media/l9/cg_ss_rin.png)

---

## $$r_{out}$$

![fit inline](../media/l9/cg_ss_rout.png)

---

## Gain


![right fit](../media/l9/cg_ss_a.png)

---


$$ i_{o} = - g_m v_{i} + \frac{v_{o} - v_{i}}{r_{ds}} $$

$$ i_{o}  = 0 $$

$$ 0 = - g_m v_{i} r_{ds}  + v_{o} - v_{i}$$

$$ v_{i} (1 + g_m r_{ds}) = v_{o} $$

$$ \frac{v_o}{v_i} = 1 + g_m r_{ds} $$

<!--pan_skip: -->

![right fit](../media/l9/cg_ss_a.png)

---


We've ignored bulk effect ($$g_s$$), source resistance ($$R_S$$) and load resistance ($$R_L$$)

$$ A = \frac{(g_{m} + g_s + g_{ds})(R_L||r_{ds})}{1 + R_S\left(\frac{g_m + g_s +
g_{ds}}{1 + R_L/r_{ds}}\right)}$$

If $$R_L >> r_{ds} $$, $$R_S  = 0$$ and $$g_s = 0$$

$$ A = \frac{(g_{m} + g_{ds})r_{ds}}{1} = 1+ g_m r_{ds} $$ 


<!--pan_skip: -->

![right fit](../media/l9/cg_ss_a.png)

---

#[fit] Common source

---



$$r_{in} \approx \infty$$

$$r_{out}  = r_{ds}$$, it's same circuit as the output of a current mirror

Gain 

![left fit](../media/l9/cs_ls_a.png)

---

![left fit](../media/l9/cs_ls_a.png)

![right fit](../media/l9/cs_ss_a.png)

---

##  Gain

$$ i_{o} = g_m v_i + \frac{v_o}{r_{ds}} $$

$$ i_o = 0 $$

$$ -g_m v_i = \frac{v_o}{r_{ds}} $$

$$ \frac{v_o}{v_i} = - g_m r_{ds}$$

<!--pan_skip: -->

![right fit](../media/l9/cs_ss_a.png)

---

<!--pan_doc: 

## Why common source?

-->

![fit](../media/l9/why_cs.png)

---
# Differential pair

Input resistance $$r_{in} \approx \infty$$

Gain  $$ A  = g_m r_{ds} $$

Output resistance $$ r_{out} = r_{ds}$$

Best analyzed with T model of transistor (see CJM page 31)

![left fit](../media/l9/df_ls_a.png)

---

## Diff pairs are cool

![left fit](../media/l9/df_ls_a.png)

 Can choose between 

 $$ v_o = g_m r_{ds} v_i$$

 and 

 $$ v_o = -g_m r_{ds} v_i$$
 
 by flipping input (or output) connections

---

![fit](../media/l10/diff.png)

---

#[fit] Thanks!

---







