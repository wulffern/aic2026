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

Three ways to get metadata, tried in this order:

1. **Xplore's "Cite This", by article number.** The button posts to
   `/rest/search/citation/format?recordIds=<arnumber>&download-format=download-bibtex`,
   which returns IEEE's own BibTeX. This is the *preferred* route and not merely
   because the metadata is authoritative: it looks the paper up by the number
   already sitting in the lecture's URL, so unlike a title search it structurally
   cannot come back with a different paper. Around 80 of the 84 candidates carry
   such a number. Xplore does sit behind bot protection, so this is allowed to
   fail per-link and fall through to Crossref.
2. **Crossref by title, then BibTeX by DOI.** No API key, and the link text in
   the lectures is usually the exact paper title:
   `https://api.crossref.org/works?query.bibliographic=<title>&rows=3`. This is
   the route that can pick the wrong paper — see Risks — so entries it produces
   are marked `% CHECK` unless the title matches character for character.
3. **Manual drop folder.** Download the `.bib` from Xplore by hand and let the
   merge step re-key it. The fallback for the NTNU Open theses and anything the
   first two miss, and the path the course owner already knows.

Each staged entry records which route produced it (`% source: ieee` or
`% source: crossref -- <why Xplore was skipped>`), so a run tells you whether
the article-number path is working without reading the job log.

### Where the Xplore route currently stands

Measured from a GitHub runner, not assumed:

- A plain client gets **HTTP 418** from both Xplore endpoints — its answer to
  anything that does not look like a browser.
- Sending browser headers (agent, `Accept`, and a `Referer` pointing at the
  document page) **clears the 418**. Both endpoints then respond.
- What comes back is still not the article. The document page arrives as
  **2055 bytes with an empty `<title>` and no metadata blob — byte-identical
  for two different article numbers**. That is a challenge page, so the
  blocking is by IP reputation, not by headers, and no amount of parser work
  will fix it. The unresolved list records exactly this, which is how it was
  diagnosed rather than guessed.

So the plumbing is right and the fallback is doing its job — the 9-entry sample
in `pdf/incoming.bib` came entirely from Crossref. Two ways to actually get the
IEEE route working, in order of effort:

1. **Run `fetch --source ieee` from your own machine**, on the NTNU network,
   where you are a recognised Xplore user. Nothing about the command is
   CI-specific; only the network is. This is the cheap one — the code is done,
   and it would resolve ~80 of the 84 candidates by article number, which is the
   only way to make the Banba/Navarro failure class impossible rather than
   merely visible.
2. **Use the official IEEE Xplore metadata API with a key** (free for
   non-commercial use). `article_number=` maps straight to full metadata with
   no bot check, which would make the article-number route work in CI too. Read
   the key from a repository secret; the workflow already passes one
   environment variable through for Crossref and would take a second the same
   way.

Until one of those lands, `both` is the right default: Xplore is tried, costs a
couple of seconds per link, and Crossref catches everything it misses.

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
| `limit` | `0` | Stop after N papers. Use `6` for a trial run before spending 80 API calls. Candidates that carry a DOI or a real title are tried first, so a small limit is still representative. |
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

Not covered: the two functions that open a socket. Those are exercised by
running `fetch` in Actions. The failure path is covered from both ends — behind
a blocking proxy the command degrades to an unresolved list with a reason per
link, and the job exits non-zero only when a lookup genuinely failed, not when
a link simply needs a human.

Two things the first trial run in Actions taught, both now fixed: `--limit`
used to slice the front of the scan list, which is lecture order, so a trial
run tested only the prose links in the early lectures and staged nothing; and
the command used to fail whenever it staged nothing, which made a
correctly-behaving trial run look broken.

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

**Phase 3 — Merge.** Done. 77 entries staged, reviewed and appended to
`aic.bib`, which now holds 645. `walden99a` turned out to duplicate the
`walden99` entry the file had held for years and was folded into it, keeping the
old key and taking the new DOI.

**Phase 4 — Rewrite.** Done. 119 links across 19 lectures now read as the title
in prose followed by `[@key]`, via `py/linkbib.py apply` rather than hand edits,
so it can be re-run. Both outputs verified: the website footnote list, and a
compiled `l07_vreg.pdf` where the title reads `... for Microprocessors [5]` with
the reference resolving in the IEEE-style list.

**Phase 5 — Consistency sweep.** Down to 4 occurrences of 2 papers, both listed
under Still Open below. The `scan` job keeps `pdf/link_candidates.tsv` current.

## Still Open

Two items, neither blocking. Both were left deliberately.

### The two NTNU Open theses

