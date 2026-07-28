# All-Lectures SVG to TikZ Translation Workflow

## Summary
Translate lecture figures from SVG/PDF artwork to maintainable hand-authored TikZ/CircuitikZ across the full course, but only for figures that are schematic-like and benefit from redraw.

The process is strictly sequential and review-gated:
1. Propose one figure.
2. Open the original source and the proposed TikZ PDF.
3. Wait for approval or comments.
4. Only after approval, proceed to the next figure.

Already-established outputs remain the model:
- `l3_sources_tikz`
- `l3_vsrc_tikz`
- `l3_vi_tikz`

## What Counts for This Workflow
Include:
- circuit schematics
- block diagrams with clear electrical structure
- switched-capacitor, OTA, PLL, ADC, DAC, oscillator, bias, regulator, logic, and signal-chain diagrams that can be redrawn idiomatically in TikZ/CircuitikZ

Exclude by default:
- plots, measurement graphs, timing captures, layout screenshots, microscopy, photos, logos, maps, process cross-sections, and dense illustration-style figures
- figures where TikZ would become a path trace rather than a clean redraw

Replacement policy:
- Do not update lecture references until that specific figure is approved.
- Drawing, compiling, and committing `tikz/<basename>.tex` plus `media/<basename>_tikz.pdf` does **not** require approval — those artifacts are inert until a lecture points at them. Only the lecture reference switch is gated.
- After approval, switch that figure's references to `../media/<basename>_tikz.pdf`.
- A figure used by more than one lecture is approved once, then switched in **every** lecture that references it in the same round. Check with `grep -rn '<basename>\.pdf' lectures/` before switching so no stale reference is left behind.
- Leave all unapproved figures untouched.

## Per-Figure Execution Loop
For every figure in the queue:

1. Read the lecture context around the figure in `lectures/<lecture>.md`.
2. Inspect the original artwork in `media/<basename>.svg` or the SVG source behind the current PDF if both exist.
3. Draft or update `tikz/<basename>.tex` using:
   - `tikz/fig_header.tex`
   - `tikz/ckt_lib.tex`
   - CircuitikZ/TikZ primitives
   - simplified, maintainable geometry rather than literal SVG tracing
4. Compile only that figure with `make tikz-one FNAME=<basename>`, which builds to
   `tikz/build/<basename>.pdf` and copies the outputs to `media/` (including an SVG
   mirror when `pdf2svg` or `dvisvgm` is available).
5. Open:
   - original SVG/PDF source
   - proposed TikZ PDF
6. Report the proposal briefly and stop.

Approval gate:
- `approve`: switch the lecture reference(s) per the replacement policy, move the figure to Approved in Saved Progress, then continue
- `comment`: revise the same figure, recompile, reopen both files, and wait again
- a figure that is drawn but not yet reviewed sits in Pending Approval; its lecture references stay on the original artwork until you say otherwise

Never switch a lecture reference without an explicit approval for that figure.

## Figure Queue by Lecture
Process lectures in this order unless reprioritized later.

### Phase 1: Highest-value schematic lectures
- `l03_refbias`
  - `l3_vsrc`
  - `l3_isrc`
  - `l3_bjtonly`
  - `l03_vref1`
  - `l03_vref2`
  - `l3_gmcell`
  - `l3_gmcap`

- `l04_afe`
  - `l4_achai`
  - `l4_radio`
  - `l4_first_order`
  - `l4_biquad`
  - `l4_gmc`
  - `l4_gmc_diff`
  - `l4_gmc_diff1`
  - `l4_gmc1st`
  - `l4_gmcbi`
  - `l4_activerc_first`
  - `l4_activebiquad`
  - `l4_activerc`
  - `l04_ota_diff`
  - `l04_ota_vsens`
  - `l04_ota_vcmfb`
  - `l04_ota_sch`

- `l05_sc`
  - `l05_fund1`
  - `l05_fund2`
  - `l05_fund3`
  - `l5_dtfig`
  - `l5_sh`
  - `l5_shaaf`
  - `l5_subsample`
  - `l5_sdomain`
  - `l5_zdomain`
  - `l5_zunstable`
  - `l5_iir`
  - `l5_fir`
  - `l5_scintro1`
  - `l5_scintro2`
  - `l5_scamp`
  - `l5_scfig`
  - `l5_scint`
  - `l5_scifig`
  - `l5_sw1`
  - `l5_sw2`
  - `l5_sw3`
  - `l5_novl`
  - `l5_scex`

