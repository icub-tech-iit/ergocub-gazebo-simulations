################################################################################
#                                                                              #
# Copyright (C) 2020 Fondazione Istitito Italiano di Tecnologia (IIT)          #
# All Rights Reserved.                                                         #
#                                                                              #
################################################################################
cmake_minimum_required(VERSION 2.6)
project(stickbot)

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/models/stickBot DESTINATION share/gazebo/models)
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/models/stickBot_feet_fixed DESTINATION share/gazebo/models)
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/models/stickBot_fixed DESTINATION share/gazebo/models)
# for now using stickBot as name, we might want to change to something more ergocub-ish

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/conf_stickBot DESTINATION share/iCub)

install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/scripts/modify_robot.py ${CMAKE_CURRENT_SOURCE_DIR}/scripts/fix_inertias.py DESTINATION bin )

# TODO: what do we do about the conf.ini? it should not be installed with the binaries, but we don't really have a context to put it on either...

