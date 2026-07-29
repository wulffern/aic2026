#!/usr/bin/env python3
"""Render a Deckset lecture to a self-contained HTML slide deck.

The files in lectures/ are Deckset source. Deckset ignores HTML comments, which
is how `<!--pan_doc: ... -->` keeps the book prose out of the deck while the web
and LaTeX builds pick it up. This generator does the same split explicitly, but
the other way round from `lecture.py post`:

    pan_doc, pan_latex   dropped   (book/web prose, never on a slide)
    pan_skip             kept      (title slides, which the web build hides)
    everything else      kept

What is left is split on `---` into slides, the Deckset layout directives are
translated to CSS, and the result is one standalone HTML file per lecture.

Deviations from Deckset, both deliberate:

  * An image with no `left`/`right`/`inline` keyword is a background image in
    Deckset, so text on the same slide overlays it. Here it is stacked under the
    text instead and given the remaining height. On an image-only slide the
    result is identical; on a slide that also carries equations it is legible,
    which the overlay is not.
  * `$$...$$` is rendered as display math only when it is the whole paragraph.
    The lectures also use it mid-sentence ("Define $$x_c(t)$$ as ..."), and
    forcing that to display breaks the sentence in half.
"""

import os
import re
import click
import markdown

from lecture import Image

# ---------------------------------------------------------------- directives

IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
SLIDE_BREAK_RE = re.compile(r"^\s*---\s*$")
PAN_OPEN_RE = re.compile(r"<!--pan_([a-z]+):")
COMMENT_CLOSE_RE = re.compile(r"--+>")

BG_RE = re.compile(r"^\s*\[\.background-color:\s*([^\]]+)\]\s*$", re.I)
FG_RE = re.compile(r"^\s*\[\.text:\s*([^\]]+)\]\s*$", re.I)
COLUMN_RE = re.compile(r"^\s*\[\.column\]\s*$", re.I)
DROP_DIRECTIVE_RE = re.compile(r"^\s*\[\.[^\]]*\]\s*$")
FIT_HEADING_RE = re.compile(r"^(#+)\s*\[\s*fit\s*\]\s*(.*)$", re.M)
# A top level heading, including Deckset's #[fit] form.
HEADING_RE = re.compile(r"^#{1,2}(?=[\s\[])")

# Below this, a lecture was written as a document rather than a deck, and its
# headings are used as slide breaks instead. Five is deliberately generous:
# nothing anyone actually presents has four slide breaks in it.
AUTOSPLIT_BELOW = 5

# pan_doc bodies are dropped, pan_skip bodies are kept.
DROP_PAN = {"doc", "latex"}


class Figure:
    """One image reference plus the Deckset keywords that place it."""

    def __init__(self, alt, src, options):
        words = alt.lower().split()
        self.placement = "fill"
        for word in words:
            if word in ("left", "right", "inline"):
                self.placement = word
                break
        self.scale = None
        for word in words:
            m = re.fullmatch(r"(\d+)%", word)
            if m:
                self.scale = int(m.group(1))
        self.image = Image(src, options)
        self.src = src

    @property
    def url(self):
        return "../media/" + self.image.filesrc

    def html(self):
        style = ""
        if self.scale:
            style = f' style="width:{self.scale}%"'
        cls = "fig fig-" + self.placement
        return f'<img class="{cls}" src="{self.url}" alt=""{style}>'


class Slide:
    def __init__(self):
        self.columns = [[]]
        self.bg = None
        self.fg = None
        self.media = []      # left/right/fill figures, hoisted out of the flow

    def add(self, line):
        self.columns[-1].append(line)

    def newcolumn(self):
        self.columns.append([])

    def isempty(self):
        if self.media:
            return False
        return not any(c.strip() for col in self.columns for c in col)


