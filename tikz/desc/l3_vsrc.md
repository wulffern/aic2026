A voltage reference routed across a chip, with the wire and both grounds
drawn as impedances rather than as ideal wires.

On the left, from the bottom up: ground, a ground impedance $Z_g$, then
the source $V_S$ reaching the main horizontal wire. The wire runs left to
right through a series impedance $Z_{src}$, then the wire's own pi model
(a shunt $C/2$ to ground, a series $Z_w$, a second shunt $C/2$ to
ground), then $Z_{dst}$.

At the destination the wire ends in an open terminal $V_{ref,+}$. Below
it a second open terminal $V_{ref,-}$ sits on top of a second $Z_g$ down
to ground. The two grounds are drawn as separate impedances and nothing
connects $V_{ref,-}$ to the wire: the reference at the destination is the
difference between the two terminals, and the destination ground is not
the source ground.
