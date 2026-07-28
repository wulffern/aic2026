# Slide deck assets

Static files copied into `docs/assets/slides/` by `make slides`. That directory
is generated and gitignored (`.gitignore` ignores `assets/`), so anything the
decks need at runtime has to live here and be copied, the same way `media/` is
the source for `docs/assets/media/`.

## vendor/tex-svg.js

MathJax 3.2.2, SVG output build, vendored deliberately rather than loaded from
a CDN. Two reasons:

- A deck is presented in a lecture room. Wi-fi there is not a dependency worth
  taking, and a CDN failure means every equation on every slide renders as raw
  TeX source.
- The SVG build needs no font files. It emits glyphs as SVG paths, so this one
  file is the whole dependency. The CHTML build would drag in about twenty
  woff2 files.

It is 2.1 MB and it never changes. Upgrade with:

    npm pack mathjax@3
    tar xzf mathjax-*.tgz package/es5/tex-svg.js package/LICENSE
    mv package/es5/tex-svg.js slides/vendor/tex-svg.js
    mv package/LICENSE slides/vendor/MATHJAX-LICENSE

Apache 2.0, see `MATHJAX-LICENSE`.
