/* Complex arithmetic and continuous-time linear system helpers.
 *
 * The notebooks that motivated this file (jupyter/xosc.ipynb, jupyter/biquad.ipynb,
 * sun_pll_sky130nm/jupyter/pll.ipynb) all do the same thing: build an expression
 * in s, substitute s = j*omega, and plot magnitude and phase. numpy does the
 * complex arithmetic for free; JavaScript does not, so it lives here.
 *
 * A complex number is a plain two-element array [re, im]. That is uglier than a
 * class but it allocates less and reads fine in the small doses these pages use.
 */

'use strict';

const LTI = (function () {

  // ── Complex ─────────────────────────────────────────────────────────────

  const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1]];
  const mul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];

  function div(a, b) {
    const d = b[0] * b[0] + b[1] * b[1];
    return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d];
  }

  const scale = (a, k) => [a[0] * k, a[1] * k];
  const inv = a => div([1, 0], a);
  const abs = a => Math.hypot(a[0], a[1]);
  const arg = a => Math.atan2(a[1], a[0]);
  const db = a => 20 * Math.log10(Math.max(abs(a), 1e-300));
  const deg = a => arg(a) * 180 / Math.PI;

  /** s = j*2*pi*f, the substitution every one of these notebooks makes. */
  const jw = f => [0, 2 * Math.PI * f];

  // ── Frequency sweeps ────────────────────────────────────────────────────

  /** n log-spaced frequencies from f0 to f1, as np.logspace does. */
  function logf(f0, f1, n) {
    const out = new Float64Array(n);
    const a = Math.log10(f0), b = Math.log10(f1);
    for (let i = 0; i < n; i++) out[i] = Math.pow(10, a + (b - a) * i / (n - 1));
    return out;
  }

  /**
   * Evaluate H at every frequency in f and return magnitude in dB and phase in
   * degrees. `H` takes a complex s and returns a complex value.
   *
   * The phase is unwrapped, because a bare atan2 jumps by 360 degrees in the
   * middle of a Bode plot and makes a phase margin impossible to read.
   */
  function bode(f, H) {
    const n = f.length;
    const mag = new Float64Array(n), ph = new Float64Array(n);
    let offset = 0, prev = null;
    for (let i = 0; i < n; i++) {
      const h = H(jw(f[i]));
      mag[i] = db(h);
      let p = deg(h);
      if (prev !== null) {
        while (p + offset - prev > 180) offset -= 360;
        while (p + offset - prev < -180) offset += 360;
      }
      ph[i] = p + offset;
      prev = ph[i];
    }
    return { mag, ph };
  }

  /**
   * First frequency where the magnitude crosses 0 dB going down, by linear
   * interpolation in log f. Returns null if it never crosses.
   */
  function unityGain(f, mag) {
    for (let i = 1; i < f.length; i++) {
      if (mag[i - 1] >= 0 && mag[i] < 0) {
        const t = mag[i - 1] / (mag[i - 1] - mag[i]);
        return Math.pow(10, Math.log10(f[i - 1]) + t * (Math.log10(f[i]) - Math.log10(f[i - 1])));
      }
    }
    return null;
  }

  /** Linear interpolation of y at frequency fx, in log f. */
  function interpAt(f, y, fx) {
    if (fx <= f[0]) return y[0];
    if (fx >= f[f.length - 1]) return y[y.length - 1];
    for (let i = 1; i < f.length; i++) {
      if (f[i] >= fx) {
        const t = (Math.log10(fx) - Math.log10(f[i - 1])) / (Math.log10(f[i]) - Math.log10(f[i - 1]));
        return y[i - 1] + t * (y[i] - y[i - 1]);
      }
    }
    return y[y.length - 1];
  }

  /** Index of the largest value, for finding a resonant peak. */
  function argmax(y) {
    let k = 0;
    for (let i = 1; i < y.length; i++) if (y[i] > y[k]) k = i;
    return k;
  }

  // ── Rational transfer functions ─────────────────────────────────────────

  /**
   * H(s) = num(s)/den(s) with coefficients in descending powers, as
   * scipy.signal and MATLAB take them: [a, b, c] means a*s^2 + b*s + c.
   */
  function poly(coeffs, s) {
    let acc = [0, 0];
    for (const c of coeffs) acc = add(mul(acc, s), [c, 0]);
    return acc;
  }

  const tf = (num, den) => s => div(poly(num, s), poly(den, s));

  /** Roots of a quadratic a s^2 + b s + c, as complex pairs. */
  function roots2(a, b, c) {
    if (a === 0) return b === 0 ? [] : [[-c / b, 0]];
    const disc = b * b - 4 * a * c;
    if (disc >= 0) {
      const r = Math.sqrt(disc);
      return [[(-b + r) / (2 * a), 0], [(-b - r) / (2 * a), 0]];
    }
    const r = Math.sqrt(-disc);
    return [[-b / (2 * a), r / (2 * a)], [-b / (2 * a), -r / (2 * a)]];
  }

  // ── Time domain ─────────────────────────────────────────────────────────

  /**
   * Step response of num(s)/den(s) by integrating the controllable canonical
   * state space form with RK4.
   *
   * Both coefficient lists are in descending powers and num must not be longer
   * than den. `dt` has to resolve the fastest pole: these loops carry poles
   * decades apart, so the caller picks it from the pole locations rather than
   * from the plot window.
   */
  function step(num, den, dt, n) {
    const order = den.length - 1;
    const a0 = den[0];
    const a = den.slice(1).map(v => v / a0);          // s^order + a[0] s^(order-1) ...
    // y = sum_j b[j] * x[j], where x[j] is the j'th derivative state and b[j]
    // is therefore the coefficient of s^j — counted from the END of the
    // descending-power list, not the start.
    const b = new Array(order).fill(0);
    const nn = num.map(v => v / a0);
    for (let i = 0; i < nn.length && i < order; i++) b[i] = nn[nn.length - 1 - i];

    // x' = A x + B u with A in companion form, y = b . x
    const deriv = (x) => {
      const d = new Float64Array(order);
      for (let i = 0; i < order - 1; i++) d[i] = x[i + 1];
      let last = 1;                                    // unit step input
      for (let i = 0; i < order; i++) last -= a[order - 1 - i] * x[i];
      d[order - 1] = last;
      return d;
    };

    const t = new Float64Array(n), y = new Float64Array(n);
    let x = new Float64Array(order);
    const addv = (p, q, k) => {
      const o = new Float64Array(order);
      for (let i = 0; i < order; i++) o[i] = p[i] + q[i] * k;
      return o;
    };
    for (let i = 0; i < n; i++) {
      t[i] = i * dt;
      let acc = 0;
      for (let j = 0; j < order; j++) acc += b[j] * x[j];
      y[i] = acc;
      const k1 = deriv(x);
      const k2 = deriv(addv(x, k1, dt / 2));
      const k3 = deriv(addv(x, k2, dt / 2));
      const k4 = deriv(addv(x, k3, dt));
      for (let j = 0; j < order; j++) {
        x[j] += dt / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]);
      }
      if (!isFinite(x[0])) break;                      // diverged; stop rather than NaN the plot
    }
    return { t, y };
  }

  return { add, sub, mul, div, scale, inv, abs, arg, db, deg, jw,
           logf, bode, unityGain, interpAt, argmax, poly, tf, roots2, step };
})();
