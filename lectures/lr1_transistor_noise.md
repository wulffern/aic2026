footer: Carsten Wulff 2026
slidenumbers:true
autoscale:true
theme: Plain Jane, 1
text:  Helvetica
header:  Helvetica
date: 2026-10-08


<!--pan_skip: -->

# Transistor noise, from Schrödinger to one trap

<!--pan_author: Written by Claude (Anthropic) -- ideas and review by Carsten~Wulff, carsten@wulff.no -->

<!--pan_title: Transistor Noise -->

<!--pan_doc:

**Keywords:** Schrödinger, Dirac, Spin, Fermi-Dirac, Planck, Shot Noise, Tunnelling, Golden Rule, Multiphonon Capture, Arrhenius, Random Telegraph Noise, Lorentzian, McWhorter, Flicker Noise

-->

---

<!--pan_doc:

*This chapter was written by Claude, Anthropic's AI, from an outline
and direction by Carsten Wulff, who reviewed and edited the result.*

The noise chapter treats noise as statistics: a mean, a variance, a
spectral density. The MOSFET chapter writes down $4kT\gamma g_m$ and
$K_f/(WLC_{ox}f)$ and moves on. Neither says where the numbers come
from.

This chapter follows one of them all the way down. The target is the
single trap: one broken bond in the oxide that grabs an electron from
the channel, holds it for a while, and lets it go. On a small
transistor you can watch it happen - the drain current jumps between
two levels like a telegraph key. Add up enough of them and you get
the flicker noise of every MOSFET you will ever design with.

Every step of that story is quantum mechanics. Schrödinger gives the
trap its wave function and the channel electron its tail into the
oxide. Dirac gives the electron its spin, which fixes how traps fill,
and gives us the rule for how fast they fill. We will not solve
anything hard. We will follow the chain, and put a number on each link.

-->

# Three things that come in pieces

<!--pan_doc:

Classical physics has no noise floor. A classical charge fluid could
be as smooth as you like. Real noise exists because three things come
in pieces, and each piece gives one kind of transistor noise.

-->

| What is discrete | Noise it gives |
|:----------------:|:--------------:|
| Charge, $q$ | Shot noise, $2qI$ |
| Energy per mode, $hf$ | Thermal noise, $4kTR$ |
| Localized states, traps | Telegraph noise, then $1/f$ |

<!--pan_doc:

The first two are old news, and we spend a slide on each. The third
is the subject of this chapter.

-->

---

#[fit] The equations

---

## Schrödinger

$$ i\hbar\frac{\partial}{\partial t}\Psi(\vec{r},t) = \left[-\frac{\hbar^2}{2m}\nabla^2 + V(\vec{r})\right]\Psi(\vec{r},t) $$

Stationary states, $\Psi = \psi(\vec{r})e^{-iEt/\hbar}$

$$ -\frac{\hbar^2}{2m}\nabla^2\psi + V\psi = E\psi $$

<!--pan_doc:

The wave function $\Psi$ is a probability amplitude:
$\vert\Psi\vert^2$ is the probability of finding the electron at
$\vec{r}$. The potential $V$ is everything the electron feels - the
silicon nuclei, the other electrons, the gate field.

Three solutions of this equation carry the whole chapter. In a
periodic crystal it gives energy bands, and near a band edge the
electron moves as if free, with an effective mass. In the surface
well of an inverted MOSFET it gives subbands, and the "2d sheet" of
the MOSFET chapter. And at a broken bond it gives a bound state: a
wave function localized to an atom or two, with an energy in the
bandgap. That is a trap.

The equation has one more thing to say, and we need it. Where $E < V$
the solution does not stop. It decays as $e^{-\kappa x}$, with
$\kappa = \sqrt{2m(V-E)}/\hbar$. The electron has a tail inside the
barrier.

-->

---

## Dirac

$$ i\hbar\frac{\partial\Psi}{\partial t} = \left(c\,\vec{\alpha}\cdot\vec{p} + \beta mc^2\right)\Psi $$

- Relativistic, and $\Psi$ has four components: spin comes out, it is not put in
- Spin-$\frac{1}{2}$ particles obey Pauli: one electron per state
- Pauli gives Fermi-Dirac statistics
- Electron magnetic moment, $g = 2$

<!--pan_doc:

Schrödinger's equation is not relativistic, and it knows nothing about
spin. Dirac wrote the relativistic version in 1928 [@dirac28], and
spin fell out of it: the wave function needs four components, and two
of them are spin up and spin down. So did the electron's magnetic
moment, with $g = 2$.

