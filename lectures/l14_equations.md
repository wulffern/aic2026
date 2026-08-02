footer: Carsten Wulff 2026
slidenumbers:true
autoscale:true
theme: Plain Jane, 1
text:  Helvetica
header:  Helvetica
date: 2026-05-01


<!--pan_skip: -->

# Equations

<!--pan_title: Equations -->

---

<!--pan_doc:

**Keywords:** Reference, Physics, Semiconductors, Diode, MOSFET, Noise, Circuits, References, Filters, Switched Capacitor, Data Converters, Regulators, PLL, Oscillators, Radio

Every equation of the lecture series in one place, ordered from fundamental
physics to the highest abstraction. No derivations and almost no words —
those live in the lectures — just the results, as a reference.

-->

# Fundamental physics

**The QED Lagrangian — everything in electronics follows from this**

$$ \mathcal{L} = \bar{\psi}[i \hbar c \gamma^\mu\partial_\mu - mc^2]\psi - q[\bar{\psi} \gamma^\mu \psi] A_\mu - \frac{1}{16 \pi}F_{\mu\nu}F^{\mu\nu} $$

**Schrödinger equation**

$$ i\hbar \frac{d}{dt} \psi(r,t) = \widehat{H} \psi(r,t) $$

**Probability density of a particle**

$$ P = \vert \psi(r,t)\vert ^2 \text{ , } \psi(r,t) = A e^{i(kr - \omega t)} $$

**Heisenberg uncertainty**

$$ \sigma_x \sigma_p \ge \frac{\hbar}{2} \text{ , } \Delta E \Delta t > \frac{h}{2\pi} $$

**Fermi-Dirac distribution, and its Boltzmann tail**

$$ f(E) = \frac{1}{e^{(E - E_F)/kT} + 1} \approx e^{(E_F - E)/kT} $$

---

**Maxwell's equations**

$$ \oint_{\partial \Omega} \mathbf{E} \cdot d\mathbf{S} = \frac{1}{\epsilon_0} \iiint_{V} \rho\cdot dV \text{ , } \oint_{\partial \Omega} \mathbf{B} \cdot d\mathbf{S} = 0 $$

$$ \oint_{\partial \Sigma} \mathbf{E} \cdot d\mathbf{\ell} = - \frac{d}{dt}\iint_\Sigma \mathbf{B}\cdot d\mathbf{S} $$

$$ \oint_{\partial \Sigma} \mathbf{B} \cdot d\mathbf{\ell} = \mu_0\left(\iint_\Sigma \mathbf{J} \cdot d\mathbf{S} + \epsilon_0 \frac{d}{dt}\iint_\Sigma\mathbf{E} \cdot d\mathbf{S} \right) $$

**Force on a charge**

$$ \vec{F} = q\vec{E} $$

---

# Semiconductors

**Density of electrons in the conduction band**

$$ n = \int_{E_C}^{\infty} N(E) f(E) dE $$

**Effective density of states**

$$ N_c = 2 \left[\frac{2 \pi k T m_n^*}{h^2}\right]^{3/2} \text{ , } N_v = 2 \left[\frac{2 \pi k T m_p^*}{h^2}\right]^{3/2} $$

**Intrinsic carrier concentration**

$$ n_i = \sqrt{N_c N_v}\, e^{-E_g/(2 k T)} $$

**Doped silicon (mass action)**

$$ n_n = N_D \text{ , } p_n = \frac{n_i^2}{N_D} \text{ ; } p_p = N_A \text{ , } n_p = \frac{n_i^2}{N_A} $$

---

**Drift current**

$$ \vec{J} = q n \mu \vec{E} $$

**Diffusion current**

$$ J = -q D_n \frac{d\rho}{dx} $$

**Thermal voltage**

$$ V_T = \frac{kT}{q} \approx 25.85\text{ mV @ 300 K} $$

---

# Diode

**Built-in voltage of a pn junction**

$$ \Phi_0 = V_T \ln\left(\frac{N_A N_D}{n_i^2}\right) $$

**Depletion width**

$$ W = \sqrt{\frac{2 \varepsilon_{si} (\Phi_0 + V_R)}{q} \cdot \frac{N_A + N_D}{N_A N_D}} $$

**Diode equation**

$$ I_D = I_S\left(e^{V_D/V_T} - 1\right) \text{ , } I_S = q A n_i^2 \left( \frac{D_n}{L_n N_A} + \frac{D_p}{L_p N_D}\right) $$

---

**Forward voltage temperature dependence**

$$ V_D = \frac{kT}{q}(\ell - 3 \ln T) + V_G \Rightarrow \frac{dV_D}{dT} = \frac{k}{q}\left(\ell - 3\ln T - 3\right) $$

**Difference of two diode voltages (PTAT)**

$$ V_{D1} - V_{D2} = V_T \ln N $$

**Generation (leakage) current of a reverse biased junction**

$$ I_{gen} = \frac{q A n_i W}{\tau_g} $$

