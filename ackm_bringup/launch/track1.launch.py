import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import AppendEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node

from launch.actions import ExecuteProcess

def generate_launch_description():
    # Setup project paths
    pkg_project_bringup = get_package_share_directory('ackm_bringup')
    pkg_project_description = get_package_share_directory('ackm_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    
	# change path
    pkg_path = '/ws/ros_ws/src/sibotr2/'
    
    set_gazebo_model_path = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH', pkg_path
    )

    set_ros_pkg_path = AppendEnvironmentVariable(
        'ROS_PACKAGE_PATH', pkg_path  
    )
    
    set_show_path = ExecuteProcess(
		cmd=['bash', '-c', 'echo GZ=$GZ_SIM_RESOURCE_PATH && echo ROS=$ROS_PACKAGE_PATH'],
		output='screen'
	)

    # Load the SDF file from "description" package
    sdf_file  =  os.path.join(pkg_project_description, 'models', 'sibot', 'model.sdf')
    with open(sdf_file, 'r') as infp:
        robot_desc = infp.read()

    # Setup to launch the simulator and Gazebo world
    gz_sim_old = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': PathJoinSubstitution([
            pkg_project_description,
            'worlds',
            'track1.sdf'
        ])}.items(),
    )

    gz_sim = IncludeLaunchDescription(
		PythonLaunchDescriptionSource(
			os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
		launch_arguments={
			'gz_args': [
				PathJoinSubstitution([
					pkg_project_description,
					'worlds',
					'track1.sdf'
				]),
				' --verbose 4'
			]
		}.items(),
	)


    # Takes the description and joint angles as inputs and publishes the 3D poses of the robot links
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[
            {'use_sim_time': True},
            {'robot_description': robot_desc},
        ]
    )
    # Visualize in RViz
    rviz = Node(
       package='rviz2',
       executable='rviz2',
       arguments=['-d', os.path.join(pkg_project_bringup, 'rviz', 'robot.rviz')],
       condition=IfCondition(LaunchConfiguration('rviz'))
    )

    # launch rqt for control and video
    rqt = Node(
		package='rqt_gui',
		executable='rqt_gui',
		name='rqt',
		output='screen'
	)

    bridge = Node(
    # Bridge ROS topics and Gazebo messages for establishing communication
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': os.path.join(pkg_project_bringup, 'config', 'ros_gz_bridge_sibot.yaml'),
            'qos_overrides./tf_static.publisher.durability': 'transient_local',
        }],
        output='screen'
    )
    gz_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-topic', '/robot_description',
            '-name', 'sibot',
            '-allow_renaming', 'true',
            '-x', '-1',
            '-y', '-1.9',
            '-z', '0.05'
        ]
    )
    return LaunchDescription([
        set_gazebo_model_path,
        set_ros_pkg_path,
        set_show_path,
        gz_sim,
        gz_spawn_entity,
        DeclareLaunchArgument('rviz', default_value='false',
                              description='Open RViz.'),
        bridge,
        robot_state_publisher,
        rviz,
        rqt
    ])
