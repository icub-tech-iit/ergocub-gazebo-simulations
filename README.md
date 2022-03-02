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
- [`robotology-superbuild` v2022.02.0](https://github.com/robotology/robotology-superbuild/releases/tag/v2022.02.0) with [`dynamics profile`](https://github.com/robotology/robotology-superbuild/blob/master/doc/cmake-options.md#dynamics) enabled and `ROBOTOLOGY_USES_GAZEBO=ON`.
- For running the [walking and balancing experiment](https://github.com/icub-tech-iit/ergocub-gazebo-simulations/edit/feat_walking_balance/README.md#walking-and-balancing-experiment) the superbuild [dynamics-full-deps](https://github.com/robotology/robotology-superbuild/blob/master/doc/cmake-options.md#dynamics-full-deps) profile and the flag `ROBOTOLOGY_USES_MATLAB` have to be enabled, alongside a matlab installation.
- [`urdfpy`](https://github.com/mmatl/urdfpy)
- [`dataclasses`](https://pypi.org/project/dataclasses/)


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

Finally, add `export YARP_ROBOT_NAME=stickBot` in your `.bashrc`.

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

The `conf.ini` file is a simple configuration file specifying the elements to modify:

```ini
[left_arm]
dimension = 0.65
radius = 0.45
density_scale = 1.5

[r_lower_leg]
dimension = 1.5
```

The upper section (the one inside `[]`) specifies the element to modify, options include `torso, right_arm, left_arm, right_leg, left_leg, arms, legs`, `all`, or the name of an individual link (**Caution**: if a link and its respective limb are both specified, the changes could accumulate!). Sections with other names will be ignored.

For any element you can specify `dimension`, `mass`, `density`, and `radius`, which will set the specific property for all the valid links. If you want relative scaling you can instead add the `_scale` suffix and the factor to multiply to the original value. If a config section includes both an absolute and a scaling modifier the absolute one takes precedence. Mass modifications take precendence over density.

### Holding Box Experiment

This sandbox uses the [`worldInterface`](http://robotology.github.io/gazebo-yarp-plugins/master/classgazebo_1_1WorldInterface.html) gazebo yarp plugin. To run it:

```bash
cd experiments/hold_box
./hold_box.sh
```

This experiment creates a StickBot in `gazebo` with its hands open. Then, a box spawns on top and the robot holds it:

https://user-images.githubusercontent.com/31577366/132519425-fcfe1ce4-3acd-40fd-a878-298949b28ecb.mp4

Instead of closing every window that opens after the test, you can call the cleanup script:

```bash
./cleanup.sh
```

To change the properties of the box being spawned you can call the `modify_box` script:

```bash
./modify_box.py # [-p {X Y Z}] [-d {D W H}] [-m {MASS}] [-r]
```

After running the test, a new directory called `telemetry_data` will appear, use the `plotTelemetry.m` script in MATLAB to plot the results for the specific joints you need:

![hold_box_matlab_plot](https://user-images.githubusercontent.com/31577366/146351517-fdf40d37-7c3b-432a-a3b1-0f6751a942cb.png)

**Flags:**
- `-p`/`--position` The spawning position of the box, inputted as three numbers representing X, Y and Z coordinates
- `-d`/`--dimensions` The dimensions of the box, inputted as three numbers representing its depth, width and height
- `-m`/`--mass` The mass of the box as a float
- `-r`/`--reset` Setting this flag returns the box to its latest version from git (by using `git-checkout`). This flag is prioritized over all other flags.

![ergocub-holding-bigger-box](https://user-images.githubusercontent.com/31577366/132665409-2bad5579-c9b9-4de1-b98c-7f3e4f97ffbe.png)

### Gym-like Movements Experiment

This experiment attaches weights to the stickBot and makes it perform gym-like motions, in order to isolate (to the stickBot's best abilities) the effort to single joints. This sandbox uses the [`worldInterface`](http://robotology.github.io/gazebo-yarp-plugins/master/classgazebo_1_1WorldInterface.html) gazebo yarp plugin, then before running the script you must append to `GAZEBO_MODEL_PATH` the `/my/workspace/robotology-superbuild/src/GazeboYARPPlugins/tutorial/model` path. Then:

```bash
cd experiments/gym
./gym_session.sh # {curls lateral_raises front_raises}
```

The three possible experiments are the following:

| Name             | Stressed Joint                         | Example                                                                                                                 |
|------------------|----------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| `curls`          | `r_elbow`, `l_elbow`                   | ![curl](https://user-images.githubusercontent.com/31577366/151012575-4c00273b-641a-4673-9699-6e5a15d43d0e.gif)          |
| `front_raises`   | `r_shoulder_pitch`, `l_shoulder_pitch` | ![front-raise](https://user-images.githubusercontent.com/31577366/151013455-aaf4def2-3edb-4b32-94ac-46710d81e4e3.gif)   |
| `lateral_raises` | `r_shoulder_roll`, `l_shoulder_roll`   | ![lateral-raise](https://user-images.githubusercontent.com/31577366/151013597-ef90ed75-3b55-490b-8234-af16285031d7.gif) |
| `twists` | `torso_yaw`   | ![twists](https://user-images.githubusercontent.com/31577366/151828875-47398cc7-0be5-4a49-9731-bb4e0434c726.gif) |
| `bends` | `torso_roll`   | ![bends](https://user-images.githubusercontent.com/31577366/151828746-5170571f-4558-49cb-b4f0-24ec38889a47.gif) |
| `extensions` | `torso_pitch`   | ![extensions](https://user-images.githubusercontent.com/31577366/151828818-00d208bb-5a9e-48af-9690-e14b15c1b25e.gif) |

After running the test, a new directory called `telemetry_data` will appear, use the `plotTelemetry.m` script in MATLAB to plot the results for the specific joints you need:

![lateral_raise_116stickbot_7kg_torque](https://user-images.githubusercontent.com/31577366/151013992-fc4eedf7-7abb-43fe-badc-5a401322ff39.png)

### Walking and Balancing Experiment

These experiments implement walking and balancing, to stress the leg joints.

For running the walking experiment, just run the `go_for_a_walk.sh` script.

```bash
cd experiments/walking
./go_for_a_walk.sh
```

Gazebo will spawn, and the robot will walk like so:

https://user-images.githubusercontent.com/31577366/153621747-eeae3d75-001b-4086-b8e5-46c2099bb782.mp4

For this to work, [`WalkingModule`](https://github.com/robotology/walking-controllers) needs to be installed in the system.

It is important to mention that the behavior can be unreliable, and the robot may some times fall. For this reason, the script runs Gazebo with a GUI (unlike the other experiments). This way one can run the experiment several times until a successful walk is achieved. Once the robot walks properly, you will have the data available.

The balancing experiment is ran using [whole-body-controllers](https://github.com/robotology/whole-body-controllers/). Particularly, the [floating-base-balancing-torque-control](https://github.com/robotology/whole-body-controllers/tree/master/controllers/floating-base-balancing-torque-control) demo. You should launch Gazebo, spawn a stickbot and then run the simulink model. From there, you can use the `plotTelemetry.m` matlab script to visualize the data in the joints of interest.

https://user-images.githubusercontent.com/31577366/154500268-94a402ef-8b72-49fa-be5a-1301de6d4d92.mp4

## Feedback and Collaboration

For bugs and feature requests feel free to [submit an issue](https://github.com/icub-tech-iit/ergocub-gazebo-simulations/issues/new) and we will look into it.