In silicon the electrons are slow, and Dirac's equation reduces to
Schrödinger's with a spin label attached. That label is not a detail.
Spin-$\frac{1}{2}$ particles obey the Pauli exclusion principle - at
most one electron per quantum state - and Pauli is why electrons fill
states by the Fermi-Dirac distribution and not by Boltzmann's.

Dirac gave us one more tool. In 1927 he worked out how fast a quantum
system jumps from one state to another under a small perturbation
[@dirac27]. Fermi later called the result his "golden rule", and the
name stuck to Fermi. We will use it to compute how fast a trap grabs an
electron.

-->

---

## Fermi-Dirac

$$ f(E) = \frac{1}{1 + e^{(E - E_F)/kT}} $$

$$ n = \int_{E_C}^{\infty} N(E) f(E)\, dE $$

<!--pan_doc:

The probability that a state at energy $E$ holds an electron. The MOSFET
chapter used it to count the electrons in the conduction band: the
density of states $N(E)$, from Schrödinger, times the occupation
$f(E)$, from Dirac and Pauli. We will use it again in two places: to
decide which traps can switch, and to find out where the $kT$ in
flicker noise comes from.

-->

---

#[fit] The old news

---

## Thermal noise is Planck

$$ S_V(f) = 4R\frac{hf}{e^{hf/kT}-1} \approx 4kTR \quad \text{if } hf \ll kT $$

$$ \frac{kT}{h} = 6.25 \text{ THz at 300 K} $$

<!--pan_doc:

Nyquist derived thermal noise in 1928 [@nyquist28], and he did not
write $4kTR$. He wrote the Planck form above. A resistor in thermal
equilibrium feeds energy into every electrical mode of the circuit
around it, and each mode, being quantized in steps of $hf$, holds the
Planck average energy. Below $kT/h$ every mode holds $kT$, and the
density is flat.

At room temperature $kT/h$ is 6 THz. No circuit in this course gets
near it, which is why we may forget Planck and write $4kTR$. A
superconducting qubit at 10 mK has $kT/h$ = 200 MHz, and there the
quantum correction is the whole design problem.

-->

---

## Shot noise is the electron charge

$$ \overline{i_n^2} = 2qI\,\Delta f $$

In weak inversion, with $\gamma = n/2$ and $g_m = I_D/nV_T$

$$ 4kT\gamma g_m = 4kT\frac{n}{2}\frac{I_D}{nV_T} = 2qI_D $$

<!--pan_doc:

Current that crosses a barrier one electron at a time is a stream of
independent arrivals, and the arrivals are random. That is shot noise.

In weak inversion the MOSFET is exactly that: electrons diffuse over the
source barrier one at a time. Put the weak-inversion $\gamma$ and $g_m$
into the thermal noise formula and it becomes $2qI_D$. Thermal noise
and shot noise in a subthreshold transistor are the same noise,
described twice.

-->

---

#[fit] One trap

---

## What a trap is

- A broken bond at the Si/SiO2 interface, or a defect a few nm into the oxide
- A bound state: $\psi_T$ localized to an atom or two
- An energy $E_T$ inside the silicon bandgap
- The unpaired electron has spin: traps were first identified by electron spin resonance

<!--pan_doc:

Silicon and its oxide do not fit perfectly. At the interface some
silicon atoms are left with a bond that has no partner - a dangling
bond - and the amorphous oxide has its own defects, oxygen vacancies
and strained bonds, a few nanometres deep. Solve Schrödinger's equation
around one and you get a bound state: a wave function localized to an
atom or two, at an energy inside the bandgap.

A dangling bond holding one electron has an unpaired spin. That spin
has a magnetic moment with $g \approx 2$, Dirac's number, and it is how
these defects were found and named: by electron spin resonance on
oxidized silicon wafers.

-->

---

## The channel electron has a tail

$$ \psi_{ch}(x) \propto e^{-\kappa x} \text{ in the oxide}, \quad \kappa = \frac{\sqrt{2 m_{ox}(\Phi_B - E)}}{\hbar} $$

$$ \Phi_B = 3.1 \text{ eV}, \quad m_{ox} \approx 0.5 m_0 \Rightarrow \kappa \approx 6.4 \text{ nm}^{-1} $$

![inline](../media/mos_2deg_tikz.pdf)

