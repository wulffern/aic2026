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

Every page states which script it comes from and where it deviates. There are a
few deviations, all deliberate and all noted on the page itself:

* `iir.html` makes the feedback coefficient a slider. The Python computes `a`
  but never multiplies it into `y[i-1]`, so the script really runs with a = 1.
* `quantization.html` and `oversampling.html` default to an integer time vector
  rather than the scripts' `np.linspace(0,N,N)`, whose step is N/(N-1). The
  off-bin tone that produces leaks through the window sidelobes and caps the
  measured SQNR near 69 dB regardless of the number of bits. Both pages keep the
  original behaviour behind a checkbox, because the difference is worth seeing.
* `sigma-delta.html` offers a clamp on the quantiser. The Python does not clamp,
  so its "1-bit" converter emits more than two levels whenever the integrator
  state runs past full scale.
* Noise is seeded (`DSP.randn(n, seed)`) rather than reseeded per call, so the
  floor stays put while a slider moves.
* `biquad.html` and `xosc.html` do by hand the algebra their notebooks hand to
  sympy, because a CAS is far too big to ship to a browser. The biquad result
  was checked against the notebook's three flow-graph equations at 200 random
  points (agreement to 1e-15); the crystal page uses the closed forms for f_s
  and f_p rather than `np.argmax` over a sampled curve.
* `buck.html` defaults to starting at the steady-state operating point. R*C and
  the switching period are four decades apart, so a cold start cannot be run to
  settling and resolved at the same time without a very long simulation. The
  notebook's cold start is a checkbox away, and with it the efficiency readout
  goes negative exactly as the notebook's does.

## Checking a page against its script

`common/dsp.js` mirrors numpy closely enough to compare numbers directly. For
example, `ex/q.py` at its defaults gives an SQNR of 15.1 dB, and so does
`quantization.html`. When changing either side, check a few numbers rather than
the shape of the curve. Reference values, all reproduced by the pages:

| source | quantity | value |
|---|---|---|
| `ex/q.py` | SQNR at 1 bit | 15.1 dB |
| `ex/vd.py` | dV_D/dT, 0 K intercept | -0.799 mV/K, 1.200 V |
| `jupyter/xosc.ipynb` | f_p at C_P = 5 pF | 10.070874 MHz |
| `jupyter/pll.ipynb` | w_pll, w_z, Q | 458 kHz, 413 kHz, 0.90 |
| `jupyter/buck.ipynb` | V_o, efficiency (settled) | 0.999 V, 70.8 % |
| `jupyter/buck_pfm.ipynb` | V_o, efficiency | 1.016 V, 92 % |
| `buck-type3.html` | crossover, PM, slowest CL pole | 50.1 kHz, 60.0 deg, 3.24 kHz |
