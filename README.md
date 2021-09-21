# ergocub-gazebo-simulations

![robots](https://user-images.githubusercontent.com/31577366/132301971-c3aa9a8c-fc27-4a74-9c83-f8e79ffa2641.png)

Repository that contains some testing utilities for the ergocub project.

This repo contains a `gazebo` model, starting from iCub3, and some scripts that can easily modify it and test it in diverse scenarios. The goal of this repo is to gain knowledge about which is the best configuration for the ergoCub in terms of limb length, mass, etc.

## Maintained by:

- German Rodriguez ([@GrmanRodriguez](https://github.com/GrmanRodriguez))
- Alex Antunes ([@AlexAntn](https://github.com/AlexAntn/))
- Nicolo Genesio ([@Nicogene](https://github.com/Nicogene/))

## Requirements:

- [`gazebo`](http://gazebosim.org/)
- [`robotology-superbuild`](https://github.com/robotology/robotology-superbuild) with [`dynamics profile`](https://github.com/robotology/robotology-superbuild/blob/master/doc/cmake-options.md#dynamics) enabled and `ROBOTOLOGY_USES_GAZEBO=ON`.

## Installation:

- Clone this repo and create a `build` directory on it:

```bash
git clone https://github.com/icub-tech-iit/ergocub-gazebo-simulations.git
cd ergocub-gazebo-simulations
mkdir build
cd build
```

- Then use `ccmake` to specify the directory where you installed `robotology-superbuild`:

```bash
ccmake ..
CMAKE_INSTALL_PREFIX             <directory-where-you-downloaded-robotology-superbuild>/build/install
```

- You can now proceed to build:

```bash
make install -j4
```

You should now see three new models when you open `gazebo` from the terminal:

![newgazebobots](https://user-images.githubusercontent.com/31577366/132303603-70e8d9cb-8bb9-40a9-9bae-7cb2a9b9b2db.png)

## Usage

### Changing robot characteristics

```bash
cd scripts
./modify_robot.py # [-c {PATH}] [-r]
```

The `modify_robot` script changes the dimensions of the stickbot according to a configuration file. It also performs the installation step, so gazebo gets updated with the newest robot right away.

**Flags:**

 - `-c`/`--config {PATH}` Path of the configuration file, default is the `conf.ini` file inside `scripts`.
 - `-r`/`--reset` Setting this flag returns the robot to its latest version from git (by using `git-checkout`). This flag is prioritized over the configuration file.

### The configuration file

The `conf.ini` file is a simple configuration file specifying the limbs to modify:

```ini
[left_arm]
dimension = 1.3
density = 1.5

[right_leg]
dimension = 1.5
```

The upper section (the one inside `[]`) specifies the limb to modify, options include `torso, right_arm, left_arm, right_leg, left_leg, arms, legs` and `all`. Sections with other names will be ignored.

For any limb you can specify `dimension` and `density` multipliers, which will multiply the specific property for all the links in the specified limb.

### Holding Box Experiment

This sandbox uses the [`worldInterface`](http://robotology.github.io/gazebo-yarp-plugins/master/classgazebo_1_1WorldInterface.html) gazebo yarp plugin, then before running the script you must append to `GAZEBO_MODEL_PATH` the `/my/workspace/robotology-superbuild/src/GazeboYARPPlugins/tutorial/model` path. Then:

```bash
cd experiments/hold_box
./hold_box.sh
```

This experiment creates a StickBot in `gazebo` with its hands open. Then, a box spawns on top and the robot holds it. `yarpscopes` show the forces and torques that are experienced by both arms:

https://user-images.githubusercontent.com/31577366/132519425-fcfe1ce4-3acd-40fd-a878-298949b28ecb.mp4

Instead of closing every window that opens after the test, you can call the cleanup script:

```bash
./cleanup.sh
```

To change the properties of the box being spawned you can call the `modify_box` script:

```bash
./modify_box.py # [-p {X Y Z}] [-d {D W H}] [-m {MASS}] [-r]
```

**Flags:**
- `-p`/`--position` The spawning position of the box, inputted as three numbers representing X, Y and Z coordinates
- `-d`/`--dimensions` The dimensions of the box, inputted as three numbers representing its depth, width and height
- `-m`/`--mass` The mass of the box as a float
- `-r`/`--reset` Setting this flag returns the box to its latest version from git (by using `git-checkout`). This flag is prioritized over all other flags.

![ergocub-holding-bigger-box](https://user-images.githubusercontent.com/31577366/132665409-2bad5579-c9b9-4de1-b98c-7f3e4f97ffbe.png)

## Feedback and Collaboration

For bugs and feature requests feel free to [submit an issue](https://github.com/icub-tech-iit/ergocub-gazebo-simulations/issues/new) and we will look into it.
