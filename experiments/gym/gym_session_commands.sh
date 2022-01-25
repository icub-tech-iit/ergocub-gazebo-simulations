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

$1