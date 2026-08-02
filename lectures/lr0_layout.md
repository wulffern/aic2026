footer: Carsten Wulff 2025
slidenumbers:true
autoscale:true
theme: Plain Jane, 1
text:  Helvetica
header:  Helvetica
date: 2025-03-20

<!--pan_title: Layout Generation-->

<!--pan_doc:

**Keywords:** Layout Generation, CICPY, Placement, Routing, Automation

-->

# Layout

The open source tools don't have any automatic analog layout. To my knowledge,
there is no general purpose analog automagic layout anywhere in the world. It's an unsolved problem.
Many have tried (including myself), but none have succeeded with a generic
analog layout engine.

There are a few things, though, that could help you on the way.

# Setup

I assume that you have the latest and greatest `aicex\ip` setup. 

See [SKY130NM
Tutorial](https://analogicus.com/aic2026/sky130nm_tutorial) if
aicex is unfamiliar.


Let's assume we use `jnw_gr05_sky130a` to test out our layout 

```bash
cd aicex/ip/
cd jnw_gr05_sky130a
git checkout a1e3dfc324194729e042f5e653777b052759863b
cd work
```

# CICPY

The first thing we need to do is to place all transistors. I do have a script to
help. Install cicpy. 

```bash 
cd aicex/ip/cicpy
git checkout master
git pull 
python3 -m pip install -e .
cd ..
cd cicspi 
git checkout main 
git pull
python3 -m pip install -e .
```

# Placement 

To generate an initial placement we can do the command below. If a layout exists
it will be overridden

```bash 
cd jnw_gr05_sky130a/work 
cicpy sch2mag JNW_GR05_SKY130A OTA_Manuel
```

![](../media/layout_ota_m1.png)

<!--pan_doc:
<sub>Figure 1: Initial cicpy sch2mag placement of OTA_Manuel in Magic - all transistors in one row, 19 DRC errors</sub>
-->

The layout engine has no idea what components belong together, for example, the
current mirror below should have been placed together 

![](../media/sch_ota_m1.png)

<!--pan_doc:
<sub>Figure 2: Xschem schematic of the OTA bias circuitry, where the current mirror pair xa07/xa20 should have been placed together</sub>
-->

We can instruct the layout engine by adding a "group" name to the instance name.
The instance name always starts with `x<something><number>` where the something
can be nothing, or a group name (a,b, not a number).

The rules for placement are:

1. Sort all instances by groups 
1. Sort all groups by instance name 
1. Place the first instance. 
1. For all instances: If the next instance has the same group, then add on top.
Otherwise increment the x location.

As such, if I rename my instances, as shown below, 

![](../media/sch_ota_m2.png)

<!--pan_doc:
<sub>Figure 3: The same OTA schematic after renaming instances with group prefixes (xa, xb, xd, xf, xg) to guide the placer</sub>
-->

Then the layout becomes a bit better 

```bash 
cicpy sch2mag JNW_GR05_SKY130A OTA_Manuel --gbreak 3 --xspace 34000 --yspace 30000
```

The gbreak command inserts a "group break" after the fourth group, such that a
new Y coordinate is selected.

The X and Y space is for the distance between groups. The unit is "Ångstrøm", so
1 um is 10 000 Å. 

![](../media/layout_ota_m2.png)

<!--pan_doc:
<sub>Figure 4: Placement after grouping, shown as instance boxes: devices of the same group stack vertically, and --gbreak 3 starts a new row</sub>
-->

![](../media/layout_ota_m3.png)

<!--pan_doc:
<sub>Figure 5: The same grouped placement with all layers drawn, DRC clean</sub>
-->

---

## Summary

<!--pan_doc:

The one-page version of this chapter:

-->

- Layout is the final translation: from schematic to the polygons the fab will etch
- Matching is geometry: symmetry, proximity, dummies, and common centroid where it counts
- The parasitics are part of the circuit - extract and re-simulate before believing any layout
- DRC and LVS are not suggestions: clean both, every time

---

# Would you like to know more?

<!--pan_doc:

Hastings' *The Art of Analog Layout* is the book on matching, and
worth owning. For the open flow used here, the Magic and netgen
documentation is the practical companion.

-->

- Hastings, *The Art of Analog Layout*
- [Magic VLSI](http://opencircuitdesign.com/magic/) and [netgen](http://opencircuitdesign.com/netgen/) documentation
