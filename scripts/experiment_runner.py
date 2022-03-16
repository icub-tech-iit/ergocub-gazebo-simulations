#!/usr/bin/env python3

from urdfpy import URDF
from enums import Limb
from pathlib import Path
from modifiers import get_modifiers
import argparse
import configparser
import os
import time
import subprocess


def main(filename):
    subprocess.Popen("ls", cwd="../experiments")
    hold_box = subprocess.Popen("./hold_box.sh", cwd="../experiments/hold_box")
    time.sleep(120)
    end_experiment = subprocess.Popen("./end_experiment.sh", cwd="../experiments/hold_box")

    print("hold_box return code:", hold_box.returncode)
    print("end_experiment return code:", end_experiment.returncode)




if __name__ == "__main__":
    dummy_file = 'no_gazebo_plugins.urdf'
    parser = argparse.ArgumentParser(description = "Run experiments with stickBot")
    parser.add_argument('filename', nargs='?', help="The filename descripting the experiment", default="../models/stickBot/model.urdf")
    args = parser.parse_args()
    main("foo.json")
    #if args.filename is not None:
    #    main(args.filename, dummy_file, args.config, args.reset)