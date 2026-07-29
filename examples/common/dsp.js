/* Signal-processing helpers shared by the interactive examples.
 *
 * Everything here mirrors what the scripts in ex/ do with numpy, deliberately
 * closely: the point of these pages is that a student can put the Python and
 * the page side by side and see the same operation. Where numpy has a
 * convenience the browser lacks (np.hanning, np.fft.fftshift) it is
 * reimplemented rather than approximated.
 */

'use strict';

const DSP = (function () {

  // ── Vectors ───────────────────────────────────────────────────────────────

  /** np.arange(0, n) */
  function arange(n) {
    const a = new Float64Array(n);
    for (let i = 0; i < n; i++) a[i] = i;
    return a;
  }

  /** np.linspace(a, b, n) — endpoint included, as numpy does by default. */
  function linspace(a, b, n) {
    const o = new Float64Array(n);
    if (n === 1) { o[0] = a; return o; }
    const d = (b - a) / (n - 1);
    for (let i = 0; i < n; i++) o[i] = a + i * d;
    return o;
  }

  /** np.logspace-ish: n points from a to b, geometrically spaced. */
  function logspace(a, b, n) {
    const o = new Float64Array(n);
    const la = Math.log(a), lb = Math.log(b);
    for (let i = 0; i < n; i++) o[i] = Math.exp(la + (lb - la) * i / (n - 1));
    return o;
  }

  function maxAbs(x) {
    let m = 0;
    for (let i = 0; i < x.length; i++) { const v = Math.abs(x[i]); if (v > m) m = v; }
    return m;
  }

  /** 20*log10(|x|), floored so an exact zero does not become -Infinity. */
  function db20(v, floor = 1e-12) { return 20 * Math.log10(Math.max(Math.abs(v), floor)); }

  function toDb(x, floor = 1e-12) {
    const o = new Float64Array(x.length);
    for (let i = 0; i < x.length; i++) o[i] = db20(x[i], floor);
    return o;
  }

  // ── Random ────────────────────────────────────────────────────────────────
  //
  // Seeded, so a page redraws identically when a slider that does not touch
  // the noise moves. np.random.randn() would reseed on every call and the
  // noise floor would shimmer under the cursor.

  /** mulberry32 — small, fast, good enough for a noise floor. */
  function rng(seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /** Box-Muller on top of `uniform`, i.e. np.random.randn(). */
  function randnFactory(uniform) {
    let spare = null;
    return function () {
      if (spare !== null) { const s = spare; spare = null; return s; }
      let u, v, s;
      do {
        u = 2 * uniform() - 1;
        v = 2 * uniform() - 1;
        s = u * u + v * v;
      } while (s === 0 || s >= 1);
      const f = Math.sqrt(-2 * Math.log(s) / s);
      spare = v * f;
      return u * f;
    };
  }

  /** n samples of standard normal noise, reproducible for a given seed. */
  function randn(n, seed = 1) {
    const g = randnFactory(rng(seed));
    const o = new Float64Array(n);
    for (let i = 0; i < n; i++) o[i] = g();
    return o;
  }

  // ── Windows ───────────────────────────────────────────────────────────────

  /**
   * np.hanning(N+1)[0:N] — the periodic Hann window the ex/ scripts use.
   *
   * np.hanning(M) is symmetric, w[i] = 0.5 - 0.5*cos(2*pi*i/(M-1)); asking for
   * M = N+1 and dropping the last point gives the periodic window, which is
   * the right one for an FFT because it does not repeat the endpoint.
   */
  function hann(N) {
    const w = new Float64Array(N);
    for (let i = 0; i < N; i++) w[i] = 0.5 - 0.5 * Math.cos(2 * Math.PI * i / N);
    return w;
  }

  function ones(N) {
    const w = new Float64Array(N);
    w.fill(1);
    return w;
  }

  // ── FFT ───────────────────────────────────────────────────────────────────

  /**
   * In-place radix-2 Cooley-Tukey, same sign convention as np.fft.fft.
   * `re.length` must be a power of two.
   */
  function fft(re, im) {
    const n = re.length;
    if ((n & (n - 1)) !== 0) throw new Error('fft: length must be a power of two');

    // Bit-reversal permutation.
    for (let i = 1, j = 0; i < n; i++) {
      let bit = n >> 1;
      for (; j & bit; bit >>= 1) j ^= bit;
      j ^= bit;
      if (i < j) {
        let t = re[i]; re[i] = re[j]; re[j] = t;
        t = im[i]; im[i] = im[j]; im[j] = t;
      }
    }

    for (let len = 2; len <= n; len <<= 1) {
      const half = len >> 1;
      const ang = -2 * Math.PI / len;
      const wr0 = Math.cos(ang), wi0 = Math.sin(ang);
      for (let i = 0; i < n; i += len) {
        let wr = 1, wi = 0;
        for (let k = 0; k < half; k++) {
          const ar = re[i + k], ai = im[i + k];
          const br = re[i + k + half], bi = im[i + k + half];
          const tr = br * wr - bi * wi;
          const ti = br * wi + bi * wr;
          re[i + k] = ar + tr; im[i + k] = ai + ti;
          re[i + k + half] = ar - tr; im[i + k + half] = ai - ti;
          const nwr = wr * wr0 - wi * wi0;
          wi = wr * wi0 + wi * wr0;
          wr = nwr;
        }
      }
    }
  }

  /** np.fft.fftshift for even length: move the zero-frequency bin to the middle. */
  function fftshift(x) {
    const n = x.length, h = n >> 1;
    const o = new Float64Array(n);
    for (let i = 0; i < n; i++) o[i] = x[(i + h) % n];
    return o;
  }

  /**
   * |fftshift(fft(w * x))| — the `freqDomain()` of ex/q.py and ex/osr.py,
   * without the normalisation, which differs from script to script.
   *
   * Returns a two-sided magnitude spectrum: bin n/2 is DC, and the x axis runs
   * from -fs/2 to +fs/2, which is why the plots show two spikes for one sine.
   */
  function magSpectrum(x, useHann = true) {
    const N = x.length;
    const w = useHann ? hann(N) : ones(N);
    const re = new Float64Array(N), im = new Float64Array(N);
    for (let i = 0; i < N; i++) re[i] = x[i] * w[i];
    fft(re, im);
    const mag = new Float64Array(N);
    for (let i = 0; i < N; i++) mag[i] = Math.hypot(re[i], im[i]);
    return fftshift(mag);
  }

  /** Normalise a spectrum to its own peak, as `freqDomain()` in ex/q.py does. */
  function normalise(mag) {
    const m = maxAbs(mag) || 1;
    const o = new Float64Array(mag.length);
    for (let i = 0; i < mag.length; i++) o[i] = mag[i] / m;
    return o;
  }

  // ── Converters ────────────────────────────────────────────────────────────

  /**
   * The `adc()` of ex/q.py: uniform mid-tread quantiser, step 2^-bits.
   *
   * Note that `bits` here counts FRACTIONAL bits, not converter resolution.
   * The step is 2^-bits, so a signal spanning +/-1 gets 2^(bits+1) steps and
   * 2^(bits+1)+1 distinct levels — five of them at bits = 1, which is not what
   * "1 bit" usually means. See quantizeBits() for the conventional reading.
   */
  function quantize(x, bits) {
    const levels = Math.pow(2, bits);
    const o = new Float64Array(x.length);
    for (let i = 0; i < x.length; i++) o[i] = Math.round(x[i] * levels) / levels;
    return o;
  }

  /**
   * A conventional B-bit converter over a full scale of +/-fs: a mid-riser
   * quantiser with exactly 2^B levels and step 2*fs/2^B, saturating at the
   * end codes.
   *
   * Mid-riser rather than mid-tread because it is the one that gives 2^B
   * levels exactly, and because at B = 1 it is a plain comparator — which is
   * what a one-bit converter is supposed to be.
   */
  function quantizeBits(x, bits, fs = 1) {
    const levels = Math.pow(2, bits);
    const d = 2 * fs / levels;
    const lo = -fs + d / 2, hi = fs - d / 2;
    const o = new Float64Array(x.length);
    for (let i = 0; i < x.length; i++) {
      const q = Math.floor(x[i] / d) * d + d / 2;
      o[i] = q < lo ? lo : q > hi ? hi : q;
    }
    return o;
  }

  /**
   * The quantiser a sigma-delta loop wants: 2^B levels spread evenly from -1
   * to +1 inclusive, step 2/(2^B - 1).
   *
   * The feedback DAC has to reach the full input range or the loop cannot
   * cancel a full-scale input, so the outermost levels sit exactly at +/-1
   * rather than half a step inside. At B = 1 this is sign(x), which is what a
   * one-bit modulator actually is.
   */
  function quantizeSD(v, bits) {
    const n = Math.pow(2, bits);
    if (n < 2) return v >= 0 ? 1 : -1;
    const d = 2 / (n - 1);
    const k = Math.round((v + 1) / d);
    return -1 + Math.max(0, Math.min(n - 1, k)) * d;
  }

  /** Number of distinct values in a vector, for reporting actual level count. */
  function levelCount(x, tol = 1e-9) {
    const seen = new Set();
    for (let i = 0; i < x.length; i++) seen.add(Math.round(x[i] / tol));
    return seen.size;
  }

  /** Keep every nfs'th sample: `x[0::nfs]`. */
  function decimate(x, nfs) {
    const n = Math.floor((x.length + nfs - 1) / nfs);
    const o = new Float64Array(n);
    for (let i = 0; i < n; i++) o[i] = x[i * nfs];
    return o;
  }

  /**
   * The `oversample()` of ex/osr.py: a running sum of OSR samples, i.e. a
   * boxcar/sinc filter, with no decimation afterwards. Written the same way
   * the Python is (forward-looking sum, truncated at the end of the vector) so
   * the two produce identical output.
   */
  function oversample(x, OSR) {
    const N = x.length;
    const y = new Float64Array(N);
    for (let n = 0; n < N; n++) {
      let s = 0;
      for (let k = 0; k < OSR; k++) if (n + k < N) s += x[n + k];
      y[n] = s;
    }
    return y;
  }

  /**
   * The 1st-order sigma-delta loop of ex/sd_1st.py.
   *
   *   x[n] = x[n-1] + (u[n] - y[n-1])          integrator
   *   y[n] = quantise(x[n] + dither)           1-bit (or B-bit) quantiser
   *
   * `dither` is the amplitude of the Gaussian added at the quantiser input,
   * matching `dither*np.random.randn()/4` in the Python (dither = 0 or 1).
   *
   * `script` selects the Python's own quantiser: an unclamped mid-tread with
   * step 2^-bits, which at bits = 1 emits seven levels rather than two and is
   * therefore not the one-bit modulator it is described as. The default is
   * quantizeSD, a proper B-bit quantiser reaching +/-1.
   */
  function sigmaDelta1(u, bits, dither, seed = 7, script = false) {
    const M = u.length;
    const levels = Math.pow(2, bits);
    const g = randnFactory(rng(seed));
    const y = new Float64Array(M);
    const x = new Float64Array(M);
    for (let n = 1; n < M; n++) {
      x[n] = x[n - 1] + (u[n] - y[n - 1]);
      const v = x[n] + dither * g() / 4 / levels;
      y[n] = script ? Math.round(x[n] * levels + dither * g() / 4) / levels
                    : quantizeSD(v, bits);
    }
    return { y, x };
  }

  /** Drop the first `n` samples, as sd_1st.py does to skip the settling. */
  function skip(x, n) { return x.slice(n); }

  // ── Measurements ──────────────────────────────────────────────────────────

  /**
   * Signal-to-noise ratio of a one-sided magnitude spectrum, in dB.
   *
   * `sig` is the bin the tone sits in; `half` bins either side of it are taken
   * as signal (a Hann window spreads a tone over three bins). Everything else
   * below `band` counts as noise. DC is excluded — the quantisers here are
   * mid-tread and their offset is not what we are measuring.
   */
  function snr(mag, sig, band, half = 3) {
    let ps = 0, pn = 0;
    for (let i = 1; i < band; i++) {
      const p = mag[i] * mag[i];
      if (Math.abs(i - sig) <= half) ps += p; else pn += p;
    }
    if (ps <= 0 || pn <= 0) return NaN;
    return 10 * Math.log10(ps / pn);
  }

  /** Effective number of bits from an SNR, inverting SQNR = 6.02 B + 1.76. */
  function enob(snrDb) { return (snrDb - 1.76) / 6.02; }

  /** One-sided magnitude spectrum (DC .. fs/2), for the SNR helpers above. */
  function magOneSided(x, useHann = true) {
    const N = x.length;
    const w = useHann ? hann(N) : ones(N);
    const re = new Float64Array(N), im = new Float64Array(N);
    for (let i = 0; i < N; i++) re[i] = x[i] * w[i];
    fft(re, im);
    const h = N >> 1;
    const mag = new Float64Array(h);
    for (let i = 0; i < h; i++) mag[i] = Math.hypot(re[i], im[i]);
    return mag;
  }

  return {
    arange, linspace, logspace, maxAbs, db20, toDb,
    rng, randnFactory, randn,
    hann, ones, fft, fftshift, magSpectrum, magOneSided, normalise,
    quantize, quantizeBits, quantizeSD, levelCount, decimate, oversample, sigmaDelta1, skip,
    snr, enob,
  };
})();
