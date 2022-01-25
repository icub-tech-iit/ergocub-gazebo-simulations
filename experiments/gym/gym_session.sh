#! /bin/bash

stretch_left()
{
    echo "ctpq time 1.0 off 0 pos (-0.0318091 16.2943 -2.60879 13.2607 -84.48 -0.00016716 0.0739929)" | yarp rpc /ctpservice/left_arm/rpc 
}

stretch_right()
{
    echo "ctpq time 1.0 off 0 pos (-0.0318091 16.2943 -2.60879 13.2607 -84.48 -0.00016716 0.0739929)" | yarp rpc /ctpservice/right_arm/rpc
}

stretch()
{
    stretch_left
    stretch_right
}

contract_left()
{
    echo "ctpq time 1.0 off 0 pos (0.100043 16.303 -2.56139 68.5599 -79.2006 -0.00652198 0.0680771)" | yarp rpc /ctpservice/left_arm/rpc
}

contract_right()
{
    echo "ctpq time 1.0 off 0 pos (0.100043 16.303 -2.56139 68.5599 -79.2006 -0.00652198 0.0680771)" | yarp rpc /ctpservice/right_arm/rpc
}

contract()
{
    contract_left
    contract_right
}

curl_left()
{
    stretch_left
    sleep 2
    contract_left
    sleep 2
    stretch_left
}

curl_right()
{
    stretch_right
    sleep 2
    contract_right
    sleep 2
    stretch_right
}

curl()
{
    stretch
    sleep 2
    contract 
    sleep 2
    stretch   
}

startup()
{
    ./cleanup.sh

    sleep 2
    export YARP_ROBOT_NAME=stickBot

    yarpserver --write --silent &

    sleep 1

    export YARP_CLOCK=/clock

    # Run gazebo world
    gazebo -slibgazebo_yarp_clock.so  gym.world &

    echo "Awaiting gazebo start up"
    sleep 18
    echo "Gazebo is ready gazebo start up"
    # Run ctpservice for moving the arms
    ctpService --robot icubSim --part left_arm &
    ctpService --robot icubSim --part right_arm &
    sleep 5
}

attach_weights()
{
    # Attach the weights to the hands
    stretch
    sleep 5
    echo "loadModelFromFile \"../../build/gym/sdf_files/left_weight\"" | yarp rpc /world_input_port
    echo "loadModelFromFile \"../../build/gym/sdf_files/right_weight\"" | yarp rpc /world_input_port
}

main()
{
    if [ "$1" == "" ];
    then
        echo "select an exercise (options: weights, curls)"
        exit
    fi
    
    startup
    
    if [ "$1" == "weights" ];
    then
        attach_weights
    elif [ "$1" == "curls" ];
    then
        attach_weights
        sleep 5
        curl
        curl
        curl
        curl
        curl
        curl
    else
        echo "invalid option (options: weights, curls)"
    fi
}

main $1
