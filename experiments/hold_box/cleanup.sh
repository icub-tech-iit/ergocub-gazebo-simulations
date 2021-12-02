#! /bin/bash

echo "Cleaning up"
killall yarpdatadumper
sleep 1
killall -9 yarpserver
killall -9 yarpscope
killall -9 yarprobotinterface
killall -9 ctpService
killall -9 gazebo
killall -9 gzserver
killall -9 gzclient