class Deck:
    def __init__(self, filename, options):
        self.filename = filename
        self.options = options
        self.name = os.path.basename(filename).replace(".md", "")
        self.meta = {}
        self.title = ""
        self.slides = []
        self.figures = []
        self._read()

    # -- parsing ----------------------------------------------------------

    def _read(self):
        with open(self.filename) as fi:
            lines = fi.readlines()

        body = self._frontmatter(lines)
        body = self._strip_pan(body)

        # Several lectures are prose notes with no --- breaks at all, which
        # would otherwise render as one unreadable wall. Fall back to breaking
        # on headings for those, and leave real decks alone.
        breaks = sum(1 for line in body if SLIDE_BREAK_RE.match(line))
        self.autosplit = breaks < AUTOSPLIT_BELOW

        self._split(body)

    def _frontmatter(self, lines):
        """Deckset frontmatter runs to the first blank line."""
        for i, line in enumerate(lines):
            if not line.strip():
                return lines[i + 1:]
            if ":" in line:
                key, _, value = line.partition(":")
                self.meta[key.strip().lower()] = value.strip()
        return []

    def _strip_pan(self, lines):
        """Drop pan_doc/pan_latex bodies and every other HTML comment."""
        out = []
        dropping = False
        for line in lines:
            if dropping:
                if COMMENT_CLOSE_RE.search(line):
                    dropping = False
                continue

            m = PAN_OPEN_RE.search(line)
            if m:
                key = m.group(1)
                if key == "title":
                    self.title = re.sub(r"-->.*$", "", line.split(":", 1)[1]).strip()
                    continue
                if key in DROP_PAN:
                    # A one-line <!--pan_doc: ... --> closes on the same line.
                    if not COMMENT_CLOSE_RE.search(line):
                        dropping = True
                    continue
                # pan_skip: keep the body, drop only the marker.
                continue

            if line.strip().startswith("<!--") and not COMMENT_CLOSE_RE.search(line):
                dropping = True
                continue
            if line.strip().startswith("<!--"):
                continue

            out.append(line)
        return out

    def _split(self, lines):
        slide = Slide()
        for line in lines:
            if SLIDE_BREAK_RE.match(line):
                if not slide.isempty():
                    self.slides.append(slide)
                slide = Slide()
                continue

            m = BG_RE.match(line)
            if m:
                slide.bg = m.group(1).strip()
                continue
            m = FG_RE.match(line)
            if m:
                slide.fg = m.group(1).strip()
                continue
            if COLUMN_RE.match(line):
                slide.newcolumn()
                continue
            if DROP_DIRECTIVE_RE.match(line):
                continue

            if self.autosplit and HEADING_RE.match(line) and not slide.isempty():
                self.slides.append(slide)
                slide = Slide()

            line = self._hoist_images(line, slide)
            slide.add(line)

        if not slide.isempty():
            self.slides.append(slide)

    def _hoist_images(self, line, slide):
        """Pull placed images out of the text flow; leave inline ones behind."""
        def repl(m):
            fig = Figure(m.group(1), m.group(2), self.options)
            self.figures.append(fig)
            if fig.placement == "inline":
                return f"@@FIG{len(self.figures) - 1}@@"
            slide.media.append(fig)
            return ""
        return IMG_RE.sub(repl, line)

    # -- rendering --------------------------------------------------------

    def _markdown(self, text):
        # Deckset's #[fit] means "set this heading as large as it will go".
        text = FIT_HEADING_RE.sub(r"\1 \2 {: .fit}", text)

        math = []

        def keep(body, display):
            math.append((body.strip(), display))
            return f"@@MATH{len(math) - 1}@@"

        text = re.sub(r"\$\$(.+?)\$\$", lambda m: keep(m.group(1), True), text, flags=re.S)
        text = re.sub(r"\$([^$\n]+?)\$", lambda m: keep(m.group(1), False), text)

        out = markdown.markdown(text, extensions=["tables", "fenced_code", "attr_list"])

        # A $$...$$ that is a paragraph on its own is display math; the same
        # delimiters used mid-sentence are not.
        for i, (body, display) in enumerate(math):
            token = f"@@MATH{i}@@"
            standalone = f"<p>{token}</p>"
            if display and standalone in out:
                out = out.replace(standalone, f'<p class="katex-display">\\[{body}\\]</p>')
            else:
                out = out.replace(token, f"\\({body}\\)")

        for i, fig in enumerate(self.figures):
            out = out.replace(f"@@FIG{i}@@", fig.html())
        return out

    def _slide_html(self, slide, number):
        cols = []
        for col in slide.columns:
            text = self._markdown("".join(col))
            if text.strip():
                cols.append(f'<div class="col">{text}</div>')

        body = ""
        if cols:
            cls = "cols" if len(cols) > 1 else "single"
            body = f'<div class="{cls}">{"".join(cols)}</div>'

        left = [f for f in slide.media if f.placement == "left"]
        right = [f for f in slide.media if f.placement == "right"]
        fill = [f for f in slide.media if f.placement == "fill"]

        stack = ""
        if fill:
            figs = "".join(f.html() for f in fill)
            stack = f'<div class="fill">{figs}</div>'

        centre = f'<div class="flow">{body}{stack}</div>'

        if left or right:
            side = "".join(f.html() for f in left + right)
            aside = f'<div class="aside">{side}</div>'
            order = [aside, centre] if left else [centre, aside]
            inner = f'<div class="split">{"".join(order)}</div>'
        else:
            inner = centre

        style = []
        if slide.bg:
            style.append(f"--bg:{slide.bg}")
        if slide.fg:
            style.append(f"--fg:{slide.fg}")
        attr = f' style="{";".join(style)}"' if style else ""

        footer = self.meta.get("footer", "")
        chrome = ""
        if footer:
            chrome += f'<div class="footer">{footer}</div>'
        if self.meta.get("slidenumbers", "").lower() == "true":
            chrome += f'<div class="number">{number}</div>'

        return (f'<section class="slide" id="s{number}"{attr}>'
                f'<div class="canvas">{inner}{chrome}</div></section>')

    def html(self):
        title = self.title or self.name
        slides = "\n".join(self._slide_html(s, i + 1)
                           for i, s in enumerate(self.slides))
        return TEMPLATE.replace("%%TITLE%%", title).replace("%%SLIDES%%", slides)

    def copyAssets(self):
        """Copy figures into docs/assets/media/.

        A lecture that references an image which is not in media/ is a broken
        reference in the lecture, not a reason to abandon the deck. Report it
        and carry on, so one bad path cannot take out the whole build."""
        self.missing = []
        for fig in self.figures:
            try:
                fig.image.copy()
            except FileNotFoundError:
                self.missing.append(fig.src)

    def warnings(self):
        for src in sorted(set(getattr(self, "missing", []))):
            print(f"Warning: {self.filename}: missing image {src}")

        """A .pdf that reaches the browser is a broken image, not a slow one.

        Image() converts PDF figures to SVG with pdftocairo or dvisvgm. If
        neither is installed the reference survives as .pdf, which no browser
        will render, so say so rather than shipping a deck full of gaps."""
        bad = sorted({f.image.filesrc for f in self.figures
                      if f.image.filesrc.lower().endswith(".pdf")})
        if bad:
            print(f"Warning: {self.filename}: {len(bad)} PDF figure(s) not "
                  f"converted to SVG; install poppler-utils (pdftocairo) or "
                  f"dvisvgm. First: {bad[0]}")
        return bad


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%%TITLE%%</title>
<style>
:root { --bg:#ffffff; --fg:#111111; --accent:#0b5cad; }
* { box-sizing: border-box; }
html {
  height:100%;
  overflow-y:scroll;
  scroll-snap-type: y mandatory;
}
body { margin:0; padding:0; background:#222; }
body { font-family: Helvetica, Arial, sans-serif; }

/* Navigation is the browser's own scrolling, snapped one slide at a time.
   Scroll wheel, trackpad, swipe, arrows, space and Page Up/Down therefore all
   work with no JavaScript at all, in every browser. The script only sizes
   text and adds fullscreen; if it fails the deck still presents. */
.slide {
  display:flex; width:100vw; height:100vh;
  align-items:center; justify-content:center;
  scroll-snap-align:start;
  scroll-snap-stop:always;   /* a fast swipe advances one slide, not five */
}

.canvas {
  position:relative;
  width:min(100vw, 177.78vh);
  height:min(56.25vw, 100vh);
  /* JS resets --u in px per slide; this keeps the deck readable if it never
     does, because every size below is calc()ed from it. */
  --u: 1vw;
  background:var(--bg); color:var(--fg);
  padding: calc(var(--u) * 5) calc(var(--u) * 6);
  font-size: calc(var(--u) * 2.6);
  line-height:1.35;
  overflow:hidden;
  display:flex; flex-direction:column;
}

.flow { display:flex; flex-direction:column; min-height:0; flex:1 1 auto; gap: calc(var(--u) * 1.5); }
.split { display:flex; flex-direction:row; align-items:center; gap: calc(var(--u) * 3); flex:1 1 auto; min-height:0; }
.split > * { flex:1 1 50%; min-width:0; min-height:0; }
.aside { display:flex; align-items:center; justify-content:center; height:100%; }
.cols { display:flex; flex-direction:row; gap: calc(var(--u) * 4); flex:0 0 auto; }
.cols > .col { flex:1 1 0; min-width:0; }
.fill { flex:1 1 auto; min-height:0; display:flex; align-items:center; justify-content:center; }

/* A placed figure fills its box in both directions: Deckset's `fit` scales an
   image up as well as down, and max-width alone only ever shrinks. object-fit
   keeps the aspect ratio, so this letterboxes rather than distorts. */
img.fig { display:block; margin:0 auto; object-fit:contain; }
.fill img.fig, .aside img.fig { width:100%; height:100%; }

/* A wide equation must shrink to its column, not run into the next one.
   MathJax's SVG output has an intrinsic width, so without this a long inline
   formula overflows silently. */
mjx-container { max-width:100%; }
mjx-container svg { max-width:100%; height:auto; }
.col { min-width:0; overflow:hidden; }
img.fig-inline { max-width:100%; max-height: calc(var(--u) * 34); margin: calc(var(--u) * 1) auto; }

h1 { font-size: calc(var(--u) * 7); margin:0 0 calc(var(--u) * 2) 0; line-height:1.1; }
h2 { font-size: calc(var(--u) * 4.6); margin:0 0 calc(var(--u) * 1.5) 0; line-height:1.15; }
h3 { font-size: calc(var(--u) * 3.4); margin:0 0 calc(var(--u) * 1) 0; }
h1.fit, h2.fit { font-size: calc(var(--u) * 9); }
p, li { margin: calc(var(--u) * 0.8) 0; }
ul, ol { margin: calc(var(--u) * 0.8) 0; padding-left: calc(var(--u) * 3.5); }
a { color:var(--accent); }
code, pre { font-family: "SF Mono", Menlo, Consolas, monospace; font-size:0.85em; }
pre { background:rgba(127,127,127,.12); padding: calc(var(--u) * 1.2); overflow:auto; }
table { border-collapse:collapse; font-size:0.9em; }
th, td { border-bottom:1px solid rgba(127,127,127,.4); padding: calc(var(--u) * 0.5) calc(var(--u) * 1); text-align:left; }
sub sub { font-size:0.7em; }

.footer, .number {
  position:absolute; bottom: calc(var(--u) * 1.8);
  font-size: calc(var(--u) * 1.5); opacity:.45;
}
.footer { left: calc(var(--u) * 6); }
.number { right: calc(var(--u) * 6); }

@media print {
  html, body { background:#fff; }
  .slide { display:flex !important; page-break-after:always; break-after:page;
           width:100%; height:auto; }
  .canvas { width:100%; height:auto; aspect-ratio:16/9; }
}
</style>
</head>
<body>
%%SLIDES%%
<script>
// Everything here is an enhancement. Navigation is native scrolling (see the
// scroll-snap rules above), so a failure in this block costs text fitting and
// the fullscreen key, never the deck itself.
const slides = [...document.querySelectorAll('.slide')];
const fitted = new Set();

function autoscale(canvas) {
  // Sizes are calc()ed from --u, so shrinking one number shrinks the slide.
  const base = canvas.clientWidth / 100;
  let k = 1;
  canvas.style.setProperty('--u', base + 'px');
  // Overflow goes both ways: too much text, or one equation too wide to wrap.
  const over = () => canvas.scrollHeight > canvas.clientHeight + 1
                  || canvas.scrollWidth > canvas.clientWidth + 1;
  for (let i = 0; i < 24 && over(); i++) {
    k *= 0.97;
    canvas.style.setProperty('--u', (base * k) + 'px');
  }
  fitted.add(canvas);
}

function fitAll() { slides.forEach(s => autoscale(s.querySelector('.canvas'))); }

// Fit slides as they come near the viewport rather than all at once: the
// longest deck here is 121 slides, and each fit costs a few forced layouts.
if (window.IntersectionObserver) {
  const io = new IntersectionObserver(entries => {
    for (const e of entries) {
      const canvas = e.target.querySelector('.canvas');
      if (e.isIntersecting && !fitted.has(canvas)) autoscale(canvas);
    }
  }, { rootMargin: '200% 0px' });
  slides.forEach(s => io.observe(s));
} else {
  fitAll();
}

let resizeTimer;
addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => { fitted.clear(); fitAll(); }, 150);
});

