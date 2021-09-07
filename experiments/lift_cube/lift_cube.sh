#! /bin/bash

echo "Cleaning up"
killall -9 yarpserver
killall -9 yarpscope
killall -9 yarprobotinterface
killall -9 ctpService
killall -9 gazebo
killall -9 gzserver
killall -9 gzclient
sleep 2
export YARP_ROBOT_NAME=iCubGazeboV3

yarpserver --write --silent &

sleep 1

export YARP_CLOCK=/clock 

# Run gazebo world
gazebo -slibgazebo_yarp_clock.so  lifting_cube.world &
echo "Awaiting gazebo start up"
sleep 30
echo "Gazebo is ready gazebo start up"
# Run ctpservice for moving the arms
ctpService --robot icubSim --part left_arm &
ctpService --robot icubSim --part right_arm &
sleep 5

echo "ctpq time 1.0 off 0 pos (-44.4 12.0 0 45 -88 3.8 0.02)" | yarp rpc /ctpservice/left_arm/rpc
echo "ctpq time 1.0 off 0 pos (-44.4 12.0 0 45 -88 3.8 0.02)" | yarp rpc /ctpservice/right_arm/rpc
sleep 5

# Import the box
echo "loadModelFromFile \"$( pwd )/sdf_files\"" | yarp rpc /world_input_port

echo "Starting yarprobotinterface"
yarprobotinterface -slibgazebo_yarp_clock.so &
sleep 10

# Run yarpscopes
echo "Running yarpscopes"
unset YARP_PORT_PREFIX; export YARP_PORT_PREFIX=/left_arm/force; yarpscope --remote /wholeBodyDynamics/left_arm/endEffectorWrench:o --index "(0 1 2)" --color "(Red Green Blue)" --title "Forces left_arm" &
unset YARP_PORT_PREFIX; export YARP_PORT_PREFIX=/left_arm/torque; yarpscope --remote /wholeBodyDynamics/left_arm/endEffectorWrench:o --index "(3 4 5)" --color "(Red Green Blue)" --title "Torques left_arm" &
unset YARP_PORT_PREFIX; export YARP_PORT_PREFIX=/right_arm/force; yarpscope --remote /wholeBodyDynamics/right_arm/endEffectorWrench:o --index "(0 1 2)" --color "(Red Green Blue)" --title "Forces right_arm" &
unset YARP_PORT_PREFIX; export YARP_PORT_PREFIX=/right_arm/torque; yarpscope --remote /wholeBodyDynamics/right_arm/endEffectorWrench:o --index "(3 4 5)" --color "(Red Green Blue)" --title "Torques right_arm" &
unset YARP_PORT_PREFIX
unset YARP_ROBOT_NAME