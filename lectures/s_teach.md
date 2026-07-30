footer: Carsten Wulff 2026
slidenumbers:true
autoscale:true
theme:Plain Jane,1

<!--pan_title: A little effort, every year -->

# A little effort, every year

## How I support students in TFE4188 Advanced Integrated Circuits

Carsten Wulff

---

#[fit] 4 of 4 groups

#[fit] taped out a chip

Spring 2026. A temperature sensor each, in 130 nm CMOS, on the
Tiny Tapeout **ttsky26c** shuttle.

In 2025 it was 2 of 7. In 2024 it was 0 of 5.

Nothing dramatic happened in between. I added one thing a year.

The course has run five times.

---

![fit](../media/s_teach_years_tikz.pdf)

---

# What actually compounded

|                              | 2022 | 2023 | 2024 | 2025 | 2026 |
| :--------------------------- | ---: | ---: | ---: | ---: | ---: |
| Lectures                     |   15 |   19 |   25 |   39 |   46 |
| Lines of lecture source      | 7100 |11800 |16000 |25700 |26600 |
| Figures                      |  238 |  517 |  514 |  722 |  925 |
| Checks per student repo      |    – |    – |    – |    5 |    7 |
| Project groups               |    – |    – |    5 |    7 |    4 |
| Student commits              |    – |    – |  289 |  772 |  762 |
| Commits per group            |    – |    – |   58 |  110 |  190 |
| Groups reaching tapeout      |    – |    – |    0 |    2 |    4 |

The groups did not get bigger. They got **three times deeper**.

---

# Why it compounds

The course does not start from zero in January. It starts from last year.

- **The lectures** are Markdown in git. Fixing one paragraph fixes it forever.
- **The publishing machinery** was not even built for this course. I wrote it
  for TFE4152 in 2021, and the course has used it ever since.
- **The reference design** is a real IP. `RPLY_TEMP` (2023) became `CNR_TS1`,
  became `JNW_TEMP`, became `LELO_TEMP` — 84 commits deep by 2026.
- **The checks run themselves.** 75 lines of CI in 2024, 311 in 2026. Every
  student push runs DRC, LVS, GDS and the tapeout pre-check.
- **Last year's groups** are this year's worked example. Group 7 of 2025 is
  cited in the 2026 project description.

I am not doing more work per student. The work I did is still working.

And the July fixes were mostly *my* bugs:

> Fixed ports. At some point I must have flipped the ports in the template :-D

That is a one-time cost. The template is right now.

---

# What I actually did, each year

My own commits in the student repos:

- **2024** — 13 commits over 5 groups. Made the repos, fixed the tech setup,
  retrofitted GitHub Actions in October. **0 of 5 taped out.**
- **2025** — 14 commits over 7 groups. Almost all of it `Made JNW_GRxx` and
  `Updated gitignore`. I barely touched their designs. **2 of 7 taped out**, as
  one shared submission I authored myself.
- **2026** — 38 commits over 4 groups. A library and a default schematic in
  January. Then, 19–21 July, I did the tapeout integration on all four:
  ports, bounding boxes, labels, tile boundary, LVS and DRC clean.
  **4 of 4, four separate submissions.**

I did not hand this one to them. I closed the last mile myself, in three days.

---

#[fit] Remove one obstacle a year

Students were always able to do this.

Every year I take away one more reason they could not.

Some years that is a CI workflow. This year it was three days in July.

Five editions later, all of them get silicon.
