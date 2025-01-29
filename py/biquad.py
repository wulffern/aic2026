#!/usr/bin/env python3

from sympy import *
init_printing(use_unicode=True)

w0,k0,k1,k2,Q = symbols("w0 k1 k2 k3 Q", real=True, constant= True)
vi,vo,s = symbols("vi vo s")

u1= -w0*vo + vi*k0

u2 = -w0/Q*vo + w0*u1/s + k1*vi + k2*s*vi

vo = u2/s

Hs = vo/vi

print(expand(simplify(Hs)))
