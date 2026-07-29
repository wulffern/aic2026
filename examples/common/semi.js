/* Semiconductor constants and the carrier-concentration model shared by the
 * diode pages. This is the `calc_ni` of ex/vd.py, which ex/antenna_diode_leakage.py
 * also reuses, plus the handful of scipy.constants values those scripts pull in.
 *
 * Everything is in SI except where the Python is in cm, in which case so is
 * this: mixing the two silently is how you end up 12 orders of magnitude out.
 */

'use strict';

const SEMI = (function () {

  // scipy.constants, to the digits the scripts actually use.
  const h  = 6.62607015e-34;      // Planck constant [J s]
  const k  = 1.380649e-23;        // Boltzmann [J/K]
  const q  = 1.602176634e-19;     // elementary charge [C]
  const m0 = 9.1093837015e-31;    // electron rest mass [kg]
  const eV = 1.602176634e-19;     // [J]
  const pi = Math.PI;

  const cm3 = 1e-6;               // 1/m^3 -> 1/cm^3
  const eps0_cm = 8.8541878128e-14;   // F/cm
  const EPS_SI = 11.7 * eps0_cm;      // F/cm

  const EG_SI = 1.12 * eV;        // silicon bandgap, held constant as in ex/vd.py

  /** Thermal voltage kT/q [V]. */
  function VT(T) { return k * T / q; }

  /**
   * Intrinsic carrier concentration [1/cm^3] from the density of states, as in
   * ex/vd.py. See Streetman pages 90-95.
   *
   * The density-of-states effective masses are the ones silicon actually has:
   * six conduction valleys with a longitudinal and two transverse masses, and
   * a heavy hole.
   */
  function ni(T, Eg = EG_SI) {
    // (m_l*m_t^2)^(1/3) times 6^(2/3): silicon has six equivalent conduction
    // band minima and the density of states counts all of them. Without the
    // degeneracy factor m_n* is 0.33*m0 rather than 1.08*m0 and n_i comes out
    // a factor sqrt(6) low.
    const mn = Math.pow(6, 2 / 3) * Math.pow(0.98 * 0.19 * 0.19, 1 / 3) * m0;
    const mp = 0.81 * m0;
    const Nc = 2 * Math.sqrt(Math.pow((2 * pi * k * T * mn) / (h * h), 3));
    const Nv = 2 * Math.sqrt(Math.pow((2 * pi * k * T * mp) / (h * h), 3));
    return Math.sqrt(Nc * Nv) * Math.exp(-Eg / (2 * k * T)) * cm3;
  }

  /** The rule of thumb: n_i doubles every 11 degrees. */
  function niSimple(T, TNOM = 300.15) {
    return 1.1e10 * Math.pow(2, (T - TNOM) / 11);
  }

  /** What BSIM 4.8 uses. */
  function niBsim(T, Eg = EG_SI, TNOM = 300.15) {
    return 1.45e10 * (TNOM / 300.15) * Math.sqrt(T / 300.15)
         * Math.exp(21.5565981 - Eg / (2 * k * T));
  }

  /**
   * Shockley diffusion saturation current [A] of a pn junction.
   *
   *   I_S = q A n_i^2 (1/NA sqrt(Dn/tau_n) + 1/ND sqrt(Dp/tau_p))
   *
   * A in cm^2, doping in 1/cm^3, D in cm^2/s, tau in s.
   */
  function isat(T, o) {
    const n = ni(T, o.Eg ?? EG_SI);
    return q * o.A * n * n *
      (1 / o.NA * Math.sqrt(o.Dn / o.tau_n) + 1 / o.ND * Math.sqrt(o.Dp / o.tau_p));
  }

  /** Built-in voltage of a pn junction [V]. */
  function vbi(T, NA, ND, Eg = EG_SI) {
    const n = ni(T, Eg);
    return VT(T) * Math.log(NA * ND / (n * n));
  }

  /** Depletion width [cm] of a one-sided junction, NA << ND. */
  function depletionWidth(T, NA, ND, VR, Eg = EG_SI) {
    return Math.sqrt(2 * EPS_SI * (vbi(T, NA, ND, Eg) + VR) / (q * NA));
  }

  /** Sah-Noyce-Shockley generation current in the depletion region [A]. */
  function igen(T, A, W, tau_g, Eg = EG_SI) {
    return q * A * ni(T, Eg) * W / tau_g;
  }

  /** Least-squares straight line through (x, y); returns [intercept, slope]. */
  function polyfit1(x, y) {
    const n = x.length;
    let sx = 0, sy = 0, sxx = 0, sxy = 0;
    for (let i = 0; i < n; i++) { sx += x[i]; sy += y[i]; sxx += x[i] * x[i]; sxy += x[i] * y[i]; }
    const d = n * sxx - sx * sx;
    const slope = (n * sxy - sx * sy) / d;
    return [(sy - slope * sx) / n, slope];
  }

  return { h, k, q, m0, eV, cm3, EPS_SI, EG_SI, VT, ni, niSimple, niBsim,
           isat, vbi, depletionWidth, igen, polyfit1 };
})();
