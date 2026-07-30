# Document Title


<!-- 

---

## Ampere's law



In books on electromagnetism you'll see different versions of these equations. They might be missing factors, and seem different. 



Multiple equation variants, same name. 


$$ \oint_{\partial \Sigma} \mathbf{B} \cdot d\mathbf{\ell} = \mu_0\left(
\iint_\Sigma \mathbf{J} \cdot d\mathbf{S} + \epsilon_0 \frac{d}{dt}\iint_\Sigma
\mathbf{E} \cdot d\mathbf{S} \right)$$

$$ \oint_{\partial \Sigma} \mathbf{B} \cdot d\mathbf{\ell} = \mu_0
\iint_\Sigma \mathbf{J} \cdot d\mathbf{S}   $$


> __To model reality, you must ignore most of it__ - Carsten


---



But how do you know what to ignore? Unfortunatly, that can only happen after understanding what's important, and what applies in a given scenario. Picking the right description of 
reality becomes easier with experience. When you start learning you may think you have to include everything to "get it right", but that usually just means you'll never get to a answer.

For the first two equations, there is not really anything to strip away. The electric flux is given by the net charge inside a volume. No time derivative, no nothing. It's really the last two where
we need to know what to ignore. 



$$ \oint_{\partial \Sigma} \mathbf{E} \cdot d\mathbf{\ell} = - \frac{d}{dt}\iint_\Sigma \mathbf{B}
\cdot d\mathbf{S}$$

$$ \oint_{\partial \Sigma} \mathbf{B} \cdot d\mathbf{\ell} = \mu_0\left(
\iint_\Sigma \mathbf{J} \cdot d\mathbf{S} + \epsilon_0 \frac{d}{dt}\iint_\Sigma
\mathbf{E} \cdot d\mathbf{S} \right)$$




Notice there are two time derivatives. In the last equation the magnetic field in a closed curve is given by the current in the surface of that curve, and the change in electric flux inside that surface. 

This last portion is called a "displacement current", for most situations the displacement currents (time derivative of the electric flux)
inside good conductors (copper) can be ignored. That is not the same as saying the electric field inside conductors is zero. The electric flux for a conductor loop is proportional to the restitivity and the current. 

The displacement current is important outside the conductor, though, and is a necessary component of an antenna. 



---

#![fit](https://upload.wikimedia.org/wikipedia/commons/e/ea/Dipole_receiving_antenna_animation_6_300ms.gif)

---

## Ignoring radiation (and capacitors)



Without displacement current then we have that magnetic field around a conductor is fully determined by the current inside. 
And the induced electric field is determined by the change in the magnetic field. 

These two equations give rise to inductance in a loop. When we change the current, the magnetic field changes, and an inverse induced electric field is setup in the conductor.
This will limit how fast the current can change, because the current is only determned by the electric field across a conductor multiplied by the conductance. 



$$ \oint_{\partial \Sigma} \mathbf{B} \cdot d\mathbf{\ell} = \mu_0
\iint_\Sigma \mathbf{J} \cdot d\mathbf{S}$$

$$ \oint_{\partial \Sigma} \mathbf{E} \cdot d\mathbf{\ell} = - \frac{d}{dt}\iint_\Sigma \mathbf{B}
\cdot d\mathbf{S}$$

---

## Ignoring time (DC)



If the current does not change, then there is no change to the magnetic field, and thus the induced electric field is zero. 



$$ \oint_{\partial \Omega} \mathbf{E} \cdot d\mathbf{S} = \frac{1}{\epsilon_0} \iiint_{V} \rho
\cdot dV$$  

$$ \oint_{\partial \Sigma} \mathbf{E} \cdot d\mathbf{\ell} = 0$$

$$ \oint_{\partial \Sigma} \mathbf{B} \cdot d\mathbf{\ell} = \mu_0
\iint_\Sigma \mathbf{J} \cdot d\mathbf{S}$$

-->
