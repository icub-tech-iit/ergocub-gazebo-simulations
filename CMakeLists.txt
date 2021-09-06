cmake_minimum_required(VERSION 2.6)


install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/models/stickBot/model.urdf ${CMAKE_CURRENT_SOURCE_DIR}/models/stickBot/model.config DESTINATION share/gazebo/models/stickBot)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/models/stickBot_feet_fixed/stickBot_feet_fixed.sdf ${CMAKE_CURRENT_SOURCE_DIR}/models/stickBot_feet_fixed/model.config DESTINATION share/gazebo/models/stickBot_feet_fixed)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/models/stickBot_fixed/stickBot_fixed.sdf ${CMAKE_CURRENT_SOURCE_DIR}/models/stickBot_fixed/model.config DESTINATION share/gazebo/models/stickBot_fixed)
# for now using stickBot as name, we might want to change to something more ergocub-ish

install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/scripts/modify_robot.py ${CMAKE_CURRENT_SOURCE_DIR}/scripts/fix_inertias.py DESTINATION bin )

# TODO: what do we do about the conf.ini? it should not be installed with the binaries, but we don't really have a context to put it on either...
