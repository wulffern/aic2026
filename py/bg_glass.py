#!/usr/bin/env python3

from scipy import constants
pi = constants.pi

#- We must use the "correct" units for planck's constant to get energy in eV
h = constants.physical_constants["Planck constant in eV/Hz"][0]
c = constants.physical_constants["speed of light in vacuum"][0]

lambda_optical = 450e-9
e_optical = h * c/lambda_optical


lambda_ultra = 380e-9
e_ultra = h * c/lambda_ultra


print("Bandgap of glass is above %.2f eV, maybe around %.2f eV " %(e_optical,e_ultra))