<!--pan_doc:
<sub>Figure 1: The inversion layer in depth, from the MOSFET chapter. The density is drawn as zero at the interface - the oxide forbids the electrons there - but forbids is too strong. A small tail leaks into the oxide</sub>

The MOSFET chapter drew the inversion electrons in the lowest subband
of the surface well, with a density that goes to zero at the oxide. It
is close to zero, not zero. The oxide is a barrier 3.1 eV high, and the
Schrödinger equation inside a barrier gives an exponential.

Put the numbers in: with an effective mass in the oxide of half the
free electron mass, $\kappa$ is 6.4 per nanometre. The probability
density goes as $\vert\psi\vert^2 \propto e^{-2\kappa x}$, and falls a
decade every 0.18 nm. Small, but a trap one nanometre into the oxide
still overlaps the channel.

-->

---

## Tunnelling sets the time constant

![inline fit](../media/rtsq_tunnel_tikz.pdf)

<!--pan_doc:
<sub>Figure 2: Above: a trap in the oxide with its level near the Fermi level can swap an electron with the channel. Below: the channel electron density on a log axis. In the oxide it is a straight line, a decade every 0.18 nm, and the time constant of a trap is set by where on that line it sits</sub>

An electron in the channel and an empty trap at depth $x_T$ are two
states with almost the same energy, coupled through the overlap of
their wave functions. The rate of hopping from one to the other is
proportional to the channel density at the trap. Figure 2 shows the
consequence: time constants that span microseconds to months, from
traps a nanometre apart.

-->

---

## Dirac's golden rule

$$ \frac{1}{\tau} = \frac{2\pi}{\hbar}\left\vert\langle\psi_T\vert H'\vert\psi_{ch}\rangle\right\vert^2 \rho(E) $$

$$ \left\vert\langle\psi_T\vert H'\vert\psi_{ch}\rangle\right\vert^2 \propto e^{-2\kappa x_T} $$

$$ \tau = \tau_0 e^{x_T/\lambda}, \quad \lambda = \frac{1}{2\kappa} \approx 0.08 \text{ nm} $$

| Trap depth | $\tau$ ($\tau_0$ = 0.1 ns) |
|:----------:|:--------------------------:|
| 0 nm  | 0.1 ns |
| 1 nm  | 40 µs |
| 2 nm  | 13 s |
| 3 nm  | 2 months |

<!--pan_doc:

The rate of a transition is the squared matrix element between the two
states times the density of final states - Dirac's result [@dirac27],
written in Dirac's own bra-ket notation. The trap wave function is
tiny, so the matrix element samples the channel wave function where
the trap sits, and the squared matrix element inherits
$e^{-2\kappa x_T}$.

The table is the punchline. Three nanometres of oxide hold sixteen
decades of time constant. No other mechanism in a transistor produces
a spread like that, and it is exactly what $1/f$ noise needs, as we
will see. The prefactor $\tau_0$ is rough - textbooks quote 0.1 ns
give or take a decade - but the slope is set by the barrier, and
that is the part that matters. McWhorter used the same tunnelling
picture in 1957 [@mcwhorter57], twenty years before anyone saw a
single trap.

-->

---

## The lattice must move

![inline](../media/rtsq_ccd_tikz.pdf)

<!--pan_doc:
<sub>Figure 3: The configuration coordinate diagram. The trap is empty on the blue curve and full on the red one, and the atoms around a full trap sit somewhere else. The electron can only hop where the curves cross, so it waits for a thermal fluctuation of the lattice to get there</sub>

Tunnelling is not the whole story, and the measurements say so: trap
time constants depend strongly on temperature, and tunnelling through
an oxide barrier barely does.

The missing piece is the atoms. When a trap captures an electron its
charge changes, and the bonds around it stretch or bend to suit. The
total energy - electron plus lattice - is a parabola in the lattice
coordinate, and there is one parabola for the empty trap and another
for the full one, shifted sideways. The electron cannot drop straight
from one to the other: at a fixed lattice position the full state
costs more energy than the electron has, and the lattice cannot absorb
the difference in one go. The hop happens where the two curves cross,
and the lattice reaches the crossing only by a thermal fluctuation.

That wait is $e^{E_B/kT}$. In golden-rule language, the density of
final states $\rho(E)$ now counts lattice vibrations - phonons - and
the overlap of lattice states before and after is what makes the rate
thermally activated. Henry and Lang worked out this multiphonon capture
in 1977 [@henry77].

