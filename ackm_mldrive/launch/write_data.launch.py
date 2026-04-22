from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():
    return LaunchDescription([

        ExecuteProcess(
            cmd=['/ws/venv/bin/python3',
                 '/ws/ros_ws/src/sibotr2/ackm_mldrive/scripts/write_data.py'],
            output='screen'
        )

    ])