- `l06_adc`
  - `l6_mwald`
  - `fig_sar_logic`
  - `l6_msch`
  - `l6_adc`
  - `l6_ct`
  - `l6_cten`
  - `l6_osr_2`
  - `l6_osr_4`
  - `l4_sdloop`
  - `l4_sd`
  - `l6_sdadc`
  - `l6_sd_d0_b1`
  - `l6_sd_d1_b1`
  - `l6_sdlog_d1_b5`
  - `l06_osd21`
  - `l6_fredrik_arch`

- `l07_vreg`
  - `l9_ldo_pmos`
  - `l9_ldo_nmos`
  - `l7_loadreg`
  - `l6_ldo_types`
  - `l7_ind_buck`
  - `l7_cap_buck`
  - `l7_ind_boost`
  - `l7_cap_boost`
  - `l7_buck`
  - `l9_sw_arch`
  - `l9_sw_state`

- `l08_pll`
  - `l10_fb`
  - `l10_freq_fb`
  - `l08_pll_m`
  - `l08_pll_sd`
  - `l08_pll_mod`
  - `l08_pll_2mod`
  - `l08_sun_pll`
  - `l10_pll_sm`
  - `SUN_PLL_ROSC`
  - `SUN_PLL_CP`
  - `SUN_PLL_LP`
  - `SUN_PLL_DIV`
  - `pll`

- `l09_osc`
  - `xosc_model`
  - `xosc_res`
  - `xosc_pierce`
  - `osc_ring`
  - `osc_ring_c`
  - `osc_ring_adv`
  - `osc_ring_cap`
  - `osc_ring_diff`
  - `lcosc`
  - `rcosc`

### Phase 2: Supporting lectures with clear redraw candidates
- `l04_dac`
  - `dac_error`
  - `dac_inl_dnl`
  - later any resistor-string / R-2R figures that prove worth redrawing

- `l01_intro`
  - `dig_des`
  - `dig_des_lr`

- `l01_project`
  - `TB_LEAK`
  - `aic2026_project_analog`

- `l11_aver`
  - `dig_des`
  - `dig_des_lr`

- `lr0_circuits`
  - `LELOTEMP_OTA_OP`

- `lr0_logic`
  - `l13/pdpu`
  - `l13/pu_pmos`
  - `l13/pd_nmos`
  - `l13/sr`
  - `l13/dlatch`
  - `l13/an2oi`
  - `l13/inv_tg`
  - `l13/ivtrix`
  - `l13/mux`
  - `l13/latch`
  - `l13/d_ff`
  - `l13/digital_ff_comb`
  - `l13/fig_sar_logic`

- `lr0_tut1`
  - `LELO_EX`

### Phase 3: Case-by-case later
- layout-heavy figures in `l06_adc`
- system/project overview drawings in `l01_project`
- map/logo/reference illustrations in `l10_lpradio`, `lp_radio_guest`, `lx_energysrc`
- semiconductor physics figures in `lr0_mosfet`, `lr0_passives`, `l00_diode`
- measurement/graph-heavy figures across `l00_*`, `l12_chinf`, and guest lectures

## Public Interfaces and Naming
Naming convention:
- source: `media/<basename>.svg` or existing equivalent
- TikZ source: `tikz/<basename>.tex`
- generated PDF: `media/<basename>_tikz.pdf`
- optional SVG mirror: `media/<basename>_tikz.svg`

Figures whose artwork lives in a `media/` subdirectory keep that structure: the
`lr0_logic` figures are `tikz/l13/<basename>.tex` → `media/l13/<basename>_tikz.pdf`.

`media/` is the only output location. Nothing in the TikZ workflow writes to
`pdf/media/` — that directory is gitignored and `Image.copy()` in `py/lecture.py`
repopulates it from `media/` on every latex build, flattening subdirectories to a
basename as it goes. Writing there by hand would only produce stale or
wrongly-nested duplicates.

Lecture markdown interface:
- approved figures reference `../media/<basename>_tikz.pdf`
- unapproved figures keep their current references

No new build system is introduced.
Use the existing local pattern already implied by:
- `tikz/fig_header.tex`
- `tikz/ckt_lib.tex`
- `pdflatex` outputs under `tikz/build/`

Root `Makefile` targets:
- `make tikz-one FNAME=<basename>` — build one figure. Accepts a bare basename, a
  subdirectory path (`l13/pdpu`), or a full path (`tikz/l3_vsrc.tex`).
