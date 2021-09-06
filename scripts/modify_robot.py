#!/usr/bin/env python3

from urdfpy import URDF, xyz_rpy_to_matrix, matrix_to_xyz_rpy
from enum import Enum, EnumMeta
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
import argparse
import configparser
import math
import os

class LimbMeta(EnumMeta):
    def __contains__(cls, item):
        try:
            cls[item]
        except ValueError:
            return False
        return True

class Geometry(Enum):
    """The different types of geometries that constitute the URDF"""
    BOX = 1
    CYLINDER = 2
    SPHERE = 3

class Side(Enum):
    """The possible sides of a box geometry"""
    WIDTH = 1
    HEIGHT = 2
    DEPTH = 3

class Limb(Enum, metaclass=LimbMeta):
    """The possible limbs of the robot"""
    NONE = 0
    RIGHT_ARM = 1
    LEFT_ARM = 2
    RIGHT_LEG = 3
    LEFT_LEG = 4
    ARMS = 5
    LEGS = 6
    TORSO = 7
    ALL = 8

class RobotElement(Enum):
    """Types of elements in the urdf"""
    LINK = 1
    JOINT = 2

class Modifier(ABC):
    """Class to contain information on how to modify a URDF element"""
    def __init__(self, name, origin_modifier, element_type):
        self.name = name
        self.origin_modifier = origin_modifier
        self.element_type = element_type

    @abstractmethod
    def get_element(self, robot, multiplier):
        pass

@dataclass
class LinkModifier(Modifier):
    """Information to modify links"""
    def __init__(self, link_name, origin_modifier, dimension = None, flip_direction = True, calculate_origin_from_dimensions = True):
        super().__init__(link_name, origin_modifier, RobotElement.LINK)
        self.dimension = dimension
        self.flip_direction = flip_direction
        self.calculate_origin_from_dimensions = calculate_origin_from_dimensions

    @staticmethod
    def get_link(robot, link_name):
        link_list = [corresponding_link for corresponding_link in robot.links if corresponding_link.name == link_name]
        if len(link_list) != 0:
            return link_list[0]
        else:
            return None

    def get_element(self, robot):
        return self.get_link(robot, self.name)

    def modify(self, robot, multiplier, density_multiplier = -1):
        link = self.get_element(robot)
        visual_obj = get_visual(link)
        current_mass = get_mass(link)
        geometry_type, visual_data = get_geometry(visual_obj)
        current_volume = calculate_volume(geometry_type, visual_data)
        density = calculate_density(current_mass, current_volume)
        density = density * density_multiplier if density_multiplier > 0 else density
        modify_volume(link, multiplier, self.dimension)
        modify_origin_link(link, self.origin_modifier, self.dimension, self.flip_direction, self.calculate_origin_from_dimensions)
        update_mass(link, density)
        update_inertia(link)

    def __str__(self):
        return f"Link modifier with name {self.name}, origin modifier {self.origin_modifier}, dimension {self.dimension}"

@dataclass
class JointModifier(Modifier):
    """Information to modify joints"""
    def __init__(self, joint_name, origin_modifier, take_half_length = False, flip_direction = True):
        super().__init__(joint_name, origin_modifier, RobotElement.JOINT)
        self.take_half_length = take_half_length
        self.flip_direction = flip_direction

    @staticmethod
    def get_joint(robot, joint_name):
        return [corresponding_joint for corresponding_joint in robot.joints if corresponding_joint.name == joint_name][0]

    def get_element(self, robot):
        return self.get_joint(robot, self.name)

    def modify(self, robot, parent):
        joint = self.get_element(robot)
        parent_visual_obj = get_visual(parent)
        parent_geometry_type, parent_visual_data = get_geometry(parent_visual_obj)
        if (parent_geometry_type == Geometry.CYLINDER):
            significant_length = parent_visual_data.length
        elif (parent_geometry_type ==  Geometry.BOX):
            significant_length = parent_visual_data.size.max()
        else:
            return
        modify_origin_joint(joint, significant_length, self.origin_modifier, self.take_half_length, self.flip_direction)

    def __str__(self):
        return f"Joint modifier with name {self.name}, origin modifier {self.origin_modifier}"