-->

---

## Capture and emission

$$ \frac{1}{\tau_c} \propto e^{-x_T/\lambda}\, e^{-E_B/kT}\, n_s $$

$$ \frac{\tau_c}{\tau_e} = \frac{1}{g}e^{(E_T - E_F)/kT}, \quad g = 2 $$

$$ \frac{\partial \ln(\tau_c/\tau_e)}{\partial V_{GS}} = -\frac{q}{kT}\frac{x_T}{t_{ox}} $$

<!--pan_doc:

Capture needs an electron in the channel near the trap, so its rate
grows with the inversion density $n_s$. Beyond that it is the product
of the two factors we have: tunnel to depth $x_T$, and wait for the
lattice.

Emission is the reverse trip, and the ratio of the two is fixed by
thermal equilibrium: the trap must be occupied with the Fermi-Dirac
probability. That is where spin enters. An empty trap can accept an
electron of either spin. A second electron costs extra Coulomb energy,
so it belongs to a different level, further up. So "full" is two
quantum states and "empty" is one, and the factor $g = 2$ is the Dirac
electron's two spin states.

A trap only switches if $E_T$ is within a few $kT$ of $E_F$. Far below,
it is always full; far above, always empty; either way it is silent.

The gate moves $E_F$ past $E_T$. In strong inversion the surface
potential is pinned, so extra gate voltage drops across the oxide, and
a trap a fraction $x_T/t_{ox}$ of the way to the gate sees that
fraction of it. Measure $\tau_c/\tau_e$ against $V_{GS}$, and the slope
tells you how deep the trap is. Kirton and Uren made a catalogue of
traps this way [@kirton89].

-->

---

#[fit] What one trap looks like

---

![fit](../media/jnwtt_rts_tikz.pdf)

<!--pan_doc:
<sub>Figure 4: Sixty seconds of the GR06 temperature sensor from the measurement chapter, slow drift removed. The reading sits on one level, drops by about 0.6 K to another, stays a second or two, and returns</sub>

This is a chip from this course. The temperature sensor's output is
not a fuzzy band but two levels, which is what a single trap would do:
empty, or full. The sensor turns currents and voltages into a
temperature reading, so the step shows up in kelvin. Whether it really
is a trap, and in which transistor, is a question we come back to once
we know how big one trap's step can be.

Ralls and colleagues first saw the same thing in the drain current of
small MOSFETs in 1984 [@ralls84]. It goes by three names: random
telegraph noise, popcorn noise, and burst noise.

-->

---

![fit](../media/jnwtt_rts_life_tikz.pdf)

<!--pan_doc:
<sub>Figure 5: The GR06 trap's mean time in the low state against inverse thermal energy. A straight line is an Arrhenius law, with an activation energy of 226 meV</sub>

And here is the lattice, measured. The time the trap stays in one state
falls exponentially with temperature: a straight line against $1/kT$,
slope 226 meV. Tunnelling alone would give a time constant almost
independent of temperature. The 226 meV is the $E_B$ of Figure 3 plus
the Fermi-Dirac shift of the previous slide - the lattice has to move
before the electron can.

-->

---

## Two states, one Lorentzian

$$ R_x(\tau) = \Delta I^2 \frac{\tau_c\tau_e}{(\tau_c + \tau_e)^2} e^{-\vert\tau\vert/\tau_0}, \quad \frac{1}{\tau_0} = \frac{1}{\tau_c} + \frac{1}{\tau_e} $$

$$ S_x(f) = 4\int_0^\infty R_x(\tau)\cos(\omega\tau)d\tau = \frac{4\,\Delta I^2}{(\tau_c+\tau_e)\left[\left(\frac{1}{\tau_c}+\frac{1}{\tau_e}\right)^2 + (2\pi f)^2\right]} $$

<!--pan_doc:

From here on the quantum mechanics is done, and we are back in the
noise chapter. A trap has two states, and the time it spends in each is
random, with means $\tau_c$ and $\tau_e$. Since the trap has no memory
of how long it has waited, the autocorrelation decays exponentially.
Fourier transform it with the one-sided definition of the noise chapter
and you get a Lorentzian: flat below the corner
$f_0 = 1/(2\pi\tau_0)$, falling as $1/f^2$ above it. Machlup worked it
out in 1954 [@machlup54].

