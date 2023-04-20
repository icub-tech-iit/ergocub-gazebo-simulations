#!/usr/bin/env python3

from urchin import URDF
from enums import Limb
from pathlib import Path
from modifiers import get_modifiers
import argparse
import configparser
import os

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

def parse_modifications(config_section):
    """Returns the modifications from a section of the ini file"""
    modifications = {}
    dimension_scale = config_section.get('dimension_scale', None)
    if dimension_scale is not None:
        modifications["dimension"] = [float(dimension_scale), False]
    density_scale = config_section.get('density_scale', None)
    if density_scale is not None:
        modifications["density"] = [float(density_scale), False]
    radius_scale = config_section.get('radius_scale', None)
    if radius_scale is not None:
        modifications["radius"] = [float(radius_scale), False]
    mass_scale = config_section.get('mass_scale', None)
    if mass_scale is not None:
        modifications["mass"] = [float(mass_scale), False]
    dimension = config_section.get('dimension', None)
    if dimension is not None:
        modifications["dimension"] = [float(dimension), True]
    density = config_section.get('density', None)
    if density is not None:
        modifications["density"] = [float(density), True]
    radius = config_section.get('radius', None)
    if radius is not None:
        modifications["radius"] = [float(radius), True]
    mass = config_section.get('mass', None)
    if mass is not None:
        modifications["mass"] = [float(mass), True]
    return modifications

def erase_dummy_file(dummy_filename):
    """Erases the dummy file"""
    os.remove(dummy_filename)

def install_urdf():
    """Uses Make to install the URDF in the build folder to the Gazebo path"""
    os.system("cd ../build && make install -j4")

def main(filename, dummy_file, config_file_path, should_reset):
    export_filename = "../build/models/stickBot/model.urdf"
    if (should_reset):
        os.system(f"cp {filename} {export_filename}")
    else:
        # The urdfpy library does not read the gazebo plugins well so they need to be
        # stripped from the file before parsing it
        main_urdf, gazebo_plugin_text = separate_gazebo_plugins(filename)
        create_dummy_file(dummy_file, main_urdf)
        robot = URDF.load(dummy_file)
        erase_dummy_file(dummy_file)
        config = configparser.ConfigParser()
        config.read(config_file_path)
        for config_section in config.sections():
            modifications = parse_modifications(config[config_section])            
            if config_section.upper() in Limb:
                selector = Limb[config_section.upper()]
            else: 
                selector = config_section
            elements_to_modify = get_modifiers(robot, selector)
            for element_to_modify in elements_to_modify:
                element_to_modify.modify(modifications)
        write_urdf_to_file(robot, export_filename, gazebo_plugin_text)
    install_urdf()

if __name__ == "__main__":
    dummy_file = 'no_gazebo_plugins.urdf'
    parser = argparse.ArgumentParser(description = "Modifies a Stick-Bot URDF file")
    parser.add_argument('filename', nargs='?', help="The filename of the robot's URDF", default="../models/stickBot/model.urdf")
    parser.add_argument('-c', '--config', help="Path to configuration file", default="conf.ini")
    parser.add_argument('-r', '--reset', help="Sets the robot back to latest version in Git", action="store_true")
    args = parser.parse_args()
    if args.filename is not None:
        main(args.filename, dummy_file, args.config, args.reset)
