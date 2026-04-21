from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ackm_description',
            executable='videopanel',
            name='videopanel',
            output='screen',
            parameters=[
                {'source_package': 'ackm_description'},
                {'source_folder': 'models/videopanel/images'},
                {'name_pic0': 'left'},
                {'name_pic1': 'right'},
                {'name_pic2': 'up'},
                {'name_pic3': 'stop'},
                {'name_pic4': 'parking'},
                {'name_pic5': 'chess'},
                {'default_pic': 3}
            ]
        ),
    ])
    