def create_backup(src, dst = "backup.urdf"):
    """Creates a backup of the current URDF in a different file"""
    current_path = str(Path().resolve())
    os.rename(f"{current_path}/{src}", f"{current_path}/{dst}")

def get_visual(link):
    """Returns the visual object of a link"""
    return link.visuals[0]

def get_geometry(visual_obj):
    """Returns the geometry type and the corresponding geometry object for a given visual"""
    if (visual_obj.geometry.box is not None):
        return [Geometry.BOX, visual_obj.geometry.box]
    if (visual_obj.geometry.cylinder is not None):
        return [Geometry.CYLINDER, visual_obj.geometry.cylinder]
    if (visual_obj.geometry.sphere is not None):
        return [Geometry.SPHERE, visual_obj.geometry.sphere]

def get_mass(link):
    """Returns the link's mass"""
    return link.inertial.mass

def calculate_volume(geometry_type, visual_data):
    """Calculates volume with the formula that corresponds to the geometry"""
    if (geometry_type == Geometry.BOX):
        return visual_data.size[0] * visual_data.size[1] * visual_data.size[2]
    elif (geometry_type == Geometry.CYLINDER):
        return math.pi * visual_data.radius ** 2 * visual_data.length
    elif (geometry_type == Geometry.SPHERE):
        return 4 * math.pi * visual_data.radius ** 3 / 3

def calculate_inertia(geometry_type, visual_data, mass):
    """Calculates inertia (ixx, iyy and izz) with the formula that corresponds to the geometry
    Formulas retrieved from https://en.wikipedia.org/wiki/List_of_moments_of_inertia"""
    if (geometry_type == Geometry.BOX):
        return mass / 12 * np.array([visual_data.size[1] ** 2 + visual_data.size[2] ** 2, 
                            visual_data.size[0] ** 2 + visual_data.size[2] ** 2,
                            visual_data.size[0] ** 2 + visual_data.size[1] ** 2])
    elif (geometry_type == Geometry.CYLINDER):
        i_xy_incomplete = (3 ** visual_data.radius ** 2 + visual_data.length ** 2) / 12
        return mass * np.array([i_xy_incomplete, i_xy_incomplete, visual_data.radius ** 2 / 2])
    elif (geometry_type == Geometry.SPHERE):
        inertia = 2 * mass * visual_data.radius ** 2 / 5
        return np.array([inertia, inertia, inertia])

def calculate_density(mass, volume):
    """Calculates density with given mass and volume"""
    return mass / volume

def modify_volume(link, multiplier, dim = None):
    """Modifies a link's volume by a given multiplier, in a manner that is logical with the link's geometry"""
    visual_obj = get_visual(link)
    geometry_type, visual_data = get_geometry(visual_obj)
    if (geometry_type == Geometry.BOX):
        if (dim is not None):
            if (dim == Side.WIDTH):
                visual_data.size[0] *= multiplier
            elif (dim == Side.HEIGHT):
                visual_data.size[1] *= multiplier
            elif (dim == Side.DEPTH):
                visual_data.size[2] *= multiplier
        else:
            print(f"Error modifying link {link.name}'s volume: Box geometry with no dimension")
    elif (geometry_type == Geometry.CYLINDER):
        visual_data.length *= multiplier
    elif (geometry_type == Geometry.SPHERE):
        visual_data.radius *= multiplier ** (1./3)