The factor $\tau_c\tau_e/(\tau_c+\tau_e)^2$ is the variance of a coin
that lands full a fraction $f_T$ of the time, $f_T(1-f_T)$. It is
largest when $E_T = E_F$ and the coin is fair.

-->

---

## How big is one step?

$$ \Delta V_T = \frac{q}{C_{ox}WL}\left(1 - \frac{x_T}{t_{ox}}\right), \quad \Delta I_D = g_m \Delta V_T $$

| W x L | $\Delta V_T$ | $\Delta I_D/I_D$ at $g_m/I_D$ = 20 |
|:-----:|:-------:|:-------:|
| 0.42 µm x 0.15 µm | 305 µV | 0.6 % |
| 1 µm x 1 µm | 19 µV | 0.04 % |
| 10 µm x 10 µm | 0.19 µV | 0.0004 % |

<sub>sky130 nfet_01v8: $t_{oxe}$ = 4.148 nm, $C_{ox}$ = 8.3 fF/µm²</sub>

<!--pan_doc:

One electron in the oxide images one electron's worth of charge onto
the gate and the channel. Seen from the gate it is a threshold shift
$q/(C_{ox}WL)$, slightly less for a trap deep in the oxide, and the
drain current moves by $g_m$ times that. The oxide thickness is in the
model card: sky130's 1.8 V nfet has an electrical oxide thickness
$t_{oxe}$ of 4.148 nm, the pfet 4.23 nm, which with $\varepsilon_{ox} =
3.9\varepsilon_0$ is 8.3 and 8.2 fF/µm².

In a minimum-size sky130 transistor that is a third of a millivolt -
more than half a percent of the current, from a single electron. Measured steps are often larger
still, because the current does not flow evenly across the channel
and a trap sitting on a busy path blocks more than its share. The
charged trap also scatters the electrons that pass it, so mobility
fluctuates along with the number of carriers. Hung's unified model
combines the two effects [@hung90].

-->

---

## How many traps?

Per decade of time constant

$$ N \approx N_t \cdot kT \cdot W L \cdot \lambda \ln 10 $$

$N_t = 4 \times 10^{17}$ cm$^{-3}$eV$^{-1}$ (sky130 nfet), $kT$ = 26 meV, $\lambda$ = 0.1 nm

| W x L | Active traps per decade |
|:-----:|:-----------:|
| 0.42 µm x 0.15 µm | 0.15 |
| 1 µm x 1 µm | 2.4 |
| 10 µm x 10 µm | 240 |

<!--pan_doc:

A trap is only noisy if its level is near $E_F$ and its time constant
is inside the band you care about. Weighted by how noisy each one is,
the energy window is $kT$ wide (we will meet that integral again). A
decade of time constant is $\lambda\ln 10$ of depth, about a quarter
of a nanometre. So count the traps in a slab that thick and $kT$ wide.

The trap density is in the model card too, if you know where to look.
Read through Hung's model, the flicker noise parameter NOIA of sky130's
nfet is 2.5e42 J$^{-1}$m$^{-3}$, which is $4 \times 10^{17}$
cm$^{-3}$eV$^{-1}$; the pfet's 1.5e42 is $2.4 \times 10^{17}$. The next
part of the chapter shows why the noise parameter is a trap density.

The count is the point. A minimum-size transistor has, on average,
about one active trap per seven decades of time constant. Most such devices are quiet, and
the unlucky one has a large telegraph signal. Noise on small devices is
not a number but a distribution, and it varies from device to device
like mismatch does. Large devices have hundreds of traps per decade, and
their steps blur into something smooth.

-->

---

#[fit] Which transistor in GR06?

---

## How GR06 works

- A PTAT current, divided by 100 in two mirrors, charges a 53.8 fF MIM capacitor
- A comparator trips when the ramp reaches $V_{ref} = V_{DD}/3$, from three poly resistors
- Pulse width $t = C V_{ref}/I \approx$ 7.1 µs, so $I \approx$ 4.5 nA
- Every analog transistor is a 3.2/0.94 µm unit, deep in weak inversion; the reset switch is 1.92/0.22

$$ \frac{\Delta t}{t} = \frac{\Delta V_{ref} + V_{os}}{V_{ref}} - \frac{\Delta I}{I} = 1760 \text{ ppm} $$

<!--pan_doc:

Before blaming a transistor, write down what the pulse width depends
on. A step of 0.53 K at 304 K is a fractional step of 1760 ppm in the
pulse width. That is 1.06 mV at the comparator input, or 0.18 % of
the charging current.

