from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from urdfpy import xyz_rpy_to_matrix, matrix_to_xyz_rpy
from enums import *
import math
import numpy as np

class Modifier(metaclass=ABCMeta):
    """Class to contain information and methods on how to modify a URDF element"""
    def __init__(self, element, origin_modifier, element_type):
        self.element = element
        self.origin_modifier = origin_modifier
        self.element_type = element_type

    @abstractmethod
    def modify(self, dimension_multiplier, density_multiplier, radius_multiplier, new_mass):
        pass

    @abstractmethod
    def modify_origin(self):
        pass

@dataclass
class LinkModifier(Modifier):
    """Class to modify links in a URDF"""
    def __init__(self, link, origin_modifier, dimension = None, flip_direction = True, calculate_origin_from_dimensions = True):
        super().__init__(link, origin_modifier, RobotElement.LINK)
        self.dimension = dimension
        self.flip_direction = flip_direction
        self.calculate_origin_from_dimensions = calculate_origin_from_dimensions

    @classmethod
    def from_name(cls, link_name, robot, origin_modifier, dimension = None, flip_direction = True, calculate_origin_from_dimensions = True):
        """Creates an instance of LinkModifier by passing the robot object and link name"""
        return cls(LinkModifier.get_element_by_name(link_name, robot), origin_modifier, dimension, flip_direction, calculate_origin_from_dimensions)

    @staticmethod
    def get_element_by_name(link_name, robot):
        """Explores the robot looking for the link whose name matches the first argument"""
        link_list = [corresponding_link for corresponding_link in robot.links if corresponding_link.name == link_name]
        if len(link_list) != 0:
            return link_list[0]
        else:
            return None

    def modify(self, dimension_multiplier = 1, density_multiplier = 1, radius_multiplier=1, new_mass=None):
        """Performs the dimension and density modifications to the current link"""
        original_density = self.calculate_density()
        self.modify_volume(dimension_multiplier, radius_multiplier)
        if new_mass is None:
            density = original_density * density_multiplier
            self.modify_mass(density)
        else:
            self.set_mass(new_mass)
        self.update_inertia()
        self.modify_origin()

    def get_visual(self):
        """Returns the visual object of a link"""
        return self.element.visuals[0]

    @staticmethod
    def get_visual_static(link):
        """Static method that returns the visual of a link"""
        return link.visuals[0]

    @staticmethod
    def get_geometry(visual_obj):
        """Returns the geometry type and the corresponding geometry object for a given visual"""
        if (visual_obj.geometry.box is not None):
            return [Geometry.BOX, visual_obj.geometry.box]
        if (visual_obj.geometry.cylinder is not None):
            return [Geometry.CYLINDER, visual_obj.geometry.cylinder]
        if (visual_obj.geometry.sphere is not None):
            return [Geometry.SPHERE, visual_obj.geometry.sphere]

    def calculate_volume(self, geometry_type, visual_data):
        """Calculates volume with the formula that corresponds to the geometry"""
        if (geometry_type == Geometry.BOX):
            return visual_data.size[0] * visual_data.size[1] * visual_data.size[2]
        elif (geometry_type == Geometry.CYLINDER):
            return math.pi * visual_data.radius ** 2 * visual_data.length
        elif (geometry_type == Geometry.SPHERE):
            return 4 * math.pi * visual_data.radius ** 3 / 3

    def get_mass(self):
        """Returns the link's mass"""
        return self.element.inertial.mass

    def set_mass(self, new_mass):
        """Sets the mass value to a new value"""
        self.element.inertial.mass = new_mass

    def calculate_density(self):
        """Calculates density from mass and volume"""
        geometry_type, visual_data = self.get_geometry(self.get_visual())
        return self.get_mass() / self.calculate_volume(geometry_type, visual_data)

    def modify_volume(self, multiplier, radius_multiplier):
        """Modifies a link's volume by a given multiplier, in a manner that is logical with the link's geometry"""
        geometry_type, visual_data = self.get_geometry(self.get_visual())
        if (geometry_type == Geometry.BOX):
            if (self.dimension is not None):
                if (self.dimension == Side.WIDTH):
                    visual_data.size[0] *= multiplier
                elif (self.dimension == Side.HEIGHT):
                    visual_data.size[1] *= multiplier
                elif (self.dimension == Side.DEPTH):
                    visual_data.size[2] *= multiplier
            else:
                print(f"Error modifying link {self.element.name}'s volume: Box geometry with no dimension")
        elif (geometry_type == Geometry.CYLINDER):
            visual_data.length *= multiplier
            visual_data.radius *= radius_multiplier
        elif (geometry_type == Geometry.SPHERE):
            visual_data.radius *= multiplier ** (1./3)

    def modify_origin(self):
        """Modifies the position of the origin by a given amount"""
        visual_obj = self.get_visual()
        geometry_type, visual_data = self.get_geometry(visual_obj)
        xyz_rpy = matrix_to_xyz_rpy(visual_obj.origin)
        if (geometry_type == Geometry.BOX):
            if (self.dimension is not None):
                if (self.dimension == Side.WIDTH):
                    index_to_change = 0
                if (self.dimension == Side.HEIGHT):
                    index_to_change = 1
                if (self.dimension == Side.DEPTH):
                    index_to_change = 2
                if (self.calculate_origin_from_dimensions):
                    xyz_rpy[index_to_change] = (visual_data.size[index_to_change] if not self.flip_direction else -visual_data.size[index_to_change]) / 2
                xyz_rpy[index_to_change] += self.origin_modifier
                visual_obj.origin = xyz_rpy_to_matrix(xyz_rpy) 
            else:
                print(f"Error modifying link {self.element.name}'s origin: Box geometry with no dimension")
        elif (geometry_type == Geometry.CYLINDER):
            xyz_rpy[2] = -visual_data.length / 2 + self.origin_modifier
            visual_obj.origin = xyz_rpy_to_matrix(xyz_rpy)
        elif (geometry_type == Geometry.SPHERE):
            return

    def modify_mass(self, density):
        """Changes the mass of a link by preserving a given density."""
        geometry_type, visual_data = self.get_geometry(self.get_visual())
        volume = self.calculate_volume(geometry_type, visual_data)
        self.element.inertial.mass = volume * density

    def calculate_inertia(self):
        """Calculates inertia (ixx, iyy and izz) with the formula that corresponds to the geometry
        Formulas retrieved from https://en.wikipedia.org/wiki/List_of_moments_of_inertia"""
        geometry_type, visual_data = self.get_geometry(self.get_visual())
        mass = self.get_mass()
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

    def update_inertia(self):
        """Updates the inertia of a link to match its volume and mass."""
        if (self.element.inertial is not None):
            inertia = self.element.inertial.inertia
            new_inertia = self.calculate_inertia()
            new_inertia[new_inertia < 0.01] = 0.01
            for i in range(3):
                for j in range(3):
                    if (i == j):
                        inertia[i,j] = new_inertia[i]
                    else:
                        inertia[i,j] = 0

    def __str__(self):
        return f"Link modifier with name {self.element.name}, origin modifier {self.origin_modifier}, dimension {self.dimension}"


