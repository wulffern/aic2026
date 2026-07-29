---
layout: page
title: Examples
permalink: /examples/
---

The Python scripts in [`ex/`](https://github.com/wulffern/aic2026/tree/main/ex)
also exist as interactive pages. The plots are the same plots; the difference is
that the constants at the top of the script are sliders, so you can find out
what happens when you change them without waiting for matplotlib. Each page says
which script it came from and where it deviates from it.

**[Open the gallery](/aic2026/assets/examples/index.html)**

# Switched capacitor circuits

- [Sampling](/aic2026/assets/examples/sampling.html) — a pulse train multiplies
  in time and copies the spectrum to every multiple of the sample rate. Move
  the tone past Nyquist and watch it alias.
  <sub>`ex/dt.py`, `ex/sub.py`</sub>
- [First order IIR](/aic2026/assets/examples/iir.html) — one line of feedback,
  one pole, and the z-plane, the time domain and the spectrum side by side.
  <sub>`ex/iir.py`</sub>

# Data converters

- [Quantization](/aic2026/assets/examples/quantization.html) — where
  SQNR = 6.02B + 1.76 dB comes from, and where it stops being true.
  <sub>`ex/q.py`, `ex/quantization.py`</sub>
- [Oversampling](/aic2026/assets/examples/oversampling.html) — three dB per
  octave, measured, against the ideal line.
  <sub>`ex/osr.py`</sub>
- [Noise shaping](/aic2026/assets/examples/sigma-delta.html) — a first order
  sigma-delta loop, its integrator state, its bitstream, and nine dB per octave.
  <sub>`ex/sd_1st.py`</sub>

# Diodes, references and energy sources

- [Diode vs temperature](/aic2026/assets/examples/diode.html) — n<sub>i</sub>(T)
  to I<sub>S</sub>(T) to V<sub>D</sub>(T), and the curvature a first-order
  bandgap cannot correct.
  <sub>`ex/vd.py`</sub>
- [Antenna diode leakage](/aic2026/assets/examples/antenna-leakage.html) —
  diffusion and generation leakage from 200 K to 1000 K, with the plasma process
  steps shaded.
  <sub>`ex/antenna_diode_leakage.py`</sub>
- [PV cell](/aic2026/assets/examples/pv.html) — I-V and P-V curves, the maximum
  power point, and why harvesting is a current problem.
  <sub>`ex/pv.py`, `ex/pv_v.py`</sub>

# Elsewhere

[cicadc](https://wulffern.github.io/cicadc/) is the same idea taken further: a
full ADC visualiser with second-order and leapfrog modulators, a decimation
filter, and a car driving along the waveform.