---

# MOSFET

**Weak inversion**

$$ I_{D} = I_{D0} \frac{W}{L} e^{V_{eff}/n V_T} \text{ if } V_{DS} > 3V_T $$

$$ n = \frac{C_{ox} + C_{j0}}{C_{ox}} \text{ , } I_{D0} = (n-1)\mu_n C_{ox} V_T^2 $$

**Strong inversion, define**

$$ V_{eff} = V_{GS} - V_{tn} \text{ , } \ell = \mu_n C_{ox}\frac{W}{L} $$

$$
I_{DS} = \ell
\begin{cases}
V_{eff} V_{DS} & \text{if }V_{DS} << V_{eff} \\[10pt]
V_{eff} V_{DS} - V_{DS}^2/2 & \text{if } V_{DS} < V_{eff}  \\[10pt]
\frac{1}{2} V_{eff}^2\left[1 + \lambda(V_{DS} - V_{eff})\right] & \text{if } V_{DS} > V_{eff} \\[10pt]
\end{cases}
$$

---

**Transconductance**

$$ g_m = \frac{\partial I_{DS}}{\partial V_{GS}} = \ell V_{eff} = \sqrt{2 \ell I_D} = \frac{2 I_D}{V_{eff}} \text{ (strong)} \text{ , } g_m = \frac{I_D}{nV_T} \text{ (weak)} $$

**Transconductance efficiency**

$$ \frac{g_m}{I_D} = \frac{1}{nV_T} \text{ (weak)} \text{ , } \frac{g_m}{I_D} = \frac{2}{V_{eff}} \text{ (strong)} $$

**Output conductance and intrinsic gain**

$$ g_{ds} = \frac{1}{r_{ds}} \approx \lambda I_D \text{ , } A = g_m r_{ds} = \frac{2}{\lambda V_{eff}} $$

---

**Capacitances**

$$ C_{gs} = \frac{2}{3}WLC_{ox} \text{ (saturation)} \text{ , } C_{gd} = C_{ox} W L_{ov} $$

$$ C_{sb} = (A_s + A_{ch}) C_{js} \text{ , } C_{js} = \frac{C_{j0}}{\sqrt{1 + \frac{V_{SB}}{\Phi_0}}} $$

**Miller's theorem**

$$ C_{in} = (1 + A)C \text{ , } C_{out} = \left(1 + \frac{1}{A}\right)C \Rightarrow C_{in} \approx C_{gd}\, g_m r_{ds} $$

---

**Matching (Pelgrom)**

$$ \sigma^2(\Delta P) = \frac{A_P^2}{WL} + S_P^2 D^2 $$

**Current mismatch (Kinget)**

$$ \frac{\sigma_{I_D}^2}{I_D^2} = \frac{1}{WL}\left[\left(\frac{g_m}{I_D}\right)^2 \sigma_{vt}^2 + \frac{\sigma_{\ell}^2}{\ell^2}\right] \text{ , } \sigma_{v_i}^2 = \frac{\sigma_{I_D}^2}{g_m^2} $$

---

# Noise

**Mean square and power spectral density**

$$ \overline{x^2(t)} = \int_{0}^{\infty}{S_x(f)df} \text{ , } S_y(f) = S_x(f)\vert H(f)\vert ^2 $$

**Thermal noise of a resistor**

$$ S_{th}(f) = 4kTR $$

**Sampled (kT/C) noise bandwidth of an RC**

$$ f_x = \frac{\pi f_0}{2} = \frac{1}{4RC} $$

**Uncorrelated sources add in power**

$$ \overline{e_{tot}^2} = \overline{e_{1}^2} + \overline{e_{2}^2} $$

---

**Signal-to-noise ratio**

$$ SNR = 10 \log\left(\frac{\overline{v_{sig}^2}}{\overline{e_{n}^2}}\right) $$

**Noise factor and Friis' formula**

$$ F = \frac{SNR_{input}}{SNR_{output}} \text{ , } NF = 10\log(F) $$

$$ F = F_1 + \frac{F_2 - 1}{G_1} + \frac{F_3 - 1}{G_1 G_2} + \cdots $$

---

# Circuits

**Common source**

$$ A = -g_m r_{ds} \text{ , } r_{out} = r_{ds} $$

**Common drain (source follower)**

$$ A = \frac{g_m}{g_m + g_{ds} + g_s} \text{ , } r_{out} \approx \frac{1}{g_m} $$

**Common gate**

$$ A = 1 + g_m r_{ds} \text{ , } r_{in} \approx \frac{1}{g_m}\left(1 + \frac{R_L}{r_{ds}}\right) $$

**Source degeneration and cascode output resistance**

$$ r_{out} = r_{ds2}\left[1 + R_s(g_{m2} + g_{ds2})\right] \approx r_{ds2}\, g_{m2} R_s $$

---

# References and bias

**Bipolar / diode core**