class JointModifier(Modifier):
    """Class to modify joints in a URDF"""
    def __init__(self, joint, origin_modifier, parent, take_half_length = False, flip_direction = True):
        super().__init__(joint, origin_modifier, RobotElement.JOINT)
        self.take_half_length = take_half_length
        self.flip_direction = flip_direction
        self.parent = parent
        

    @classmethod
    def from_name(cls, joint_name, robot, origin_modifier, take_half_length = False, flip_direction = True):
        """Creates an instance of LinkModifier by passing the robot object and link name"""
        joint = JointModifier.get_element_by_name(joint_name, robot)
        parent = LinkModifier.get_element_by_name(joint.parent, robot)
        return cls(joint, origin_modifier, parent, take_half_length, flip_direction)

    @staticmethod
    def get_element_by_name(joint_name, robot):
        """Explores the robot looking for the joint whose name matches the first argument"""
        joint_list = [corresponding_joint for corresponding_joint in robot.joints if corresponding_joint.name == joint_name]
        if len(joint_list) != 0:
            return joint_list[0]
        else:
            return None

    def modify(self, dimension_multiplier = None, density_multiplier = None, radius_multipler=None, new_mass=None):
        """Performs the dimension and density modifications to the current link"""
        significant_length = self.get_parent_significant_length()
        self.modify_origin(significant_length)

    def get_parent_significant_length(self):
        """Gets the significant length of the parent link that defines the new position of the joint"""
        parent_visual_obj = LinkModifier.get_visual_static(self.parent)
        parent_geometry_type, parent_visual_data = LinkModifier.get_geometry(parent_visual_obj)
        if (parent_geometry_type == Geometry.CYLINDER):
            return parent_visual_data.length
        elif (parent_geometry_type ==  Geometry.BOX):
            return parent_visual_data.size.max()
        else:
            return 0

    def modify_origin(self, length):
        """Modifies the position of the origin by a given amount"""
        xyz_rpy = matrix_to_xyz_rpy(self.element.origin)
        xyz_rpy[2] = length / (2 if self.take_half_length else 1)
        if self.flip_direction:
            xyz_rpy[2] *= -1
        xyz_rpy[2] += self.origin_modifier
        self.element.origin = xyz_rpy_to_matrix(xyz_rpy)