- `make tikz` — build every figure under `tikz/`, at any depth.
- `make tikz-check` — compile every figure into `tikz/build/` without writing any
  output to `media/`. This is what CI runs.
- `make tikz-preview` — rasterise the `tikz/build/` PDFs to `preview/*.png`
  (needs `pdftoppm` from poppler). Run after `tikz-check`.
- `make preview FNAME=<basename>` — render a figure's original artwork and its
  TikZ redraw side by side into `preview/`, for the approval gate. Needs
  `pip install -r requirements-preview.txt`.
- `make print-tikz` — list the discovered figure sources.

Discovery is `find tikz -name '*.tex'` minus `fig_header.tex` and `ckt_lib.tex`,
so a new figure needs no Makefile edit regardless of its name or depth.

CI: `.github/workflows/tikz.yaml` runs `make tikz-check` on the
`texlive/texlive:TL2022-historic` image, failing the build when a figure source
stops compiling. It then runs `make tikz-preview` and uploads `preview/` as the
`tikz-previews` artifact, one PNG per figure, downloadable from the run summary.

It runs on **every branch and pull request**, not just `main` — the review loop
depends on pushing a draft and reading its preview before the lecture reference
is switched. It is a separate workflow from `matrix_build.yaml` for that reason;
the docs workflow is `main`-only and deploys Pages.

On a push (not a pull request) the job then runs `make tikz` and commits any
changed `media/*_tikz.pdf` back to the branch as "Rebuild TikZ figures [skip ci]".
So authoring a figure needs no local TeX install: commit `tikz/<basename>.tex`
alone and CI produces the PDF beside it.

Two consequences worth knowing:
- `make tikz-one` pins `SOURCE_DATE_EPOCH` and `FORCE_SOURCE_DATE`, because
  pdfTeX otherwise stamps a fresh `/CreationDate` into every PDF and CI would
  re-commit all the figures on each run. Rebuilds are byte-identical, so a
  no-op run commits nothing. Always build through the Makefile, never by
  calling `pdflatex` directly, or the next CI run will churn the file.
- The push is non-force. If the branch moves while the job runs, the push is
  rejected and the job fails; re-running it is the fix.

If you do have TeX locally, `make tikz-one FNAME=<basename>` still produces the
same bytes, and committing source and PDF together stays the tidier history.

## Reviewing Figures Without a TeX Install
`py/preview.py` renders committed artwork to PNG — PDF via `pypdfium2`, SVG via
`cairosvg`, bitmaps by copy. It reads what is already in `media/`; it does not
compile TikZ.

    pip install -r requirements-preview.txt
    make preview FNAME=l03_ptat        # original and redraw, side by side
    python3 py/preview.py media/l5_scamp.svg -o preview/

This covers two things the workflow needs: inspecting source artwork before
drafting a redraw, and reviewing any figure whose `_tikz.pdf` is committed.
Compiling a *new* draft still needs `pdflatex`, locally or through the CI job.

## Acceptance Criteria and Tests
For each proposal:
- LaTeX compiles without errors.
- The proposed PDF opens successfully.
- The redraw preserves the original topology, labels, polarity, control arrows, and signal names.
- The figure is cleaner than the SVG and maintainable as source.
- The visual language matches the existing TikZ figures in the repo.
- Only the reviewed figure is changed in that round.

For each lecture after approved replacements:
- lecture markdown references only approved `_tikz.pdf` figures
- no unrelated lecture figures are changed
- `tikz/<basename>.tex` and `media/<basename>_tikz.pdf` are committed together
- no lecture still references the old artwork for an approved figure

## Assumptions and Defaults
- Continue the queue from the Current next figure in Saved Progress.
- “Proposal” means a real draft plus compiled PDF, not a text-only sketch.
- The queue is lecture-ordered, but may be reprioritized at any time.
- Runtime approval may be required if opening GUI files needs escalated execution.
- Existing dirty or generated repo state is preserved and never cleaned up as part of this workflow.

## Saved Progress

### Approved and switched
In `lectures/l03_refbias.md`:
- `l3_sources`
- `l3_vsrc`
- `l3_isrc`
- `l3_bjtonly`
- `l3_vi`
- `l03_ptat` — shared figure, also switched in `lectures/l01_project.md` and
  `lectures/g03.md`
- `l03_vref1`
- `l03_vref2`
- `l3_gmcell`
- `l3_gmcap`

That is 10 figures, in three lectures.

### Pending approval
- none

