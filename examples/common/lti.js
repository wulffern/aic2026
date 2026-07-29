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

  /**
   * All roots of a polynomial in descending powers, by Durand-Kerner.
   *
   * Good enough for the degree-5 characteristic polynomials these loops
   * produce, and it needs no matrix code. Returns complex pairs, unsorted.
   */
  function roots(desc) {
    // Drop leading zeros, then work in ascending order and monic.
    let d = desc.slice();
    while (d.length > 1 && d[0] === 0) d.shift();
    const n = d.length - 1;
    if (n < 1) return [];
    const c = d.slice().reverse().map(v => v / d[0]);   // ascending, monic in c[n]

    const ev = z => {
      let r = [0, 0];
      for (let i = n; i >= 0; i--) r = [r[0] * z[0] - r[1] * z[1] + c[i], r[0] * z[1] + r[1] * z[0]];
      return r;
    };

    // Spread the initial guesses around a circle scaled to the coefficients, so
    // the iteration does not start every root on top of its neighbour.
    let scale = 0;
    for (let i = 0; i < n; i++) scale = Math.max(scale, Math.pow(Math.abs(c[i]), 1 / (n - i)));
    scale = scale || 1;
    let z = [];
    for (let i = 0; i < n; i++) {
      const th = 2 * Math.PI * i / n + 0.4;
      z.push([scale * Math.cos(th), scale * Math.sin(th)]);
    }

    for (let it = 0; it < 500; it++) {
      let moved = 0;
      for (let i = 0; i < n; i++) {
        let den = [1, 0];
        for (let j = 0; j < n; j++) {
          if (i === j) continue;
          const dz = [z[i][0] - z[j][0], z[i][1] - z[j][1]];
          den = [den[0] * dz[0] - den[1] * dz[1], den[0] * dz[1] + den[1] * dz[0]];
        }
        const dd = den[0] * den[0] + den[1] * den[1];
        if (dd === 0) continue;
        const num = ev(z[i]);
        const q = [(num[0] * den[0] + num[1] * den[1]) / dd,
                   (num[1] * den[0] - num[0] * den[1]) / dd];
        z[i] = [z[i][0] - q[0], z[i][1] - q[1]];
        moved = Math.max(moved, Math.hypot(q[0], q[1]));
      }
      if (moved < 1e-12 * scale) break;
    }
    return z;
  }

  /** Multiply two polynomials given in ascending powers. */
  function polymulAsc(p, q) {
    const r = new Array(p.length + q.length - 1).fill(0);
    for (let i = 0; i < p.length; i++) for (let j = 0; j < q.length; j++) r[i + j] += p[i] * q[j];
    return r;
  }

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
   * Controllable canonical realisation of num(s)/den(s), both in descending
   * powers of s. `num` must not be longer than `den`.
   *
   *   x[0]' = x[1],  x[1]' = x[2], ...
   *   x[n-1]' = -sum_j a_j x[j] + u
   *   y       =  sum_j b[j] x[j]
   *
   * a_j and b[j] are the coefficients of s^j, counted from the END of the
   * descending-power lists.
   */
  function realise(num, den) {
    const order = den.length - 1;
    const a0 = den[0];
    const a = den.slice(1).map(v => v / a0);          // a[0] = a_{n-1} ... a[n-1] = a_0
    const b = new Array(order).fill(0);
    const nn = num.map(v => v / a0);
    for (let i = 0; i < nn.length && i < order; i++) b[i] = nn[nn.length - 1 - i];
    return { order, a, b };
  }

  /** dx/dt for a realisation driven by scalar input u. */
  function ssDeriv(sys, x, u) {
    const d = new Float64Array(sys.order);
    for (let i = 0; i < sys.order - 1; i++) d[i] = x[i + 1];
    let last = u;
    for (let i = 0; i < sys.order; i++) last -= sys.a[sys.order - 1 - i] * x[i];
    d[sys.order - 1] = last;
    return d;
  }

  /** Output y = b . x. */
  function ssOut(sys, x) {
    let y = 0;
    for (let i = 0; i < sys.order; i++) y += sys.b[i] * x[i];
    return y;
  }

  /** One RK4 step of a realisation, holding u constant across the step. */
  function ssStep(sys, x, u, dt) {
    const addv = (p, q, k) => {
      const o = new Float64Array(sys.order);
      for (let i = 0; i < sys.order; i++) o[i] = p[i] + q[i] * k;
      return o;
    };
    const k1 = ssDeriv(sys, x, u);
    const k2 = ssDeriv(sys, addv(x, k1, dt / 2), u);
    const k3 = ssDeriv(sys, addv(x, k2, dt / 2), u);
    const k4 = ssDeriv(sys, addv(x, k3, dt), u);
    const o = new Float64Array(sys.order);
    for (let i = 0; i < sys.order; i++) {
      o[i] = x[i] + dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
    }
    return o;
  }

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
    const sys = realise(num, den);
    const order = sys.order;
    const b = sys.b;
    const deriv = (x) => ssDeriv(sys, x, 1);          // unit step input

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
           realise, ssDeriv, ssOut, ssStep, roots, polymulAsc,
           logf, bode, unityGain, interpAt, argmax, poly, tf, roots2, step };
})();
