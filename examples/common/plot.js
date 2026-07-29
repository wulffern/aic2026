/* A small canvas plotting library for the interactive examples.
 *
 * The ex/ scripts draw with matplotlib: a grid of subplots, each with axes,
 * a grid, labels and a few lines. This is the same idea in about 300 lines of
 * canvas, because pulling a charting library in would mean either a CDN (which
 * breaks the pages offline, and these are teaching material students read on
 * a train) or vendoring something far larger than the pages themselves.
 *
 * Usage:
 *
 *   const chart = Plot.mount('c', { aspect: 0.55, draw: render });
 *   function render(cx, W, H) {
 *     const g = Plot.grid(W, H, 1, 2);
 *     const p = new Plot.Panel(cx, g[0], { xlabel: 'n', ylabel: 'x[n]' });
 *     p.limits(0, 100, -1, 1).frame();
 *     p.line(xs, ys, '#3361e6');
 *   }
 */

'use strict';

const Plot = (function () {

  const CSS = getComputedStyle(document.documentElement);
  const col = name => CSS.getPropertyValue('--' + name).trim() || '#888';

  const C = {
    get bg()    { return col('bg'); },
    get edge()  { return col('edge'); },
    get grid()  { return col('grid'); },
    get text()  { return col('text'); },
    get muted() { return col('muted'); },
  };

  const FONT = "11px 'Courier New', monospace";
  const FONT_SM = "10px 'Courier New', monospace";

  // ── Canvas mounting ─────────────────────────────────────────────────────
  //
  // The canvas is sized in CSS pixels and backed by a device-pixel buffer, so
  // the plots stay sharp on a retina screen and legible on a phone.

  function mount(id, opts) {
    const cv = typeof id === 'string' ? document.getElementById(id) : id;
    const cx = cv.getContext('2d');
    const maxWidth = opts.maxWidth || 1200;
    const aspect = opts.aspect || 0.55;              // height / width, desktop
    const aspectNarrow = opts.aspectNarrow || 1.25;  // height / width, < 700 px
    const narrowAt = opts.narrowAt || 700;

    let W = maxWidth, H = maxWidth * aspect;

    function resize() {
      const dpr = window.devicePixelRatio || 1;
      const narrow = window.innerWidth < narrowAt;
      W = Math.min(maxWidth, window.innerWidth - 24);
      H = Math.round(W * (narrow ? aspectNarrow : aspect));
      cv.width = Math.round(W * dpr);
      cv.height = Math.round(H * dpr);
      cv.style.width = W + 'px';
      cv.style.height = H + 'px';
      cx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function redraw() {
      cx.save();
      cx.fillStyle = C.bg;
      cx.fillRect(0, 0, W, H);
      cx.restore();
      opts.draw(cx, W, H, W < narrowAt);
    }

    let timer;
    window.addEventListener('resize', () => {
      clearTimeout(timer);
      timer = setTimeout(() => { resize(); redraw(); }, 120);
    });

    resize();
    return { redraw, canvas: cv, ctx: cx, width: () => W, height: () => H };
  }

  // ── Panel geometry ──────────────────────────────────────────────────────

  /**
   * Split the canvas into a rows x cols grid of panel boxes, row-major.
   * The gaps have to leave room for one panel's y labels and the next
   * panel's frame, hence the fairly generous defaults.
   */
  function grid(W, H, rows, cols, o) {
    o = o || {};
    const padX = o.padX ?? 6, padY = o.padY ?? 6;
    const gapX = o.gapX ?? 10, gapY = o.gapY ?? 14;
    const cw = (W - 2 * padX - (cols - 1) * gapX) / cols;
    const ch = (H - 2 * padY - (rows - 1) * gapY) / rows;
    const boxes = [];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        boxes.push({
          x0: padX + c * (cw + gapX),
          y0: padY + r * (ch + gapY),
          x1: padX + c * (cw + gapX) + cw,
          y1: padY + r * (ch + gapY) + ch,
        });
      }
    }
    return boxes;
  }

  // ── Ticks ───────────────────────────────────────────────────────────────

  /** Round tick positions covering [min, max], roughly `n` of them. */
  function niceTicks(min, max, n) {
    if (!(max > min)) return [min];
    const raw = (max - min) / Math.max(1, n);
    const mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const norm = raw / mag;
    const step = (norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 5 ? 5 : 10) * mag;
    const out = [];
    for (let t = Math.ceil(min / step) * step; t <= max + step * 1e-9; t += step) {
      out.push(Math.abs(t) < step * 1e-9 ? 0 : t);
    }
    return out;
  }

  /** Decade ticks for a log axis, with the 2..9 minors marked but unlabelled. */
  function logTicks(min, max) {
    const major = [], minor = [];
    const d0 = Math.floor(Math.log10(min)), d1 = Math.ceil(Math.log10(max));
    for (let d = d0; d <= d1; d++) {
      const base = Math.pow(10, d);
      if (base >= min && base <= max) major.push(base);
      for (let m = 2; m <= 9; m++) {
        const v = m * base;
        if (v >= min && v <= max) minor.push(v);
      }
    }
    return { major, minor };
  }

  /** Compact number formatting: no more digits than the reader needs. */
  function fmt(v, span) {
    if (v === 0) return '0';
    const a = Math.abs(v);
    // Choose the notation from the axis SPAN, not from the individual tick, so
    // one axis does not end up labelled "50000, 1e5".
    const s = span === undefined ? a : span;
    if (s >= 1e5 || s < 1e-4) {
      const e = Math.floor(Math.log10(a));
      const m = v / Math.pow(10, e);
      const ms = Math.abs(m - Math.round(m)) < 0.05 ? String(Math.round(m)) : m.toFixed(1);
      return ms + 'e' + e;
    }
    // Enough decimals to tell neighbouring ticks apart. Deriving this from the
    // span alone gave "0.001" twice in a row on a 1.1e-3 wide axis.
    const step = s / 5;
    const dec = Math.max(0, Math.min(8, Math.ceil(-Math.log10(step / 2))));
    let out = v.toFixed(dec);
    // Only trim inside a fraction — "100" must not become "1".
    if (out.indexOf('.') >= 0) out = out.replace(/0+$/, '').replace(/\.$/, '');
    return out;
  }

  /** 10^n as "1e-3" style text for log-axis labels. */
  function fmtDecade(v) {
    const e = Math.round(Math.log10(v));
    if (e >= -2 && e <= 3) return String(Math.pow(10, e));
    return '1e' + e;
  }

  // ── Panel ───────────────────────────────────────────────────────────────

  function Panel(cx, box, o) {
    o = o || {};
    this.cx = cx;
    this.box = box;
    this.title = o.title || '';
    this.xlabel = o.xlabel || '';
    this.ylabel = o.ylabel || '';
    this.xlog = !!o.xlog;
    this.ylog = !!o.ylog;
    this.grid = o.grid !== false;
    const m = o.margin || {};
    this.m = {
      l: m.l ?? (this.ylabel ? 56 : 44),
      r: m.r ?? 10,
      t: m.t ?? (this.title ? 20 : 8),
      b: m.b ?? (this.xlabel ? 34 : 22),
    };
    this.xmin = 0; this.xmax = 1; this.ymin = 0; this.ymax = 1;
  }

  Panel.prototype.limits = function (xmin, xmax, ymin, ymax) {
    this.xmin = xmin; this.xmax = xmax; this.ymin = ymin; this.ymax = ymax;
    return this;
  };

  Object.defineProperties(Panel.prototype, {
    left:   { get() { return this.box.x0 + this.m.l; } },
    right:  { get() { return this.box.x1 - this.m.r; } },
    top:    { get() { return this.box.y0 + this.m.t; } },
    bottom: { get() { return this.box.y1 - this.m.b; } },
  });

  Panel.prototype.px = function (x) {
    const f = this.xlog
      ? (Math.log10(Math.max(x, 1e-300)) - Math.log10(this.xmin)) / (Math.log10(this.xmax) - Math.log10(this.xmin))
      : (x - this.xmin) / (this.xmax - this.xmin);
    return this.left + f * (this.right - this.left);
  };

  Panel.prototype.py = function (y) {
    const f = this.ylog
      ? (Math.log10(Math.max(y, 1e-300)) - Math.log10(this.ymin)) / (Math.log10(this.ymax) - Math.log10(this.ymin))
      : (y - this.ymin) / (this.ymax - this.ymin);
    return this.bottom - f * (this.bottom - this.top);
  };

  /** Border, grid, ticks and labels. Call before drawing any data. */
  Panel.prototype.frame = function () {
    const cx = this.cx;
    const L = this.left, R = this.right, T = this.top, B = this.bottom;

    cx.save();
    cx.font = FONT_SM;
    cx.lineWidth = 1;

    // Vertical grid + x ticks
    const xs = this.xlog ? logTicks(this.xmin, this.xmax) : null;
    const xticks = this.xlog ? xs.major : niceTicks(this.xmin, this.xmax, 5);
    if (this.xlog) {
      cx.strokeStyle = C.grid;
      cx.globalAlpha = 0.5;
      cx.beginPath();
      for (const v of xs.minor) {
        const x = Math.round(this.px(v)) + 0.5;
        cx.moveTo(x, T); cx.lineTo(x, B);
      }
      cx.stroke();
      cx.globalAlpha = 1;
    }
    cx.strokeStyle = C.grid;
    cx.fillStyle = C.muted;
    cx.textAlign = 'center';
    cx.textBaseline = 'top';
    for (const v of xticks) {
      const x = Math.round(this.px(v)) + 0.5;
      if (x < L - 1 || x > R + 1) continue;
      if (this.grid) { cx.beginPath(); cx.moveTo(x, T); cx.lineTo(x, B); cx.stroke(); }
      cx.fillText(this.xlog ? fmtDecade(v) : fmt(v, this.xmax - this.xmin), x, B + 5);
    }

    // Horizontal grid + y ticks
    const ys = this.ylog ? logTicks(this.ymin, this.ymax) : null;
    const yticks = this.ylog ? ys.major : niceTicks(this.ymin, this.ymax, 5);
    if (this.ylog) {
      cx.strokeStyle = C.grid;
      cx.globalAlpha = 0.5;
      cx.beginPath();
      for (const v of ys.minor) {
        const y = Math.round(this.py(v)) + 0.5;
        cx.moveTo(L, y); cx.lineTo(R, y);
      }
      cx.stroke();
      cx.globalAlpha = 1;
    }
    cx.strokeStyle = C.grid;
    cx.fillStyle = C.muted;
    cx.textAlign = 'right';
    cx.textBaseline = 'middle';
    for (const v of yticks) {
      const y = Math.round(this.py(v)) + 0.5;
      if (y < T - 1 || y > B + 1) continue;
      if (this.grid) { cx.beginPath(); cx.moveTo(L, y); cx.lineTo(R, y); cx.stroke(); }
      cx.fillText(this.ylog ? fmtDecade(v) : fmt(v, this.ymax - this.ymin), L - 6, y);
    }

    // Border
    cx.strokeStyle = C.edge;
    cx.strokeRect(Math.round(L) + 0.5, Math.round(T) + 0.5, Math.round(R - L), Math.round(B - T));

    // Labels
    cx.fillStyle = C.muted;
    cx.font = FONT;
    if (this.xlabel) {
      cx.textAlign = 'center'; cx.textBaseline = 'bottom';
      cx.fillText(this.xlabel, (L + R) / 2, this.box.y1 - 2);
    }
    if (this.ylabel) {
      cx.save();
      cx.translate(this.box.x0 + 11, (T + B) / 2);
      cx.rotate(-Math.PI / 2);
      cx.textAlign = 'center'; cx.textBaseline = 'middle';
      cx.fillText(this.ylabel, 0, 0);
      cx.restore();
    }
    if (this.title) {
      cx.fillStyle = C.text;
      cx.textAlign = 'left'; cx.textBaseline = 'bottom';
      cx.fillText(this.title, L, T - 5);
    }
    cx.restore();
    return this;
  };

  Panel.prototype.clip = function (fn) {
    const cx = this.cx;
    cx.save();
    cx.beginPath();
    cx.rect(this.left, this.top, this.right - this.left, this.bottom - this.top);
    cx.clip();
    fn(cx);
    cx.restore();
    return this;
  };

  /**
   * Polyline through (xs[i], ys[i]). `xs` may be omitted (pass null) to use
   * the sample index, which is what matplotlib does for `plt.plot(y)`.
   *
   * Long vectors are decimated to the pixel grid — an 8192-point spectrum in a
   * 300 px panel is 27 points per column, and drawing the min/max of each
   * column instead keeps the envelope while cutting the path length by 10x.
   */
  Panel.prototype.line = function (xs, ys, color, o) {
    o = o || {};
    const cx = this.cx;
    const n = ys.length;
    const cols = Math.max(1, Math.round(this.right - this.left));
    this.clip(() => {
      cx.strokeStyle = color;
      cx.lineWidth = o.width || 1;
      if (o.dash) cx.setLineDash(o.dash);
      cx.beginPath();
      if (n > cols * 2) {
        // Envelope mode: one vertical segment per pixel column.
        let started = false;
        let bucket = -1, lo = 0, hi = 0, sx = 0;
        for (let i = 0; i < n; i++) {
          const x = this.px(xs ? xs[i] : i);
          const b = Math.round(x);
          const y = this.py(ys[i]);
          if (b !== bucket) {
            if (bucket >= 0) {
              if (!started) { cx.moveTo(sx, lo); started = true; } else cx.lineTo(sx, lo);
              cx.lineTo(sx, hi);
            }
            bucket = b; lo = y; hi = y; sx = x;
          } else {
            if (y < lo) lo = y;
            if (y > hi) hi = y;
          }
        }
        if (bucket >= 0) {
          if (!started) cx.moveTo(sx, lo); else cx.lineTo(sx, lo);
          cx.lineTo(sx, hi);
        }
      } else {
        for (let i = 0; i < n; i++) {
          const x = this.px(xs ? xs[i] : i), y = this.py(ys[i]);
          if (i === 0) cx.moveTo(x, y); else cx.lineTo(x, y);
        }
      }
      cx.stroke();
      cx.setLineDash([]);
    });
    return this;
  };

  /** Sample-and-hold staircase, for anything that has been sampled. */
  Panel.prototype.stairs = function (xs, ys, color, o) {
    o = o || {};
    const cx = this.cx;
    this.clip(() => {
      cx.strokeStyle = color;
      cx.lineWidth = o.width || 1;
      cx.beginPath();
      for (let i = 0; i < ys.length; i++) {
        const x0 = this.px(xs ? xs[i] : i);
        const x1 = this.px(xs ? (xs[i + 1] ?? xs[i] + (xs[i] - xs[i - 1] || 1)) : i + 1);
        const y = this.py(ys[i]);
        if (i === 0) cx.moveTo(x0, y); else cx.lineTo(x0, y);
        cx.lineTo(x1, y);
      }
      cx.stroke();
    });
    return this;
  };

  Panel.prototype.dots = function (xs, ys, color, r) {
    const cx = this.cx;
    r = r || 2;
    this.clip(() => {
      cx.fillStyle = color;
      for (let i = 0; i < ys.length; i++) {
        const x = this.px(xs ? xs[i] : i), y = this.py(ys[i]);
        if (x < this.left - r || x > this.right + r) continue;
        cx.beginPath();
        cx.arc(x, y, r, 0, 2 * Math.PI);
        cx.fill();
      }
    });
    return this;
  };

  /** Vertical stems from y = 0, matplotlib's stem plot. */
  Panel.prototype.stem = function (xs, ys, color) {
    const cx = this.cx;
    this.clip(() => {
      cx.strokeStyle = color;
      cx.lineWidth = 1;
      cx.beginPath();
      const y0 = this.py(Math.max(this.ymin, Math.min(0, this.ymax)));
      for (let i = 0; i < ys.length; i++) {
        const x = this.px(xs ? xs[i] : i);
        cx.moveTo(x, y0);
        cx.lineTo(x, this.py(ys[i]));
      }
      cx.stroke();
    });
    return this;
  };

  Panel.prototype.hline = function (y, color, dash) {
    const cx = this.cx;
    this.clip(() => {
      cx.strokeStyle = color;
      cx.lineWidth = 1;
      if (dash) cx.setLineDash(dash);
      const yy = Math.round(this.py(y)) + 0.5;
      cx.beginPath(); cx.moveTo(this.left, yy); cx.lineTo(this.right, yy); cx.stroke();
      cx.setLineDash([]);
    });
    return this;
  };

  Panel.prototype.vline = function (x, color, dash) {
    const cx = this.cx;
    this.clip(() => {
      cx.strokeStyle = color;
      cx.lineWidth = 1;
      if (dash) cx.setLineDash(dash);
      const xx = Math.round(this.px(x)) + 0.5;
      cx.beginPath(); cx.moveTo(xx, this.top); cx.lineTo(xx, this.bottom); cx.stroke();
      cx.setLineDash([]);
    });
    return this;
  };

  /** Shaded band between two x values, matplotlib's axvspan. */
  Panel.prototype.vspan = function (x0, x1, color, alpha) {
    const cx = this.cx;
    this.clip(() => {
      cx.globalAlpha = alpha ?? 0.12;
      cx.fillStyle = color;
      const a = this.px(x0), b = this.px(x1);
      cx.fillRect(a, this.top, b - a, this.bottom - this.top);
      cx.globalAlpha = 1;
    });
    return this;
  };

  /**
   * Text placed by fraction of the plot area, so a caption stays put when the
   * limits change. `fx`/`fy` run 0..1 from the bottom left.
   */
  Panel.prototype.note = function (fx, fy, text, color, align) {
    const cx = this.cx;
    cx.save();
    cx.font = FONT_SM;
    cx.textAlign = align || 'left';
    cx.textBaseline = 'top';
    const x = this.left + fx * (this.right - this.left);
    const y0 = this.bottom - fy * (this.bottom - this.top);
    const lines = String(text).split('\n');

    // Notes sit on top of data and grid lines, so lay a background down first
    // or the text is unreadable wherever a trace happens to pass through it.
    let w = 0;
    for (const ln of lines) w = Math.max(w, cx.measureText(ln).width);
    const h = lines.length * 13;
    const bx = align === 'right' ? x - w : align === 'center' ? x - w / 2 : x;
    cx.globalAlpha = 0.78;
    cx.fillStyle = C.bg;
    cx.fillRect(bx - 3, y0 - 2, w + 6, h + 2);
    cx.globalAlpha = 1;

    cx.fillStyle = color || C.muted;
    let y = y0;
    for (const ln of lines) {
      cx.fillText(ln, x, y);
      y += 13;
    }
    cx.restore();
    return this;
  };

  /** Small in-panel legend, top-right by default. */
  Panel.prototype.legend = function (items, corner) {
    const cx = this.cx;
    cx.save();
    cx.font = FONT_SM;
    const pad = 6, lh = 13, sw = 14;
    let w = 0;
    for (const it of items) w = Math.max(w, cx.measureText(it.label).width);
    w += sw + 8 + 2 * pad;
    const h = items.length * lh + 2 * pad - 2;
    const right = (corner || 'tr').includes('r');
    const topc = (corner || 'tr').includes('t');
    const x = right ? this.right - w - 6 : this.left + 6;
    const y = topc ? this.top + 6 : this.bottom - h - 6;
    cx.fillStyle = C.bg;
    cx.globalAlpha = 0.82;
    cx.fillRect(x, y, w, h);
    cx.globalAlpha = 1;
    cx.strokeStyle = C.edge;
    cx.strokeRect(x + 0.5, y + 0.5, w, h);
    cx.textBaseline = 'middle';
    cx.textAlign = 'left';
    items.forEach((it, i) => {
      const yy = y + pad + i * lh + 4;
      cx.strokeStyle = it.color;
      cx.lineWidth = it.width || 2;
      if (it.dash) cx.setLineDash(it.dash);
      cx.beginPath(); cx.moveTo(x + pad, yy); cx.lineTo(x + pad + sw, yy); cx.stroke();
      cx.setLineDash([]);
      cx.fillStyle = C.text;
      cx.fillText(it.label, x + pad + sw + 6, yy);
    });
    cx.restore();
    return this;
  };

  // ── Misc ────────────────────────────────────────────────────────────────

  /** [min, max] of an array, ignoring anything not finite. */
  function extent(a) {
    let lo = Infinity, hi = -Infinity;
    for (let i = 0; i < a.length; i++) {
      const v = a[i];
      if (!isFinite(v)) continue;
      if (v < lo) lo = v;
      if (v > hi) hi = v;
    }
    return [lo, hi];
  }

  /** Round [lo, hi] outwards to whole ticks, with a little headroom. */
  function padExtent(lo, hi, frac) {
    frac = frac ?? 0.06;
    if (!(hi > lo)) { return [lo - 1, hi + 1]; }
    const d = (hi - lo) * frac;
    return [lo - d, hi + d];
  }

  return { mount, grid, Panel, niceTicks, logTicks, fmt, fmtDecade, extent, padExtent, C };
})();

