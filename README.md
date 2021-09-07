# ergocub-gazebo-simulations

![robots](https://user-images.githubusercontent.com/31577366/132301971-c3aa9a8c-fc27-4a74-9c83-f8e79ffa2641.png)

Repository for testing different versions of ergocub using gazebo.

## Maintained by:

- German Rodriguez ([@GrmanRodriguez](https://github.com/GrmanRodriguez))
- Alex Antunes ([@AlexAntn](https://github.com/AlexAntn/))
- Nicolo Genesio ([@Nicogene](https://github.com/Nicogene/))

## Requirements:

- [`gazebo`](http://gazebosim.org/)
- [`gazebo-yarp-plugins`](https://github.com/robotology/gazebo-yarp-plugins)
- [`icub-models`](https://github.com/robotology/icub-models)

A convenient way to install the required software and their dependencies is to use the [`robotology-superbuild`](https://github.com/robotology/robotology-superbuild).

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

```bash
cd scripts
./modify_robot.py # [-c {PATH}] [-r]
```

The `modify_robot` script changes the dimensions of the stickbot according to a configuration file. It also performs the installation step, so gazebo gets updated with the newest robot right away.

**Flags:**

 - `-c`/`--config {PATH}` Path of the configuration file, default is the `conf.ini` file inside `scripts`.
 - `-r`/`--reset` Setting this flag returns the robot to its latest version from git (by using `git-checkout`). This flag is prioritized over the configuration file.

## The configuration file

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

## Feedback and Collaboration

For bugs and feature requests feel free to [submit an issue](https://github.com/icub-tech-iit/ergocub-gazebo-simulations/issues/new) and we will look into it.
