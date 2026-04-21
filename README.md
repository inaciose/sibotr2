# Mobile Robots Simulation in ROS2 with Gazebo Sim Harmonic
# Ackermann Steering Vehicle for FNR autonoumous driving contest 2022 track

Based on the work of alitekes available at:  
https://github.com/alitekes1/ackermann-vehicle-gzsim-ros2  


## Requirements

- **ROS2 (Humble)**
- **Gazebo Sim Harmonic**
- **RViz2**
- **Nav2**

## Docker image

```bash
docker pull inaciose/ros-jazzy-desktop:noble  
```

## Docker launcher

```bash
#!/usr/bin/env bash

xhost +local:

docker run -it --rm \
  --gpus all \
  --name jazzy \
  --net=host \
  --privileged \
  -e NVIDIA_DRIVER_CAPABILITIES=all \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e DISPLAY=$DISPLAY \
  -e QT_X11_NO_MITSHM=1 \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v /dev/bus/usb:/dev/bus/usb \
  -v ~/docker_ws/jazzy_ws:/ws \
  -w /ws \
  inaciose/ros-jazzy-desktop:noble \
  bash
```

## Local Installation

1. Clone and Build<br>
```bash
mkdir -p /ws/ros_ws/src && cd /ws/ros_ws/src
git clone https://github.com/inaciose/sibotr2
colcon build && source install/setup.bash
cd ..
```

## Usage

### 1. Basic Simulation and Manual Control

1.  Launch the simulation:
    ```bash
    ros2 launch ackm_bringup track1.launch.py
    ```

2.  panel signal change:
    ```bash
    # X: [0, 5]
    signal.sh signal.sh videopanelX
    ```

### 2. SLAM (Simultaneous Localization and Mapping)

-   To run SLAM Toolbox for mapping, launch the following after starting the simulation:
    ```bash
    ros2 launch ackm_bringup slam.launch.py
    ```

### 3. Navigation with Nav2

-   To run the simulation with the Nav2 stack for autonomous navigation, launch the following after starting the simulation:
    ```bash
    ros2 launch ackm_bringup navigation_bringup.launch.py
    ```

## Mo info
https://github.com/alitekes1/ackermann-vehicle-gzsim-ros2  



