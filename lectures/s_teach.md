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

In 2025 it was 2 of 7. In 2024 it was 0 of 1.

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
| Checks per student repo      |    – |    – |    3 |    5 |    7 |
| Project groups               |    – |    – |    1 |    7 |    4 |
| Student commits              |    – |    – |   71 |  772 |  762 |
| Groups reaching tapeout      |    – |    – |    0 |    2 |    4 |

Nothing here more than doubled in one year. All of it doubled over five.

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

---

# What it cost

I planned this course for two years before it ran once.

- 2020: first thoughts, 3 January. It did not run.
- 2024: three CI workflow files. **75 lines of YAML.**
- 2025: two more workflows, and I named tapeout as the goal.
- 2026: the Tiny Tapeout pre-check moved into CI, and Nordic paid the shuttle.

The step that took 2 of 7 groups to 4 of 4 was not a better lecture.
It was removing the last manual step between a finished layout and a
submitted design.

---

#[fit] Remove one obstacle a year

Students were always able to do this.

Every year I take away one more reason they could not.

Five editions later, all of them get silicon.
