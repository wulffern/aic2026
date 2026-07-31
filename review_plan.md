# Lecture Technical Review

Per-lecture review of the physics, maths and circuit reasoning — the one
thing `make check` cannot do. Tracked here the way
`tikz_translation_plan.md` tracks figures: one row per lecture, findings
listed until resolved, nothing edited silently.

## Method

For each lecture, in one sitting:

1. Re-derive every displayed equation, or check it against a source
   (CJM, Razavi, a paper in `pdf/aic.bib`).
2. Check every number the prose quotes against the figure or script that
   produces it (`ex/*.py`, `jupyter/*.ipynb`).
3. Check that each figure shows what the surrounding text claims.
4. Classify findings: **mechanical** (typo, wrong subscript, stale number —
   fix directly, note here) vs **substantive** (wrong claim, shaky
   derivation, teaching that depends on an error — bring to the author
   with a proposed correction, do not edit unilaterally).

## Status

Priority order: derivation-heavy lectures first.

| lecture | status | notes |
|---|---|---|
| `lr0_mosfet` | **reviewed 2026-07-30** | findings 4–13 below, all fixed; second-half prose filled in; three figure-review rounds (physics, clarity, in-context) done |
| `l03_refbias` | **reviewed 2026-07-31** | Brokaw R1/R2 inversion and the zero-TC condition fixed; startup section added; Figure 11/12 prose written; findings 4-14 below |
| `l05_sc` | pending | findings 1, 2 below |
| `l06_adc` | pending | finding 3 below |
| `l08_pll` | pending | |
| everything else | later | |

## Findings

Found in passing during the 2026-07-30 build/figure work; not yet resolved.

1. **`l05_sc` IIR stability claim — resolved 2026-07-30.** The first-order
   section now states $|a| < 1$ (with $b$ a pure gain), and per the
   author's direction the python example became a **second-order** filter
   with poles at $z = a \pm jb$ — where "stable as long as $|a+jb| < 1$"
   is exactly true and ties back to the z-plane discussion. New "Second
   order filter" section, regenerated `l5_iir` figure (shared y-axis on
   the two spectra), `ex/iir.py` and `examples/iir.html` updated to match.
2. **`l05_sc` impulse response cases — resolved 2026-07-30.** $k$ is now
   defined in the prose as the initial state $y[0]$.
### `l03_refbias` review, 2026-07-31 — all fixed in place

4. **Brokaw coefficient was inverted.** The figure puts $\Delta V_{BE}$
   across $R_2$ and $2I$ through $R_1$, so the PTAT term is $2R_1/R_2$;
   the text printed $2R_2/R_1$, and the design condition with it. Sizing
   from the old formula gave a reference around 1.85 V.
5. **"Set the bracket to zero" was not the zero-TC condition.** It kills
   the term in bare $T$ but leaves the slope of the $T\ln T$ term:
   $-(m-1)k/q \approx -170$ uV/K, about $-140$ ppm/K, and ~30 mV of droop
   over the range - contradicting the chapter's own Figure 11, which is
   flat to 3 mV. The condition is bracket $= (m-1)k/q$, which puts the
   maximum at $T_0$ and the output at $V_{G0} + (m-1)kT_0/q \approx 1.25$ V.
   Checked numerically: peak at 26.9 C, 2.5 mV spread over -40..125 C,
   which is what the simulation shows.
6. **Constant $g_m$ was described as proportional to the resistor.** It is
   inversely proportional: $g_{m1} = 1/Z$, and the general
   $\frac{2}{R}(1-1/\sqrt{K})$ is now stated.
7. **No startup anywhere in a bias chapter.** New section with
   `l3_startup` figure: the zero-current state satisfies every loop
   equation, $M_{SU}$ conducts only while the NMOS rail is low, and the
   two rules (transient from zero supply, check the device turns off).
8. **1.12 eV used as the 0 K intercept.** 1.12 eV is the 300 K gap, 1.17 eV
   at 0 K, and the extrapolated intercept is 1.20-1.22 V - a voltage, not
   an energy. Contradicted the chapter's own line 11 lines earlier.
