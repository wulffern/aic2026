# Interactive Examples — Remaining Work

Status as of the merge of PR #11 (`8d5d344`). The interactive pages themselves
are done and live: 15 pages in `examples/`, copied to `docs/assets/examples/`
by `make examples`, linked from `docs/examples.md` and from eight lectures.

What follows is what was deliberately *not* done, and why.

## 1. Source-material discrepancies in `ex/` — RESOLVED 2026-07-30

All three fixed per the author's decision ("fix according to prose"):
`ex/iir.py` multiplies `a` into `y[i-1]`; `ex/sd_1st.py` has a clamped
2^B-level quantiser (B=1 is sign()) and a 0.7 FS input, dither stays 1/4 LSB;
the `np.linspace(0,N,N)` time bases became `np.arange(N)` in `dt.py`,
`sub.py`, `iir.py`, `q.py` and `osr.py`. `dt.py` keeps its record
deliberately incoherent (f1 = 233.5/N) so `l05_sc`'s windowing paragraph
stays true. All ten committed figures were regenerated and compared against
the old ones; the `l06_adc` harmonic-bin prose was updated (the highest spur
is now bin 651 — the folded 11th harmonic, 2048−1397 — replacing the old
"bin 396" discussion). The pages' script-quirk notes were rewritten as
historical. Original findings below, kept for the record.

## 1-old. Source-material discrepancies in `ex/`

The interactive pages were written by porting the `ex/*.py` scripts to
JavaScript and cross-checking the numbers. Three of the scripts turned out to
disagree with what the surrounding lecture text says they do. In each case the
page documents the deviation (see `examples/README.md`) and implements the
textbook behaviour, but the Python script and the committed `media/*.svg`
figures still have the original behaviour. Fixing any of them changes figures
that appear in the book and on the site, so they need the author's call on
intent.

### 1.1 `ex/iir.py` — the pole is on the unit circle

`a = 0.25` is defined, printed as part of `z = a + 1j*b`, and used to seed
`y[0] = a`, but it is never multiplied into `y[i-1]`. The recursion is

```python
y[i] = x[i] + y[i-1]
```

so the filter is a pure accumulator with a pole at exactly z = 1, not at
z = 0.25 as `z = a + 1j*b` implies. The magnitude response therefore has an
infinite DC gain rather than the finite 1/(1-a) the lecture discusses.

- Fix: `y[i] = x[i] + a*y[i-1]`.
- Blast radius: `media/l5_iir.svg`, and the `l05_sc` text that reads the plot.

### 1.2 `ex/sd_1st.py` — the "1-bit" quantiser is not clamped

The quantiser rounds to a grid but never saturates, so with the default input
amplitude the modulator output takes seven distinct values, not two. That
makes the noise-shaping plot optimistic relative to a real 1-bit modulator: a
true 2-level quantiser overloads at that amplitude and the measured SNR slope
collapses (measured on the page: 7.0 / 7.6 / 4.1 / 13.0 dB per octave of OSR
at full scale, versus 9.1 / 7.7 / 7.7 at 0.7 full scale).

- Fix: clamp the quantiser output to its two levels, and drop the default
  input amplitude to ~0.7 FS so the loop stays stable.
- Blast radius: `media/l6_sd_*.svg` and the noise-shaping discussion in
  `l06_adc`.

### 1.3 `np.linspace(0, N, N)` — off-by-one time base

`ex/dt.py`, `ex/sub.py`, `ex/iir.py`, `ex/q.py` and `ex/osr.py` all build their
time vector with `np.linspace(0, N, N)`, whose step is N/(N-1) rather than 1.
Every tone is therefore slightly off-bin.

This one is the most interesting, because the bug is load-bearing for the
teaching: **`l05_sc`'s paragraph explaining why a Hanning window is needed is
only true because of this bug.** Fix the time base with
`np.arange(N)` (or `np.linspace(0, N, N, endpoint=False)`) and every tone lands
exactly on a bin, the record becomes coherent, and the rectangular window is
already leak-free — which makes the window paragraph obsolete.

- Options: (a) leave it and add a sentence saying the record is deliberately
  incoherent so the window has something to do; (b) fix the time base and
  rewrite the windowing paragraph around a deliberately incoherent second
  example.
- Blast radius: `media/l5_dtfig.svg`, `media/l5_iir.svg`, `media/l6_q_*.svg`,
  `media/l6_osr_*.svg`, and the windowing text in `l05_sc`.

## 2. Unverified: the live site

The pages were verified locally with headless Chromium, and every plotted
quantity was cross-checked against numpy or against the source notebook. The
deployed pages at `https://wulffern.github.io/aic2026/examples/` have **not**
been opened — the sandbox egress proxy returns 403 for `github.io`, for both
`curl` and the fetch tool. Worth a manual click-through of the gallery and one
or two pages after the next Pages deploy, mainly to confirm that
`make examples` put the files where `docs/examples.md` expects them.

## 3. Already fixed (for the record)

Fixed in PR #11, no action needed:

- `calc_ni` in `ex/vd.py` and `ex/antenna_diode_leakage.py` was missing the
  6^(2/3) valley degeneracy in the electron DOS effective mass. This moved the
  five derived leakage numbers quoted in `l00_diode`, which were updated to
  match.
- `jupyter/buck.ipynb` reported a negative efficiency because the settled-state
  average was taken over a window that included the start-up transient. It now
  warm-starts from `IX_initial` and averages over the last 50 µs; efficiency
  reads 67.51 %.
- The "bits" sliders on `quantization.html`, `oversampling.html` and
  `sigma-delta.html` produced 2^B + 1 levels instead of 2^B.