The reference is a resistive divider from the supply. Anything that
steps the supply by 0.18 % - 3 mV - would look exactly like a trap. That
is the first suspect to rule out.

-->

---

## Is it the supply?

![inline fit](../media/jnwtt_trap_supply_tikz.pdf)

<!--pan_doc:
<sub>Figure 6: One minute of GR06 and GR07, recorded together on the same die, as fractional deviations on the same scale. While GR06 reads low, GR07 moves $-11 \pm 12$ ppm. A supply step would have moved it $-1763$ ppm</sub>

GR07, the other sensor on the die, compares against $V_{DD}/4$ from its
own divider and reports a frequency instead of a width. A fractional
supply step moves both by the same amount, with opposite signs. So
record both at once, label each moment by GR06's state, and ask how
far GR07 moves between the two labels.

It moves $-11 \pm 12$ ppm. The error bar comes from the data: slide
GR06's labels 20 s to 400 s against GR07, where nothing real can line
up, and the same calculation scatters by 12 ppm. A supply step would
have given $-1763$ ppm. The supply is less than about 2 % of the step.

-->

---

## Memoryless

![inline fit](../media/jnwtt_trap_dwell_tikz.pdf)

$$ \tau_0 = \left(\frac{1}{3.8 \text{ s}} + \frac{1}{1.5 \text{ s}}\right)^{-1} = 1.1 \text{ s}, \quad f_0 = \frac{1}{2\pi\tau_0} = 0.15 \text{ Hz} $$

<!--pan_doc:
<sub>Figure 7: Twenty-six minutes of GR06 at about 31 °C, cut into visits to each level. The fraction of visits that lasted longer than $t$ falls as a straight line on a log axis - an exponential. The dashed lines are exponentials with the measured means, not fits</sub>

A trap has no memory: the chance it lets go in the next millisecond does
not depend on how long it has held on. That makes the dwell times
exponential, and a log survival plot turns an exponential into a
straight line. Both levels give one. The short end of the low state
falls a little faster than the line, likely from short visits the
detector splits or misses at this noise level.

The two means put the Lorentzian corner at 0.15 Hz.

-->

---

## The suspects

| Device | W/L [µm] | $\Delta V_T$, one electron | $\Delta t/t$ |
|:------|:-------:|:-------:|:-------:|
| Comparator input pair | 4 x 3.2/0.94 | 1.6 µV | 3 ppm |
| Comparator load | 3.2/0.94 | 6.4 µV | 11 ppm |
| Reset switch, off leakage | 1.92/0.22 | 46 µV | < 1 ppm |
| PTAT core | 3.2/0.94 | 6.4 µV | 30 to 90 ppm |
| Ramp current mirror unit | 3.2/0.94 | 6.4 µV | 190 ppm |
| **Measured** | | | **1760 ppm** |

<sub>$C_{ox}$ = 8.2 fF/µm² (pfet), 8.3 fF/µm² (nfet), from $t_{oxe}$ in the sky130 model cards; $nV_T$ = 34 mV</sub>

<!--pan_doc:

Every number in the last column is one electron's
$\Delta V_T = q/(C_{ox}WL)$, carried through to the pulse width.

The comparator is the least likely culprit. Its input pair is the
largest device in the sensor, so one electron shifts its offset by
1.6 µV, and the step needs 1.06 mV. Its load refers to the input at
about the same weight as the pair, because both run at the same current
in weak inversion.

The reset switch is small, but it is off during the ramp. It leaks
about 2 pA against 4.5 nA, and one electron changes that leakage by a
tenth of a percent.

The current path is the best candidate. Each of the three single units
that carry the ramp current - the PTAT output and the two
hundredfold-division mirrors - converts a threshold step straight into
current, $\Delta I/I = \Delta V_T/nV_T$, because in weak inversion
$g_m/I_D = 1/nV_T$. That is 190 ppm, nine times short of the
measurement.

Nine times is not a contradiction. The $\Delta V_T$ formula assumes the
charge is spread evenly over the gate. In weak inversion it is not:
the random dopants leave a lumpy barrier, the current crowds into the
low spots, and a trap above one of them removes more than its share.
The trapped charge also scatters the electrons that pass it [@hung90].
Both push the step up, and in weak inversion they can push it up a
lot. A 3 µm² pfet has about four active traps per decade of time
constant, so one near a second is no surprise.

-->

---

## How to tell

