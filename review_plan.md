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
| `lr0_mosfet` | **reviewed 2026-07-30** | findings 4–13 below, all fixed |
| `l03_refbias` | pending | bandgap curvature maths; Figure 11/12 prose |
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