def modify_origin_link(link, modifier, dim=None, flip_direction = True, origin_from_dimensions = True):
    """Modifies the position of the origin by a given amount"""
    visual_obj = get_visual(link)
    geometry_type, visual_data = get_geometry(visual_obj)
    xyz_rpy = matrix_to_xyz_rpy(visual_obj.origin)
    if (geometry_type == Geometry.BOX):
        if (dim is not None):
            if (dim == Side.WIDTH):
                index_to_change = 0
            if (dim == Side.HEIGHT):
                index_to_change = 1
            if (dim == Side.DEPTH):
                index_to_change = 2
            if (origin_from_dimensions):
                xyz_rpy[index_to_change] = (visual_data.size[index_to_change] if not flip_direction else -visual_data.size[index_to_change]) / 2
            else:
                xyz_rpy[index_to_change] = 0
            xyz_rpy[index_to_change] += modifier 
        else:
            print(f"Error modifying link {link.name}'s origin: Box geometry with no dimension")
    elif (geometry_type == Geometry.CYLINDER):
        xyz_rpy[2] = -visual_data.length / 2 + modifier
        visual_obj.origin = xyz_rpy_to_matrix(xyz_rpy)
    elif (geometry_type == Geometry.SPHERE):
        return

def modify_origin_joint(joint, significant_length, modifier, take_half_length, flip_direction):
    """Modifies a joint by using its modifier"""
    xyz_rpy = matrix_to_xyz_rpy(joint.origin)
    xyz_rpy[2] = significant_length / (2 if take_half_length else 1)
    if flip_direction:
        xyz_rpy[2] *= -1
    xyz_rpy[2] += modifier
    joint.origin = xyz_rpy_to_matrix(xyz_rpy)

def update_mass(link, density):
    """Updates the mass of a link by preserving a given density.
    To be called after modify_volume"""
    visual_obj = get_visual(link)
    geometry_type, visual_data = get_geometry(visual_obj)
    volume = calculate_volume(geometry_type, visual_data)
    link.inertial.mass = volume * density

def update_inertia(link):
    """Updates the inertia of a link to match its volume and mass.
    To be called after modify_volume and update_mass"""
    visual_obj = get_visual(link)
    geometry_type, visual_data = get_geometry(visual_obj)
    if (link.inertial is not None):
        inertia = link.inertial.inertia
        new_inertia = calculate_inertia(geometry_type, visual_data, get_mass(link))
        new_inertia[new_inertia < 0.01] = 0.01
        for i in range(3):
            for j in range(3):
                if (i == j):
                    inertia[i,j] = new_inertia[i]
                else:
                    inertia[i,j] = 0

def write_urdf_to_file(urdf, filename, gazebo_plugins):
    """Saves the URDF to a valid .urdf file, also adding the gazebo_plugins"""
    urdf.save(filename)
    lines = ''
    with open(filename, 'r') as f:
        lines = f.readlines()
        lines.pop()
        lines = lines + gazebo_plugins

    with open(filename, 'w') as f:
        f.writelines(lines)

def get_elements_to_modify(limb):
    """Returns a list of modifiers for a given limb"""
    right_arm_modifiers = [
        LinkModifier('r_upper_arm', 0.022),
        LinkModifier('r_forearm', 0.03904),
        JointModifier('r_elbow', 0.0344),
        JointModifier('r_wrist_pitch',0.0506)
    ]
    left_arm_modifiers = [
        LinkModifier('l_upper_arm', 0.022),
        LinkModifier('l_forearm', 0.03904),
        JointModifier('l_elbow',0.0344),
        JointModifier('l_wrist_pitch',0.0506)
    ]
    right_leg_modifiers = [
        LinkModifier('r_hip_3', 0.058),
        LinkModifier('r_lower_leg', -0.03),
        JointModifier('r_hip_yaw', 0.1451),
        JointModifier('r_knee', 0.0536),
        JointModifier('r_ankle_pitch', -0.055989)
    ]
    left_leg_modifiers = [
        LinkModifier('l_hip_3', 0.058),
        LinkModifier('l_lower_leg', -0.03),
        JointModifier('l_hip_yaw', 0.1451),
        JointModifier('l_knee', 0.0536),
        JointModifier('l_ankle_pitch', -0.055989)
    ]
    torso_modifiers = [
        LinkModifier('root_link', 0, Side.DEPTH),
        LinkModifier('torso_1', 0, Side.DEPTH, False),
        LinkModifier('torso_2', 0, Side.DEPTH),
        LinkModifier('chest', 0, Side.DEPTH, True),
        JointModifier('torso_pitch', -0.078, False, False),
        JointModifier('torso_yaw', -0.07113, False, False),
        JointModifier('r_hip_pitch', 0.0494, True),
        JointModifier('l_hip_pitch', 0.0494, True),
        JointModifier('r_shoulder_pitch', 0.0554, True, False),
        JointModifier('l_shoulder_pitch', 0.0554, True, False),
        JointModifier('neck_fixed_joint', 0.0607, True, False)
    ]
    if (limb == Limb.RIGHT_ARM):
        return right_arm_modifiers
    elif (limb == Limb.LEFT_ARM):
        return left_arm_modifiers
    elif (limb == Limb.LEFT_LEG):
        return left_leg_modifiers
    elif (limb == Limb.RIGHT_LEG):
        return right_leg_modifiers
    elif (limb == Limb.ARMS):
        return right_arm_modifiers + left_arm_modifiers
    elif (limb == Limb.LEGS):
        return right_leg_modifiers + left_leg_modifiers
    elif (limb == Limb.ALL):
        return right_arm_modifiers + left_arm_modifiers + right_leg_modifiers + left_leg_modifiers + torso_modifiers
    elif (limb == Limb.TORSO):
        return torso_modifiers
    elif (limb == Limb.NONE):
        return []

