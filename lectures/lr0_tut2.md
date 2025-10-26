date: 2025-10-27

<!--pan_title: Advanced Sky130 Tutorial of a folded cascode OTA -->

Before you attack this tutorial I would recommend you go through the regular
[Sky130nm
tutorial](https://analogicus.com/aic2026/2025/10/26/Sky130nm-tutorial.html)

## The circuit

We'll use a folded cascode OTA. It's one of the better OTAs. It's versetile, and
can be made to be linear, high input swing, high gain, and is extensible with
gain boosters. 

The one we'll make here is targeting a simple unity gain feedback circuit where
the input voltage is about 1V - 1.6 V.

## The IP 

Create the ip 

```bash
cicconf newip exfc --project lelo --technology sky130A --ip tech_sky130A/cicconf/lelo.yaml
```

