# Converting Lecture Links to Bib References

## Summary

Most lectures point students at papers with a bare markdown link — a title and an
IEEE Xplore URL under *Want to learn more?*. A few lectures (`l00_diode`,
`l01_project`, `l04_afe`, `lr0_noise`) instead cite properly with `[@key]` against
`pdf/aic.bib`. This plan converts the link-style pointers to real bibliography
entries so every lecture cites the same way, the book gets a proper reference
list, and a dead Xplore URL no longer loses the reference.

The conversion is per-lecture and review-gated, the same way
`tikz_translation_plan.md` works: nothing lands in a lecture until the entries
behind it are in `pdf/aic.bib` and the pair has been looked at.

## What the Scan Found

`py/linkbib.py scan` is the phase-1 inventory. It reads only; it never edits a
lecture.

```sh
python3 py/linkbib.py scan
python3 py/linkbib.py scan --tsv pdf/link_candidates.tsv
```

Current numbers:

| | |
|---|---|
| Occurrences of a citable link | 123 |
| Distinct papers behind them | 84 |
| Papers linked from more than one place | 24 |
| Already in `pdf/aic.bib` | 5 |
| **New bib entries needed** | **79** |

Spread across 20 lectures, the biggest being `lx_energysrc` (13), `l05_sc` (12),
`l07_vreg` (12), `l06_adc` (11), and `l10_lpradio` (10). The full per-occurrence
list is `pdf/link_candidates.tsv`. Five are not IEEE: two NTNU Open theses, a
Springer article, an arXiv paper, and a Cambridge book DOI.

The 24 repeats are the strongest argument for doing this at all — one paper
(`document/7906479`, the compiled SAR ADC) is linked from nine places across
seven lectures, each with its own hand-typed title. One bib key fixes all nine.

### In scope

Links whose host publishes citable literature: `ieeexplore.ieee.org`,
`ntnuopen.ntnu.no`, `link.springer.com`, `doi.org`, `arxiv.org`, `dl.acm.org`,
`researchgate.net`.

### Out of scope, stays a plain link

- Wikipedia (79), GitHub (58 + 8 bare), YouTube (13), vendor and tool pages
  (Synopsys, Cadence, Siemens, ngspice, Nordic, …), `analogicus.com` (30).
- Google Patents — `l06_adc` links a patent; not a paper.
- IEEE URLs that are not one article: `/search/` result pages (`l04_afe` Gm-C,
  `l12_chinf` LVDS and SERDES), `/book/`, and the eight `/mediastore_new/` image
  URLs in `lx_energysrc` (those are figures, and already commented out).
- Links straight to an image file on an otherwise citable host — the ResearchGate
  band-diagram figure in `l00_need_to_know` is artwork, not a reference.

`linkbib.py` encodes both lists, so the scan output *is* the scope.

## Where the Metadata Comes From

IEEE Xplore offers a per-article citation download, but it is behind session
state and a bot check, so it cannot be scripted directly. Three ways to get
metadata, in the order to try them:

1. **Crossref by title, then BibTeX by DOI.** No API key. The link text in the
   lectures is already the exact paper title, which makes this reliable:
   `https://api.crossref.org/works?query.bibliographic=<title>&rows=3`, then
   `curl -LH "Accept: application/x-bibtex" https://doi.org/<doi>`. Verify the
   returned title against the link text and reject anything below a similarity
   threshold — a wrong-but-plausible entry is worse than a missing one.
2. **IEEE Xplore metadata API**, if a key is available. `article_number=` maps an
   Xplore document ID straight to a DOI and full metadata, no title guessing.
   Better for the handful of items Crossref cannot match.
3. **Manual drop folder.** Download the `.bib` from Xplore by hand into
   `pdf/incoming/`, and let the merge step re-key and fold it into `aic.bib`.
   This is the fallback for the NTNU Open theses and anything else the first two
   miss, and it is the path the course owner already knows.