$$ V_{BE} = V_T \ln\frac{I_C}{I_S} \text{ (CTAT)} \text{ , } \Delta V_{BE} = V_T \ln N \text{ (PTAT)} $$

**Brokaw bandgap output**

$$ V_{REF} = V_{BE3} + \frac{R_2}{R_3} V_T \ln\frac{R_2}{R_1} $$

**Bandgap voltage with curvature**

$$ V_{BG} = V_{G0} + (m-1)\frac{kT}{q}\ln{\frac{T_0}{T}} + T\left[\frac{k}{q}\ln{\frac{J_2}{J_1}}\frac{2R_2}{R_1} - \frac{V_{G0} - V_{be0}}{T_0}\right] $$

---

# Filters

**Pole/zero frequency**

$$ \omega_{p\vert z} \propto \frac{1}{RC} \text{ (Active-RC)} \text{ , } \omega_{p\vert z} \propto \frac{G_m}{C} \text{ (Gm-C)} $$

**General biquad**

$$ H(s) = \frac{\frac{C_1}{C_B}s^2 + \frac{G_2}{C_B}s + \frac{G_1G_3}{C_A C_B}}{s^2 + \frac{G_5}{C_B}s + \frac{G_3 G_4}{C_A C_B}} $$

---

# Switched capacitor

**SC resistance**

$$ Z_{I} = \frac{1}{C_1 f_\phi} $$

**SC gain stage and integrator**

$$ H(z) = \frac{C_1}{C_2}z^{-1} \text{ , } H(z) = \frac{C_1}{C_2}\frac{z^{-1}}{1 - z^{-1}} $$

**First and second order IIR**

$$ H(z) = \frac{b}{z-a} \text{ , } H(z) = \frac{b z}{z^2 - 2a z + (a^2+b^2)} $$

---

# Data converters

**Quantization noise**

$$ \overline{e_n^2} = \frac{\Delta^2}{12} \Rightarrow SQNR \approx 6.02B + 1.76 \text{ dB} $$

**Oversampling**

$$ SQNR \approx 6.02B + 1.76 + 10\log(OSR) $$

**First order noise shaping**

$$ Y(z) = STF(z)U(z) + NTF(z)E(z) \text{ , } STF = z^{-1} \text{ , } NTF = 1 - z^{-1} $$

$$ SQNR = 6.02B + 1.76 - 5.17 + 30\log(OSR) $$

---

**Figures of merit**

$$ FOM_W = \frac{P}{2^B f_s} \text{ , } FOM_S = SNDR + 10\log\left(\frac{f_s/2}{P}\right) $$

**DAC: a digital number scales a reference**

$$ V_{out} = D_{in} \times V_{ref} $$

---

# Voltage regulation

**The inductor and capacitor of a switcher**

$$ I_x(t) = \frac{1}{L}\int{V_x(t)dt} \text{ , } V_o(t) = \frac{1}{C}\int{(I_x(t) - I_o(t))dt} $$

**Ideal buck output**

$$ V_o = V_{in} \times \text{Duty-Cycle} $$

---

# PLL

**A modulated carrier, and phase versus frequency**

$$ A_m(t)\cos\left(2\pi f_{c}t + \phi_{m}(t)\right) \text{ , } \phi(t) = 2\pi\int_0^t f(t)dt $$

**Loop gain of a charge-pump PLL**

$$ L(s) = \frac{K_{osc} K_{pd} K_{lp} H_{lp}(s)}{N s} $$

$$ K_{osc} = 2\pi\frac{df}{dV_{cntl}} \text{ , } K_{pd} = \frac{I_{cp}}{2\pi} \text{ , } K_{lp}H_{lp}(s) = \frac{1}{s(C_1 + C_2)}\frac{1 + sRC_1}{1 + sR\frac{C_1C_2}{C_1+C_2}} $$

---

# Oscillators

**Crystal input impedance**

$$ Z_{in} \approx \frac{L C_F s^2 + 1}{L C_F C_P s^2 + C_F + C_P} $$

**Ring oscillator frequency**

$$ f = \frac{1}{2 N t_{pd}} \text{ , } t_{pd} \approx RC \Rightarrow f = \frac{\mu_n (VDD-V_{th})}{\frac{4}{3} N L^2} $$

**Current starved ring**

$$ f \approx \frac{I_{control}}{C \frac{VDD}{2} N} $$

---

# Radio

**Friis transmission (free space)**

$$ P_{RX} = \frac{P_{TX}}{D^2}\left[\frac{\lambda}{4\pi}\right]^2 $$

**Receiver sensitivity**

$$ P_{RX_{sens}} = -174\text{ dBm} + 10\log_{10}(DR) + NF + E_b/N_0 $$

---

<!--pan_skip: -->

#[fit] Thanks!

---

# Would you like to know more?

<!--pan_doc:

Every equation here is derived in its own chapter of this book; the section titles above point at them

Johns and Martin carry the same set with more algebra [@johns]

-->
