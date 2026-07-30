# examples/

Interactive versions of the Python scripts in [`ex/`](../ex) and the notebooks
in [`jupyter/`](../jupyter), in the style of
[wulffern/cicadc](https://github.com/wulffern/cicadc): one self-contained page
per script, dark canvas plots, sliders for the constants that are hard-coded at
the top of the Python.

`make examples` copies this directory to `docs/assets/examples/`, which is
published with the site. Lectures link to
`https://wulffern.github.io/aic2026/assets/examples/<page>.html`, an absolute
URL so the links also work from the PDF and the EPUB.

## Layout

    index.html            gallery
    sampling.html         ex/dt.py, ex/sub.py
    iir.html              ex/iir.py
    quantization.html     ex/q.py, ex/quantization.py
    oversampling.html     ex/osr.py
    sigma-delta.html      ex/sd_1st.py
    diode.html            ex/vd.py
    antenna-leakage.html  ex/antenna_diode_leakage.py
    pv.html               ex/pv.py, ex/pv_v.py
    biquad.html           jupyter/biquad.ipynb
    buck.html             jupyter/buck.ipynb
    buck-pfm.html         jupyter/buck_pfm.ipynb
    buck-type3.html       closed loop buck.ipynb only describes
    xosc.html             jupyter/xosc.ipynb
    pll.html              sun_pll_sky130nm/jupyter/pll.ipynb
    common/aic.css        shared chrome (cicadc palette)
    common/plot.js        canvas plotting: panels, axes, log axes, legends
    common/dsp.js         FFT, Hann, quantiser, sigma-delta loop, SNR
    common/semi.js        n_i(T), I_S, depletion width, straight-line fit
    common/lti.js         complex arithmetic, Bode, state space, polynomial roots

Four notebooks deliberately have no page. `jupyter/dt.ipynb` and
`jupyter/diode_voltage.ipynb` are the same models as `ex/dt.py` and `ex/vd.py`,
already covered by `sampling.html` and `diode.html`. `jupyter/circuits.ipynb`
and `sun_pll_sky130nm/jupyter/pfd.ipynb` read real SPICE output through
`cicsim`, so there is no model to turn into sliders.

## Rules

No dependencies and no network access. No CDN, no MathJax, no charting library:
these pages are read on trains and from local clones, and a page that needs the
network is a page that does not work when you need it. Formulas are HTML
(`<sub>`, `<sup>`), plots are canvas.

Each page has the same shape, so one is a template for the next: header, signal
chain strip, canvas, controls, readouts, legend, prose, footer. The controls are
wired by `UI.bind()` from `data-bind` attributes, and `Plot.mount()` handles
device pixel ratio and resizing. A page's own script is then usually two
functions, `compute()` and `render()`.

Every page states which script it comes from and where it deviates. Three
historical script bugs the pages originally worked around were fixed in the
scripts on 2026-07-30 (`ex/iir.py` now multiplies `a` into `y[i-1]`; the
`np.linspace(0,N,N)` time bases became `np.arange(N)`; `ex/sd_1st.py` grew a
clamped 2^B-level quantiser and a 0.7 FS input). The remaining deviations, all
deliberate and all noted on the page itself:

* `quantization.html` and `oversampling.html` keep the old off-bin
  `np.linspace(0,N,N)` time base behind the coherent-sampling checkbox,
  because the leakage failure mode (SQNR pinned near 69 dB regardless of
  bits) is worth seeing.
* `sigma-delta.html` keeps the old unclamped quantiser behind a checkbox for
  the same reason: a "1-bit" converter emitting seven levels is a good
  cautionary tale.
* Noise is seeded (`DSP.randn(n, seed)`) rather than reseeded per call, so the
  floor stays put while a slider moves.
* A "Bits" slider means B bits = 2^B levels, on every page. `ex/q.py`'s
  `adc()` (quoted verbatim in the lecture, so left alone) counts *fractional*
  bits — its step is 2^-bits, so a signal spanning +/-1 gets 2^(bits+1)+1
  levels, five of them at "1 bit", and beats 6.02B + 1.76 by a whole bit.
  `quantization.html` and `oversampling.html` therefore default to
  `DSP.quantizeBits` (mid-riser, 2^B levels, saturating), with the script's
  version one checkbox away.
* `biquad.html` and `xosc.html` do by hand the algebra their notebooks hand to
  sympy, because a CAS is far too big to ship to a browser. The biquad result
  was checked against the notebook's three flow-graph equations at 200 random
  points (agreement to 1e-15); the crystal page uses the closed forms for f_s
  and f_p rather than `np.argmax` over a sampled curve.
* `buck.html` defaults to starting at the steady-state operating point. R*C and
  the switching period are four decades apart, so a cold start cannot be run to
  settling and resolved at the same time without a very long simulation. This
  page is what turned up the bug in `jupyter/buck.ipynb`, since fixed, where the
  same averaging over an unsettled run printed a negative efficiency; unticking
  the warm start reproduces it.

## Checking a page against its script

`common/dsp.js` mirrors numpy closely enough to compare numbers directly. For
example, `ex/q.py` before the 2026-07-30 time-base fix gave an SQNR of
15.1 dB, and `quantization.html` reproduces that with the script `adc()`
ticked and coherent sampling unticked. When changing either side, check a few
numbers rather than the shape of the curve. Reference values, all reproduced
by the pages:

| source | quantity | value |
|---|---|---|
| `ex/q.py` (script adc(), 1 bit) | SQNR | 15.1 dB |
| `quantization.html` (B-bit, B=4..12) | SQNR vs 6.02B+1.76 | within 0.5 dB |
| `sigma-delta.html` (1 bit, amp 0.7) | shaped SNR per octave | ~9 dB |
| `ex/vd.py` | n_i(300 K), dV_D/dT, 0 K intercept | 9.01e9 /cm3, -0.954 mV/K, 1.200 V |
| `jupyter/xosc.ipynb` | f_p at C_P = 5 pF | 10.070874 MHz |
| `jupyter/pll.ipynb` | w_pll, w_z, Q | 458 kHz, 413 kHz, 0.90 |
| `jupyter/buck.ipynb` | V_o, efficiency (settled mode) | 0.9989 V, 67.5 % |
| `jupyter/buck_pfm.ipynb` | V_o, efficiency | 1.016 V, 92 % |
| `buck-type3.html` | crossover, PM, slowest CL pole | 50.1 kHz, 60.0 deg, 3.24 kHz |