def get_modifiers(robot, selector):
    """Returns a list of modifiers for a given limb/link"""
    modifiers_mapper = {
        'r_upper_arm': [
            LinkModifier.from_name('r_upper_arm',robot, 0.022),
            JointModifier.from_name('r_elbow',robot, 0.0344)
        ],
        'r_forearm': [
            LinkModifier.from_name('r_forearm',robot, 0.03904),
            JointModifier.from_name('r_wrist_pitch',robot, 0.0506)
        ],
        'l_upper_arm': [
            LinkModifier.from_name('l_upper_arm',robot, 0.022),
            JointModifier.from_name('l_elbow',robot, 0.0344)
        ],
        'l_forearm': [
            LinkModifier.from_name('l_forearm',robot, 0.03904),
            JointModifier.from_name('l_wrist_pitch',robot, 0.0506)
        ],
        'r_hip_3': [
            LinkModifier.from_name('r_hip_3',robot, 0.058),
            JointModifier.from_name('r_hip_yaw',robot, 0.1451),
            JointModifier.from_name('r_knee',robot, 0.0536)
        ],
        'r_lower_leg': [
            LinkModifier.from_name('r_lower_leg',robot, -0.03),
            JointModifier.from_name('r_ankle_pitch',robot, -0.055989)
        ],
        'l_hip_3': [
            LinkModifier.from_name('l_hip_3',robot, 0.058),
            JointModifier.from_name('l_hip_yaw',robot, 0.1451),
            JointModifier.from_name('l_knee',robot, 0.0536)
        ],
        'l_lower_leg': [
            LinkModifier.from_name('l_lower_leg',robot, -0.03),
            JointModifier.from_name('l_ankle_pitch',robot, -0.055989)
        ],
        'root_link': [
            LinkModifier.from_name('root_link',robot, 0, Side.DEPTH, calculate_origin_from_dimensions = False),
            JointModifier.from_name('torso_pitch',robot, -0.078, flip_direction=False),
            JointModifier.from_name('r_hip_pitch',robot, 0.0494, take_half_length=True),
            JointModifier.from_name('l_hip_pitch',robot, 0.0494, take_half_length=True)
        ],
        'torso_1': [
            LinkModifier.from_name('torso_1',robot, 0, Side.DEPTH, calculate_origin_from_dimensions = False),
            JointModifier.from_name('torso_yaw',robot, -0.07113, flip_direction=False),
        ],
        'torso_2': [
            LinkModifier.from_name('torso_2',robot, 0, Side.DEPTH, calculate_origin_from_dimensions = False),
            JointModifier.from_name('torso_yaw',robot, -0.07113, flip_direction=False)
        ],
        'chest': [
            LinkModifier.from_name('chest',robot, 0, Side.DEPTH, calculate_origin_from_dimensions = False),
            JointModifier.from_name('r_shoulder_pitch',robot, 0.0554, take_half_length=True, flip_direction=False),
            JointModifier.from_name('l_shoulder_pitch',robot, 0.0554, take_half_length=True, flip_direction=False),
            JointModifier.from_name('neck_fixed_joint',robot, 0.0607, take_half_length=True, flip_direction=False)
        ]

    }

    if isinstance(selector, str):
        if selector in modifiers_mapper:
            return modifiers_mapper[selector]
        else:
            return []
    elif (selector == Limb.RIGHT_ARM):
        return modifiers_mapper["r_upper_arm"] + modifiers_mapper["r_forearm"]
    elif (selector == Limb.LEFT_ARM):
        return modifiers_mapper["l_upper_arm"] + modifiers_mapper["l_forearm"]
    elif (selector == Limb.LEFT_LEG):
        return modifiers_mapper["l_lower_leg"] + modifiers_mapper["l_hip_3"]
    elif (selector == Limb.RIGHT_LEG):
        return modifiers_mapper["r_lower_leg"] + modifiers_mapper["r_hip_3"]
    elif (selector == Limb.ARMS):
        return modifiers_mapper["r_upper_arm"] + modifiers_mapper["r_forearm"] + modifiers_mapper["l_upper_arm"] + modifiers_mapper["l_forearm"]
    elif (selector == Limb.LEGS):
        return modifiers_mapper["l_lower_leg"] + modifiers_mapper["l_hip_3"] + modifiers_mapper["r_lower_leg"] + modifiers_mapper["r_hip_3"]
    elif (selector == Limb.TORSO):
        return modifiers_mapper["root_link"] + modifiers_mapper["torso_1"] + modifiers_mapper["torso_2"] + modifiers_mapper["chest"]
    elif (selector == Limb.ALL):
        all_modifiers = []
        for i in modifiers_mapper:
            all_modifiers += modifiers_mapper[i]
        return all_modifiers
    elif (selector == Limb.NONE):
        return []
    else:
        return []