| Source | Step $\Delta t/t$ vs $T$ | Step $\Delta t/t$ vs $V_{DD}$ |
|:------|:-------:|:-------:|
| Comparator offset | constant | $\propto 1/V_{DD}$ |
| Supply | ruled out | ruled out |
| Weak inversion current | $\propto 1/T$ or faster | constant |
| Measured | falls, 2500 to 1750 ppm from 5 °C to 45 °C | not measured |

<!--pan_doc:

A threshold step is a fixed voltage. At the comparator it is compared
with $V_{ref}$, so its fractional effect does not depend on temperature
and scales as $1/V_{DD}$. In a weak-inversion mirror it is compared with
$nkT/q$, so its fractional effect falls with temperature and does not
care about the supply.

The chamber sweep of the measurement chapter has the temperature
column. The fractional step falls from about 2500 ppm at 5 °C to
1750 ppm at 45 °C - faster than $1/T$, and the points scatter, but it
falls. That points at the current path. Above 50 °C the two levels
merge into the noise and the step estimate is biased low, so those
points are left out.

The supply column would settle it. Run the board's core supply at a
few voltages around 1.8 V: a step that stays at 1760 ppm is in the
current path, a step that scales as $1/V_{DD}$ is at the comparator.

-->

---

#[fit] Many traps

---

## McWhorter: uniform in depth is $1/f$

$$ \tau = \tau_0 e^{x/\lambda} \Rightarrow dx = \lambda\frac{d\tau}{\tau} $$

$$ S(f) \propto \int_{\tau_1}^{\tau_2} \frac{\tau}{1 + \omega^2\tau^2}\frac{d\tau}{\tau} = \frac{1}{\omega}\left[\arctan(\omega\tau)\right]_{\tau_1}^{\tau_2} \approx \frac{\pi}{2\omega} $$

for $1/\tau_2 \ll \omega \ll 1/\tau_1$

<!--pan_doc:

Spread the traps evenly in depth. Each one contributes a Lorentzian,
$\tau/(1+\omega^2\tau^2)$. Since $\tau$ is exponential in depth, an even
spread in depth is an even spread in $\ln\tau$: as many traps per
decade of time constant at a microsecond as at a second. Add up the
Lorentzians, and the sum is exactly $1/f$ between the slowest and the
fastest trap.

This is McWhorter's model [@mcwhorter57]. It needs nothing exotic -
just traps scattered through the oxide, and the exponential that
Schrödinger put in the tail of the channel electron.

-->

---

![fit](../media/rts_noise_tikz.pdf)

<!--pan_doc:
<sub>Figure 8: From the MOSFET chapter. One trap gives a two-level signal and a Lorentzian. Forty traps with time constants spread evenly over three decades sum to $1/f$, slope $-1.02$</sub>

The same argument, done numerically. Nothing was fitted: forty
Lorentzians spread evenly in $\log\tau$, added. Above the corner of the
fastest trap the slope steepens back towards $1/f^2$, because there are
no faster traps left. A real flicker noise spectrum ends the same way,
for the same reason.

-->

---

## Back to the design equation

$$ S_{V_G}(f) = \frac{q^2\, kT\, \lambda\, N_t}{W L\, C_{ox}^2\, f} $$

- $\lambda$: Schrödinger, the tunnelling length
- $kT$: Fermi-Dirac, $\int f(1-f)\,dE = kT$
- $N_t$: the process, how broken the oxide is
- $1/WL$: more traps, each smaller - $WL \times (1/WL)^2$

<!--pan_doc:

Do the McWhorter integral with every factor kept and you get the
number-fluctuation model of flicker noise. It is the $K_f/(WLC_{ox}f)$
of the MOSFET chapter, with $K_f$ opened up.

Every factor is a piece of this chapter. The $\lambda$ is the 0.08 nm
tunnelling length. The $kT$ is not thermal noise sneaking in: it is the
width of the energy window where traps switch, since only traps near
$E_F$ are noisy and the variance of each, $f_T(1-f_T)$, integrates over
energy to exactly $kT$. The $N_t$ is the process. And the $1/WL$ is
the competition between more traps and smaller steps: a bigger device
has more traps, proportional to $WL$, but each step in $V_T$ shrinks as
$1/WL$, and power goes as the step squared.

That is why flicker noise falls with gate area and nothing else in the
hand formula, and why a PMOS, with its holes a little further from the
interface, is often quieter.

-->

---

## The model card knows

BSIM4, flicker noise model 1, as used by ngspice:

