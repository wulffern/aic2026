# examples/

Interactive versions of the Python scripts in [`ex/`](../ex), in the style of
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
    common/aic.css        shared chrome (cicadc palette)
    common/plot.js        canvas plotting: panels, axes, log axes, legends
    common/dsp.js         FFT, Hann, quantiser, sigma-delta loop, SNR
    common/semi.js        n_i(T), I_S, depletion width, straight-line fit

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

## Checking a page against its script

`common/dsp.js` mirrors numpy closely enough to compare numbers directly. For
example, `ex/q.py` at its defaults gives an SQNR of 15.1 dB, and so does
`quantization.html`. When changing either side, check a few numbers rather than
the shape of the curve.
