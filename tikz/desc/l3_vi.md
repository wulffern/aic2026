A voltage to current converter: an OTA forces a reference voltage across
a resistor, and a PMOS mirror copies the resulting current out.

On the left a 1.2 V source sits on ground and drives one OTA input. The
OTA output drives the gates of two PMOS devices, MP1 and MP2, whose
sources are on the supply. MP1's drain runs down through a resistor $R$
to ground, and the top of that resistor feeds back to the OTA's other
input.

The loop therefore holds the top of $R$ at 1.2 V, so MP1 carries
$1.2\,\mathrm{V}/R$. MP2 mirrors it, and its drain is the output
$I_{OUT}$, drawn leaving downward.
