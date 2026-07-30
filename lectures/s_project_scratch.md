
# Project JNW (2025)


**"You can use logic to justify almost anything. That's its power. And its flaw."** - Kathryn Janeway, Star Trek Voyager: Prime Factors


<!--pan_doc: 

The project for 2025 is to 

-->

 
**Design a integrated temperature sensor with digital read-out**

<!--pan_doc: 

An outline of the plan is shown below. 

At the end of the project you will have a function that converts temperature to a digital value.

$$
D = f_0(T)
$$

 I've broken down the challenge into three steps, first convert Temperature into a current

$$
I = f_1(T)
$$

Then convert current into a time 

$$
t = f_2(I)
$$

then time to digital

$$
D = f_3(t) = f_3(f_2(f_1(T))) = f_0(T)
$$

The third milestone is the layout, while the fourth milestone is the report. 

You can find an example of last years designs at [cnr\_gr02\_sky130nm](https://github.com/analogicus/cnr_gr02_sky130nm)

You will be using a repository on github for all your design data. In that repository I've made it possible to run github actions, or github workflows. For each of the milestones there are associated workflows (SIM/DOCS/GDS/DRC/LVS). 

-->


---

![fit](../media/project_plan.pdf)


<!--pan_doc:

**Milestone 0:** The zero milestone is not really part of the project, but it does introduce you too how you will work with the files in the project. It's important that you do this right away. To complete the milestone, upload a link to blackboard with your github repository for the tutorial [Skywater 130 nm Tutorial](https://analogicus.com/aic2025/2025/01/01/Sky130nm-tutorial.html)
 

**Milestone 1:** The first milestone is to make a circuit that can convert from a temperature, to a current that is proportional to temperature. You will run a simulation on github that demonstrates that the circuit works. That is the SIM workflow.

**Milestone 2:** In the second milestone you will complete the schematic design of the circuit, and possibly also do some SystemVerilog to demonstrate that you get a digital value out that is proportional to temperature. Here, the simulations on github may be too long, so it's sufficient to describe the circuit, and how it works in detail in the documentation. This is the DOC workflow.

**Milestone 3:** The third milestone, making the layout, is optional, however, it will be impossible to get an A without getting some points from the layout milestone. Once the layout is complete, I expect that the design rule checks (DRC), Layout versus Schematic (LVS), and GDS (stream out to a [GDSII](https://en.wikipedia.org/wiki/GDSII) file) is passing on github.

**Milestone 4:** I will force you to work in groups. As such, it may be that some contribute more than others. To ensure that the grading is fair, the report will be individual. It's OK to share figures, tables, and so on, but the PDF shall be written by you and you alone.

-->

---

## Grading

| Milestone | What does it mean                                               | Condition for more than 0 points | Possible Points |
|:---------|:---------------------------------------------------------------|:--------------------------------|:---------------|
| M1 I=f(T) | Circuit that can convert a temperature into a current           | SIM passing                      | 10              |
| M2 D=f(T) | Circuit that can convert from temperature into  a digital value | DOC passing                      | 20              |
| M3 Layout | Layout of your circuit                                          | DRC/LVS/GDS passing              | 20              |
| M4 Report | Individual report                                               | Uploaded to blackboard           | 48              |
| Coolness  | Extra points that I may choose to award                         |                                  | 10              |
| Total     |                                                                 |                                  | 108             |


<!--pan_doc:

## Group dynamics

How you work together is important. No-one can do everything by them self. I know from experience it can be 
magical when bright brains come together. The collective brain can be smarter, better, faster, than anyone 
in the group. 

That's why I think it's important not to just work in groups, but also focus on how we work in groups.

A group shall be maximum 4 members. There must be at least 3 that don't know each-other that well. 

The group will meet once per week in the exercise hours.

### Check-in

All group session must start with a Check-in (10 minutes)

Some example questions could be 

- Share one thing that is going on in your life (personal or professional.)
- What is one thing that you are grateful for right now?
- What is something funny that happened?

Some examples answers could be:

- My dog died yesterday, so I'm not feeling great today.
- I woke up early, had an omelet, and went running, so I feel motivated and fantastic.
- I feel *blaaah* today, motivation is lacking. 
- I went running yesterday and did not discover before I got home that I'd forgotten to put my pants on, even though it was
  -10 C.

The point of this exercise is to get to know each other a bit, and attempt to create psychological safety in the group.

-->

---

#[fit] Software

<!--pan_doc:

We'll use professional 
-->
Open source software (xschem, ngspice, sky130A PDK, Magic VLSI, netgen)

<!--pan_doc:

I've made a rather detailed (at least I think so myself) tutorial on how to make a current mirror with the open source tools.
I strongly recommend you start with that first. 
-->

 [Skywater 130 nm Tutorial](https://analogicus.com/aic2025/2025/01/01/Sky130nm-tutorial.html)
 
 
<!--pan_doc:
 
 I've also made some more complex examples, that can be found at the link below. There are digital logic cells, standard transistors, and few other blocks. 
 
-->
 
 [aicex](https://wulffern.github.io/aicex)

---

<!--pan_skip: -->

# Lower your expectations on EDA software

Expect that you will spend at least $$2\pi$$ times more time than planned *(mostly due to software issues)* 

---

<!--pan_skip: -->

#[fit] Questions 

---

<!--pan_skip: -->

# Do
- google
- ask a someone in your class
- use the "øvingstime and labratorieøvelse" to talk to teaching assistants and hopefully me. 
- come to the office (B311) on Thursday's

---

<!--pan_skip: -->

#[fit] Thanks!


