# All-Lectures SVG to TikZ Translation Workflow

## Summary
Translate lecture figures from SVG/PDF artwork to maintainable hand-authored TikZ/CircuitikZ across the full course, but only for figures that are schematic-like and benefit from redraw.

**Approval authority changed.** The user delegated the per-figure decision:
switch a reference in as soon as you have verified the redraw is a faithful
match, and only stop to ask when you are genuinely unsure. That removes the
human gate, so the verification step is now the only thing standing between a
bad redraw and the live lecture. Do it properly:

1. Open the original artwork and read what it actually says.
2. Draw, build, and **render the result and look at it** — a green build says
   nothing about whether the drawing is right.
3. Check the redraw against the original point by point: topology, every label,
   polarity and direction, and anything the surrounding lecture prose depends
   on.
4. Match verified → switch the reference and say what you checked.
   Genuinely unsure, or the redraw deviates on purpose in a way that changes
   the teaching → leave it pending and ask.

A deliberate correction of an error in the original is still fine, and still
has to be called out explicitly rather than slipped in.

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
- Update a lecture reference once the redraw is verified against the original,
  per the authority note above.
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

Outcome of the verification in step 6:
- verified match: switch the lecture reference(s) per the replacement policy,
  record it in Saved Progress, continue
- unsure: leave it in Pending Approval, its references on the original
  artwork, and ask

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
- semiconductor physics figures in `lr0_passives`, `l00_diode`
  (`lr0_mosfet`'s were promoted to the head of the queue on 2026-07-30 at
  the author's request — see Current next figure)
- measurement/graph-heavy figures across `l00_*`, `s_chinf`, and guest lectures

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

### lr0_mosfet — physics review round, 2026-07-30
The author suspected translation losses; a figure-by-figure physics
review of all 29 new drawings found three, all cases where the redraw
dropped something the captions or prose explicitly claim:
- the V_DS sequence showed no inversion layer while the captions
  describe one — the electron sheet is now drawn: full in triode,
  tapering to zero at the drain at $V_{DS}=V_{eff}$, ending before the
  drain in saturation (with the $V_{Ch}$ arrow on the pinch point);
- `weakinv` showed no electrons while the prose says the first few
  arrive — a sparse handful now sits under the oxide;
- `mos_bands_drainv` had four equal current arrows while the prose
  argues 1 and 3 outweigh 2 and 4 — 2 and 4 are now visibly smaller,
  4 smallest (drain-to-bulk injection is the suppressed one).
Verified correct and left alone: the controlled-source directions (the
upward $g_s v_{sb}$ equals $g_{mb} v_{bs}$ with the standard sign),
Miller's $(1+1/A)$, the field/force directions in the drain-corner trio
(the CHISEL forces are consistently forces on holes), the band-bending
sequence, DIBL, and the concentration curves.

### lr0_mosfet — COMPLETE 2026-07-30
All three batches drawn and switched (31 `_tikz` references in the
lecture). Batch 3 closed it out: `mos_np`, `mos_bands`,
`mos_bands_drainv`, the `mos_gbands` flat/bend/muchbend sequence and
`dibl`. Notable discovery: the original `mos_np`/`mos_bands`/
`mos_bands_drainv` PDFs (and two of the gbands set) were one shared
drawing distinguished only by CropBox — the redraw gives each figure its
own source. Still referencing originals on purpose: the simulation plots
(`vgate`, `vdrain`, `vgaini`, `gmid`, `l5_velocity`), the paper scan
(`aicdn*`), `3dcross` (3D render), `Red_and_blue_pill.jpg`,
`Popcorn_noise_graph.png`, `nand_tr.png` (queue with the lr0_logic
gate-level batch), and `fig_nmospmos`/`fig_diff`/`fig_l8_*` which are
already clean vector schematics.

### lr0_mosfet batch 2 (core) — switched 2026-07-30
The two cross-section families, drawn from the shared `tikz/mos_lib.tex`:
`mosfet_off`, `mosfet_subthreshold`, `mosfet_strong_inversion`,
`mosfet_strong_inversion_and_saturation` (glowing-blue field-effect intro),
and `accumulated`, `depleted`, `weakinv`, `vds_l_veff`, `vds_veff`,
`vds_h_veff` (red/blue carrier cartoons). Checked against the originals:
the carrier colour language, the hole-population progression
(accumulation at the surface → depletion gap → gate charge), the
depletion edge deepening towards the drain across the V_DS sequence, the
verbatim "$V_{GS} \sim\, ?$" label on depleted, and the green pinch-off
annotations on vds_h_veff. Still open: the one-off cross-sections
(drain_close, caps, gateleakage, hci, chisel, wpe, stress) and the band
diagrams (batch 3). `lectures/mosfet_backup` is untracked scratch and was
left pointing at the originals.

### lr0_mosfet batch 1 — switched 2026-07-30
`large_signal`, `small_signal`, `small_signal_w_gs`, `hfmodel`, `miller`
redrawn in circuitikz and switched in `lectures/lr0_mosfet.md` after
point-by-point comparison (terminals, source arrow directions — the
$g_s v_{sb}$ source points up as in the originals — element labels, the
$C_1$/$C_{gd}$ colour cues and the dashed Miller frame all match).
`fig_nmospmos` was already clean vector art and needs no redraw. Still
open in this lecture: the annotated cross-sections and the band diagrams
(batches 2 and 3 in Current next figure).

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

The `l3_ptat`, `l3_ptat1`, `l3_ptat2` and `l5_scex` artwork marks the OTA
polarity backwards: + on the left input, - on the right. Rising current raises
the right-hand node by I*R1 more than the left, so + belongs on the right for
the loop to settle. The redraws correct this. `l5_scex` first shipped with the
artwork's polarity copied straight over, because this note was not checked
against a figure in another lecture that happens to contain the same core.
**Any figure containing a diode-ratio reference has this to check**, not just
the `l03_refbias` ones.

Before starting any lecture, list its figures with
`grep -o '](\.\./media/[^)]*)' lectures/<lecture>.md` and triage them, rather
than trusting the queue to be complete. The ~117 total understates the work.

## New Figures Requested (not conversions)
These are new teaching content for `l03_refbias`, requested by the user. They
need lecture text as well as figures, and the text is the harder half.

**Start here next session, in this order: curvature correction first**, then
Widlar, then the MOS-based reference. Take them ahead of `l05_sc` and ahead of
the remaining `l03_refbias` conversion work.

All three figures are drawn and rendered: `tikz/l3_curv.tex`,
`tikz/l3_widlar.tex`, `tikz/l3_mosref.tex`.

**All three are approved and merged.**

Widlar went in *before* the Brokaw section at the user's request, rather than
after the Banba material, so it is Figure 9 and every figure from Brokaw onward
shifted up by one. Curvature correction and the MOS reference went in where
they were drafted, between the Banba section and the `#[fit] Bias` divider, as
`##[fit]` subsections of the bandgap part.

Final numbering: 9 Widlar, 10 Brokaw, 11 `l3_bgsim`, 12 `l3_bgsimtfs`, 13–16
the Banba sequence, 17 curvature, 18 MOS reference, 19 `l3_vi`,
20 `l3_gmcell`.

Renumbering a lecture means bumping two forms — the `<sub>Figure N:` captions
and the in-text "as shown in Figure N" references. A regex over `Figure (\d+)`
with a lower bound catches both, and there are no other forms in this lecture.
Rebuild with `python3 py/lecture.py post lectures/l03_refbias.md` afterwards
and read the generated markdown; it catches a mangled `pan_doc` block that a
diff review will not.

### On the MOS reference figure
The first draft used the textbook enhancement/depletion pair, with the
depletion device conducting at $V_{GS}=0$ because its threshold is negative.
The user rejected the framing: in nanoscale CMOS essentially every device sits
at 300 mV or more, the native device is the only exception, and
enhancement/depletion is not language this course should use. The redraw is the
$\Delta V_t$ loop — a 1:1 PMOS mirror over a standard-$V_t$ device and a native
device of equal $W/L$, with $R$ in the native device's source, so
$IR = V_{t1}-V_{t2}$.

It is deliberately the same topology as `l3_gmcell`, because that carries the
argument better than any amount of prose: same loop, but the GM cell's number
comes from a 4:1 size ratio (lithography, a ratio of like things) and this
one's comes from two unrelated channel implants. Keep the two figures visually
parallel if either is re-laid-out.

When writing about device flavours in this course, use the PDK vocabulary —
standard/low/high $V_t$ and native — not enhancement/depletion.

The section's strongest argument, added at the user's request, is where the
native threshold actually comes from: with no channel implant it rides on the
substrate doping, which is fixed when the ingot is grown rather than by any
step the fab controls. Boron's segregation coefficient is below one, so the
melt enriches as the boule is pulled and the tail end is more heavily doped
than the seed end by tens of percent; the wafer vendor sells a resistivity
range, not a resistivity; and none of it is visible to a process control that
watches implants. One end of the subtraction is an implanter recipe in the fab,
the other is a crystal grower at another company.

The ingot argument is a **bulk** argument, and the section says so. Two slides
follow it on FD-SOI, where the channel is undoped and the threshold comes from
the gate work function and the back plane instead. The conclusion survives —
two unrelated recipes, and the wafer-supplier dependence moves from resistivity
to silicon film thickness rather than disappearing — but the reasoning is
different and the section must not be left implying bulk everywhere. The same
slides correct the "use the parasitic vertical PNP every CMOS process has"
advice, which is false in the thin film: in FD-SOI the bandgap goes in a hybrid
opening.

### Deck vs book structure
Content inside `<!--pan_doc: ... -->` is book/web only. A slide whose entire
body is a `pan_doc` block renders **blank** in the deck. Either give the slide
something bare — a heading, a figure, an equation, or in this case the warning
sentence itself — or drop the `---` and let the prose ride along with the
previous slide, which is what the lecture already does for the long `l3_isrc`
discussion. A `##` heading inside `pan_doc` gives the book structure without
creating a slide; a bare `##` heading gives both.

Check with: split the lecture on `\n---\n`, strip the comment blocks, and flag
any slide whose remainder is empty. Only the file's trailing fragment should
come up.

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

### 2026-07-30 session progress (autonomous batch)

- `lr0_passives`: five sketches redrawn and switched (`pas_poly`,
  `pas_ndiff`, `pas_metal`, `pas_pn`, `pas_pres`); `inversion.pdf`
  replaced by the existing `mosfet_strong_inversion` cartoon; the MOM
  capacitor 3D render kept (generated artwork). Verified against
  originals point by point; pn depletion made asymmetric (ND >> NA).
- `lr0_circuits`: triage of `l8/fig_cm*`, `fig_l8_cmsys`,
  `fig_l8_cmfixproc`, `fig_diff` found clean vector art, no redraw
  needed. `cm_sdeg` and `cm_gain_boost` were redrawn earlier the same
  day on the author's figure-14/16 note.
- `dig_des` + `dig_des_lr` redrawn as TikZ flowcharts (house font,
  red/blue path colors, pill terminals) and switched in BOTH
  `l01_intro` and `l11_aver`. Topology checked edge for edge.

### lr0_logic batch 1 done (2026-07-30)

First eleven figures switched, using the `tikz/l13/<name>.tex` ->
`media/l13/<name>_tikz.pdf` subdirectory convention: `inv`, `nand_tr`,
`nor_tr`, `pu_pmos`, `pd_nmos` (transistor level, house Tnmos/Tpmos
macros), `pull` and `pdpu` (block diagram and logic-value table),
`nand`, `nor`, `and`, `or` (circuitikz logic ports; and/or show the
NAND+INV / NOR+INV decomposition with the red arrow). The
`$$\Rightarrow$$` mnemonic fragments in the doc output became plain
`=>`. Still hand drawn in this lecture: `rules.pdf` (the YES/NO smiley
sketch - kept on purpose, it has charm; author's call), the plots
(`transistor_log/lin`), tool screenshots, and batch 2: `binary`,
`mux`, `latch`, `dlatch`, `d_ff`, `digital_ff_comb`, `inv_tg`,
`an2oi`, `ivtrix`, `fig_sar_logic`, `mealy/moore_machine`, plus the
`l14/`, `l16/`, `l19/` sets. UPDATE, same day: batch 2 is done too -
`binary`, `dlatch`, `latch`, `d_ff`, `digital_ff_comb`, `mux`,
`an2oi`, `inv_tg`, `ivtrix` all drawn, verified against the originals
point by point (topology, labels, truth-table values), and switched in
`lr0_logic` and `s_need_to_know`. Remaining in this lecture: the
`l14/`, `l16/`, `l19/` sets, `mealy/moore_machine`, and
`fig_sar_logic`.

### Current next figure
`l04_dac` is complete, so the queue moves on. In order, and each one triaged
by listing its figures first rather than trusting the queue below:

0. **`lr0_mosfet`** — promoted to the top of the queue by the author,
   2026-07-30 ("lets bump the mosfet to the top of the tikz redraw list").
   Previously parked in Phase 3 as semiconductor-physics artwork; that
   parking no longer applies to this lecture. Triage by listing, but the
   figure set is roughly three kinds:
   - *Straight circuitikz*: `large_signal`, `small_signal`,
     `small_signal_w_gs`, `hfmodel`, `miller` (top schematic + the two
     block diagrams), `fig_nmospmos`. Classic schematic redraws.
   - *Annotated cross-sections* (hand-drawn carrier cartoons):
     `mosfet_off/subthreshold/strong_inversion(+_and_saturation)`,
     `accumulated/depleted/weakinv`, `vds_l_veff/vds_veff/vds_h_veff`,
     `drain_close`, `caps`, `gateleakage`, `hci`, `chisel`, `wpe`,
     `stress`, `3dcross`. TikZ filled shapes + node labels; keep the
     red/blue carrier colour language, which the new Figure 18–20 captions
     now describe in words.
   - *Band/potential diagrams*: `mos_np`, `mos_bands`, `mos_bands_drainv`,
     `mos_gbands(_bend,_muchbend)`, `dibl`. Curves + annotations, close to
     the `l5_sdomain`/`l5_zdomain` style already drawn.
   Out of scope in this lecture: the simulation plots (`vgate`, `vdrain`,
   `vgaini`, `gmid`) and the paper scan (`aicdn*`), plus
   `Red_and_blue_pill.jpg` for obvious reasons.

1. **`l01_intro`** and **`l11_aver`** — they share `dig_des` and `dig_des_lr`,
   so whichever is drawn first finishes both, and the reference switch has to
   cover both lectures in the same round.
2. **`lr0_circuits`** — the queue lists only `LELOTEMP_OTA_OP`, but the
   lecture also carries 19 figures in `media/l8/`, `l9/` and `l10/`, and the
   `l8/fig_cm*.pdf` current mirrors and cascodes are exactly the kind of
   schematic this workflow is for. Triage those before deciding the size of
   the job; the `jnw_*` files are gm/ID plots and out of scope.
3. **`lr0_tut1`** — `LELO_EX`, a single figure. The rest is screenshots.
4. **`l01_project`** — `TB_LEAK` and `aic2026_project_analog`. Expect some of
   this lecture's artwork to be system/overview drawings that belong in
   Phase 3 rather than here. `l03_ptat` is already switched here.
5. **`lr0_logic`** — **27** distinct figures under `media/l13/`, not the 13 the
   queue lists, plus `mealy_machine`/`moore_machine` at the top level and
   whole further sets under `l14/`, `l16/` and `l19/` that the queue never
   mentions. This is the biggest job left in Phase 2 by some way. It is also
   the first batch to use the subdirectory convention
   (`tikz/l13/<name>.tex` → `media/l13/<name>_tikz.pdf`). Gate-level drawings,
   so `circuits.logic.US` rather than `circuitikz` devices, and worth a shared
   include for the pull-up/pull-down pair the first several figures repeat.

Phase 1 is finished apart from the lectures never started: `l06_adc`,
`l07_vreg`, `l08_pll` and `l09_osc` are still untouched and are much bigger
than anything in Phase 2. If the goal is the book looking consistent rather
than the queue being drained in order, those four are where the remaining
volume is — worth deciding before starting Phase 2.

Two open questions from earlier rounds are still unanswered and cost nothing
to settle when the relevant lecture next comes up: `l04_ff_gm` in `l04_afe`
(redrawing a figure lifted from a cited thesis — the author's call, not a
match question), and the `G_m2`/`G_m3` damping term in `l04_afe.md` and
`l05_sc.md`, where the printed equation disagrees with the circuit.

### `l04_dac` is complete
Seventeen figures drawn and switched: `dac_r_div`, `dac_r_div2`, `dac_r_div2b`,
`dac_r_switches`, `dac_r_rows`, `dac_r_segmented`, `dac_2r_0`, `dac_2r_1`,
`dac_2r_2`, `dac_2r_full`, `dac_bin_states`, `dac_bin_btran`,
`dac_thermo_states`, `dac_thermo_tran`, `dac_r_thermo`, `dac_i`,
`dac_i_vbias`.

On the two current mode DACs. `dac_i_vbias` took four passes and every
correction came from the user, not from the build. What it is, settled:

- **V_bias is a constant that comes from outside.** It gates the cascode in
  the reference branch and runs the length of the array as a rail. The
  reference branch does not make it.
- **One side of each steering pair sits directly on that rail; the other side
  takes the bit.** The bit swings about V_bias, so it has to cross the level
  in both directions to tip the pair, and only has to move far enough either
  side of it to do so. An inset waveform says that. A first attempt put
  drivers on both gates instead, which drew a different circuit.
- **The diode connection is taken from the top of the stack, above the
  cascode**, so the mirror's gate carries the whole stack's voltage rather
  than its own drain's, and that node is the gate rail the cells' tail
  devices share.

What this round cost, and the lesson: the slanted bias stub, the labels
struck through by their own wires, the gate rail left dangling at an old x
after the riser moved, the header describing a superseded circuit, and the
V_bias wire laid across the steering device — every one was visible in a
render and none was caught by a green build. **Render it, put it beside the
original, and read both ends of every wire before showing it.** The compare
mode exists for exactly this: `make preview FNAME=<name>`.

Two habits that came out of it and are worth keeping:
- Take a wire's endpoint off the device's own anchor rather than off
  computed numbers when it has to clear the symbol: `\draw let \p1 =
  (M.gate) in (M.gate) -- (\x1-0.35,\y1) -- (\x1-0.35,\ybias);`. No later
  coordinate edit can put it back on top of the device.
- When an edit moves a coordinate, check **both** ends of every path that
  used it. A one-ended replace is what produced the slanted stub and the
  dangling rail.

Both figures now draw the cell **once**, inside a dashed boundary, with a
narrow blank boundary after it standing for the cells that are not drawn and
a caption reading "N copies of the same cell, sized 1, 2, 4 ... N", at the
user's request: the originals leave the repetition to a row of dots between
two slices, and that does not say that the array is one cell copied. The
boxes butt up against each other so the row reads as an array. Both figures
are built on one geometry, so between the two slides only the part that
changes looks different — keep them in step if either is re-laid-out.

Out of scope in `l04_dac`, after opening each: `dac_error` and `dac_inl_dnl`
are matplotlib plots, and `NIST.SP_.1247.png` is a bitmap.

The queue in this document listed only `dac_error` and `dac_inl_dnl` for this
lecture, and both of those are the ones that turned out to be out of scope —
the queue was not just incomplete here, it was inverted. Triage by listing.

### New shared includes from `l04_dac`
- `tikz/rdac_lib.tex` — the pass device with its control label above the gate,
  the terminal circle, the sideways ground the originals draw for a summing
  node, the steering SPDT (`\rdacSpdt`, which also draws the stub up to the
  rail so the arm meets it), and `\rdacAmp`, an amplifier drawn point-right
  with `-` above `+`.
- `tikz/dacsm_lib.tex` — the state bubble and the transition arrow for the
  four coding slides.

Both are in `TIKZ_INCLUDES`.

**Calc parses tokens, so a macro that expands to a coordinate cannot be
passed into another macro that uses it inside `($...$)`.** It dies as
"Paragraph ended before \tikz@cc@parse@factor was complete", pointing at a
blank line rather than at the call. Two fixes, both used here: capture the
argument with `\coordinate (foo) at #2;` first and use `(foo)` after, or lay
the geometry down as named coordinates and pass names. TikZ also wants a
literal `(` after `at`, so `\coordinate (x) at \somemacro{1}{2};` fails even
on its own.

`\vresistor` is `\grid` = 1.6 tall, not 1.5, and the taps in the string DACs
are spaced off that number. Reading positions back off the drawn coordinates
rather than off the numbers in the layout is what keeps the rails square.

One deliberate deviation, in `dacsm_lib`: where two states carry a transition
each way, the arrows bend either side of the centre line instead of running
parallel as the originals draw them. Drawn node to node an arrow is clipped
at the circle border; a hand-offset straight one runs into the bubble.

A device drawn on an upward path has its gate on the left, and `mirror` puts
it on the right — which is what a reference device facing its array wants, so
the diode connection can loop up the outside of the channel instead of the
gate rail running back across the symbol. Drawing the path *downward* also
moves the gate, but it swaps drain and source: the source then lands on the
current source rather than on ground. Mirror, do not reverse.

### Working with the CI figure rebuild
The `TikZ figures` workflow rebuilds and commits `media/*_tikz.pdf` on every
push, and its TeX Live (TL2022-historic) does not produce the same bytes as a
local TL2024. So editing a figure, pushing, and pulling gives a **conflict on
the figure's PDF** nearly every time — six of them in this round. The fix is
always the same and is not a merge: rebuild from source and stage that.

    make tikz-one FNAME=<name>
    git add media/<name>_tikz.pdf media/<name>_tikz.svg

Never resolve one of these by taking either side of the merge: the committed
PDF has to be the one the current source produces.

### `l04_afe` is complete
16 figures drawn and switched. `l4_activebiquad` and `l4_gmcbi` were the two
shared with `l05_sc`, and switching them finished that lecture too;
`l4_activebiquad` is also referenced as a **PDF** by `l10_lpradio` and
`lp_radio_guest`, and those switched in the same round. `fig_inv` is used by
four lectures (`l04_afe`, `l02_esd`, `s_chinf`, `lr0_mosfet`) and all four
switched together.

`grep -o '](\.\./media/[^)]*)'` is not enough on its own: it finds `.pdf`
references as well as `.svg` ones, and a figure can be referenced both ways in
different lectures. Grep for the bare basename, not for `<basename>.svg`.

Out of scope in `l04_afe`, after opening each one:
- bitmaps: `503px-Silicon-unit-cell-3D-balls.png`, `inv_stick.png`,
  `digital_shoulder.png`, `analog_designer.png`, `qt_sd.png`
- `l04_ota_sch` — a four-panel schematic-capture screenshot of the design
  database, instance names and all. Redrawing it would be a trace of a tool
  window, not a redraw of a circuit.
- `l04_ff_gm` — **undecided, needs the user.** It is a clean CMOS
  transconductor schematic and would redraw easily, but it is a figure lifted
  from a cited master's thesis, caption ("Figure 5.16: Transconductor
  schematic") and all. Redrawing it turns "here is their figure" into "here is
  my drawing of their circuit". That is the author's call, not a match
  question, so it is left on the original.

### New shared includes from this lecture
- `tikz/gmc_lib.tex` — the trapezoid transconductor symbol (tall input edge,
  short output edge) shared by `l4_gmc`, `l4_gmc_diff`, `l4_gmc_diff1` and
  `l4_gmc1st`, plus `\gmcDiffFrame` for the `l4_gmc_diff`/`l4_gmc_diff1` pair,
  which differ only in the output terminal marks and the arrow directions.
  `\gmcBodyL` is the mirrored body, used for `l4_gmc1st`'s second cell.
- `tikz/sfg_lib.tex` — the summing node and the `1/s` block shared by
  `l4_first_order` and `l4_biquad`, which are the same size in the original
  artwork too.

Both were added to `TIKZ_INCLUDES` in the Makefile, without which the build
tries to compile them as figures.

`l4_gmcbi` uses a different transconductor symbol — the chamfered box with
`+ +` and `- -` on two rails — because the original does. Do not unify it with
`gmc_lib`'s trapezoid.

### The l4_gmcbi damping term
`l4_gmcbi`'s circuit puts `G_m3` across node B with its output crossed, which
is a resistor of `1/G_m3` damping that node. Working the KCL through gives

    v_out/v_in = [s^2 C_X/(C_X+C_B) + s Gm5/(C_X+C_B) + Gm2 Gm4/(C_A(C_X+C_B))]
               / [s^2 + s Gm3/(C_X+C_B) + Gm1 Gm2/(C_A(C_X+C_B))]

Every term matches the H(s) printed in `l04_afe.md` and `l05_sc.md` except the
damping one, where both lectures write `G_{m2}`. It cannot be `G_m2`: that
transconductor is already the one from node A to node B, and it appears in
both the omega_0^2 term and the numerator. The redraw follows the circuit.
**The lecture equations were left alone** — fixing prose is outside the figure
migration, and the user should decide.

### More LaTeX rules earned this round
- **Brace every computed coordinate.** TikZ scans a coordinate for its closing
  parenthesis, so `(#1+0.94,#2+(#4))` ends at the `)` after `#4` and the node
  loses its label text: "A node must have a (possibly empty) label text".
  Write `({#1+0.94},{#2+(#4)})`. Cost a CI round trip.
- **`\def` stores text, so negate at the call site, not in the macro.**
  `\def\xa{-4.8}` makes `-\xa` expand to `--4.8`. Store column offsets as
  positive numbers and write `(-\xa,...)` for the left half of a symmetric
  figure.
- A wire that stops at a riser is not a wire that reaches the device.
  `l4_activebiquad` first shipped with `G_1` ending at node X's riser instead
  of continuing to the OTA input, which left the inverting input floating.
  A green build says nothing about this; the render does.

`tikz/boot_lib.tex` holds the bootstrapped switch, shared by `l5_sw2` (one of
them) and `l5_sw3` (two). `\bootBlock` draws it above its input rail and
`\bootBlockDn` below. `l5_sw3` needs the mirrored one: with both networks
pointing the same way the lower one lands in the middle of the figure and the
wires from `A_n` to the dummies have nowhere to run, which is exactly what
makes the original crowded there. The circuit is symmetric, so mirroring costs
nothing and buys the dummies the whole middle of the drawing.

`tikz/sc_lib.tex` holds the switched-capacitor amplifier pieces. `\scIntroFrame`
draws everything `l5_scintro1` and `l5_scintro2` share and leaves the two
switch positions to the caller, because those two switch states are the entire
difference between the phases and the whole point of the pair. `\scAmpFrame`
does the same for `l5_scamp` and `l5_scint`: the integrator is the gain stage
with the C2 reset switch removed, and the lecture makes that point explicitly,
so only `l5_scamp` draws the reset.

`tikz/plane_lib.tex` holds the s-plane and z-plane pieces: the axes, the unit
circle, and pole and zero markers. Pole positions are given in units of the
circle radius, so `(0.5,0.3)` means half a radius out, which is how you think
about them. Same rule as `spec_lib.tex`: a new shared include must be added to
`TIKZ_INCLUDES` in the Makefile or the build tries to compile it as a figure.

`l05_sc` is complete: the last two figures, `l4_activebiquad` and `l4_gmcbi`,
were drawn with `l04_afe` and switched in both lectures in the same round.

Switched in `lectures/l05_sc.md`: `l05_fund1`, `l05_fund2`,
`l05_fund3`, `l5_sh`, `l5_shaaf`, `l5_subsample`, `l5_sdomain`, `l5_zdomain`,
`l5_zunstable`, `l5_fir`, `l5_sw1`, `l5_scintro1`, `l5_scintro2`, `l5_scamp`,
`l5_scint`, `l5_scfig`, `l5_scifig`, `l5_sw2`, `l5_sw3`, `l5_novl`, `l5_scex`.

The two waveform sketches scale each plot to its own trace: `\scWaveFrame`
takes the top of the V_o axis, 1.6 for `l5_scfig` and 4.3 for `l5_scifig`.
Drawing both on the integrator's axis strands the gain stage's trace, which
only ever reaches V_i, in the bottom fifth of an empty box. The originals do
scale per plot; it is not a liberty.

`l5_scex`'s reference core is drawn to match `l03_ptat`: diode-connected PNPs
rather than the artwork's plain diodes, the area ratio marked on the device as
`xN` rather than as a floating "1 : N", and + on the branch carrying the
resistor. A student meets this circuit in `l03_refbias` first, so the two
should be recognisably the same drawing. The two figures are not shared source
and should not be — `l03_ptat` is a tall standalone built on `ckt_lib`'s grid
macros with a rotated OTA, while `l5_scex` needs a short wide core so the
switched-capacitor stage fits beside it on one slide.

`l5_sw2`'s two bulk networks end in bare symbols in the original. They are the
supply rails: the n-well to V_DD and the p-substrate to ground while the switch
is off, which is the only bias that keeps both junctions reverse biased, and
the drawing has a ground on the lower one already.

`tikz/spec_lib.tex` holds the sampling-spectrum pieces shared by `l5_sh`,
`l5_shaaf` and `l5_subsample`: the axis with its Nyquist ticks, the wanted
signal, a tone, a filter trapezoid, and the chain blocks. The three slides
argue by looking alike, so keep them on one geometry. Any new shared include
must be added to `TIKZ_INCLUDES` in the Makefile or the build will try to
compile it as a figure and fail.

Approved and switched in `lectures/l05_sc.md`: `l05_fund1`, `l05_fund2`,
`l05_fund3`.

`l05_fund1`, `l05_fund2` and `l05_fund3` are the same circuit three ways, and
the slides make their point by looking alike. `l05_fund2` and `l05_fund3`
share a column grid — V_I port at `-\grid*1.5`, phi_1 switch from 0 to
`\grid`, C1 spanning `\grid` to `\grid*2`, V_O column at `\grid*3`, common
ground rail at -2.8. Keep them in step if either is re-laid-out.

An NMOS drawn along a left-to-right path puts its gate on **top**, which is
what these figures want; `mirror` would put it underneath. That is the
horizontal counterpart of `\lvnmos` having its gate on the left.

### `l05_sc` triage
`l05_sc` is reprioritised ahead of `l04_afe` at the user's request. The
switched-capacitor idiom established in `l3_gmcap` carries straight over.

The lecture references 29 figures. The queue in this document listed 23 and,
as with `l03_refbias`, was not exhaustive:

- Out of scope, bitmaps: `lewis.png`, `diff_ota.png`, `diff_ota_bias.png`,
  `l00_SAR9B_CV.png`.
- Shared with `l04_afe`: `l4_activebiquad`, `l4_gmcbi`. Whichever lecture gets
  there first draws them, and the reference switch then has to cover both
  lectures in the same round.
- `l5_dtfig` and `l5_iir` are **out** of scope: both are matplotlib plots of
  simulated data with thousands of points, not line drawings. They were listed
  in the queue and I initially waved the whole list through as in scope without
  opening them, which was wrong. Open every figure before triaging it.
- The remaining 21 are in scope. That includes
  `l5_sdomain`, `l5_zdomain` and `l5_zunstable`, which are pole/zero plane
  diagrams rather than circuit schematics: the user confirmed they are wanted.
  So the "circuit schematics only" rule at the top of this document is not
  absolute — a clean line drawing that TikZ can express as geometry counts,
  and only traced artwork and real plots of data stay out.

The `l05_fund1`/`2`/`3` originals are hand-drawn, unlike the `l03_refbias`
artwork, so the redraws will not look like the source at all. That is the
point, but it makes a side-by-side comparison less useful than it was for
`l03_refbias`; judge these on whether the topology and labels survive.

`l05_fund1` carries a non-overlapping clock diagram under the schematic. It is
drawn with a `\foreach` inside the path rather than as a list of coordinates,
so the period, pulse width and height are single `\def`s at the top of the
block.

### Notes
- **Draw in black.** The hand-drawn originals are in dark blue ink with green
  and red annotations, and the first `l05_sc` redraws copied that. The user
  does not want it: the redraws are not meant to imitate the pen. Use the
  default black for every line and every ordinary label, and reach for colour
  only where it *encodes* something the reader has to tell apart — the green
  signal against the red and magenta tones and the orange filter in the
  sampling spectra, and stable against unstable in `l5_zunstable`. Those stay
  because the figure argues with them; nothing else does.
- A TeX macro name is **letters only**. `\newcommand{\scXc2}{...}` does not
  fail where it is defined; it fails later as "Undefined control sequence
  `\scXc`", because TeX read the name as `\scXc` and left the `2` behind.
  Spell the digit out: `\scXctwo`.
- **`\input` a shared library *inside* `\begin{circuitikz}`, never above it.**
  Every pre-existing figure does this with `ckt_lib.tex` and it is not a style
  preference: a definitions file inputted into the document body of a
  `standalone` document contributes an empty paragraph, and `crop` then sizes
  the page around it. The figure still compiles and still looks right — it just
  carries a wide blank margin. `l5_scintro1` wasted 45 % of its width that way,
  and the spectrum and plane figures 13–16 % each, before this was spotted.
  Worth checking: measure the ink bounding box of the rendered PNG against the
  image size and expect a couple of per cent of margin, not fifteen.
- Prefix every `\newcommand` in a figure. `l5_sh` first used `\th` for a tone
  height, which is a LaTeX built-in (thorn), and the redefinition is a *fatal*
  error, not a warning — it cost a CI round trip. `\shHalf`, `\shTone` and so
  on are safe; `\th`, `\vh`, `\tone` are not obviously so.
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
