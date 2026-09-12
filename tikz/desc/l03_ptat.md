A PTAT current generator: two diode-connected PNP transistors of
different size, held at the same voltage by an OTA driving a PMOS
mirror.

The two branches sit side by side. In each, a PNP has its base tied to
its collector and the collector grounded, so it works as a diode. The
left device Q1 is one unit; the right device Q2 is $\times N$, so at the
same current it sits at a lower $V_{BE}$. A resistor $R_1$ stands on top
of Q2's emitter, and the difference $\Delta V_{BE}$ appears across it.

Above both branches is a PMOS current mirror, MP1 on the left and MP2 on
the right, sources to the supply and gates tied together. The OTA sits
between the branches with its output driving both gates; its inputs go
to the two drain nodes, so the loop forces the two branch voltages
equal. The right branch drain carries the output current, labelled
$I_{PTAT}$.

The voltages are marked across each device: $V_{D1}$ on Q1, $V_{D2}$ on
Q2 and $V_{R1}$ across the resistor.
