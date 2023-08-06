#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy

from FiberFusing.axes import Axes
from FiberFusing import utils
from FiberFusing import Circle


class BackGround(utils.StructureBaseClass):
    def __init__(self, index, radius: float = 1000, position: tuple = (0, 0)):
        self.index = index
        self.position = position
        self.radius = radius

    @property
    def structure_dictionary(self):
        polygon = Circle(
            position=self.position,
            radius=self.radius,
            index=self.index
        )

        return {
            'name': {
                'index': self.index,
                'polygon': polygon
            }
        }

    def overlay_structures_on_mesh(self, mesh: numpy.ndarray, coordinate_axis: Axes) -> numpy.ndarray:
        """
        Return a mesh overlaying all the structures in the order they were defined.

        :param      coordinate_axis:  The coordinates axis
        :type       coordinate_axis:  Axis

        :returns:   The raster mesh of the structures.
        :rtype:     numpy.ndarray
        """
        return self._overlay_structure_dictionary_on_mesh_(
            structure_dictionnary=self.structure_dictionary,
            mesh=mesh,
            coordinate_axis=coordinate_axis
        )


# -