9. **$m$ used before definition**, and the $-1$ attributed to $I_S$ alone;
   it comes from the bias current being PTAT. Also flagged that $m\approx3$
   assumes temperature independent diffusion, measured is 3.6-4.
10. **Figures 11 and 12 were unread.** Fig 11 now states the 3 mV / 15 ppm
    scale, the peak as the design's zero-TC point, and the bow as the
    residual term. Fig 12's spread is corner-driven linear tilt (the
    maximum moves), not incomplete curvature cancellation as the text
    claimed.
11. `M_{PC}`/`M_{PD}` named in prose but unlabelled in the figure - labelled.
12. Switched capacitor figure had no number, caption or prose - now
    Figure 22 with $Z = 1/(fC_1)$ and $g_{m1} = fC_1$ stated.
13. $R_4 = R_2/(m-1)$ requires the same resistor type - said.
14. Minor: bipolar "drain" current, LM113 arithmetic, `%` eaten by LaTeX,
    seven typos.

### `lr0_mosfet` review, 2026-07-30 — all fixed in place

4. First weak-inversion equation lacked the slope factor $n$ that every
   later occurrence has; also dropped the spurious $-1$ (that term belongs
   to the $V_{DS}$ dependence, not the gate term).
5. Miller slide: $C_{out} = (1+\frac{1}{2})C \to (1+\frac{1}{A})C$, and the
   unexplained $C_1 \to C_{in} \approx C_{gd}g_m r_{ds}$.
6. Matching summary said strong-inversion $g_m/I_D = \frac{1}{2V_{eff}}$,
   contradicting the correct $\frac{2}{V_{eff}}$ earlier in the same
   lecture; fixed to $\frac{2}{V_{eff}}$.
7. PMOS slide quoted $2.3\times10^5$ m/s as the carrier max velocity —
   that is the **thermal** velocity; the saturation velocity is
   $\approx 1\times10^5$ m/s, as the velocity-saturation slide itself says
   ($10^7$ cm/s). Relabelled and noted the distinction.
8. Channel-length modulation: bracket typo
   $[1+\lambda V_{DS} - \lambda V_{eff})] \to [1+\lambda(V_{DS}-V_{eff})]$.
9. Drain junction cap was written $C_{js}$ (copy of the source one) though
   it uses $V_{DB}$; now $C_{jd}$.
10. Temperature slide's square law was missing $W/L$.
11. Kinget mismatch expression: $\sigma_\ell^2/\ell \to \sigma_\ell^2/\ell^2$
    (relative variance; dimensionally consistent) in all four occurrences.
12. Lorentzian: $\frac{A}{1+f^2/f_0} \to \frac{A}{1+(f/f_0)^2}$.
13. `$$e^{V_eff/nV_T}$$` subscript typo; ~15 spelling/grammar fixes
    (heared, co-valent, Columb, excelent, relativistc, visa versa, …);
    multimeter input resistance 1 → 10 MΩ (typical DMM); status 0.3 → 0.4.

