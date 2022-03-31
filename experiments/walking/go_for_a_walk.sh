#! /bin/bash

startup()
{
    rm -rf ./telemetry_data

    ./cleanup.sh

    sleep 2
    export YARP_ROBOT_NAME=stickBot

    yarpserver --write --silent &

    sleep 1

    export YARP_CLOCK=/clock

    # Run gazebo world
    gazebo -slibgazebo_yarp_clock.so walk.world --verbose &

    echo "Awaiting gazebo start up"
    sleep 18
    echo "Gazebo is ready gazebo start up"

}

walk()
{
    echo "resetOffset all" | yarp rpc /wholeBodyDynamics/rpc
    sleep 2
    WalkingModule --from ./walking_controller_config/dcm_walking_with_joypad.ini &
    sleep 4
    echo "prepareRobot" | yarp rpc /walking-coordinator/rpc
    sleep 15
    echo "startWalking" | yarp rpc /walking-coordinator/rpc
    sleep 10
    echo "setGoal 8 0" | yarp rpc /walking-coordinator/rpc
    sleep 35
}

main()
{
    startup
    walk
    ./end_experiment.sh
}

main
