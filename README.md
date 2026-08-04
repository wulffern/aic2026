# aic2026
Advanced Integrated Circuits 2026

## License

Two licenses, by scope.

- **Course material** — the lectures in `lectures/`, the generated book and
  slides, and the original figures in `media/` and `tikz/` — is licensed
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See
  `LICENSE-BOOK`. Reuse it, adapt it, teach from it; credit Carsten Wulff,
  link the license, and say if you changed anything.
- **Code** — `py/`, `ex/`, `slides/`, `docker/`, and the makefiles — is
  licensed MIT. See `LICENSE-CODE`.

A few third-party figures keep their own licenses (CC BY 3.0, CC BY 4.0 and
CC BY-SA 2.5/3.0/4.0). Each is credited in its figure caption, and those
terms govern that figure rather than the CC BY 4.0 above.

## New year

- Clone repo into new dir (aic2027)
- Create git repo for new year
- Change origin
- Push

Generated artifacts are not tracked: `pdf/` holds only sources (the
build runs in `.build/`), and `media/*_tikz.*` come from `make tikz`.
Possible follow-up for a new year: generate the hand-drawn SVGs'
PDF exports with `rsvg-convert` too and untrack them after a visual
check of the book.