Not changed (author's voice/opinion, or correct as written): the
weak-inversion barrier narrative, the band-diagram "fictive MOSFET"
caveat, $n \approx 1.5$, $I_{D0} = (n-1)\mu_n C_{ox} V_T^2$, the square-law
derivation (checked line by line), Pelgrom, and the intrinsic-gain algebra.

3. **`l06_adc` sampling noise-floor remark.** "The increase in the noise
   level should be due to noise folding, and reduced number of points in
   the FFT, but I have not confirmed (maybe you could confirm?)" — the
   author's own open question. Straightforward to confirm numerically
   from `ex/q.py`: folding of the wideband Gaussian noise plus the
   4× shorter record each contribute; worth writing the two numbers into
   the prose and closing the question.

## `lr0_logic` hidden figures — done 2026-07-31

`py/lecture.py` `_convertImage` used `re.search`, so a Deckset line
carrying two or three images side by side lost all but the first on the
way to `docs/_posts` and to the book. Now uses `re.findall` and emits all
of them. Four figures surfaced: `dff_setup_10`, `dff_hold_-30`,
`l16/logic`, and the second half of the inverter/NOR/NAND row (that last
one sits inside a `pan_skip` block, so it stays slide-only by design).
The three lines in `l04_afe` and `s_need_to_know` are all inside
`pan_skip` or standalone decks, so nothing else changed.

Captions for Figures 33, 34 and 57 had been written as if each pair were
one figure and were rewritten. Note for future captions: LaTeX gives
every image its own float and will scatter a pair across a page or a
column boundary, so *never* write "left plot"/"right plot" for images
from the same source line — identify each by what it shows.

Closed: **`media/l16/stop_activity.pdf` and `reduce_freq.pdf` are not
duplicates.** They render identically only without `-cropbox`; with the
CropBox honoured they are clearly different drawings. Same trap as the
six redrawn figures.

Open question for the author: `media/l16/logic.pdf` carries three
hand-written marks on the cloud labelled `A`, `X` and `C`→`V`. The
caption describes them generically as the points where the dynamic power
equation can be attacked; if the letters mean something more specific it
is worth saying so.

## `l06_adc` — reviewed 2026-07-31

The author's open question in the text ("the increase in the noise level
should be due to noise folding, and reduced number of points in the FFT,
but I have not confirmed") is answered and removed. It is exactly
10 log(nfs) = 6.02 dB, verified over 200 trials. The two mechanisms are
two bookings of the same 6 dB, not additive: the relative floor is
6 sigma^2 / M, the shorter record is the M, and folding is what keeps
sigma^2 from dropping. Filter before decimating and they cancel exactly
(measured 0.02 dB).

Four wrong results, all confirmed numerically or against the figures
before changing anything: the bin-651 "highest harmonic" story (stale
since the quantizer fix — the harmonics are exactly 1/p and bin 651 is
eleventh in rank), 4A^2/2^B for 4A^2/2^{2B} in the SQNR derivation, the
sigma-delta loop equation with the feedback sign inverted, and the NTF
derivation asserting Y = E + HY. Plus the claim that OSR=4 lowers the
near-DC noise floor, which is measurably 0.8 dB the other way.

Still open in this chapter:

- Figure 21 (`l6_q_1_fharm.svg`) is asked to show bin 1397 but at the
  printed size every harmonic of interest is inside |f/fs| < 0.09. It
  wants a zoomed inset before the sentence about it is fully honest.
- `ex/sd_1st.py` and `ex/q.py` use different quantizer definitions
  (mid-tread 2/(2^B-1) versus mid-rise 2/2^B). Both are real converters
  and the text now says so, but making them the same function would be
  better than explaining the difference.

## Queued from the author, 2026-07-31

1. **Script-generated plots to TikZ** — infrastructure done
   2026-07-31, 41 of 44 converted; the remaining 3 have no source.

   `py/tikzplot.py` renders plot data through `tikz/fig_header.tex`, so
   a plot and a schematic on the same page share a font, a line width
   and a palette. `fig_header.tex` gained `groupplots` and a pinned
   `compat=1.16`. See the new section in `tikz/STYLE.md` for how to use
   it from a script.

   Converted, 32 figures: the three switched-capacitor plots, all eight
   ADC spectra, the photovoltaic sweep, the antenna diode leakage, the
   seven gm/ID design curves, the intrinsic carrier concentration, the
   diode forward voltage, the measured gm/ID curve, the four flip-flop
   setup and hold transients, the two ring oscillator sweeps, and the
   three basic NMOS curves. Between them they exercise log axes,
   legends, shaded bands, reference rules and stacked shared-axis
   panels, so the library covers every case in the book.

   **Self-contained since 2026-07-31.** The simulation columns the
   figures use are vendored into `ex/data/` as plain CSV (208 KB, no
   cicsim needed to read them), so every plot regenerates from this
   repository alone — verified by running all of them with `HOME`
   pointed at a nonexistent directory. `make plots` regenerates
   everything, `make plots-one FNAME=<script>` one of them, and
   `make plots-data` re-vendors from aicex and dicex, which is the only
   target that needs those repositories.

   Two things had to be fixed before `make plots` actually reproduced
   the committed figures: six scripts drew noise from an unseeded
   `np.random` (now seeded), and `q.py`, `osr.py` and `sd_1st.py`
   selected their variants through environment variables so a plain run
   emitted one figure of three (each now emits all of them). Run twice,
   `make plots` leaves the tree unchanged.

   **Where the data came from.** `~/pro/aicex/ip/jnw_atr_sky130a/sim` for
   the gm/ID sweeps (cicsim raw files); `~/pro/dicex` for the flip-flop
   timing (`lectures/l14`), the ring oscillator sweeps (`ex4`) and the
   NMOS curves (`sim/spice/NCHIO`). The PLL loop model, the DAC
   linearity pair and the four buck figures need no data at all — they
   were notebook cells computing their own numbers, now scripts in
   `ex/`. None of it is needed to build the book, only to regenerate a
   figure.

   **Two bugs the conversion found.** The PLL phase margin was 55
   degrees because the notebook evaluated the loop on a 50-point grid
   and took the first sample below 0 dB as the crossover; interpolated
   it is 51 degrees at 0.59 MHz. And `l07_buck_pwm_fig_settled` had
   been shipping with an empty middle panel, its y limits pinned to a
   range the settled output voltage never enters. Both are fixed, and
   the scripts now print the numbers the captions quote.

   The gm/ID seven came out of `jupyter/circuits.ipynb` and now come
   from `ex/jnw_gmid.py`, which reads the ngspice sweeps under
   `~/pro/aicex/ip/jnw_atr_sky130a/sim`. A notebook re-run out of order
   produces figures that quietly stop agreeing with each other; one
   script over one pass of the data cannot.

   **Still matplotlib: three, all without a locatable source.**
   `l5_velocity` (lr0_mosfet), `l7_loadreg` (l07_vreg) and
   `cpumax` (lr0_logic). Searched aicex, dicex, aic2025 and the
   notebooks; nothing generates them, so they would have to be
   re-simulated or redrawn by hand rather than converted.

   The two SUN_PLL figures were finished 2026-07-31 from a fresh corner
   sweep and a fresh transient: `SUN_PLL_ROSC_KVCO` (ex/rosc_kvco.py)
   and `sun_pll_lay_typ` (ex/pll_settling.py). The second was also
   *stale* — it showed the loop settling by 8 us, from a netlist with the
   faster schematic oscillator; the current extraction settles at 12.

   One figure that will improve when converted: `pll.pdf` has its
   x-axis label hidden behind the legend box, noted in the `l08_pll`
   review above.

## `l05_sc` — reviewed 2026-07-31

The two findings recorded earlier for this chapter had already been
resolved during the IIR work, so this was a fresh pass.

Fixed: the FIR transfer function summed `z^-1` instead of `z^-i` (three
copies of a one-sample delay, so a pure delay rather than a filter — the
figure's own header comment had it right); the bilinear transform was
missing its `2/T`; three stray parentheses and a bare `C` for `C_1` in
the three switched-capacitor impedance derivations; and the dangling
`V_1 = l` / `V_2 =` labels in the two charge-transfer figures, which were
faithful to the hand-drawn original and read as missing values.

Prose: the chapter asserted `V_n^2 > 2kT/C` with no derivation. Now
derived, including the point that the switch resistance cancels, and the
consequence that halving the noise costs four times the capacitor and
four times the power.

All three open items closed 2026-07-31. The settling requirement said
`\log` where the worked example's 6.9 time constants is `-ln(1/1024)`;
the impedance step now uses the charge *difference* per cycle it always
meant; and the `|a| >= 1` wording is split into three cases so the
marginal one agrees with the z-domain section. Lead-ins written for the
integrator's Z-domain derivation, the non-overlapping clock generator
and the closing example, which is most of the course in one equation and
now has each factor traced back to the chapter it came from.

**This chapter is done.**

## `l08_pll` — reviewed 2026-07-31

The chapter's own admission — "I don't remember why, check in the book"
— about `K_pd = I_cp / 2 pi` is answered and removed. A phase error
`dphi` holds UP high for `dphi / 2 pi` of the reference period, so the
average current is `I_cp dphi / 2 pi` and the gain per radian follows.
Two consequences added: the gain is independent of reference frequency,
and it is an *average*, valid only because the filter is slow compared
with the reference.

Figure 17 is now checked against the linear model's own precondition
rather than merely described: 0 dB crossing near 500 kHz against an
8 MHz reference is a sixteenth, clearing the one-tenth rule.

Fixed: `t` used as both limit and integration variable in the phase
definition; a stray `K_vco` in a chapter that says `K_osc` everywhere
else; `VPLF` for `VLPF`, which is a net name and would send a reader
looking for something that does not exist; three other spellings.

Verified and left alone: both loop-filter expressions (the second-order
one checked term by term against `(R + 1/sC1) || 1/sC2`), `L(s)`,
`phi_d/phi_in = 1/(1+L)`, `K_osc = 2 pi df/dV`, `K_div = 1/N`, and
Figures 17 and 18, which do show the 55 degree phase margin and the
256 MHz settling their captions claim.

Still open:

- Figure 17's top panel has its x-axis label hidden behind the legend
  box. It is one of the matplotlib figures covered by the plot-to-TikZ
  item above.
- The "why clocks" narrative at the start is long and slide-shaped, but
  it is the author's voice and reads fine as prose. Left alone.

**The review queue is now empty.** Every lecture with recorded findings
has been through a pass. The remaining work is the plot-to-TikZ item and
Phase 3 of the TikZ plan.


## Simulation runtime, measured 2026-07-31

The SUN_PLL transient was suspected of being slow for want of
`.option sparse`. It is already enabled and confirmed active in the log
("Using SPARSE 1.3 as Direct Linear Solver"), so there is nothing there.
Threading is not the constraint either: the runs draw 133-165 % CPU on a
10 core machine despite `set num_threads=16`, so the serial sparse solve
dominates.

The cost is `reltol`. Measured on one netlist, one corner, 15 us, with
only that option changed:

| reltol | run | raw |
|---|---|---|
| 1e-3 | 339 s | 8.2 MB |
| 1e-4 | 1452 s | 34.6 MB |

**4.3x**, and the settled frequency agrees to 0.07-0.15 % (256.11 vs
255.98 MHz). They differ by 4-7 % during the slewing transient, where
the frequency is sweeping through hundreds of megahertz anyway. The
production value of 1e-4 is ten times tighter than ngspice's own
default.

Not changed: that is a signoff-accuracy decision for the author. The
`#ifdef` pattern already in `tran.spi` would take a third tier
(Debug 1e-2, default 1e-3, Signoff 1e-4).

## `l07_vreg` — reviewed 2026-07-31

First of the chapters that had no recorded findings and had never been
read end to end.

The one that mattered: the chapter says a good switched converter
reaches the low nineties and then shows a model at 67 %, with nothing
reconciling them. Measured from the model, the entire 0.48 mW loss is
`I_rms^2 R` in the switches — 0.477 mW, within half a percent — because
the inductor carries 21.8 mA RMS of ripple to deliver 1 mA of DC. That
is now the paragraph it should always have been, including why light
loads are inefficient and what the fix costs.

Also: the pass-fet range is five orders of magnitude, not "almost 6",
and the paragraph now says why a five-decade range is a compensation
problem rather than a boast. `V_{VDDH}` for `V_{DDH}`.

Verified and left alone: the 400 W / 320 W / 6400 degree thermal
example, the 93 % comparison, both capacitive converter ratios, the
reverse common-gate argument for NMOS pass-fet PSRR (ripple on the
output really is pushed back onto the input with gain), and the
zero-cross comparator.

Open, and it is figure work rather than prose: **Figure 8 has no axis
labels at all**, only the raw filename in a legend. Its testbench is at
`cnr_atr_sky130nm/sim/LDO_PFET/loadreg.spi` but the output directory is
gone, so redrawing it means re-running the sweep. That is also what
would move `l7_loadreg` off the last-three matplotlib list.

## Review queue, second pass

Chapters that have never been read end to end, in the order I would take
them:

1. ~~`l07_vreg`~~ — done 2026-07-31
2. `l09_osc` — oscillators, and the chapter most likely to have algebra
3. `l04_dac` — its figures were reviewed but the prose was not
4. `l10_lpradio`
5. the project lectures