> Note: a containerised environment often cannot reach `api.crossref.org` or
> `doi.org` — an agent or corporate proxy answers 403 to CONNECT, which is
> exactly what happened while this plan was written. That is the main reason
> the fetch step runs in GitHub Actions, where the network is open. Scan,
> merge, and rewrite all work offline.

## The GitHub Action

`.github/workflows/bib.yaml` has the two halves.

**`scan`** runs on every push touching `lectures/`, `py/linkbib.py`, or the
workflow. It runs the unit tests, re-derives `pdf/link_candidates.tsv`, and
commits it if it changed — the same commit-generated-output idiom as
`tikz.yaml`. Adding a raw paper link to a lecture then shows up as a diff on
that file, so the inventory cannot quietly go stale.

**`fetch`** is `workflow_dispatch` only, with two inputs:

| Input | Default | Meaning |
|---|---|---|
| `limit` | `0` | Stop after N papers. Use `5` for a trial run before spending 80 API calls. |
| `commit` | off | Commit `pdf/incoming.bib` to the branch. Off deliberately. |

It resolves candidates against Crossref, writes `pdf/incoming.bib` and
`pdf/link_unresolved.tsv`, uploads both as artifacts, and prints the staged
BibTeX plus an unresolved table to the run summary. Artifacts upload even when
the job fails, because a run that resolved nothing still explains itself in the
unresolved list.

`commit` is off by default on purpose: a Crossref title match can be
confidently wrong, and a bad entry is far harder to spot once it is in the book
than while it is sitting in `incoming.bib`. Nothing in the workflow ever writes
to `pdf/aic.bib` or to a lecture.

Set a `CROSSREF_MAILTO` repository variable to put the queries in Crossref's
polite pool — optional, but faster and less likely to be throttled.

### What is tested, and what is not

`py/test_linkbib.py` (30 tests, stdlib `unittest`, no new dependency) covers URL
normalisation, the scope rules, author formatting, key minting against the real
`aic.bib`, Crossref-record parsing from a fixture, and the emitted BibTeX —
including a test that new entries do *not* carry the `};` terminator. The scan
tests run against the actual lectures, so they notice drift.

Not covered: the two functions that open a socket. Those are exercised the
first time `fetch` runs in Actions. Its failure path is tested, though — behind
a blocking proxy the command degrades to an unresolved list with the reason
recorded per link, and exits non-zero.

## Entry Shape and Keys

Follow what `aic.bib` already does: `<firstauthorlastname><yy>`, lowercase for
recent additions (`tang20`, `harpe12a`, `iizuka06`), with `a`/`b` suffixes on
collision. Dedupe candidates against the existing 569 entries by DOI first, then
by squashed title, before minting a key.

Every new entry carries `doi=` and, where there is no DOI, `url=`. This matters
because both output paths already know what to do with them:

- **Book/PDF** — `pandoc --citeproc --csl=pdf/ieee-with-url.csl` prints the URL
  in the reference list.
- **Website** — `Bibtex.toMarkdownRef` in `py/lecture.py:129` emits `<url>` and
  `<https://doi.org/…>` as autolinks in the footnote definition.

So a converted link stays clickable for students on the web. Nothing in the
pipeline needs changing to get that.

## How a Lecture Gets Rewritten

Two patterns, depending on where the link sits.

**A. Reference lists and *Want to learn more?* sections** — the title is the
content; students need to see what they are about to read. Keep the title as
text and append the citation:

```markdown
A 10-bit 50-MS/s SAR ADC With a Monotonic Capacitor Switching Procedure [@Liu10]
```

Not `[@Liu10]` alone, which would render on the web as a bare `[^12]` marker and
turn a readable reading list into a column of numbers. Where a link already has
an annotation after it — `l07_vreg` has a sentence of commentary on each paper —
the annotation is untouched.

**B. Inline prose mentions** — the link interrupts a sentence. Replace it
outright, matching how `l01_project` already reads:

