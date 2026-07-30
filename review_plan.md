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

1. **`l05_sc` IIR stability claim.** The text says "if $a > 1$, then the
   filter is unstable. Same if $b > 1$. As long as $|a + jb| < 1$ the
   filter should be stable." For $H(z) = b/(z-a)$ the pole is at $z = a$
   and stability depends **only** on $|a| < 1$; $b$ is a gain and
   $z = a + jb$ is not the pole location. The `z = a + 1j*b` line in
   `ex/iir.py` (quoted in the lecture) encodes the same confusion.
   Substantive: needs the author's intended framing.
2. **`l05_sc` impulse response cases.** $h[n]$ is given as $k$ for $n<1$
   and $a^{n-1}b + a^n k$ for $n \ge 1$ — the $k$ terms look like they
   come from a non-zero initial state ($y[0]=a$ in the script?) but $k$
   is never defined in the text. Check against AIC 13.x (the text already
   notes "Fig 13.12 in AIC is wrong").
3. **`l06_adc` sampling noise-floor remark.** "The increase in the noise
   level should be due to noise folding, and reduced number of points in
   the FFT, but I have not confirmed (maybe you could confirm?)" — the
   author's own open question. Straightforward to confirm numerically
   from `ex/q.py`: folding of the wideband Gaussian noise plus the
   4× shorter record each contribute; worth writing the two numbers into
   the prose and closing the question.
