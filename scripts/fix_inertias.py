#!/usr/bin/env python3

from urchin import URDF, xyz_rpy_to_matrix, matrix_to_xyz_rpy
import numpy as np
from enum import Enum

class Geometry(Enum):
    """The different types of geometries that constitute the URDF"""
    BOX = 1
    CYLINDER = 2
    SPHERE = 3

def get_visual(link):
    """Returns the visual object of a link"""
    return link.visuals[0]

def get_mass(link):
    """Returns the link's mass"""
    return link.inertial.mass

def set_inertial_origin(link):
    """Sets the XYZ origin of a link's inertia"""
    visual = get_visual(link)
    link.inertial.origin = visual.origin

def set_inertia(link, new_inertia):
    """Updates the inertia of a link"""
    if (link.inertial is not None):
        inertia = link.inertial.inertia
        for i in range(3):
            for j in range(3):
                if (i == j):
                    inertia[i,j] = new_inertia[i]
                else:
                    inertia[i,j] = 0

def get_geometry(visual_obj):
    """Returns the geometry type and the corresponding geometry object for a given visual"""
    if (visual_obj.geometry.box is not None):
        return [Geometry.BOX, visual_obj.geometry.box]
    if (visual_obj.geometry.cylinder is not None):
        return [Geometry.CYLINDER, visual_obj.geometry.cylinder]
    if (visual_obj.geometry.sphere is not None):
        return [Geometry.SPHERE, visual_obj.geometry.sphere]

def calculate_inertia(geometry_type, visual_data, mass):
    """Calculates inertia (ixx, iyy and izz) with the formula that corresponds to the geometry
    Formulas retrieved from https://en.wikipedia.org/wiki/List_of_moments_of_inertia"""
    if (geometry_type == Geometry.BOX):
        return mass / 12 * np.array([visual_data.size[1] ** 2 + visual_data.size[2] ** 2, 
                            visual_data.size[0] ** 2 + visual_data.size[2] ** 2,
                            visual_data.size[0] ** 2 + visual_data.size[1] ** 2])
    elif (geometry_type == Geometry.CYLINDER):
        i_xy_incomplete = (3 * visual_data.radius ** 2 + visual_data.length ** 2) / 12
        return mass * np.array([i_xy_incomplete, i_xy_incomplete, visual_data.radius ** 2 / 2])
    elif (geometry_type == Geometry.SPHERE):
        inertia = 2 * mass * visual_data.radius ** 2 / 5
        return np.array([inertia, inertia, inertia])

def main():
    robot = URDF.load('model.urdf')
    for link in robot.links:
        if (len(link.visuals) == 0):
            continue
        link_visual = get_visual(link)
        geometry_type, visual_data = get_geometry(link_visual)
        mass = get_mass(link)
        correct_inertia = calculate_inertia(geometry_type, visual_data, mass)
        correct_inertia[correct_inertia < 0.01] = 0.01 
        set_inertial_origin(link)
        set_inertia(link, correct_inertia)
    robot.save('inertias_fixed.urdf')

if __name__ == "__main__":
    main()