```markdown
In [@tang20] they used a leakage based digital ring oscillator
```

### The slides caveat

Ten of the thirteen *Want to learn more?* sections live inside `<!--pan_doc: -->`,
so they never reach a slide and `[@key]` is safe. Three do not: **`l03_refbias`,
`l04_mac`, and `lx_energysrc`** have the section in plain body text, where
`py/slides.py` would render the literal string `[@key]` on a slide. For those
three, either wrap the section in `pan_doc` like the others (recommended — it is
what the rest of the course does) or leave them as plain links. Decide before
touching them, not during.

## Bib Hygiene Found Along the Way

Three problems in `pdf/aic.bib` that predate this work. None of them block the
conversion, and new entries should simply not repeat them:

1. **443 entries close with `};` instead of `}`.** The stray semicolon is not
   valid BibTeX. Tolerated by pandoc today; would break any other tool.
2. **Journal names are undefined macros.** `journal= IEEE_J_JSSC` with no
   `@string{IEEE_J_JSSC = ...}` anywhere in the file and no strings file
   included. Whatever those references currently render as, it is not the
   journal name. Fix by adding the IEEE `@string` block, or by expanding the
   macros in place.
3. **Not one entry has a `url=` field**, despite the CSL being *IEEE with URL*
   and the website code being ready to print it. Only 45 of 569 have a `doi=`.

A cleanup pass for these is worth doing, but as its own change — mixing it into
the link conversion makes both harder to review.

## Phases

**Phase 1 — Inventory.** Done. `py/linkbib.py scan` produces the candidate list
and the numbers above, and the `scan` job keeps it current.

**Phase 2 — Fetch and stage.** Done, as the `fetch` job. Run it from the Actions
tab with `limit: 5` first to see the entry quality, then with `limit: 0` for the
rest. Download the `bib-incoming` artifact, or re-run with `commit: true` to get
the files onto the branch. Nothing touches `aic.bib` yet.

**Phase 3 — Merge.** Review `pdf/incoming.bib`, dedupe against `aic.bib` by DOI
and title, then append. Verify the book still builds — `make latex-nobuild` — with
the entries present but not yet cited. This is the checkpoint: the bibliography
is correct before any lecture depends on it.

**Phase 4 — Rewrite, one lecture at a time.** For each lecture, apply pattern A
or B per link, then build both outputs and read them:

```sh
python3 py/lecture.py post  lectures/<name>.md    # check the footnote list
python3 py/lecture.py latex lectures/<name>.md    # check the reference list
```

Order: start with `l04_dac` (4 links, already has a `# References` heading and an
existing `[@cjm11]` citation — smallest useful proof) then `l02_esd` (6, textbook
`pan_doc` case), then work up through the larger lectures. Handle the three
slide-visible sections only after that decision is made.

**Phase 5 — Consistency sweep.** The `scan` job does this continuously:
`pdf/link_candidates.tsv` shrinks as lectures convert, and whatever remains is
either deliberately out of scope or missed. Confirm the 24 multi-lecture papers
all resolved to one key each, and that `pdf/aic.pdf` and the site both render
the new references.

## Risks

- **Wrong paper matched by title.** The main correctness risk. Mitigated by
  verifying the fetched title against the link text and routing anything
  ambiguous to manual review rather than guessing.
- **Footnote numbering on the web.** `Lecture._replaceCites` numbers citations
  continuing from the existing `[^n]` footnotes in a lecture. Lectures that mix
  hand-written footnotes with citations — `l00_diode` has `[^1]` through `[^4]` —
  need their rendered post checked, not just their source.
- **Losing the annotation.** `l07_vreg` and `l09_osc` carry real teaching value
  in the prose around each link. Pattern A preserves it; a blind
  find-and-replace would not.
- **Churn across 21 lectures.** Per-lecture commits keep it reviewable and let
  the work stop cleanly at any point.
