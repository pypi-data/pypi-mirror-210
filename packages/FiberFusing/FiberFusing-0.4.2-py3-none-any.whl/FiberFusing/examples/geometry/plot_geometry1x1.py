"""
1x1 Geometry
============
"""

from FiberFusing import Geometry, Fused1, BackGround
from FiberFusing.fiber_catalogue import SMF28

wavelength = 1.55e-6

air = BackGround(index=1.0)

clad = Fused1(fiber_radius=62.5e-6, index=1.4444)

fibers = [
    SMF28(wavelength=wavelength, position=core) for core in clad.cores
]

geometry = Geometry(
    background=air,
    additional_structure_list=[clad],
    x_bounds='centering',
    y_bounds='centering',
    n=180
)

geometry.add_fiber(*fibers)

geometry.plot().show()


# -
