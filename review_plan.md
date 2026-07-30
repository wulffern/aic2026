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
| `lr0_mosfet` | pending | first in line |
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
3. **`l06_adc` sampling noise-floor remark.** "The increase in the noise
   level should be due to noise folding, and reduced number of points in
   the FFT, but I have not confirmed (maybe you could confirm?)" — the
   author's own open question. Straightforward to confirm numerically
   from `ex/q.py`: folding of the wideband Gaussian noise plus the
   4× shorter record each contribute; worth writing the two numbers into
   the prose and closing the question.