Four links, two papers, and the only candidates the conversion did not reach:

| Lecture | Paper |
|---|---|
| `l04_afe` (×2), `l06_adc` | Design Considerations for a Low-Power Control-Bounded A/D Converter |
| `l08_pll` | Ultra Low Power Frequency Synthesizer |

Neither is in Xplore or Crossref — no article number, and the best Crossref
title match scored 0.55 and 0.84. They need entries written by hand from the
NTNU Open record; guessing the authors would be worse than leaving the links.
Once the two `@phdthesis` (or `@mastersthesis`) entries are in `aic.bib`:

```sh
python3 py/linkbib.py apply     # picks them up from the location comments
python3 py/linkbib.py scan      # should report zero candidates
```

### Citations that land on slides

`py/slides.py` has no citation handling, so `[@razavi17]` renders as that
literal string on any slide where it is not inside a `<!--pan_doc: -->` block.
The course had 2 such citations before this work (`l00_diode:155`,
`lr0_noise:319`); it now has 58, so what was a curiosity is worth a decision.

Three ways out, cheapest last:

1. **Teach `slides.py` to render citations.** It already reads `pdf/aic.bib`
   indirectly through nothing at all today, but `linkbib.read_bib_keys` and the
   `Bibtex` class in `lecture.py` both parse it. Rendering `[@key]` as a small
   author-year mark fixes all 58 at once and improves the two that predate this
   work. This is the one to do.
2. **Wrap the affected sections in `pan_doc`.** Correct for the *Want to learn
   more?* lists in `l03_refbias`, `l04_mac` and `lx_energysrc`, which are already
   web-and-book content rather than slide content. Does nothing for the inline
   prose citations.
3. **Leave it.** The string is ugly on a slide but not wrong, and the decks are
   presented by someone who knows what it means.

## Risks

- **Wrong paper matched by title.** The main correctness risk, and it is not
  hypothetical — the first staging run hit it. `l03_refbias` links *"A CMOS
  bandgap reference circuit with sub-1-V operation"* (Banba, JSSC 1999,
  `document/760378`). Crossref returned Navarro's ISCAS 2011 *"A **simple** CMOS
  bandgap reference circuit with sub-1-V operation"* — a different paper whose
  title contains the one asked for. The two score ~0.96 against each other, so
  **no similarity threshold separates them**; raising the bar would only start
  rejecting correct matches with punctuation drift.

  The mitigation is therefore not a better threshold but visibility: an entry
  whose Crossref title is not character-for-character the link text is marked
  `% CHECK` in `incoming.bib`, with both titles printed above it, and listed
  first in the run summary. Those get read before merging. This is the concrete
  reason `commit` defaults to off.
- **Footnote numbering on the web.** `Lecture._replaceCites` numbers citations
  continuing from the existing `[^n]` footnotes in a lecture. Lectures that mix
  hand-written footnotes with citations — `l00_diode` has `[^1]` through `[^4]` —
  need their rendered post checked, not just their source.
- **Losing the annotation.** `l07_vreg` and `l09_osc` carry real teaching value
  in the prose around each link. Pattern A preserves it; a blind
  find-and-replace would not.
- **Churn across 21 lectures.** Per-lecture commits keep it reviewable and let
  the work stop cleanly at any point.

## What Actually Bit

For the record, since none of these were the risk anyone would have guessed:

- **Crossref returning a different paper whose title contains the one asked
  for**, twice. Banba 1999 came back as Navarro 2011; "Attention Is All You
  Need" came back as a 2025 book chapter called "Is Attention All You Need?".
  Resolving by IEEE article number removed the whole class for the 74 entries
  that had one. The `% CHECK` mark caught the arXiv one, which had no number.
- **Staging comments merged into `aic.bib`.** `Bibtex._read` in `lecture.py`
  accumulates from one `@` to the next, so each `% lecture:line` comment ended
  up inside the DOI of the entry above it, and the website rendered
  `<https://doi.org/10.1109/JSSC.2003.820870   % l08_pll.md:649 % source: ieee>`.
  Fixed at both ends: comments stripped from the bibliography, and the parser
  now skips comment lines.
- **Unicode and `{\rm ...}` in imported titles** broke four standalone PDFs and
  the book, since Crossref and Xplore both hand back µ, σ and old font commands.
  `latexify()` rewrites them on import.
- **A duplicate that no dedupe check could see.** `walden99a` matched neither by
  DOI (the old entry had none) nor by link text ("1999, R. Walden: Analog-to-
  digital converter survey and analysis" against "Analog to Digital Converter
  Survey and Analysis"). Only comparing the *resolved* title caught it.
