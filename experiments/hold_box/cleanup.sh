#! /bin/bash

echo "Cleaning up"
sleep 1

if [[ -z $COMSPEC ]];
then
    # Not Windows
    killall -9 yarpserver
    killall -9 ctpService
    killall -9 gazebo
    killall -9 gzserver
    killall -9 gzclient
else
    # Windows
    taskkill //F //IM yarpserver.exe
    taskkill //F //IM ctpService.exe
    taskkill //F //IM gazebo.exe
    taskkill //F //IM gzserver.exe
    taskkill //F //IM gzclient.exe
fi;