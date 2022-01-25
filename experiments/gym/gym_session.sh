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

front_raise_lift_left()
{
    echo "ctpq time 1.0 off 0 pos (-73.3629 16.3326 -2.6125 13.235 -84.4803 -0.00264766 0.109959)" | yarp rpc /ctpservice/left_arm/rpc	
}

front_raise_lift_right()
{
    echo "ctpq time 1.0 off 0 pos (-73.3629 16.3326 -2.6125 13.235 -84.4803 -0.00264766 0.109959)" | yarp rpc /ctpservice/right_arm/rpc	
}

front_raise_lift()
{
    echo "ctpq time 1.0 off 0 pos (-73.3629 16.3326 -2.6125 13.235 -84.4803 -0.00264766 0.109959)" | yarp rpc /ctpservice/left_arm/rpc
    echo "ctpq time 1.0 off 0 pos (-73.3629 16.3326 -2.6125 13.235 -84.4803 -0.00264766 0.109959)" | yarp rpc /ctpservice/right_arm/rpc	
}

front_raise_left()
{
    stretch
    sleep 2
    front_raise_lift_left
    sleep 2
    stretch
}

front_raise_right()
{
    stretch
    sleep 2
    front_raise_lift_right
    sleep 2
    stretch
}

front_raise()
{
    stretch
    sleep 2
    front_raise_lift
    sleep 2
    stretch
}

lateral_raise_lift_left()
{
    echo "ctpq time 1.0 off 0 pos (6.99373 87.153 76.7017 4.05757 -88 0.023628 0.0902894)" | yarp rpc /ctpservice/left_arm/rpc
}

lateral_raise_lift_right()
{
    echo "ctpq time 1.0 off 0 pos (6.99373 87.153 76.7017 4.05757 -88 0.023628 0.0902894)" | yarp rpc /ctpservice/right_arm/rpc
}

lateral_raise_lift()
{
    echo "ctpq time 1.0 off 0 pos (6.99373 87.153 76.7017 4.05757 -88 0.023628 0.0902894)" | yarp rpc /ctpservice/left_arm/rpc
    echo "ctpq time 1.0 off 0 pos (6.99373 87.153 76.7017 4.05757 -88 0.023628 0.0902894)" | yarp rpc /ctpservice/right_arm/rpc
}

lateral_raise_drop_left()
{
    echo "ctpq time 1.0 off 0 pos (7.02536 15.375 76.6976 3.71276 -88 -0.0322056 0.107769)" | yarp rpc /ctpservice/left_arm/rpc
}

lateral_raise_drop_right()
{
    echo "ctpq time 1.0 off 0 pos (7.02536 15.375 76.6976 3.71276 -88 -0.0322056 0.107769)" | yarp rpc /ctpservice/right_arm/rpc
}

lateral_raise_drop()
{
    echo "ctpq time 1.0 off 0 pos (7.02536 15.375 76.6976 3.71276 -88 -0.0322056 0.107769)" | yarp rpc /ctpservice/left_arm/rpc
    echo "ctpq time 1.0 off 0 pos (7.02536 15.375 76.6976 3.71276 -88 -0.0322056 0.107769)" | yarp rpc /ctpservice/right_arm/rpc
}

lateral_raise_left()
{
    lateral_raise_drop_left
    sleep 2
    lateral_raise_lift_left
    sleep 2
    lateral_raise_drop_left
}

lateral_raise_right()
{
    lateral_raise_drop_right
    sleep 2
    lateral_raise_lift_right
    sleep 2
    lateral_raise_drop_right
}

lateral_raise()
{
    lateral_raise_drop
    sleep 2
    lateral_raise_lift
    sleep 2
    lateral_raise_drop
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
    gzserver -slibgazebo_yarp_clock.so  gym.world &

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
        echo "select an exercise (options: weights, curls, front_raises, lateral_raises)"
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
        sleep 5
    elif [ "$1" == "front_raises" ];
    then
        attach_weights
        sleep 5
        front_raise
        front_raise
        front_raise
        front_raise
        front_raise
        front_raise
        sleep 5
    elif [ "$1" == "lateral_raises" ];
    then
        attach_weights
        sleep 5
        lateral_raise
        lateral_raise
        lateral_raise
        lateral_raise
        lateral_raise
        lateral_raise
        sleep 2
        stretch
        sleep 5
    else
        echo "invalid option (options: weights, curls, front_raises, lateral_raises)"
    fi

    ./end_experiment.sh
}

main $1
