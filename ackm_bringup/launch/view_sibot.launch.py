#
import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
	
	pkg_project_bringup = get_package_share_directory('ackm_bringup')
	pkg_project_description = get_package_share_directory('ackm_description')

	sdf_file  =  os.path.join(pkg_project_description, 'models', 'sibot', 'model.sdf')
	
	with open(sdf_file, 'r') as infp:
		robot_desc = infp.read()

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
    
	#joint_state_publisher = Node(
    #    package='joint_state_publisher_gui',
    #    executable='joint_state_publisher_gui'
    #)
    
	rviz = Node(
       package='rviz2',
       executable='rviz2',
       arguments=['-d', os.path.join(pkg_project_bringup, 'rviz', 'robot.rviz')]
    )

	rqt = Node(
		package='rqt_gui',
		executable='rqt_gui',
		name='rqt',
		output='screen'
	)
	
	return LaunchDescription([
        robot_state_publisher,
        #joint_state_publisher,
        #rqt,
        rviz
    ])
