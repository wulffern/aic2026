footer: Carsten Wulff 2025
slidenumbers:true
autoscale:true
theme: Plain Jane, 1
text:  Helvetica
header:  Helvetica
date: 2025-02-06

<!--

References:

[A 1 TOPS/W Analog Deep Machine-Learning Engine With Floating-Gate Storage in 0.13 µm CMOS](https://ieeexplore.ieee.org/document/6919341)
 

-->

<!--pan_title: Lecture 4 - Analog Neural Networks -->

<!--pan_skip: -->
## TFE4188
# Analog Neural Networks


---

[Attention Is All You Need](https://arxiv.org/abs/1706.03762)

![right fit](../media/transformer.pdf)

---

[Neural Nets 3blue1brown](https://www.3blue1brown.com/topics/neural-networks)

<!--pan_skip: -->

![right fit](https://youtu.be/aircAruvnKk)

---

$$ a_{l+1} = \sigma(W_l a_l + b_l) $$

A NN consists of addition, multiplication, and a non-linear function


![right fit ](https://upload.wikimedia.org/wikipedia/commons/5/54/Feed_forward_neural_net.gif)

---

$$ \mathbf{y} = \sigma\left(\begin{bmatrix}
w_{11} & w_{12} & \ldots & w_{1n} \\
w_{21} & w_{22} & \ldots & w_{2n} \\
\vdots & \vdots & \ddots & \vdots \\
w_{m1} & w_{m2} & \ldots & w_{mn}
\end{bmatrix} 
\begin{bmatrix}
x_1 \\
x_2 \\
\vdots \\
x_n
\end{bmatrix} + 
\begin{bmatrix}
b_1 \\
b_2 \\
\vdots \\
b_m
\end{bmatrix}\right)
$$

---

$$
{\mathrm{ OA}}_{(x,y,k)} = f \left ({\sum _{i=0}^{R-1} \sum _{j=0}^{S-1} \sum _{c=0}^{C-1} {\mathrm{ IA}}_{(x+i,y+j,c)} \times W_{(i,j,c,k)} }\right)
$$

---

Assume N neurons

- N multiplications per neuron 
- N + 1 additions per neuron
- 1 sigmoid per neuron

For efficient inference, additions and multiplications should be low power!

![fit right](../media/nn.pdf)

---

<!--pan_skip: -->

#[fit] Addition

---

<!--pan_skip: --> 

#[fit] [Kirchoff's circuit laws](https://en.wikipedia.org/wiki/Kirchhoff%27s_circuit_laws)

---

## Kirchoff's voltage law

> The directed sum of the potential differences around any closed loop is zero

![fit right](https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Kirchhoff_voltage_law.svg/878px-Kirchhoff_voltage_law.svg.png)

$$ V_1 + V_2 + V_3 + V_4 = 0$$

--- 

![fit](../media/voltage_addition.pdf)

---


## Kirchoff's current law 

> The algebraic sum of currents in a network of conductors meeting at a point is
> zero 

![fit right](https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/KCL_-_Kirchhoff%27s_circuit_laws.svg/789px-KCL_-_Kirchhoff%27s_circuit_laws.svg.png)

$$ i_1 + i_2 + i_3 + i_4 = 0 $$

---

![fit](../media/current_addition.pdf)

---

## Charge concervation

See [Charge concervation](https://en.wikipedia.org/wiki/Charge_conservation) on Wikipedia 

![fit right](../media/charge_concervation.pdf)


$$ Q_4 = Q_1 + Q_2 + Q_3 $$

$$V_4 = \frac{ C_1 V_1 + C_2 V_2 + C_3 V_3}{C_1 + C_2 + C_3} $$


---

#[fit] Multiplication

---

## Digital capacitance  


$$V_4 = \frac{ C_1 V_1 + C_2 V_2 + C_3 V_3}{C_1 + C_2 + C_3} $$

$$V_O = \frac{C_1}{C_{TOT}} V_1 + \dots + \frac{C_N}{C_{TOT}} V_N $$

Make capacitors digitally controlled, then 

$$ w_1 = \frac{C_1}{C_{TOT}} $$


<sub>Might have a slight problem with variable gain as a function of total capacitance </sub>


<!--pan_skip: -->

![fit right](../media/charge_concervation.pdf)


---

##[fit] Mixing 

---

$$I_{M1} = G_{m} V_{GS} $$

$$ I_o = I_{M1} t_{input} $$

![right fit](../media/mixing.pdf)

---


##[fit] Translinear principle

---

### MOSFET in sub-threshold

![right fit](../media/vgate.pdf)

$$ I = I_{D0} \frac{W}{L} e^{(V_{GS} - V_{th})/n U_{T}}\text{ ,} U_T = \frac{k T}{q} $$

$$ I = \ell e^{V_{GS}/n U_{T}}\text{ , } \ell = I_{D0}\frac{W}{L} e^{-V_{th}/n U_{T}} $$

$$ V_{GS} = n U_{T} \ln\left(\frac{I}{\ell}\right) $$

---

<!--pan_skip: -->

![fit](../media/translinear.pdf)

---


![right fit ](../media/translinear.pdf)

$$V_1 + V_2 = V_3 + V_4$$

$$ n U_{T}\left[\ln\left(\frac{I_1}{\ell_1}\right) +
\ln\left(\frac{I_2}{\ell_2}\right)\right] = n
U_{T}\left[\ln\left(\frac{I_3}{\ell_3}\right) +
\ln\left(\frac{I_4}{\ell_4}\right)\right]  $$


$$ \ln\left(\frac{I_1 I_2}{\ell_1 \ell_2}\right) = \ln\left(\frac{I_3
I_4}{\ell_3 \ell_4}\right) $$


$$ \frac{I_1 I_2}{\ell_1 \ell_2}= \frac{I_3
I_4}{\ell_3 \ell_4} $$

$$ I_1 I_2  = I_3 I_4\text{ , if } \ell_1 \ell_2= \ell_3 \ell_4 $$


---

$$ I_1 I_2  = I_3 I_4 $$

$$ I_1 = I_a\text{ ,}I_2 = I_b + i_b\text{ ,}I_3 = I_b\text{ ,}I_4 = I_a + i_a$$

$$ I_a (I_b + i_b)  = I_b (I_a + i_a) $$

$$ I_a I_b + I_a i_b = I_b I_a + I_b i_a $$

---

$$ i_b = \frac{I_b}{I_a} i_a $$

---

$$  \ell_1 \ell_2= \ell_3 \ell_4  $$


$$ \ell_1 = I_{D0}\frac{W}{L} e^{-V_{th}/n U_{T}} $$

$$ \ell_2 = I_{D0}\frac{W}{L} e^{-(V_{th} \pm \sigma_{th})/n U_{T}} = \ell_1 e^{\pm \sigma_{th}/n U_{T}} $$


$$ \sigma_{th} = \frac{a_{vt}}{\sqrt{W L}} $$

$$ \frac{\ell_2}{\ell_1} =  e^{\pm \frac{a_{vt}}{\sqrt{W L}}/n U_{T}} $$

---

### Demo 

[JNW\_SV\_SKY130A](https://github.com/wulffern/jnw_sv_sky130a)

---

#[fit] Want to learn more?

---

[An Always-On 3.8 u J/86 % CIFAR-10 Mixed-Signal Binary CNN Processor With All Memory on Chip in 28-nm CMOS](https://ieeexplore.ieee.org/document/8480105)

<!--pan_skip: -->

![inline fit](../ip/8480105.gif)

---

[CAP-RAM: A Charge-Domain In-Memory Computing 6T-SRAM for Accurate and Precision-Programmable CNN Inference](https://ieeexplore.ieee.org/document/9441013)


<!--pan_skip: -->

![inline fit](../ip/chen2-3056447-small.gif)


---

[ARCHON: A 332.7TOPS/W 5b Variation-Tolerant Analog CNN Processor Featuring Analog Neuronal Computation Unit and Analog Memory](https://ieeexplore.ieee.org/document/9731654)

<!--pan_skip: -->

![inline fit](../ip/9731654-fig-2-source-large.gif)

---

[IMPACT: A 1-to-4b 813-TOPS/W 22-nm FD-SOI Compute-in-Memory CNN Accelerator Featuring a 4.2-POPS/W 146-TOPS/mm2 CIM-SRAM With Multi-Bit Analog Batch-Normalization](https://ieeexplore.ieee.org/document/10129929)

---

#[fit] Thanks!

---