/* ── Control wiring ────────────────────────────────────────────────────────
 *
 * Every page has the same shape of controls, so the boilerplate lives here:
 * a slider updates one field of a state object, writes its formatted value
 * into the readout span, and triggers a redraw.
 */

const UI = (function () {

  /**
   * Bind every [data-bind] slider/checkbox in the document to `state`.
   *
   *   <input type="range" data-bind="bits" data-fmt="b" min=1 max=8 step=1>
   *
   * The element id names the readout span: id="sl-bits" pairs with "v-bits".
   * `fmts` maps a field name to a function turning its value into label text.
   */
  function bind(state, fmts, onChange) {
    const els = document.querySelectorAll('[data-bind]');
    els.forEach(el => {
      const key = el.dataset.bind;
      const show = () => {
        const out = document.getElementById('v-' + key);
        if (out) out.textContent = fmts[key] ? fmts[key](state[key]) : String(state[key]);
      };
      const read = () => (el.type === 'checkbox' ? el.checked : +el.value);
      state[key] = read();
      show();
      el.addEventListener('input', () => { state[key] = read(); show(); onChange(key); });
    });
    return { refresh: () => els.forEach(el => el.dispatchEvent(new Event('input'))) };
  }

  /**
   * A row of mode buttons. Each button carries data-mode; clicking one sets
   * `state[key]` and moves the `on` class.
   */
  function modes(rowId, state, key, onChange) {
    const row = document.getElementById(rowId);
    if (!row) return;
    const btns = [...row.querySelectorAll('.modebtn')];
    const sync = () => btns.forEach(b => b.classList.toggle('on', b.dataset.mode === String(state[key])));
    btns.forEach(b => b.addEventListener('click', () => {
      state[key] = b.dataset.mode;
      sync();
      onChange(key);
    }));
    sync();
  }

  /** Write a number into a #readout box. */
  function readout(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  /** Highlight the active blocks of the signal-chain strip. */
  function chain(map) {
    for (const [id, on] of Object.entries(map)) {
      const el = document.getElementById(id);
      if (el) el.classList.toggle('on', !!on);
    }
  }

  return { bind, modes, readout, chain };
})();
