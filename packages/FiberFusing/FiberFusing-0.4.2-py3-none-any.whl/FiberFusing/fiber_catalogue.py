#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.fiber_base_class import GenericFiber, get_silica_index

micro = 1e-6

__all__ = [
    'DCF13',
    'DCF1300S_20',
    'DCF1300S_33',
    'F2028M24',
    'F2028M21',
    'F2028M12',
    'F2058G1',
    'F2058L1',
    'SMF28',
    'HP630',
    'CustomFiber',
    'get_silica_index'
]


class CustomFiber(GenericFiber):
    def __init__(self, wavelength: float, position: tuple = (0, 0)):
        self.structure_dictionary = {}
        self._wavelength = wavelength
        self.position = position

        self.add_air()


class GradientFiber(GenericFiber):
    # Fiber from https://www.nature.com/articles/s41598-018-27072-2
    def __init__(self, wavelength: float,
                       core_radius: float,
                       delta_n: float,
                       position: tuple = (0, 0)):

        self.structure_dictionary = {}
        self._wavelength = wavelength
        self.position = position
        self.delta_n = delta_n
        self.core_radius = core_radius
        self.brand = "Unknown"
        self.model = "Unknown"

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()
        self.add_silica_pure_cladding(radius=62.5e-6, name='outer-clad')

        index, delta_n = self.interpret_delta_n()

        self.add_next_structure_with_gradient(
            name='core',
            index=index,
            radius=self.core_radius,
            graded_index_factor=delta_n
        )

    def interpret_delta_n(self) -> tuple:
        """
        Interpret the inputed value of delta_n.

        :returns:   Tuple with the core refractive index and delta_n numerical value
        :rtype:     tuple
        """
        if isinstance(self.delta_n, str) and self.delta_n[-1] == '%':
            factor = float(self.delta_n.strip('%')) / 100
            delta_n = self.pure_silica_index * factor
            return delta_n + self.pure_silica_index, delta_n

        else:
            return self.delta_n + self.pure_silica_index, self.delta_n


class CapillaryTube(GenericFiber):
    def __init__(self, wavelength: float,
                       radius: float,
                       delta_n: float,
                       position: tuple = (0, 0)):

        self.structure_dictionary = {}
        self._wavelength = wavelength
        self.position = position
        self.delta_n = delta_n
        self.radius = radius
        self.brand = "Unknown"
        self.model = "Unknown"

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()

        self.add_next_structure_with_index(
            name='inner-clad',
            index=self.pure_silica_index + self.delta_n,
            radius=self.radius
        )


class FluorineCapillaryTube(GenericFiber):
    def __init__(self, wavelength: float,
                       radius: float,
                       delta_n: float = -15e-3,
                       position: tuple = (0, 0)):

        self.structure_dictionary = {}
        self._wavelength = wavelength
        self.position = position
        self.delta_n = delta_n
        self.radius = radius
        self.brand = "Unknown"
        self.model = "Unknown"

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()

        self.add_next_structure_with_index(
            name='inner-clad',
            index=self.pure_silica_index + self.delta_n,
            radius=self.radius
        )


class DCF13(GenericFiber):
    brand = "Thorlabs"
    model = "DCF13"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()

        self.add_silica_pure_cladding(radius=62.5e-6, name='outer-clad')

        self.add_next_structure_with_NA(
            name='inner-clad',
            na=0.2,
            radius=19.9 / 2 * micro
        )

        self.add_next_structure_with_NA(
            name='core',
            na=0.12,
            radius=105.0 / 2 * micro
        )


class DCF1300S_20(GenericFiber):
    brand = "COPL"
    model = "DCF1300S_20"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()
        self.add_silica_pure_cladding(radius=62.5e-6, name='outer-clad')

        self.add_next_structure_with_NA(
            name='inner-clad',
            na=0.11,
            radius=19.9 / 2 * micro
        )

        self.add_next_structure_with_NA(
            name='core',
            na=0.12,
            radius=9.2 / 2 * micro
        )


class DCF1300S_33(GenericFiber):
    brand = "COPL"
    model = "DCF1300S_33"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()
        self.add_silica_pure_cladding(radius=62.5e-6, name='outer-clad')

        self.add_next_structure_with_NA(
            name='inner-clad',
            na=0.11,
            radius=33.0 / 2 * micro
        )

        self.add_next_structure_with_NA(
            name='core',
            na=0.125,
            radius=9.0 / 2 * micro
        )


