# Copyright (C) 2006-2021 Istituto Italiano di Tecnologia (IIT)
# All rights reserved.
#
# This software may be modified and distributed under the terms of the
# BSD-3-Clause license. See the accompanying LICENSE file for details.

cmake_minimum_required(VERSION 3.12)
project(ergocub-gazebo-simulation
                       VERSION 0.0.0
                       LANGUAGES NONE)

file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/models DESTINATION ${CMAKE_BINARY_DIR})
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/experiments/hold_box/sdf_files DESTINATION ${CMAKE_BINARY_DIR}/hold_box)
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/experiments/gym/sdf_files DESTINATION ${CMAKE_BINARY_DIR}/gym)
install(DIRECTORY ${CMAKE_BINARY_DIR}/models/ DESTINATION share/iCub/robots)
# for now using stickBot as name, we might want to change to something more ergocub-ish

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/conf_stickBot DESTINATION share/iCub)

install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/scripts/modify_robot.py ${CMAKE_CURRENT_SOURCE_DIR}/scripts/fix_inertias.py DESTINATION bin )
# TODO: what do we do about the conf.ini? it should not be installed with the binaries, but we don't really have a context to put it on either...

