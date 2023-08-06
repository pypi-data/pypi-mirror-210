#!/usr/bin/env python
# -*- coding: utf-8 -*-


import numpy
from FiberFusing import Circle
from FiberFusing import plot_style
from FiberFusing.axes import Axes
from FiberFusing.utils import get_rho_gradient, get_silica_index, StructureBaseClass
import pprint
import logging

# MPSPlots imports
from MPSPlots import colormaps
from MPSPlots.Render2D import Scene2D, Axis, Mesh, Polygon, ColorBar

pp = pprint.PrettyPrinter(indent=4, sort_dicts=False, compact=True, width=1)


class GenericFiber(StructureBaseClass):
    def __init__(self, wavelength: float, position: tuple = (0, 0)):
        self.structure_dictionary = {}
        self._wavelength = wavelength
        self.position = position
        self.brand = "Unknown"
        self.model = "Unknown"

    def set_position(self, position: tuple):
        for structure_name, structure in self.structure_dictionary.items():

            if structure['radius'] is None:
                continue

            new_polygon = Circle(
                position=position,
                radius=structure['radius'],
                index=structure['index']
            )

            structure['polygon'] = new_polygon

    @property
    def bounds(self):
        fiber_structure_list = []
        for fiber_structure in self.inner_structure:
            fiber_structure_list.append(fiber_structure)

        min_x, min_y, max_x, max_y = [], [], [], []

        for name, structure in self.inner_structure.items():
            bounds = structure['polygon'].bounds

            min_x.append(bounds[0])
            min_y.append(bounds[1])
            max_x.append(bounds[2])
            max_y.append(bounds[3])

        return (
            numpy.min(min_x),
            numpy.min(min_y),
            numpy.max(max_x),
            numpy.max(max_y)
        )

    def show_NA(self):
        for structure_name, structure in self.structure_dictionary.items():
            value = structure.get('na')
            print(structure_name, f'NA: {value}')

    def show_radius(self):
        for structure_name, structure in self.structure_dictionary.items():
            value = structure.get('radius')
            print(structure_name, f'radius: {value}')

    def show_index(self):
        for structure_name, structure in self.structure_dictionary.items():
            value = structure.get('index')
            print(structure_name, f'index: {value}')

    @property
    def wavelength(self):
        if self._wavelength is None:
            raise Exception("Wavelength has not be defined for the fiber.")
        return self._wavelength

    @wavelength.setter
    def wavelength(self, value: tuple):
        self._wavelength = value
        self.initialize()

    @property
    def pure_silica_index(self):
        return get_silica_index(wavelength=self.wavelength)

    def NA_to_core_index(self, NA: float, index_clad: float):
        return numpy.sqrt(NA**2 + index_clad**2)

    def core_index_to_NA(self, interior_index: float, exterior_index: float):
        return numpy.sqrt(interior_index**2 - exterior_index**2)

    @property
    def polygones(self):
        if not self._polygones:
            self.initialize_polygones()
        return self._polygones

    @property
    def full_structure(self):
        return self.structure_dictionary

    @property
    def fiber_structure(self):
        return {k: v for k, v in self.full_structure.items() if k not in ['air']}

    @property
    def inner_structure(self):
        return {k: v for k, v in self.full_structure.items() if k not in ['air', 'outer-clad']}

    def add_air(self, radius: float = 1e3):
        polygon = Circle(
            position=(0, 0),
            radius=radius,
            index=1.0
        )

        self.structure_dictionary['air'] = {
            "na": None,
            "radius": None,
            "index": 1,
            "V": None,
            "polygon": polygon
        }

    def add_silica_pure_cladding(self, radius: float = 62.5e-6, name: str = 'outer-clad'):
        self.add_next_structure_with_index(
            name=name,
            index=self.pure_silica_index,
            radius=radius
        )

    def add_next_structure_with_NA(self, name: str, na: float, radius: float):
        """
        Add a new circular structure following the previously defined.
        This structure is defined with a name, numerical aperture, and radius.

        :param      name:    The name of the structure
        :type       name:    str
        :param      na:      The numerical aperture of the structure
        :type       na:      float
        :param      radius:  The radius of the circular structure
        :type       radius:  float

        :returns:   No returns
        :rtype:     None
        """
        previous_structure_name = [*self.structure_dictionary.keys()][-1]

        exterior_index = self.structure_dictionary[previous_structure_name]['index']

        index = self.NA_to_core_index(na, exterior_index)

        V = 2 * numpy.pi / self.wavelength * numpy.sqrt(index**2 - exterior_index**2) * radius

        polygon = Circle(
            position=self.position,
            radius=radius,
            index=index
        )

        self.structure_dictionary[name] = {
            "na": na,
            "radius": radius,
            "index": index,
            "V": V,
            "polygon": polygon
        }

    def add_next_structure_with_index(self, name: str, index: float, radius: float) -> None:
        """
        Add a new circular structure following the previously defined.
        This structure is defined with a name, index, and radius.

        :param      name:    The name of the structure
        :type       name:    str
        :param      index:   The index of the structure
        :type       index:   float
        :param      radius:  The radius of the circular structure
        :type       radius:  float

        :returns:   No returns
        :rtype:     None
        """
        previous_structure_name = [*self.structure_dictionary.keys()][-1]

        exterior_index = self.structure_dictionary[previous_structure_name]['index']

        delta_index = numpy.sqrt(index**2 - exterior_index**2)

        V = 2 * numpy.pi / self.wavelength * delta_index * radius

        polygon = Circle(
            position=self.position,
            radius=radius,
            index=index
        )

        self.structure_dictionary[name] = {
            "radius": radius,
            "index": index,
            "V": V,
            "polygon": polygon,
        }

    def add_next_structure_with_gradient(self, name: str, index: float, radius: float, graded_index_factor: float = 0):
        """
        Add a new circular structure with graded index following the previously defined.
        This structure is defined with a name, index, gradient factor, and radius.

        :param      name:                  The name of the structure
        :type       name:                  str
        :param      index:                 The index of the structure
        :type       index:                 float
        :param      graded_index_factor:   The index of the structure
        :type       graded_index_factor:   float
        :param      radius:                The radius of the circular structure
        :type       radius:                float

        :returns:   No returns
        :rtype:     None
        """
        polygon = Circle(
            position=self.position,
            radius=radius,
            index=index
        )

        self.structure_dictionary[name] = {
            "radius": radius,
            "index": index,
            "polygon": polygon,
            "graded_index_factor": graded_index_factor
        }

    def __str__(self):
        ID = ""

        ID += f"brand: {self.brand:<20s}\n"
        ID += f"model: {self.model:<20s}\n"
        ID += "structure:\n"

        for name, structure in self.fiber_structure.items():
            ID += f"\t{name:<20s}"
            for key, value in structure.items():
                if key == 'polygon':
                    continue
                ID += f"{key}: {value:<20.3}"
            ID += "\n"

        return ID

    def __repr__(self):
        return self.__str__()

    def render_patch_on_ax(self, ax: Axis) -> None:
        """
        Add the patch representation of the geometry into the given ax.

        :param      ax:   The ax to which append the representation.
        :type       ax:   Axis
        """

        for name, structure in self.fiber_structure.items():
            artist = Polygon(
                instance=structure['polygon']._shapely_object
            )

            ax.add_artist(artist)

        ax.set_style(**plot_style.geometry)
        ax.title = 'Fiber structure'

    def render_raster_on_ax(self, ax: Axis, structure, coordinate_axis: Axes) -> None:

        boolean_raster = structure['polygon'].get_rasterized_mesh(coordinate_axis=coordinate_axis)

        artist = Mesh(
            x=coordinate_axis.x_vector,
            y=coordinate_axis.y_vector,
            scalar=boolean_raster,
            colormap='Blues'
        )

        ax.add_artist(artist)

    def render_mesh_on_ax(self, ax: Axis, coordinate_axis: Axes):
        """
        Add the rasterized representation of the geometry into the given ax.

        :param      ax:   The ax to which append the representation.
        :type       ax:   Axis
        """

        colorbar = ColorBar(
            discreet=False,
            position='right',
            numeric_format='%.4f'
        )

        raster = self.overlay_structures(coordinate_axis=coordinate_axis)

        artist = Mesh(
            x=coordinate_axis.x_vector,
            y=coordinate_axis.y_vector,
            scalar=raster,
            colormap='Blues'
        )

        ax.colorbar = colorbar
        ax.title = 'Rasterized mesh'
        ax.set_style(**plot_style.geometry)
        ax.add_artist(artist)

    def render_gradient_on_ax(self, ax: Axis, coordinate_axis: Axes) -> None:
        """
        Add the rasterized representation of the gradient of the geometrys into the give ax.

        :param      ax:   The ax to which append the representation.
        :type       ax:   Axis
        """
        raster = self.overlay_structures(coordinate_axis=coordinate_axis)

        rho_gradient = get_rho_gradient(mesh=raster, coordinate_axis=coordinate_axis)

        colorbar = ColorBar(
            log_norm=True,
            position='right',
            numeric_format='%.1e',
            symmetric=True
        )

        artist = Mesh(
            x=coordinate_axis.x_vector,
            y=coordinate_axis.y_vector,
            scalar=rho_gradient,
            colormap=colormaps.blue_white_red
        )

        ax.colorbar = colorbar
        ax.title = 'Refractive index gradient'
        ax.set_style(**plot_style.geometry)
        ax.add_artist(artist)

    def shift_coordinates(self, coordinate_axis: Axis, x_shift: float, y_shift: float) -> numpy.ndarray:
        """
        Return the same coordinate system but x-y shifted

        :param      coordinates:  The coordinates
        :type       coordinates:  numpy.ndarray
        :param      x_shift:      The x shift
        :type       x_shift:      float
        :param      y_shift:      The y shift
        :type       y_shift:      float

        :returns:   The shifted coordinate
        :rtype:     numpy.ndarray
        """
        shifted_coordinate = coordinate_axis.to_unstructured_coordinate()
        shifted_coordinate[:, 0] -= x_shift
        shifted_coordinate[:, 1] -= y_shift

        return shifted_coordinate

    def get_shifted_distance_mesh(self, coordinate_axis: Axis, x_position: float, y_position: float, into_mesh: bool = True) -> numpy.ndarray:
        """
        Returns a mesh representing the distance from a specific point.

        :param      coordinate_axis:  The coordinate axis
        :type       coordinate_axis:  Axis
        :param      x_postition:      The x shift
        :type       x_position:       float
        :param      y_position:       The y shift
        :type       y_position:       float
        :param      into_mesh:        Into mesh
        :type       into_mesh:        bool

        :returns:   The shifted distance mesh.
        :rtype:     { return_type_description }
        """
        shifted_coordinate = self.shift_coordinates(
            coordinate_axis=coordinate_axis,
            x_shift=x_position,
            y_shift=y_position
        )

        distance = numpy.sqrt(shifted_coordinate[:, 0]**2 + shifted_coordinate[:, 1]**2)

        if into_mesh:
            distance = distance.reshape(coordinate_axis.shape)

        return distance

    def get_graded_index_mesh(self, coordinate_axis: numpy.ndarray, polygon, delta_n: float) -> numpy.ndarray:
        """
        Returns the mesh that represent the refractive index gradient of the fiber structure.

        :param      coordinate_axis:  The coordinate axis
        :type       coordinate_axis:  numpy.ndarray
        :param      polygon:          The polygon
        :type       polygon:          Polygone object
        :param      delta_n:          The difference between highest and lowest RI value in the gradient.
        :type       delta_n:          float

        :returns:   The graded index mesh.
        :rtype:     numpy.ndarray
        """
        shifted_distance_mesh = self.get_shifted_distance_mesh(
            coordinate_axis=coordinate_axis,
            x_position=polygon.center.x,
            y_position=polygon.center.y,
            into_mesh=True
        )

        boolean_raster = polygon.get_rasterized_mesh(coordinate_axis=coordinate_axis)

        shifted_distance_mesh = -boolean_raster * shifted_distance_mesh**2

        shifted_distance_mesh -= shifted_distance_mesh.min()

        if shifted_distance_mesh.max() != 0:
            shifted_distance_mesh /= shifted_distance_mesh.max()
        else:
            logging.warning("Cannot apply graded index factor correctly!")
            return shifted_distance_mesh

        shifted_distance_mesh *= delta_n

        shifted_distance_mesh -= delta_n

        return shifted_distance_mesh

    def overlay_structures(self, coordinate_axis: Axis) -> numpy.ndarray:
        """
        Return a mesh overlaying all the structures in the order they were defined.

        :param      coordinate_axis:  The coordinates axis
        :type       coordinate_axis:  Axis

        :returns:   The raster mesh of the structures.
        :rtype:     numpy.ndarray
        """
        mesh = numpy.zeros(coordinate_axis.shape)

        return self.overlay_structures_on_mesh(
            mesh=mesh,
            coordinate_axis=coordinate_axis,
            structures_type='all'
        )

    def overlay_structures_on_mesh(self, mesh: numpy.ndarray, coordinate_axis: Axis, structures_type: str = 'inner-structure') -> numpy.ndarray:
        """
        Return a mesh overlaying all the structures in the order they were defined.

        :param      coordinate_axis:  The coordinates axis
        :type       coordinate_axis:  Axis

        :returns:   The raster mesh of the structures.
        :rtype:     numpy.ndarray
        """
        match structures_type:
            case 'inner-structure':
                structure_dictionnary = self.inner_structure
            case 'fiber-structure':
                structure_dictionnary = self.fiber_structure
            case 'all':
                structure_dictionnary = self.full_structure

        return self._overlay_structure_dictionary_on_mesh_(
            structure_dictionnary=structure_dictionnary,
            mesh=mesh,
            coordinate_axis=coordinate_axis
        )

    def plot(self, resolution: int = 300) -> None:
        """
        Plot the different representations [patch, raster-mesh, raster-gradient]
        of the geometry.

        :param      resolution:  The resolution to raster the structures
        :type       resolution:  int
        """
        min_x, min_y, max_x, max_y = self.get_structure_max_min_boundaries()

        coordinate_axis = Axes(
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
            nx=resolution,
            ny=resolution
        )

        coordinate_axis.add_padding(padding_factor=1.2)

        figure = Scene2D(unit_size=(4, 4), tight_layout=True)

        ax0 = Axis(row=0, col=0)
        ax1 = Axis(row=0, col=1)
        ax2 = Axis(row=0, col=2)

        self.render_patch_on_ax(ax=ax0)
        self.render_mesh_on_ax(ax=ax1, coordinate_axis=coordinate_axis)
        self.render_gradient_on_ax(ax=ax2, coordinate_axis=coordinate_axis)

        figure.add_axes(ax0, ax1, ax2)

        return figure

    def get_structures_boundaries(self) -> numpy.ndarray:
        """
        Returns array representing the boundaries of each of the existing structures

        :returns:   The structures boundaries.
        :rtype:     numpy.ndarray
        """
        boundaries = []
        for structure_name, structure in self.structure_dictionary.items():
            if structure_name == 'air':
                continue
            if not structure.get('polygon', False):
                continue

            boundaries.append(structure["polygon"].bounds)

        boundaries = numpy.array(boundaries)

        return boundaries

    def get_structure_max_min_boundaries(self) -> numpy.ndarray:
        """
        Returns array representing max and min x and y [4 points] boundaries
        of the total structures except for air.

        :returns:   The structures max/min boundaries.
        :rtype:     numpy.ndarray
        """
        boundaries = self.get_structures_boundaries()

        min_x, min_y, max_x, max_y = boundaries.T

        min_x = min_x.min()
        max_x = max_x.max()
        min_y = min_y.min()
        max_y = max_y.max()

        return min_x, min_y, max_x, max_y

# -