Also converted and switched: `l3_ptat`, `l3_ptat1`, `l3_ptat2` — 13 figures total.

Development now happens directly on `main` at the user's request; the CI job
commits rebuilt figures back to whichever branch it runs on.

### `l03_refbias` is complete
Every schematic in the lecture is now a TikZ redraw — 15 figures. The only
remaining references are `l3_bgsim`, `l3_bgsimtfs` and `vd`, which are
simulation and measurement plots and correctly out of scope.

The queue in this document was **not exhaustive**: five schematics it never
listed (`l3_brokaw`, `l3_ptat`, `l3_ptat1`, `l3_ptat2`, `l3_ptat3`) were found
only by listing the lecture's figures directly.

The `l3_ptat`, `l3_ptat1` and `l3_ptat2` artwork marks the OTA polarity
backwards: + on the left input, - on the right. Rising current raises the
right-hand node by I*R1 more than the left, so + belongs on the right for the
loop to settle. The redraws correct this.

Before starting any lecture, list its figures with
`grep -o '](\.\./media/[^)]*)' lectures/<lecture>.md` and triage them, rather
than trusting the queue to be complete. The ~117 total understates the work.

## New Figures Requested (not conversions)
These are new teaching content for `l03_refbias`, requested by the user. They
need lecture text as well as figures, and the text is the harder half.

**Start here next session, in this order: curvature correction first**, then
Widlar, then the MOS-based reference. Take them ahead of `l05_sc` and ahead of
the remaining `l03_refbias` conversion work.

1. **Curvature correction.** `l3_bgsimtfs` and `vd` already show the residual
   curvature; nothing in the lecture corrects it. This closes that loop.
2. **Widlar reference.** Historical breadth alongside the Brokaw citation
   already in the lecture at line 362.
3. **MOS-based reference.** The user is explicit that this must be presented
   with a strong caveat, not as a recommendation:

   > MOS-based references that rely on the difference between two threshold
   > voltages are very risky and should not be attempted. Process control over
   > the separate Vt sources is poor and their stability is poor, so the
   > difference is neither well controlled nor stable.

   Draw and explain it as something to recognise and avoid, not as a design to
   copy. The warning is the point of including it.

### Current next figure
- `l05_sc`, reprioritised ahead of `l04_afe` at the user's request. The
  switched-capacitor idiom established in `l3_gmcap` carries straight over.

### Notes
- `l3_bjtonly` final geometry includes manual fixes by the user; preserve current source unless explicitly changing it.
- `l03_ptat` redraws the original's plain diodes as diode-connected PNPs, adds OTA
  input polarity the artwork did not specify, and labels the right-hand node `V_R1`
  rather than carrying over the original's `V_e1 ~ V_o1` equality annotation.
- `l03_vref1` labels the output branch's node `V_D3`; the original artwork says
  `V_D2` there while drawing `D3`, and the prose at `l03_refbias.md:317` says
  $V_{D3}$, so the artwork is the thing that is wrong. There is no `V_R2` — the
  node above `R2` is `V_REF`, which already names it.
- `l03_ptat` and `l03_vref1` share a 2.5-grid column spacing so the part of the
  circuit they have in common reads identically across the two slides. Keep them
  in step if either is re-laid-out.
- The OTA sits in a 90-degree rotated scope, and `circuitikz` is set up with
  `transform shape`, so any label passed to `\cicOtaSSWP` is rotated with the
  body — which turns a minus sign into a vertical bar. Both figures therefore
  call the macro with empty labels and draw `+`/`-` afterwards as plain nodes,
  at coordinates captured inside the scope. Do the same in any future rotated
  OTA. Setting `transform shape=false` on the scope is not a fix: it un-rotates
  the glyphs but recomputes their anchors, which displaces them.
- `media/l03_vref1_tikz.pdf` was committed in `db7c3db` without a `tikz/l03_vref1.tex`
  source; that source is in no commit in the repository. The orphan PDF has been
  removed and `l03_vref1` returns to the queue as a fresh draw. Never commit a
  `_tikz.pdf` without its source in the same commit.
- The queue reaches beyond `l*` basenames (`xosc_model`, `rcosc`, `pll`,
  `SUN_PLL_ROSC`, `dac_error`, `fig_sar_logic`, `TB_LEAK`, `LELO_EX`,
  `LELOTEMP_OTA_OP`) and beyond a flat directory (`l13/*`). The build targets now
  handle both; earlier they globbed `tikz/l*.tex` only.