$$ S_{I_D} \propto \frac{q^2\, kT\, \mu\, I_D}{10^{10}\, f^{EF} A_{bulk} C_{oxe} L^2} \left[\text{NOIA} \ln(\ldots) + \ldots\right] $$

| sky130 01v8 | $t_{oxe}$ | NOIA [J$^{-1}$m$^{-3}$] | $N_t$ [cm$^{-3}$eV$^{-1}$] | EF |
|:-----:|:-----:|:-----:|:-----:|:-----:|
| nfet | 4.148 nm | 2.5e42 | $4.0 \times 10^{17}$ | 0.84 |
| pfet | 4.23 nm | 1.5e42 | $2.4 \times 10^{17}$ | 1.0 |

<!--pan_doc:

The simulator's flicker noise model is this chapter, compiled. BSIM4's
unified model is Hung's [@hung90], and Hung's is McWhorter's number
fluctuation plus the mobility fluctuation of a charged trap. The
constant $10^{10}$ in the denominator is not a fudge: it is the
tunnelling attenuation coefficient, $1/\lambda$ in metres, so the
simulator assumes $\lambda$ = 0.1 nm, close to our 0.08 nm. The $kT$
is the Fermi-Dirac window. And NOIA, the parameter the foundry fits to
measured noise, is the trap density $N_t$ in J$^{-1}$m$^{-3}$ - divide by
the electron charge to get eV.

EF is the exponent of $f$. The pfet's is 1, McWhorter's ideal. The
nfet's is 0.84: its spectrum falls slower than $1/f$, so it has more
fast traps than an even spread would give. In the tunnelling picture
the traps are not uniform in depth - they crowd towards the interface,
where the time constants are short.

So the next time a simulation hands you a flicker noise corner, you
know what it is made of: a trap density, a tunnelling length, a Fermi
window and an area.

-->

---

#[fit] The trap has spin

---

## Reading one spin with a transistor

- A submicron MOSFET with one telegraphing trap
- Microwaves at the electron spin resonance frequency, $hf = g\mu_B B$
- At resonance the telegraph statistics change
- $g \approx 2$: the Dirac electron, seen in the drain current

<!--pan_doc:

The last slide closes the loop to Dirac. In 2004 Xiao, Martin,
Yablonovitch and Jiang took a small silicon MOSFET with a single
telegraphing trap, put it in a magnetic field, and shone microwaves on
it [@xiao04]. When the microwave photon energy matched the spin flip
energy of the trapped electron, $g\mu_B B$, the telegraph signal
changed. A second electron can join the first only with the opposite
spin, and the microwaves were flipping the first one. They had read out
the spin of a single electron through the drain current of a
transistor.

The noise we fight in a bandgap reference is the same physics that
silicon spin qubits are built on. One trap, one electron, one spin.

-->

---

# Summary

<!--pan_doc:

The one-page version of this chapter:

-->

- Noise exists because charge, energy and states come in pieces
- Thermal noise is Planck, and flat below 6 THz; in weak inversion it is shot noise
- A trap is a bound state in the oxide, and the channel electron reaches it by tunnelling: a decade of time constant per 0.18 nm of depth
- Capture also moves the lattice, which makes it Arrhenius - 226 meV on GR06
- Spin and Pauli fix how traps fill; only traps near $E_F$ switch
- One trap is a telegraph signal and a Lorentzian; many traps, even in depth, are $1/f$
- Small transistors have less than one active trap per few decades, so their noise varies from device to device
- The simulator's flicker model is the same physics: sky130's NOIA is a trap density, 4e17 per cm³ per eV
- GR06's step is a trap, not the supply: GR07 does not follow, and the dwell times are exponential. The current mirrors are the likeliest home

---

# Would you like to know more?

<!--pan_doc:

The review of individual traps in MOSFETs, and the place to start [@kirton89]

The first clear observation of single traps in silicon inversion layers [@ralls84]

The tunnelling model of $1/f$ noise [@mcwhorter57], and the spectrum of a two-state signal [@machlup54]

Multiphonon capture, the reason traps are thermally activated [@henry77]

Number and mobility fluctuation combined into one flicker noise model [@hung90]

Dirac's two papers: the golden rule [@dirac27] and the electron [@dirac28]

Thermal noise from Planck, in the original [@nyquist28]

The spin of one trapped electron, read through a transistor [@xiao04]

The solid state noise reference [@ziel]

-->
