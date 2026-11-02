cmake_minimum_required(VERSION 3.8)
project(pushbot_description)

find_package(ament_cmake REQUIRED)

# No code to compile: just install the folders so ros2 launch / $(find ...) can locate them
install(DIRECTORY urdf launch rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