def separate_gazebo_plugins(filename):
    """Splits the URDF content in two parts: one relative to the robot and another to the gazebo plugins"""
    gazebo_lines = []
    other_lines= []
    with open(filename, "r") as f:
        lines = f.readlines()
        is_gazebo = False
        for line in lines:
            if '<gazebo' in line or '< gazebo' in line:
                is_gazebo = True
            if (is_gazebo):
                gazebo_lines.append(line)
            else:
                other_lines.append(line)
    other_lines.append('</robot>')
    return [other_lines, gazebo_lines]
        
def create_dummy_file(dummy_filename, text):
    """Creates a dummy file to save information"""
    with open(dummy_filename, 'w') as f:
        f.writelines(text)

def erase_dummy_file(dummy_filename):
    """Erases the dummy file"""
    os.remove(dummy_filename)

def install_urdf():
    os.system("cd ../build && make install -j4")

def main(filename, dummy_file, config_file_path, should_reset):
    # The urdfpy library does not read the gazebo plugins well so they need to be
    # stripped from the file before parsing it
    if (should_reset):
        os.system("git checkout ../models/stickBot/model.urdf")
    else:
        main_urdf, gazebo_plugin_text = separate_gazebo_plugins(filename)
        create_dummy_file(dummy_file, main_urdf)
        robot = URDF.load(dummy_file)
        erase_dummy_file(dummy_file)
        config = configparser.ConfigParser()
        config.read(config_file_path)
        for config_section in config.sections():
            dimension_multiplier = float(config[config_section].get('dimension', '1.0'))
            density_multiplier = float(config[config_section].get('density', '-1'))
            if config_section.upper() in Limb:
                limb = Limb[config_section.upper()]
                elements_to_modify = get_elements_to_modify(limb)
                for element_to_modify in elements_to_modify:
                    if (element_to_modify.element_type == RobotElement.LINK):
                        element_to_modify.modify(robot, dimension_multiplier, density_multiplier)
                    elif (element_to_modify.element_type == RobotElement.JOINT):
                        joint_parent = LinkModifier.get_link(robot, element_to_modify.get_element(robot).parent)
                        element_to_modify.modify(robot, joint_parent)
        write_urdf_to_file(robot, filename, gazebo_plugin_text)
    install_urdf()

if __name__ == "__main__":
    dummy_file = 'no_gazebo_plugins.urdf'
    parser = argparse.ArgumentParser(description = "Modifies a Stick-Bot URDF file")
    parser.add_argument('filename', nargs='?', help="The filename of the robot's URDF", default="../models/stickBot/model.urdf")
    parser.add_argument('-c', '--config', help="Path to configuration file", default="conf.ini")
    parser.add_argument('-r', '--reset', help="Sets the robotback to latest version in Git", action="store_true")
    args = parser.parse_args()
    if args.filename is not None:
        main(args.filename, dummy_file, args.config, args.reset)