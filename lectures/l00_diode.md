footer: Carsten Wulff 2024
slidenumbers:true
autoscale:true
theme: Plain Jane, 1
text:  Helvetica
header:  Helvetica
date: 2024-10-25


<!--pan_skip: -->

# Diodes

---

<!--pan_doc: 

**Status:** 1.0

<iframe width="560" height="315" src="https://www.youtube.com/embed/F1-piS8uL1w?si=wnFQ83kHPuYBtYS2&amp;start=3200" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

-->

<!--pan_title: Diodes -->

# Why

Diodes are a magical [^1] semiconductor device that conduct current in one direction. It's one of the fundamental electronics components, and it's a good idea to understand how they work.


<!--pan_doc:

If you don't understand diodes, then you won't understand transistors, neither
bipolar, or field effect transistors.

A useful feature of the diode is the exponential relationship
between the forward current, and the voltage across the device.

To understand why a diode works it's necessary to understand the physics behind
semiconductors. 

This paper attempts to explain in the simplest possible terms how a diode works [^2]

-->

---

<!--pan_doc: 

# Silicon

Integrated circuits use single crystalline silicon. The silicon crystal is grown
with the [Czochralski method](https://en.wikipedia.org/wiki/Czochralski_method)
which forms a ingot that is cut into wafers. The wafer is a regular
silicon crystal, although, it is not perfect. 

A [silicon]() crystal unit cell, as seen in Figure 1 is a diamond faced cubic with 8 atoms in the corners spaced at 0.543 nm, 6 at the center of the
faces, and 4 atoms inside the unit cell at a nearest neighbor distance of 0.235
nm. 


![Silicon crystal unit cell\label{fig:silicon}](../media/503px-Silicon-unit-cell-3D-balls.png)

<sub>Figure 1: Silicon crystal unit cell</sub>

As you hopefully know, the energy levels of an electron around a positive
nucleus are quantized, and we call them orbitals (or shells). For an atom far
away from any others, these orbitals, and energy levels are distinct. As we
bring atoms closer together, the orbitals start to interact, and in a crystal,
the distinct orbital energies split into bands of allowed energy states. No two
electrons, or any Fermion (spin of $1/2$), can occupy the same quantum state.
We call the outermost "shared" orbitial, or band, in a crystal the valence band.
Hence covalent bonds. 

If we assume the crystal is perfect, then at 0 Kelvin all electrons will be part of
covalent bonds. Each silicon atom share 4
electrons with its neighbors. What we really mean when we say "share 4
electrons" is that the wave-functions of the outer orbitals interact, and
we can no longer think of the orbitals as belonging to either of the silicon
nuclei. All the neighbors atoms "share" electrons, and
nowhere is there an vacant state, or a hole, in the valence band. 

If such a crystal were to exist, where there were no holes in the valence band, 
and a net neutral charge, the crystal could not conduct any drift current. Electrons would move 
around continuously, swapping states, but there could be no net drift of charge carriers. 

In an atom, or a crystal, there are also higher energy states where the carriers
are "free" to move. We call these energy levels, or bands of energy levels,
conduction bands. In singular form "conduction band", refers to the lowest
available energy level where the electrons are free to move. 

Due to imperfectness of the silicon crystal, and non-zero temperature, there
will be some electrons that achieve sufficient energy to jump to the conduction
band. The electrons in the conduction band leave vacant states, or holes, in the
valence band. 

Electrons can move both in the conduction band, as free electrons, and in the
valence band, as a positive particle, or hole. Both bands can support drift and diffusion currents.

-->


# Intrinsic carrier concentration

The intrinsic carrier concentration of silicon, or the density of free electrons and holes at a given temperature, is given by 



<!--pan_skip: -->

# $$ n_i = \sqrt{N_c N_v} e^{\frac{-E_g}{2 k T}}  $$

---


<!--pan_doc: 

$$
n_i = \sqrt{N_c N_v} e^{-E_g/(2 k T)} 
\tag{1} 
\label{eq:ni}
$$

where $E_g$ is the bandgap energy of silicon (approx 1.12 eV), $k$ is Boltzmann's constant, $T$ is
the temperature in Kelvin, $N_c$ is the density of states in conduction band,
and $N_v$ is the density of states in the valence band. 

-->


The density of states are

$$ N_c = 2 \left[\frac{2 \pi  k T m_n^*}{h^2}\right]^{3/2} \text{  } N_v = 2 \left[\frac{2 \pi  k T m_p^*}{h^2}\right]^{3/2} $$

<!--pan_doc: 

where $h$ is Planck's constant, $m_n^\ast$ is the effective mass of electrons, and
$m_p^\ast$ is the effective mass of holes.

-->

---

<!--pan_doc:

Leave it to engineers to simplify equations beyond understanding. Equation \eqref{eq:ni} is complicated, and the density of states includes the effective mass of electrons and holes, which is a parameter that depends on the curvature of the band structure. To engineers, this is too complicated, and $n_i$ has been simplified so it "works" in daily calculation. 

Through engineering simplification, however, physics understanding is lost. 

In [@cjm11] they claim the intrinsic carrier concentration is a constant, although
they do mention $n_i$ doubles every 11 degrees Kelvin. 

-->

In BSIM 4.8 [@bsim] the intrinsic carrier concentration is 

$$ n_{i} = 1.45e10 \frac{TNOM}{300.15} \sqrt{\frac{T}{300.15} \exp^{21.5565981
- \frac{E_g}{2kT}}} $$



<!--pan_doc: 
Comparing the three models in Figure 2, we see the shape of BSIM and
the full equation is almost
the same, while the "doubling every 11 degrees" is just wrong.

-->

![right fit Intrinsic carrier concentration versus temperature\label{fig:ni}](../media/ni.pdf)

<!--pan_doc:
<sub>Figure 2: Intrinsic carrier concentration versus temperature</sub>


At room temperature the intrinsic carrier consentration is approximately
$n_{i} =  1 \times 10^{16}$ carriers/m$^3$.

That may sound like a big number, however, if we calculate the electrons
per $um^{3}$ it's
$n_{i} = \frac{1 \times 10^{16}}{(1 \times 10^{6})^{3}} \text{ carriers}/\mu \text{m}^{3}< 1$,
so there are really not that many free carriers in intrinsic silicon.

From Figure 2 we can see that $n_i$ changes greatly as a function of temperature, but the understanding "why" is not easy to get from "doubling every 11 degrees". To understand the temperature behavior of diodes, we must understand Eq \eqref{eq:ni}.


So where does Eq \eqref{eq:ni} come from? I find it unsatisfying
if I don't understand where things come from. I like to understand why there is
an exponential, or effective mass, or Planck's constant. If you're like me, then
read the next section. If you don't care, and just want to memorize the
equations, or indeed the number of intrinsic carrier concentration number at
room temperature, then skip the next section.

-->



<!--pan_doc:

# It's all quantum

There are two components needed to determine how many electrons are in the
conduction band. The density of available states, and the probability of an
electron to be in that quantum state. 

For the density of states we must turn to quantum mechanics. The probability
amplitude of a particle can be described as  

$$\psi = Ae^{i(k \textbf{r} - \omega t)}$$ 

where $k$ is the wave number, and $\omega$ is the angular frequency, and
$\textbf{r}$ is a spatial vector. 

In one dimension we could write $\psi(x,t) = Ae^{i(kx - \omega t)}$ 

In classical physics we described the Energy of the system as
$$\frac{1}{2 m} p^2 + V = E$$ 
where $p = m v$, $m$ is the mass, $v$ is the velocity and $V$ is the potential.

In the quantum realm we must use the Schrodinger equation to compute the time
evolution of the Energy, in one space dimension


$$-\frac{\hbar^2}{2 m} \frac{\partial^2}{\partial^2 x}\psi(x,t) +
V(x)\psi(x,t) = i\hbar\frac{\partial}{\partial t} \psi(x,t) $$

where $m$ is the mass, $V$ is the potential, $\hbar = h/2\pi$.

We could rewrite the equation above as 

$$ \widehat{H} \psi(x,t) = i \hbar \frac{\partial}{\partial t}  \psi(x,t)  =
\widehat{E}  \psi(x,t)$$

where $\widehat{H}$ is sometimes called the *Hamiltonian* and is an operator,
or something that act on the wave-function. In [Feynman's
Lectures on Physics](https://www.feynmanlectures.caltech.edu)  Feynman
called the Hamiltonian the *Energy Matrix* of a system. I like that better. The
$\widehat{E}$ is the energy operator, something that operates on the
wave-function to give the Energy. 

We could re-arrange

$$ [\widehat{H} - \widehat{E}]\psi(r,t) = 0$$
 
This is an equation with at least 5 unknowns, the space vector in three dimensions, time, and the
energy matrix  $\widehat{H}$. 

The dimensions of the energy matrix depends
on the system. The energy matrix further up is for one free electron. For an atom, the
energy matrix will have more dimensions to describe the possible quantum states. 

I consider all energy matricies as infinite dimensions, but most state transitions are so unlikely that they can be safely ignored. 
 
I was watching [Quantum computing in the 21st
Century](https://youtu.be/zxml8UQSwC0) and David Jamison mentioned that the
largest system we could today compute would be a system with about 30
electrons. 

We know exactly how the equations of quantum mechanics
appear to be, and they've proven extremely successful, we must make
simplifications before we can predict how electrons behave in complicated
systems like the silicon lattice with approximately 0.7 trillion electrons per
cube micro meter. You can check the calculation
 
$$ \left[\frac{1 \text{ }\mu\text{m}}{ 0.543\text{ nm}}\right]^3 \times 8 \text{ atoms per unit
 cell} \times 14 \text{ electrons per atom}$$ 

-->

---

## Density of states 

<!--pan_doc:

To compute "how many Energy states are there per unit volume in the
conduction band", or the "density of states", we start with the three
dimensional Schrodinger equation for a free electron

-->

[.column]

$$-\frac{\hbar^2}{2m}\nabla^2\psi = E\psi$$

<!--pan_doc:

I'm not going to repeat the computation here, but rather paraphrase the steps.
You can find the full derivation in [Solid State Electronic
Devices](https://www.amazon.com/Solid-State-Electronic-Devices-7th/dp/0133356035).


The derivation starts by computing the density of states in the k-space, or
 momentum space, 
 
 -->
 
$$N(dk) = \frac{2}{(2 \pi)^p} dk$$

<!--pan_doc: 
 
Where $p$ is the number of dimensions (in our case 3).

The band structure $E(k)$ is used to convert to the density of states to a
function of energy $N(E)$. The simplest band structure, and an approxmiation of
the lowest conduction band is
-->

$$E(k) = \frac{\hbar^2 k^2}{2 m^*}$$

<!--pan_doc:

where $m^*$ is the effective mass of the particle. It is within this effective
mass that we "hide" the complexity of the actual three-dimensional crystal
structure of silicon. 

The effective mass when we compute the density of states is  

-->

[.column]

$$m^* = \frac{\hbar^2}{\frac{d^2 E}{dk^2}}$$

<!--pan_doc: 

as such, the effective mass depends on the localized band structure of the
silicon unit cell, and depends on direction of movement, strain of the silicon
lattice, and probably other things.

In 3D, once we use the above equations, one can compute that the density of
states per unit energy is 

-->

$$N(E)dE = \frac{2}{\pi^2}\frac{m^*}{\hbar^2}^{3/2} E^{1/2}dE$$

<!--pan_doc:

In order to find the number of electrons, we need the probability of an electron
being in a quantum state, which is given by the [Fermi-Dirac
distribution](https://en.wikipedia.org/wiki/Fermi–Dirac_statistics)

-->

---

<!--pan_skip: -->

$$f(E) = \frac{1}{e^{(E - E_F)/kT}  + 1} $$

---

<!--pan_doc: 

$$
 f(E) = \frac{1}{e^{(E - E_F)/kT}  + 1}
\tag{2}
\label{eq:fm}
$$


where $E$ is the energy of the electron, $E_F$ is the [Fermi
level](https://en.wikipedia.org/wiki/Fermi_level) or checmical potential,
$k$ is Boltzmann's constant, and $T$ is the temperature in Kelvin. 

Fun fact, the Fermi level difference between two points is what you measure with a voltmeter.

If the
$E -E_F > kT$, then we can start to ignore the $+1$ and the probability reduces
to

$$ f(E) = \frac{1}{e^{(E-E_F)/kT}} = e^{(E_F - E)/kT}$$

A few observiation on the Fermi-Dirac distribution. If the Energy of a state
is at the Fermi level, then $f(E) = \frac{1}{2}$, or a 50 % probability of being occupied. 

In a metal, the Fermi level lies within a band, as the conduction
band and valence band overlap. As a result, there are a bunch of free electrons
that can move around. Metal does not have the same type of covalent bonds as
silicon, but electrons are shared between a large part of the metal structure. I would also assume that
the location of the Fermi level within the band structure explains the difference in
conductivity of metals, as it would determined how many electrons are free to
move. 

In an insulator, the Fermi level lies in the bandgap between valence band and
conduction band, and usually, the bandgap is large, so there is a
low probability of finding electrons in the conduction band. 

In a semiconductor we also have a bandgap, but much lower energy than an insulator.
If we have thermal equilibrium, no external forces, and
we have an un-doped (intrinsic) silicon semiconductor, then the fermi level $E_F$ lies half way between the
conduction band edge $E_C$ and the valence band edge $E_V$. 

The bandgap is defined
as the $E_C - E_V = E_g$, and we can use that to get 
$E_F - E_C = E_C - E_g/2 - E_C= -E_g/2$. This is why the bandgap of silicon
keeps showing up in our diode equations.

The number of electrons per delta energy will then be given by  

-->

$$N_e dE = N(E)f(E)dE$$

<!--pan_doc: 

, which can be integrated to get 

-->

---

$$
n_e = 2\left( \frac{2 \pi m^\ast k T}{h^2}\right)^{3/2} e^{(E_F - E_C)/kT}
$$

---

<!--pan_skip: -->

For intrinsic silicon at thermal equlibrium, we could write

$$
n_0 = 2\left( \frac{2 \pi m^\ast k T}{h^2}\right)^{3/2} e^{-E_g/(2kT)}
$$


---

<!--pan_doc: 

For intrinsic silicon at thermal equlibrium, we could write

$$
n_0 = 2\left( \frac{2 \pi m^\ast k T}{h^2}\right)^{3/2} e^{-E_g/(2kT)}
\tag{3}
\label{eq:nc0}
$$



As we can see, Equation \eqref{eq:nc0} has the same coefficients and form as the
computation in Equation \eqref{eq:ni}. The
difference is that we also have to account for holes. At thermal equilibrium
and intrinsic silicon $n_i^2 = n_0 p_0$

## How to think about electrons (and holes)
I've come to the realization that to imagine electrons as balls moving around in
the silicon crystal is a bad mental image. 

For example, for a metal-oxide-semiconductor field effect transistor (MOSFET) it is not
the case that the electrons that form the inversion layer under strong inversion
come from somewhere else. They are already at the silicon surface, but they are
bound in covalent bonds (there are literaly trillions of bound electrons in a
typical transistor). 

What happens is that the applied voltage at the gate shifts the energy bands
close to the surface (or bends the bands in relation to the Fermi level), and the density of carriers in the
conduction band in that
location changes, according to the type of derivations above. 

Once the electrons are in the conduction band, then they follow the same
equations as diffusion of a gas,  [Fick's law of
diffusion](https://en.wikipedia.org/wiki/Fick%27s_laws_of_diffusion). 
Any charge density concentration difference will give rise to a [diffusion
current](https://en.wikipedia.org/wiki/Diffusion_current) given by 

\begin{equation}
\tag{4}
\label{eq:diff}
J_{\text{diffusion}} = - qD_n \frac{\partial \rho}{\partial x}
\end{equation}

where $J$ is the current density, $q$ is the charge, $\rho$ is the charge density, and  $D$ is a diffusion
coefficient that through the [Einstein
relation](https://en.wikipedia.org/wiki/Diffusion_current) can be expressed as
$D = \mu k T$, where mobility $\mu = v_d/F$ is the ratio of drift velocity $v_d$
to an applied force $F$.  

To make matters more complicated, an inversion layer of a MOSFET is not in three
dimensions, but rather a [two dimensional electron
gas](https://en.wikipedia.org/wiki/Two-dimensional_electron_gas), as the density of
states is confined close to the silicon surface. As such, we should not expect the
mobility of bulk silicon to be the same as the mobility of a MOSFET transistor.

-->

# Doping


<!--pan_doc:
We can change the property of silicon by introducing other elements, something
we've called [doping](https://en.wikipedia.org/wiki/Doping_(semiconductor)).
Phosphor has one more electron than silicon, Boron has one less
electron. Injecting these elements into the silicon crystal
lattice changes the number of free electron/holes.

These days, we usually dope with [ion implantation](https://en.wikipedia.org/wiki/Ion_implantation), while in the olden days,
most doping was done by [diffusion](https://ieeexplore.ieee.org/document/1050758). You'd paint something containing Boron on the
silicon, and then heat it in a furnace to "diffuse" the Boron atoms into the
silicon.

If we have an
element with more electrons we call it a donor, and the donor
concentration $N_{D}$. 

The main effect of doping is that it changes the location
of the Fermi level at thermal equilibirum. For donors, the Fermi level will
shift closer to the conduction band, and increase the probabilty of free
electrons, as determined by Equation \eqref{eq:fm}.

Since the crystal now has an abundance of
free electrons, which have negative charge, we call it n-type.

If the element has less electrons we call
it an acceptor, and the acceptor concentration $N_{A}$. Since the
crystal now has an abundance of free holes, we call it p-type. 

The doped material does not have a net charge, however, as it's the same number of
electrons and protons, so even though we dope silicon, it does remain neutral.

The 
doping concentrations are larger than the intrinsic carrier
concentration, from maybe $10^{21}$ to $10^{27}$ carriers/m$^{3}$. To
separate between these concentrations we use $p-,p,p+$ or $n-, n, n+$.

-->

The number of electrons and holes in a n-type material is

$$ n_n = N_D \text{ ,  } p_n = \frac{n_i^2}{N_D} $$

and in a p-type material

$$ p_p = N_A \text{ , } n_p = \frac{n_i^2}{N_A} $$


<!--pan_doc: 

In a p-type crystal there is a majority of holes, and a minority of
electrons. Thus we name holes majority carriers, and electrons minority
carriers. For n-type it's opposite.

--->

---

# PN junctions

<!--pan_doc:

Imagine an n-type material, and a p-type material, both are neutral in
charge, because they have the same number of electrons and protons. Within both
materials there are free electrons, and free holes which move around
constantly. 

Now imagine we bring the two materials together, and we call where they meet the
junction. Some of the electrons
in the n-type will wander across the junction to the p-type material, and visa versa.
On the opposite side of the junction they might find an opposite charge, and might get locked in place.
They will become stuck. 

After a while, the diffusion of charges across the junction creates a depletion region with immobile
charges. Where as the two materials used to be neutrally charged, there
will now be a build up of negative charge on the p-side, and positive
charge on the n-side. 

-->

---

## Built-in voltage

<!--pan_doc: _

The charge difference will create a field, and a built-in voltage will develop across the depletion
region. 

The density of free electrons in the conduction band is

-->

[.column]

$$
n = \int_{E_C}^{\infty} N(E) f(E) dE 
$$

<!--pan_doc: _

, where $N(E)$ is the density of states, and $f(E)$ is a probability of a
electron being in that state (Equation \eqref{eq:fm}). 

We could write the density of electrons on the n-side as 

-->

$$
n_n = e^{E_{F_n}/kT} \int_{E_C}^{\infty} N_n(E) e^{-E/kT}dE 
$$

<!--pan_doc: 

since the Fermi level is independent of the energy state of the electrons (I think).

The density of electrons on the p-side could be written as

-->

$$
n_p = e^{E_{F_p}/kT} \int_{E_C}^{\infty} N_p(E) e^{-E/kT}dE 
$$

<!--pan_doc:

If we assume that the density of states, $N_n(E)$ and $N_p(E)$ are the same, and
the temperature is the same, then

-->

$$
\frac{n_n}{n_p} = \frac{ e^{E_{F_n}/kT}}{e^{E_{F_p}/kT}} = e^{(E_{F_n} - E_{F_p})/kT}
$$

<!--pan_doc:

The difference in Fermi levels is the built-in voltage multiplied by the unit
charge.

-->

[.column]

$$
E_{F_n} - E_{F_p} = q\Phi
$$

<!--pan_doc:

and by substituting for the minority carrier concentration on the p-side we get

-->

$$\frac{N_A N_D}{n_i^2} = e^{q\Phi_0/kT}$$

or rearranged to 

$$\Phi_0 = \frac{kT}{q} ln\left(  \frac{N_A N_D}{n_i^2} \right)$$

---

## Current

<!--pan_doc: 

The derivation of current is a bit involved, but let's try.

The hole concentration on the p-side and n-side could be written as 

-->

[.column]

$$
\frac{p_p}{p_n} = e^{-q\Phi_0/kT}
$$

<!--pan_doc:

The negative sign is because the built in voltage is positive on the n-type side 

Asssume that $-x_{p0}$ is the start of the junction on the p-side, and $x_{n0}$
is the start of the junction on the n-side.

Assume that we lift the p-side by a voltage $qV$

Then the hole concentration would change to

-->

$$
\frac{p(-x_{p0})}{p(x_{n0})} = e^{q(V-\Phi_0)/kT}
$$

<!--pan_doc: 

while on the n-side the hole concentration would be 

-->

$$
\frac{p(x_{n0})}{p_n} = e^{qV/kT}
$$

<!--pan_doc:

So the excess hole concentration on the n-side due to an increase of $V$ would
be 

-->

[.column]

$$
\Delta p_n = p(x_{n0}) - p_n = p_n\left( e^{qV/kT} -1 \right)
$$

<!--pan_doc: 

The diffusion current density, given by Equation \eqref{eq:diff} states 

-->

$$
J(x_n) = -q D_p \frac{\partial \rho}{\partial x} 
$$

<!--pan_doc:

Thus we need to know the charge density as a function of $x$. I'm not sure why,
but apparently it's

-->

$$
\partial \rho(x_n) = \Delta p_n e^{-x_n/L_p}
$$

<!--pan_doc:

where $L_p$ is a diffusion length. I think the equation above, the exponential decay as a function of length, is related to the probabilty of electron/hole recombination, and how the rate of recombination must be related to the exceess hole concentration, as such related to [Exponential decay](https://en.wikipedia.org/wiki/Exponential_decay).

Anyhow, we can now compute the current density, and need only compute it for
$x_n$ = 0, so you can show it's 

-->

$$
J(0) = q\frac{D_p}{L_p} p_n \left( e^{qV/kT} - 1\right)
$$

<!--pan_doc:

which start's to look like the normal diode equation. The $p_n$ is the minority
concentration of holes on the n-side, which we've before estimated as $p_n =
\frac{n_i^2}{N_D}$ 

We've only computed for holes, but there will be electron transport from the
p-side to the n-side also. 

We also need to multiply by the area of the diode to get current from current
density. The full equation thus becomes

-->

---

$$
I = q A n_i^2 \left( \frac{1}{N_A}\frac{D_n}{L_n} + \frac{1}{N_D}\frac{D_p}{L_p}
\right)\left[ e^{qV/kT} - 1 \right]
$$

---

<!--pan_doc:

where $A$ is the area of the diode, $D_n$,$D_p$ is the diffusion coefficient of electrons
and holes and $L_n$,$L_p$ is the diffusion length of electrons and holes. 

Which we usually write as 

$$ I_D = I_S(e^{\frac{V_D}{V_T}} - 1 ),\text{ where } V_T = kT/q $$


-->

---

## Forward voltage temperature dependence

<!--pan_doc: 

We can rearrange $I_D$ equation to get

-->

$$ V_D = V_T \ln\left(\frac{I_D}{I_S}\right) $$

---

<!--pan_doc:

and at first glance, it appears like $V_D$ has a positive temperature
coefficient. That is, however, wrong.

First rewrite

-->

[.column]

$$ V_D = V_T \ln{I_D} - V_T \ln{I_S} $$

$$ \ln{I_S} =  2 \ln{n_i} +  \ln{Aq\left (\frac{D_n}{L_n N_A} +
\frac{D_p}{L_p N_D}\right)} $$

<!--pan_doc:

Assume that diffusion coefficient [^3], and diffusion lengths are independent of
temperature. 

That leaves $n_i$ that varies with temperature.

-->

$$ n_i = \sqrt{B_c B_v} T^{3/2} e^\frac{-E_g}{2 kT} $$

<!--pan_doc:

where 

-->



$$ B_c = 2 \left[\frac{2 \pi  k m_n^*}{h^2}\right]^{3/2} \text{  } B_v = 2 \left[\frac{2 \pi  k m_p^*}{h^2}\right]^{3/2} $$



[.column]

$$ 2 \ln{n_i} = 2\ln{\sqrt{B_c B_v}}  + 3 \ln T -
\frac{V_G}{V_T}$$

<!--pan_doc:

with $V_G = E_G/q$ and inserting back into equation for $V_D$

-->

$$ V_D = \frac{kT}{q}(\ell  - 3 \ln T) + V_G $$ 

<!--pan_doc:

Where $\ell$ is temperature independent, and given by

-->

$$ \ell= \ln{I_D} - \ln{\left (Aq\frac{D_n}{L_n N_A} +
\frac{D_p}{L_p N_D}\right)}  - 2 \ln{\sqrt{B_c B_v}} $$


---


From  equations above we can see that at 0 K, we expect the diode voltage to be
equal to the bandgap of silicon. Diodes don't work at 0 K though. 

<!--pan_doc: 

From the diode voltage relation we can calculate the derivative (ask chat to -->
<!--explain it to you ), and you'll get

-->

$$ \frac{dV_D}{dT} = \frac{k}{q}\bigl(\ell - 3 \ln T - 3\bigr). $$

<!--pan_doc:
and we can see the slope is negative with a factor of $\ln(T)$, which turns out
to be very close to linear for the temperature range we're interested in (-40C
to 125C)

-->

The slope of the diode voltage can be seen to depend on the area, the current,
doping, diffusion constant, diffusion length and the effective masses. 

<!--pan_doc:

Figure 3 shows the $V_D$ and the deviation of $V_D$ from a straight line. The
non-linear component of $V_D$ is only a few mV. If we could combine $V_D$ with a
voltage that increased with temperature, then we could get a stable voltage
across temperature to within a few mV.

-->


![right fit Diode forward voltage as a function of temperature \label{fig:vd}](../media/vd.pdf)

<!--pan_doc:
<sub>Figure 3: Diode forward voltage as a function of temperature</sub>
-->

---

## Current proportional to temperature 

<!--pan_doc: 

Assume we have a circuit like Figure 4. 

Here we have two diodes, biased at different current densities. The voltage on
the left diode $V_{D1}$ is equal to the sum of the voltage on the right diode $V_{D2}$ and voltage
across the resistor $R_1$. The current in the two diodes are the same due to
the current mirror. A such, we have that

-->

$$ I_S e^\frac{qV_{D1}}{kT} = N I_S e^\frac{qV_{D2}}{kT} $$

Taking logarithm of both sides, and rearranging, we see that 

$$ V_{D1} - V_{D2} = \frac{kT}{q}\ln{N}$$


<!--pan_doc: 

Or that the difference between two diode voltages biased at different current densities is proportional to absolute
temperature. 

In the circuit above, this $\Delta V_D$ is across the resistor
$R_1$, as such, the $I_D  = \Delta V_D/R_1$. We have a current that is
proportional to temperature.

If we copied the current, and sent it into a series combination of a resistor
$R_2$ and a diode, we could scale the $R_2$ value to give us the exactly right
slope to compensate for the negative slope of the $V_D$ voltage. 

The voltage across the resistor and diode would be constant over temperature,
with the small exception of the non-linear component of $V_D$.

-->

![right fit Circuit to generate a current proportional to kT\label{fig:ptat}](../media/l3_ptat.pdf)

---

## Reverse leakage

<!--pan_doc:

So far we have only looked at the diode in forward bias, where the
exponential term dominates and the current is set by the diffusion
saturation $I_S$. In integrated circuits we equally often care about
what happens when the diode is reverse biased, with $V_D < 0$. The
exponential term is then negligible, and you might expect the current
to be zero. It is not.

What happens physically is that the reverse bias lifts the Fermi level
on the n-side relative to the p-side. The built-in field grows, the
depletion region widens, and any minority carrier that wanders into
that region is immediately swept across to the other side. The
question of "how much current" is therefore really the question of
"how many minority carriers are produced per second, and where".

In a real n+/p-substrate junction there are two places where minority
carriers appear:

1. In the *quasi-neutral* p-substrate, a short diffusion length away
   from the junction. These thermally generated electrons diffuse to
   the depletion edge and are then collected.
2. *Inside* the depletion region itself, through generation at
   Shockley-Read-Hall trap centers in the silicon bandgap.

The first gives the Shockley diffusion saturation current $I_S$, the
second gives the Sah-Noyce-Shockley generation current $I_{gen}$.
They have different temperature dependencies, and which one dominates
depends on temperature, doping, and how clean the silicon is.

-->

---

## Diffusion leakage

[.column]

$$ I_S = q A n_i^2 \left( \frac{1}{N_A}\sqrt{\frac{D_n}{\tau_n}} + \frac{1}{N_D}\sqrt{\frac{D_p}{\tau_p}} \right) $$

<!--pan_doc:

This is exactly the $I_S$ from the forward-bias derivation, just
re-interpreted. Under reverse bias the minority-carrier concentration
at the edge of the depletion region is forced to *zero* (every carrier
that arrives is swept across). The concentration gradient between the
bulk equilibrium $n_p = n_i^2/N_A$ on the p-side and zero at the
depletion edge drives a steady diffusion of electrons toward the
junction, and similarly of holes from the n-side.

The factor that matters for temperature is $n_i^2$. From Equation
\eqref{eq:ni}, $n_i^2 \propto T^3 \exp(-E_g/kT)$. The $T^3$ comes
from the densities of states $N_c, N_v \propto T^{3/2}$, which is a
genuine quantum-mechanical effect: as temperature rises, more
states become thermally accessible above $E_c$ and below $E_v$. The
$\exp(-E_g/kT)$ dominates the slope, but the $T^3$ prefactor
contributes a non-trivial correction that is bigger than people
usually admit. The log-derivative of $n_i^2$ is

$$ \frac{d \ln n_i^2}{dT} = \frac{E_g}{kT^2} + \frac{3}{T} $$

At $T = 300\, K$ the $3/T$ term is about $7\, \%$ of the
exponential term; at $T = 1000\, K$ it is about $25\, \%$. So the
density-of-states prefactor visibly steepens the leakage curve at
high temperature, and you cannot drop it if you care about anything
beyond a back-of-envelope estimate.

The diffusion current doubles roughly every $4$-$5\, K$ near room
temperature, which is the familiar "reverse current doubles every
10 K" rule of thumb for ideal junctions [^4].

For an n+/p-well antenna diode, the $1/N_D$ term is negligible
because $N_D \gg N_A$, and $I_S$ is set almost entirely by
electron injection from the p-well.

Both $D$ and $\tau$ depend on temperature too, and that matters once
the sweep is several hundred kelvin wide. Phonon-limited mobility
goes as $\mu \propto T^{-2.4}$ above $\sim 300\, K$, so via the
Einstein relation $D = \mu k T/q \propto T^{-1.4}$. The SRH lifetime
goes as $\tau = 1/(\sigma v_{th} N_t)$ with $v_{th} \propto
\sqrt{T}$, so $\tau \propto T^{-1/2}$ (taking $\sigma$ and $N_t$
constant). The combination $\sqrt{D/\tau}$ in $I_S$ therefore drifts
as $T^{-0.45}$, so $I_S$ at $1000\, K$ is about $0.6\times$ what a
"constant $D$, $\tau$" model would predict. That is small compared
to the many decades of swing in $n_i^2$, but it is the dominant
reason the diffusion curve in Figure 5 starts to flatten at the top
end. The script `ex/antenna_diode_leakage.py` includes both
$T$-dependencies.

-->

---

## Generation in the depletion region

[.column]

$$ I_{gen} = \frac{q A n_i W}{\tau_g} $$

$$ W = \sqrt{\frac{2 \varepsilon_{si} (\Phi_0 + V_R)}{q} \cdot \frac{N_A + N_D}{N_A N_D}} $$

<!--pan_doc:

Real silicon is not a perfect crystal. Process damage, residual
metallic impurities and dangling bonds at interfaces create trap
levels somewhere in the bandgap. A trap near mid-gap can capture an
electron from the valence band (creating a hole) and then emit it to
the conduction band (creating an electron). Inside a reverse-biased
depletion region, both carriers are immediately swept apart by the
field, the trap empties, and the cycle repeats. The net effect is a
steady generation of electron-hole pairs that shows up as reverse
current.

The Sah-Noyce-Shockley analysis gives the result above, where $W$ is
the depletion width and $\tau_g$ is an effective generation lifetime
(typically a few $\tau_n$). For a one-sided n+/p junction with
$N_A \ll N_D$ the depletion width simplifies to

$$ W \approx \sqrt{\frac{2 \varepsilon_{si} (\Phi_0 + V_R)}{q N_A}} $$

which sits almost entirely on the lightly doped substrate side.

The temperature scaling is now $n_i$, not $n_i^2$. The exponential
in $n_i$ has $E_g/(2kT)$ and the density-of-states prefactor is
$T^{3/2}$ rather than $T^3$, so the slope is roughly half that of
$I_S$. $I_{gen}$ doubles every $8$-$10\, K$ near room temperature.
At low and moderate temperatures, where $n_i$ is small, this
slower-scaling term still dominates because it has the smaller
exponent. As temperature rises and $n_i$ grows by many decades, the
steeper $I_S \propto n_i^2$ eventually overtakes it.

The $1/\tau_g$ in $I_{gen}$ also drifts with temperature: with
$\tau \propto T^{-1/2}$ the generation term picks up an extra
$\sqrt{T}$ factor on top of the $n_i W$ scaling, which is why at the
top of the sweep $I_{gen}$ does not flatten out as much as one might
expect from $n_i$ alone.

The reverse bias $V_R$ enters through $W$, so $I_{gen}$ has a weak
$\sqrt{V_R}$ dependence. Diffusion current $I_S$ is essentially
independent of bias once the junction is reverse-biased by more than
a few $kT/q$. This is the standard way to separate the two
experimentally: $I_S$ saturates, $I_{gen}$ grows with $\sqrt{V_R}$.

-->

---

## Antenna ndiode, 200 K to 1000 K

<!--pan_doc:

A useful integrated-circuit example is the *antenna diode*. During
plasma etch and ion-implant steps in fabrication, long metal traces
collect charge. If the trace is connected to a transistor gate, the
gate dielectric can break down before the chip ever sees a power
supply. Foundry design rules specify maximum *antenna ratios* (metal
area to gate area) per layer; if a net exceeds the ratio, the routing
tool inserts an *antenna diode* on the net to bleed the plasma charge
to substrate. In normal operation that diode sits reverse-biased and
must contribute negligible static current.

The diode itself is simply an n+ source/drain implant placed in the
NMOS p-well. The relevant doping is:

- p-substrate (handle wafer): $N_{sub} \approx 10^{15}\, cm^{-3}$
- p-well (retrograde, set by short-channel control):
  $N_A \approx 10^{17}-10^{18}\, cm^{-3}$
- n+ source/drain: $N_D \approx 10^{20}\, cm^{-3}$

It is the p-well doping that matters at the junction, because the n+
sits inside the well, not directly on substrate. The effective $N_A$
seen by the antenna ndiode is therefore one to two orders of
magnitude higher than the wafer doping, which makes the depletion
narrower and the reverse leakage *smaller* than a naive
"n+/p-substrate" estimate would suggest.

Figure 5 plots the reverse leakage of such a junction:
$N_A = 10^{17}\, cm^{-3}$ (p-well), $N_D = 10^{20}\, cm^{-3}$
(n+ S/D), $V_R = 1\, V$, swept from 200 K to 1000 K. The current is
plotted *per $1\, \mu m^2$ of junction area*, so a $0.2 \times 0.2\,
\mu m^2$ antenna ndiode is the curve times $0.04$, and a $1 \times
1\, \mu m^2$ diode reads off directly. The script is
`ex/antenna_diode_leakage.py` and reuses the $n_i(T)$ derivation
from `ex/vd.py`.

Three things to take away from the figure:

- Generation current dominates from cryogenic temperatures up to
  roughly $600\, K$, exactly where the steeper $n_i^2$ slope of the
  diffusion term catches up. Above that the diode is in the
  "diffusion-limited" regime.
- Per $\mu m^2$, the leakage is in the $\mathrm{fA}$ range at room
  temperature and climbs many decades by $1000\, K$. A
  $0.2 \times 0.2\, \mu m^2$ antenna ndiode is $25\times$ smaller
  again. For arrayed circuits that rely on stored charge (DRAM,
  image sensors, switched-capacitor sample-and-holds, dynamic CMOS
  logic) this junction leakage ultimately sets retention and hold
  time at elevated temperature.
- The slope on a log axis is set by the $\exp(-E_g/(2kT))$ in $n_i$
  plus the $T^{3/2}$ density-of-states prefactor. Every junction in
  a given silicon process scales with temperature the same way; only
  the absolute level changes with area, doping and lifetime.

It is also worth noting that at the upper end of the sweep $n_i$
approaches and eventually exceeds $N_A$. The diode then loses
junction behaviour and the silicon behaves as an intrinsic resistor.
This is why high-temperature electronics typically uses
wide-bandgap materials such as silicon carbide.

-->

![right fit Reverse leakage of a 0.2x0.2 um$^2$ antenna ndiode\label{fig:antenna_leak}](../media/antenna_diode_leak.pdf)

<!--pan_doc:
<sub>Figure 5: Reverse leakage of an n+/p-well antenna ndiode per
1 um$^2$ of junction area, from 200 K to 1000 K, $V_R = 1$ V.
Multiply by your actual diode area in um$^2$.</sub>
-->

---

<!--pan_skip: -->

#[fit] Thanks!


---

<!--pan_doc:

<sub>Figure 4: Circuit to generate a current proportional to kT</sub>
-->



<!--pan_doc:

# Equations aren't real

> Nature does not care about equations. It just is. 

We know, at the fundamental
level, nature appears to obey the mathematics on quantum mechanics, however, due to
the complexity of nature, it's not possible today (which is not the same as
impossible), to compute exactly how the current in a diode works. We can get
close, by measuring a diode we know well, and hope that the next time we make
the same diode, the behavior will be the same. 

As such, I want to warn you about the "lies" or "simplifications" we tell you. Take the
diode equation above, some parts, like the intrinsic carrier concentration $n_i$
has roots directly from quantum mechanics, with few simplifications, which means
it's likely solid truth, at least for a single unit cell. 

But there is no reason
nature should make all unit cells the same, and infact, we know they are not the
same, we put in dopants. As we scale down to a few nano-meter transistors the simplification
that "all unit cells of silicon are the same, and extend to infinity" is no
longer true, and must be taken into account in how we describe reality.

Other parts, like the exact value of the bandgap $E_g$, the diffusion constant
$D_p$ or diffusion length $L_p$ are macroscopic phenomena,  we can't
expect them to be $100$ % true. The values would be based on measurement, but not
always exact, and maybe, if you rotate your diode 90 degrees on the integrated circuit, the values could be different. 

You should realize that the consequence of our imperfection is that the equations in
electronics should always be taken with a grain of salt. 

Nature does not care about your equations. Nature will easily have the
superposition of trillions of electrons, and they don't have to
agree with your equations. 

But most of the time, the behavior is similar.

## References

-->

[^1]: It doesn't stop being magic just because you know how it works. Terry Pratchett, The Wee Free Men

<!--pan_doc:
[^2]: Simplify as much as possible, but no more. Einstein
[^3]: From the Einstein relation $D = \mu k T$ it does appear that the diffusion coefficient increases with temperature, however, the mobility decreases with temperature. I'm unsure of whether the mobility decreases with the same rate though.
[^4]: This rule of thumb applies to the diffusion-dominated regime. For the generation-dominated regime, which is where most small junctions actually live at room temperature, the doubling interval is closer to 8-10 K because $I_{gen} \propto n_i$ rather than $n_i^2$.
-->
