#! /bin/bash

./cleanup.sh

sleep 2
export YARP_ROBOT_NAME=stickBot

yarpserver --write --silent &

sleep 1

if [[ -z $COMSPEC ]];
then
    # Not Windows
    export YARP_CLOCK=/clock
else
    # Windows
    export YARP_CLOCK=//clock
fi;

# Run gazebo world
gzserver -slibgazebo_yarp_clock.so  hold_box.world &
echo "Awaiting gazebo start up"
sleep 18
echo "Gazebo is ready gazebo start up"
# Run ctpservice for moving the arms
ctpService --robot icubSim --part left_arm &
ctpService --robot icubSim --part right_arm &
sleep 5

echo "ctpq time 1.0 off 0 pos (-44.4 12.0 0 45 -88 3.8 0.02)" | yarp rpc " /ctpservice/left_arm/rpc"
echo "ctpq time 1.0 off 0 pos (-44.4 12.0 0 45 -88 3.8 0.02)" | yarp rpc " /ctpservice/right_arm/rpc"
sleep 5

# Import the box
echo "loadModelFromFile \"../../build/hold_box/sdf_files\"" | yarp rpc " /world_input_port"

unset YARP_ROBOT_NAME