function current() {
  const mid = innerHeight / 2;
  return Math.max(0, slides.findIndex(s => {
    const r = s.getBoundingClientRect();
    return r.top <= mid && r.bottom > mid;
  }));
}
function go(n) {
  const t = slides[Math.max(0, Math.min(slides.length - 1, n))];
  if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// The browser already scrolls on these keys; taking them over just makes each
// press move exactly one slide.
addEventListener('keydown', e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const k = e.key;
  if (['ArrowRight', 'ArrowDown', 'PageDown', ' '].includes(k)) { go(current() + 1); e.preventDefault(); }
  else if (['ArrowLeft', 'ArrowUp', 'PageUp'].includes(k)) { go(current() - 1); e.preventDefault(); }
  else if (k === 'Home') { go(0); e.preventDefault(); }
  else if (k === 'End') { go(slides.length - 1); e.preventDefault(); }
  else if (k === 'f') {
    const el = document.documentElement;
    // Safari still only has the prefixed call.
    (el.requestFullscreen || el.webkitRequestFullscreen)?.call(el);
  }
});

window.MathJax = {
  tex: { inlineMath: [['\\(', '\\)']], displayMath: [['\\[', '\\]']] },
  svg: { fontCache: 'local' },
  // Refit once the maths is typeset, so the measurements are of the rendered
  // equations rather than the placeholder text.
  startup: {
    pageReady: () => MathJax.startup.defaultPageReady().then(() => {
      fitted.clear();
      fitAll();
      if (location.hash) document.querySelector(location.hash)?.scrollIntoView();
    })
  }
};
</script>
<script src="vendor/tex-svg.js"></script>
</body>
</html>
"""


@click.command()
@click.argument("filename")
@click.option("--outdir", default="docs/assets/html", help="Where to write the deck")
def slides(filename, outdir):
    """Render FILENAME, a Deckset lecture, to an HTML slide deck."""
    options = dict()
    options["jekyll"] = "/"          # Image copies to docs/assets/media/
    options["dir"] = os.path.dirname(filename)

    os.makedirs(outdir, exist_ok=True)
    os.makedirs("docs/assets/media/", exist_ok=True)

    deck = Deck(filename, options)
    deck.copyAssets()
    deck.warnings()

    out = os.path.join(outdir, deck.name + ".html")
    with open(out, "w") as fo:
        fo.write(deck.html())
    print(f"Info: {filename} -> {out} ({len(deck.slides)} slides)")


if __name__ == "__main__":
    slides()
