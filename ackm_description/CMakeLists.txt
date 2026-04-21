cmake_minimum_required(VERSION 3.8)
project(ackm_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(rclcpp REQUIRED)
find_package(OpenCV REQUIRED)
find_package(std_msgs REQUIRED)
find_package(ament_cmake REQUIRED)
find_package(robot_state_publisher REQUIRED)
find_package(xacro REQUIRED)

find_package(gz-sim8 REQUIRED)
find_package(gz-rendering8 REQUIRED)
find_package(gz-transport13 REQUIRED)


if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

add_executable(videopanel src/videopanel.cpp)

ament_target_dependencies(videopanel
  rclcpp
  OpenCV
  std_msgs
  ament_index_cpp
)

install(TARGETS
  videopanel
  DESTINATION lib/${PROJECT_NAME}
)

add_library(gzDynamicPanelTexturePlugin SHARED src/gzDynamicTexturePlugin.cc)

target_link_libraries(gzDynamicPanelTexturePlugin
  gz-sim8::gz-sim8
  gz-rendering8::gz-rendering8
  gz-transport13::gz-transport13
  opencv_core
  opencv_imgcodecs
  opencv_imgproc
)

target_include_directories(gzDynamicPanelTexturePlugin PRIVATE
  ${OpenCV_INCLUDE_DIRS}
)

install(TARGETS
  gzDynamicPanelTexturePlugin
  LIBRARY DESTINATION lib
)

install(DIRECTORY
  models
  worlds
  hooks
  launch
  scripts
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()
