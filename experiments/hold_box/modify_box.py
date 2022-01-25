#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import argparse
import os

def get_box_size(element):
    return element.find('geometry').find('box').find('size')

def set_spawn_position(model, new_spawn_position):
    box_pose = model.find('pose')
    box_pose.text = f"{new_spawn_position[0]} {new_spawn_position[1]} {new_spawn_position[2]} 0 0 0"

def set_box_dimensions(model, new_box_dimensions):
    link = model.find('link')
    box_size_collision = get_box_size(link.find('collision'))
    box_size_collision.text = f"{new_box_dimensions[0]} {new_box_dimensions[1]} {new_box_dimensions[2]}"
    box_size_visual = get_box_size(link.find('visual'))
    box_size_visual.text = f"{new_box_dimensions[0]} {new_box_dimensions[1]} {new_box_dimensions[2]}"

def set_box_mass(model, new_box_mass):
    link = model.find('link')
    box_mass = link.find('inertial').find('mass')
    box_mass.text = str(new_box_mass)

def main(filename, spawn_position, box_dimensions, box_mass, should_reset):
    if (should_reset):
        os.system(f"cp sdf_files/hold_box.sdf {filename}")
    else:
        tree = ET.parse(filename)
        root = tree.getroot()
        model = root[0]
        if (spawn_position is not None):
            set_spawn_position(model, spawn_position)
        if (box_dimensions is not None):
            set_box_dimensions(model, box_dimensions)
        if (box_mass is not None):
            set_box_mass(model, box_mass)
        tree.write(filename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Modifies the lifting cube test")
    parser.add_argument('-p', '--position', nargs=3, help="The coordinates where the box will spawn from", type=float, default=None)
    parser.add_argument('-d', '--dimensions', nargs=3, help="The dimensions of the box", type=float, default=None)
    parser.add_argument('-m', '--mass', type=float, default=None, help="The mass of the box")
    parser.add_argument('-r', '--reset', help="Sets the test back to latest version in Git", action="store_true")
    args = parser.parse_args()
    filename = '../../build/hold_box/sdf_files/hold_box.sdf'
    main(filename, args.position, args.dimensions, args.mass, args.reset)