class DCF1300S_26(GenericFiber):
    brand = "COPL"
    model = "DCF1300S_26"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()
        self.add_silica_pure_cladding(radius=62.5e-6, name='outer-clad')

        self.add_next_structure_with_NA(
            name='inner-clad',
            na=0.117,
            radius=26.8 / 2 * micro
        )

        self.add_next_structure_with_NA(
            name='core',
            na=0.13,
            radius=9.0 / 2 * micro
        )


class DCF1300S_42(GenericFiber):
    brand = "COPL"
    model = "DCF1300S_42"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()
        self.add_silica_pure_cladding(radius=62.5e-6, name='outer-clad')

        self.add_next_structure_with_NA(
            name='inner-clad',
            na=0.116,
            radius=42.0 / 2 * micro
        )

        self.add_next_structure_with_NA(
            name='core',
            na=0.13,
            radius=9.0 / 2 * micro
        )


class F2058L1(GenericFiber):
    brand = "COPL"
    model = "F2058L1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()
        self.add_silica_pure_cladding(radius=62.5e-6, name='outer-clad')

        self.add_next_structure_with_NA(
            name='inner-clad',
            na=0.117,
            radius=19.6 / 2 * micro
        )

        self.add_next_structure_with_NA(
            name='core',
            na=0.13,
            radius=9.0 / 2 * micro
        )


class F2058G1(GenericFiber):
    brand = "COPL"
    model = "F2058G1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()
        self.add_silica_pure_cladding(radius=62.5e-6, name='outer-clad')

        self.add_next_structure_with_NA(
            name='inner-clad',
            na=0.115,
            radius=32.3 / 2 * micro
        )

        self.add_next_structure_with_NA(
            name='core',
            na=0.124,
            radius=9.0 / 2 * micro
        )


class F2028M24(GenericFiber):
    model = "F2028M24"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()
        self.add_silica_pure_cladding(radius=62.5e-6, name='outer-clad')

        self.add_next_structure_with_NA(
            name='inner-clad',
            na=0.19,
            radius=14.1 / 2 * micro
        )

        self.add_next_structure_with_NA(
            name='core',
            na=0.11,
            radius=2.3 / 2 * micro
        )


class F2028M21(GenericFiber):
    model = "F2028M21"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()
        self.add_silica_pure_cladding(radius=62.5e-6, name='outer-clad')

        self.add_next_structure_with_NA(
            name='inner-clad',
            na=0.19,
            radius=17.6 / 2 * micro
        )

        self.add_next_structure_with_NA(
            name='core',
            na=0.11,
            radius=2.8 / 2 * micro
        )


class F2028M12(GenericFiber):
    model = "F2028M12"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()
        self.add_silica_pure_cladding(radius=62.5e-6, name='outer-clad')

        self.add_next_structure_with_NA(
            name='inner-clad',
            na=0.19,
            radius=25.8 / 2 * micro
        )

        self.add_next_structure_with_NA(
            name='core',
            na=0.11,
            radius=4.1 / 2 * micro
        )


class SMF28(GenericFiber):
    brand = 'Corning'
    model = "SMF28"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()
        self.add_silica_pure_cladding(radius=62.5e-6, name='outer-clad')

        self.add_next_structure_with_NA(
            name='core',
            na=0.12,
            radius=8.2 / 2 * micro
        )


class HP630(GenericFiber):
    brand = 'Thorlab'
    model = "HP630"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()
        self.add_silica_pure_cladding(radius=62.5e-6, name='outer-clad')

        self.add_next_structure_with_NA(
            name='core',
            na=0.13,
            radius=3.5 / 2 * micro
        )


class FiberCoreA(GenericFiber):
    brand = 'FiberCore'
    model = 'PS1250/1500'
    note = "Boron Doped Photosensitive Fiber"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()
        self.add_silica_pure_cladding(radius=62.5e-6, name='outer-clad')

        self.add_next_structure_with_NA(
            name='core',
            na=0.12,
            radius=8.8 / 2 * micro
        )


class FiberCoreB(GenericFiber):
    brand = 'FiberCore'
    model = 'SM1250'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize()

    def initialize(self):
        self.structure_dictionary = {}

        self.add_air()
        self.add_silica_pure_cladding(radius=62.5e-6, name='outer-clad')

        self.add_next_structure_with_NA(
            name='core',
            na=0.12,
            radius=9 / 2 * micro
        )

# -
